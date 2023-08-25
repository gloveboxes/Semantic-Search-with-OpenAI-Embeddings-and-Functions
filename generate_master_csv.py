# from the transcript files, generate a master csv file
# from the transcipt folder read all the .json files

import glob
import os
import json
import csv
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.text_splitter import TokenTextSplitter
# from langchain.text_splitter import CharacterTextSplitter
import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")


# text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
#     chunk_size=6000, chunk_overlap=820
# )

r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=8192 * 4,
    chunk_overlap=3200
)

sessions = []

for file in glob.glob("./transcripts/*.json"):

    # load the json file
    meta = json.load(open(file))

    vtt = './transcripts/' + meta['videoId'] + '.vtt'
    text = ""

    # check that the .vtt file exists
    if not os.path.exists(vtt):
        print("vtt file does not exist: ", vtt)
        continue

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


    split_text = r_splitter.split_text(text)

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
