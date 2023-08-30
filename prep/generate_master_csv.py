''' This script generates a master csv file from the transcript files.'''

# from the transcript files, generate a master csv file
# from the transcript folder read all the .json files then load the associated .vtt file

import glob
import os
import json
import csv
import re
from langchain.text_splitter import TokenTextSplitter

# allow for a 15% overlap between chunks
# https://platform.openai.com/docs/api-reference/embeddings/create
text_splitter = TokenTextSplitter(chunk_size=8191, chunk_overlap=1200)

sessions = []


def get_transcript(meta):
    '''get the transcript from the .vtt file'''
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
        print("vtt file does not exist: ", vtt)
        return None

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
                continue

            # replace the string Caption: with empty string
            line = line.replace('Caption:', '')

            # replace new line with empty string
            line = line.replace('\n', '')

            # replace &#39; with '
            line = line.replace('&#39;', "'")

            text += line
    return text


for file in glob.glob("./transcripts/*.json"):

    # load the json file
    meta = json.load(open(file))

    transcript = get_transcript(meta)
    if transcript is None:
        continue

    split_text = text_splitter.split_text(transcript)

    for chunk in split_text:
        meta['text'] = chunk
        sessions.append(meta.copy())


# # write the sessions to a csv file
with open('master.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['videoId', 'title', 'description', 'speaker', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for session in sessions:
        writer.writerow(session)