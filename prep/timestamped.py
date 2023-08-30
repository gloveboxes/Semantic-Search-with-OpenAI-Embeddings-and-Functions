''' This script generates a master csv file from the transcript files.'''

# from the transcript files, generate a master csv file
# from the transcript folder read all the .json files then load the associated .vtt file

from datetime import datetime, timedelta
import glob
import os
import json
import csv
import re


segments = []
SEGMENT_MIN_LENGTH = 5


def parse_vtt_transcript(vtt, segment):
    '''parse the vtt file and return the transcript'''
    # segments = []
    text = ""
    current_time = None
    segment_begin_time = None
    segment_finish_time = None
    segment_count = 0

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
                    current_time = datetime.strptime(time_stamps[0], "%H:%M:%S.%f")
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
                    # add 15% of the text to the previous segment
                    words = text.split(' ')
                    word_count = len(words)
                    if word_count > 0:
                        append_text = ' '.join(words[0: int(word_count * 0.15)])
                        segments[-1]['text'] += append_text

                segment_count += 1
                segment['start'] = segment_begin_time.strftime('%H:%M:%S')
                segment['text'] = text
                segments.append(segment.copy())
                # reset the segment_begin_time
                text = line
                segment_begin_time = None
                segment_finish_time = None

    # add the last text segment segments dictionary
    if segment_begin_time is not None and text != "":
        segments[-1]['text'] += text


def get_transcript(meta):
    '''get the transcript from the .vtt file'''
    vtt = './prep/transcripts/' + meta['videoId'] + '.vtt'

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
        print("vtt file does not exist: ", vtt)
        return None

    parse_vtt_transcript(vtt, meta)


for file in glob.glob("./prep/transcripts/*.json"):

    # load the json file
    meta = json.load(open(file, encoding='utf-8'))

    get_transcript(meta)

# gen_overlapping_segments()

# # write the sessions to a csv file
with open('master.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['videoId', 'title',
                  'description', 'speaker', 'start', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for segment in segments:
        writer.writerow(segment)
