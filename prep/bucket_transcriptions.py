''' This script generates a master csv file from the transcript files.'''

# from the transcript files, generate a master csv file
# from the transcript folder read all the .json files then load the associated .vtt file

from datetime import datetime, timedelta
import glob
import os
import json
import re


segments = []
SEGMENT_MIN_LENGTH = 5
PERCENTAGE_OVERLAP = 0.05

total_segments = 0
total_files = 0


def print_to_stderr(*a):
    '''print to stderr'''
    # Here a is the array holding the objects
    # passed as the argument of the function
    print(*a, file=sys.stderr)

def gen_metadata_master(meta):
    '''generate the metadata master csv file'''
    text = meta['title'] + " " + meta['description']
    meta['start'] = '00:00:00'

    text = text.strip()

    if text == "" or text is None:
        meta['text'] = "No description available."
    else:
        # clean the text
        text = text.replace('\n', '')
        meta['text'] = text.strip()


def parse_vtt_transcript(vtt, segment):
    '''parse the vtt file and return the transcript'''
    global total_segments
    # segments = []
    text = ""
    current_time = None
    segment_begin_time = None
    segment_finish_time = None
    segment_count = 0

    # add the speaker name to the transcript
    if 'speaker' in meta:
        text = "The speaker's name is " + meta['speaker'] + "."
    # add the title to the transcript
    if 'title' in meta:
        text += meta['title'] + "."

    # add the description to the transcript
    if 'description' in meta:
        text += meta['description'] + "."

    # open the vtt file
    with open(vtt, 'r', encoding='utf-8') as f:
        # read the file line by line
        for line in f:
            # ignore the empty lines
            if line == '\n':
                continue

            # ignore line with WEBVTT\n
            if line == 'WEBVTT\n':
                continue

            # ignore the line with time stamps
            if re.match(r'^\d', line):

                time_stamps = line.split(' --> ')

                try:
                    current_time = datetime.strptime(
                        time_stamps[0], "%H:%M:%S.%f")
                except ValueError:
                    continue

                if segment_begin_time is None:
                    # get the time stamps

                    segment_begin_time = current_time
                    # calculate the finish time from the segment_begin_time by adding 5 minutes
                    segment_finish_time = segment_begin_time + \
                        timedelta(minutes=SEGMENT_MIN_LENGTH)

                continue

            if current_time is None:
                continue

            # replace the string Caption: with empty string
            line = line.replace('Caption:', '')

            # replace new line with empty string
            line = line.replace('\n', '')

            # replace &#39; with '
            line = line.replace('&#39;', "'")

            if current_time < segment_finish_time:
                # add the text to the transcript
                text += line
            else:
                # add 15% of the text to the previous segment
                if segment_count > 0:
                    # add % of the text to the previous segment
                    words = text.split(' ')
                    word_count = len(words)
                    if word_count > 0:
                        append_text = ' '.join(
                            words[0: int(word_count * PERCENTAGE_OVERLAP)])
                        segments[-1]['text'] += append_text

                segment_count += 1
                total_segments += 1
                segment['start'] = segment_begin_time.strftime('%H:%M:%S')
                segment['text'] = text
                segments.append(segment.copy())
                # reset the segment_begin_time
                text = line
                segment_begin_time = None
                segment_finish_time = None

    # Append the last text segment to the last segment in segments dictionary
    if segment_begin_time is not None and text != "":
        segments[-1]['text'] += text


def get_transcript(meta):
    '''get the transcript from the .vtt file'''
    global total_files
    vtt = './transcripts/' + meta['videoId'] + '.vtt'

    text = ""

    # add the speaker name to the transcript
    if 'speaker' in meta:
        text = "The speaker's name is " + meta['speaker'] + "."
    # add the title to the transcript
    if 'title' in meta:
        text += meta['title'] + "."

    # add the description to the transcript
    if 'description' in meta:
        text += meta['description'] + "."

    # check that the .vtt file exists
    if not os.path.exists(vtt):
        print_to_stderr("vtt file does not exist: ", vtt)
        return None
    else:
        print_to_stderr("Processing file: ", vtt)
        total_files += 1

    parse_vtt_transcript(vtt, meta)


for file in glob.glob("./transcripts/*.json"):

    # load the json file
    meta = json.load(open(file, encoding='utf-8'))

    get_transcript(meta)


print_to_stderr("Total files: ", total_files)
print_to_stderr("Total segments: ", total_segments)

# save segments to a json file
with open('./output/master_transcriptions.json', 'w', encoding='utf-8') as f:
    json.dump(segments, f, ensure_ascii=False, indent=4)
