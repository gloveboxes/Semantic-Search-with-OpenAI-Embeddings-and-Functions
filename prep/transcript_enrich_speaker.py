''' This script will get the speaker name from the YouTube video metadata and the first minute of the transcript using the OpenAI Functions entity extraction.'''

import sys
import json
import os
import glob
import threading
import queue
import random
import time
import argparse
import openai


API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
TRANSCRIPT_FOLDER = 'transcripts'
PROCESSING_THREADS = 5
SEGMENT_MIN_LENGTH_MINUTES = 2

OPENAI_MAX_TOKENS = 1024
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = os.environ['AZURE_OPENAI_MODEL_DEPLOYMENT_NAME']


openai.api_type = "azure"
openai.api_key = API_KEY
openai.api_base = RESOURCE_ENDPOINT
openai.api_version = "2023-07-01-preview"

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder")
args = parser.parse_args()

TRANSCRIPT_FOLDER = args.folder if args.folder else TRANSCRIPT_FOLDER


get_speaker_name = {
    "name": "get_speaker_name",
    "description": "Get the speakers name for the session.",
    "parameters": {
        "type": "object",
        "properties": {
            "speaker_name": {
                "type": "string",
                "description": "The speakers name"
            }
        },
        "required": ["speaker_name"]
    }
}

openai_functions = [
    get_speaker_name
]


# these maps are used to make the function name string to the function call
definition_map = {"get_speaker_name": get_speaker_name}

q = queue.Queue()


class Counter:
    '''thread safe counter'''

    def __init__(self):
        '''initialize the counter'''
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        '''increment the counter'''
        with self.lock:
            self.value += 1
            return self.value


counter = Counter()

def get_speaker_info(text):
    '''Gets the OpenAI functions from the text.'''

    request_retry_time = 5 + random.randint(0, 5)

    function_name = None
    arguments = None

    try:
        response_1 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": "Don't try and guess the speakers name if unsure."},
                {"role": "user", "content": text},
            ],
            functions=openai_functions,
            temperature=0.0,
            max_tokens=OPENAI_MAX_TOKENS,
            engine=AZURE_OPENAI_MODEL_DEPLOYMENT_NAME,
        )

        # The assistant's response includes a function call. We extract the arguments from this function call

        result = response_1.get('choices')[0].get('message')

        if result.get("function_call"):
            function_name = result.get("function_call").get("name")
            arguments = json.loads(result.get("function_call").get("arguments"))

        return function_name, arguments
    
    except openai.error.InvalidRequestError as invalid_request_exception:
        print_to_stderr(f"Invalid request: {invalid_request_exception}")
        print_to_stderr(f"Error with segment: {text}")
        # just return the original text
        return text

    # https://callmefred.com/how-to-fix-openai-error-ratelimiterror-the-server-had-an-error/
    # https://platform.openai.com/docs/guides/error-codes/handling-errors

    except openai.error.RateLimitError:
        print_to_stderr(
            f"Rate limit exceeded. Retrying in {request_retry_time} seconds...")
        time.sleep(request_retry_time)
        return get_speaker_info(text)

    except openai.error.APIError:
        print_to_stderr(f"API error occurred. Retrying in {request_retry_time} seconds...")
        time.sleep(request_retry_time)
        return get_speaker_info(text)

    except openai.error.ServiceUnavailableError:
        print_to_stderr(
            f"Service is unavailable. Retrying in {request_retry_time} seconds...")
        time.sleep(request_retry_time)
        return get_speaker_info(text)

    except openai.error.Timeout as timeout_exception:
        print_to_stderr(
            f"Request timed out: {timeout_exception}. Retrying in {request_retry_time} seconds...")
        time.sleep(request_retry_time)
        return get_speaker_info(text)

    except openai.error.OpenAIError as openai_error_exception:
        print_to_stderr(
            f"OpenAI error occurred: {openai_error_exception}. Retrying in {request_retry_time} seconds...")
        time.sleep(request_retry_time)
        return get_speaker_info(text)

    except Exception as general_exception:
        print_to_stderr(general_exception)
        print_to_stderr("Error with chunk: ", text)
        return function_name, arguments



def print_to_stderr(*a):
    '''print to stderr'''
    # Here a is the array holding the objects
    # passed as the argument of the function
    print(*a, file=sys.stderr)

def clean_text(text):
    '''clean the text'''
    text = text.replace('\n', '') # remove new lines
    text = text.replace('&#39;', "'")
    text = text.replace('>>', '') # remove '>>'
    text = text.replace('  ', ' ') # remove double spaces

    return text


def get_first_segment(file_name):
    '''Gets the first segment from the filename'''

    text = ""
    current_seconds = None
    segment_begin_seconds = None
    segment_finish_seconds = None

    vtt = file_name.replace('.json', '.json.vtt')

    with open(vtt, 'r', encoding='utf-8') as json_file:
        json_vtt = json.load(json_file)

        for segment in json_vtt:
            current_seconds = segment.get('start')

            if segment_begin_seconds is None:
                segment_begin_seconds = current_seconds
                # calculate the finish time from the segment_begin_time
                segment_finish_seconds = segment_begin_seconds + SEGMENT_MIN_LENGTH_MINUTES * 60

            if current_seconds < segment_finish_seconds:
                # add the text to the transcript
                text += clean_text(segment.get('text')) + " "

    return text

def process_queue():
    '''process the queue'''
    while not q.empty():
        filename = q.get()

        file_number = counter.increment()

        with open(filename, 'r', encoding='utf-8') as json_file:

            metadata = json.load(json_file)
            if 'speaker' in metadata and metadata['speaker'] != '':
                print_to_stderr("Speaker already exists for " + filename + " is " + metadata['speaker'])
                continue

            base_text = metadata['description'] + " " + get_first_segment(filename)
            # replace new line with empty string
            base_text = base_text.replace('\n', ' ')

            function_name, arguments = get_speaker_info(base_text)

            if function_name is not None:
                speaker = arguments.get('speaker_name')
                if speaker == 'unknown' or speaker == '[inaudible]':
                    print_to_stderr("Speaker not found for " + filename)
                    continue

                print_to_stderr(f"File {file_number}  {filename} is " + speaker)
                metadata['speaker'] = speaker
                json.dump(metadata, open(filename, 'w', encoding='utf-8'))
            else:
                print_to_stderr("Speaker not found for " + filename)

        q.task_done()
        time.sleep(0.2)


print_to_stderr(f"Transcription folder {TRANSCRIPT_FOLDER}")
print_to_stderr("Starting Speaker Update")

# load all the transcript json files into the queue
folder = os.path.join(TRANSCRIPT_FOLDER, '*.json')

for filename in glob.glob(folder):
    # load the json file
    q.put(filename)


print_to_stderr("Starting speaker name update. Files to be processed: ", q.qsize())
start_time = time.time()

# create multiple threads to process the queue
threads = []
for i in range(PROCESSING_THREADS):
    t = threading.Thread(target=process_queue)
    t.start()
    threads.append(t)

# wait for all threads to finish
for t in threads:
    t.join()

finish_time = time.time()
print_to_stderr("Finished speaker name update. Total time taken: ", finish_time - start_time)
