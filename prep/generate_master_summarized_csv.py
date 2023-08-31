''' This script generates a master csv file from the transcript files.'''

# from the transcript files, generate a master csv file
# from the transcript folder read all the .json files then load the associated .vtt file

import glob
import os
import json
import csv
import re
import openai
from langchain.text_splitter import TokenTextSplitter

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

openai.api_type = "azure"
openai.api_key = API_KEY
openai.api_base = RESOURCE_ENDPOINT
openai.api_version = "2023-07-01-preview"

# allow for a 15% overlap between chunks
# https://platform.openai.com/docs/api-reference/embeddings/create
text_splitter = TokenTextSplitter(chunk_size=768, chunk_overlap=80)

sessions = []


def get_transcript(meta):
    '''get the transcript from the .vtt file'''
    vtt = './prep/transcripts/' + meta['videoId'] + '.vtt'

    text = ""

    meta['start'] = "00:00:00"

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


count = 0

for file in glob.glob("./prep/transcripts/*.json"):

    count += 1
    print(count)
    # if count > 10:
    #     break

    # load the json file
    meta = json.load(open(file))

    transcript = get_transcript(meta)
    if transcript is None:
        continue

    split_text = text_splitter.split_text(transcript)
    text = ""

    for chunk in split_text:

        try:

            messages = [{"role": "system", "content": "Condense this youtube transcript suitable for experts."},
                        {"role": "user", "content": chunk}]

            response = openai.ChatCompletion.create(
                engine="glovebox-chat",
                messages=messages,
                temperature=0.2,
                max_tokens=512,
                top_p=0.0,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)

            print(response.choices[0]['message']['content'])
            text += response.choices[0]['message']['content']

        except Exception as e:
            print(e)
            print("Error with chunk: ", chunk)
            continue

    meta['text'] = text
    sessions.append(meta.copy())


# # write the sessions to a csv file
with open('master_summarized.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['videoId', 'start', 'title',
                  'description', 'speaker', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for session in sessions:
        writer.writerow(session)
