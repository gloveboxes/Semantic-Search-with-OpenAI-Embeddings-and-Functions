''' This script will take a text column and create embeddings for each text using the OpenAI API.'''

import sys
import re
import os
import json
import threading
import queue
import time
import openai
from openai.embeddings_utils import get_embedding
import tiktoken

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
PROCESSING_THREADS = 6

openai.api_type = "azure"
openai.api_key = API_KEY
openai.api_base = RESOURCE_ENDPOINT
openai.api_version = "2023-05-15"

tokenizer = tiktoken.get_encoding("cl100k_base")

total_segments = 0
current_segment = 0
output_segments = []


def print_to_stderr(*a):
    '''print to stderr'''
    # Here a is the array holding the objects
    # passed as the argument of the function
    print(*a, file=sys.stderr)


print_to_stderr("Starting OpenAI Embeddings")


# load sessions_list from json file
with open("./output/master_enriched.json", "r", encoding='utf-8') as f:
    segments = json.load(f)

total_segments = len(segments)


def normalize_text(s, sep_token=" \n "):
    '''normalize text by removing extra spaces and newlines'''
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,", "", s)
    # remove all instances of multiple spaces
    s = s.replace("..", ".")
    s = s.replace(". .", ".")
    s = s.replace("\n", "")
    s = s.strip()

    return s

def get_text_embedding(text):
    '''get the embedding for a text'''

    embedding = None

    try:
        embedding = get_embedding(text, engine='text-embedding-ada-002')
    except Exception as e:
        print(e)
        print("Retrying...")
        time.sleep(5)
        get_text_embedding(text)

    return embedding


def process_queue():
    '''process the queue'''
    while not q.empty():
        segment = q.get()

        # if 'ada_v2' in segment:
        #     output_segments.append(segment.copy())
        #     continue
        print(segment['title'])
        text = segment['text']

        if len(tokenizer.encode(text)) > 8191:
            continue

        text = normalize_text(text)
        segment['text'] = text

        embedding = get_text_embedding(text)
        if embedding is None:
            output_segments.append(segment.copy())
            continue

        segment['ada_v2'] = embedding.copy()
        
        output_segments.append(segment.copy())
        q.task_done()
        time.sleep(0.2)


print_to_stderr("Total segments to be processed: ", len(segments))

# add segment list to a queue
q = queue.Queue()
for segment in segments:
    q.put(segment)

# create multiple threads to process the queue
threads = []
for i in range(PROCESSING_THREADS):
    t = threading.Thread(target=process_queue)
    t.start()
    threads.append(t)

# wait for all threads to finish
for t in threads:
    t.join()

# convert time '00:01:20' to seconds
def convert_time_to_seconds(value):
    '''convert time to seconds'''
    time_value = value.split(':')
    if len(time_value) == 3:
        h, m, s = time_value
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
        return 0


# sort the output segments by videoId and start
output_segments.sort(key=lambda x: (x['videoId'], convert_time_to_seconds(x['start'])))

print_to_stderr("Total segments processed: ", len(output_segments))

# save the embeddings to a json file
with open("./output/master_enriched.json", "w", encoding='utf-8') as f:
    json.dump(output_segments, f, indent=4)
