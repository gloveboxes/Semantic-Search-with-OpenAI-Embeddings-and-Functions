''' This script will take a text column and create embeddings for each text using the OpenAI API.'''

import re
import os
import pandas as pd
import openai
from openai.embeddings_utils import get_embedding
import tiktoken

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

openai.api_type = "azure"
openai.api_key = API_KEY
openai.api_base = RESOURCE_ENDPOINT
openai.api_version = "2023-05-15"


# load df from a json file

# example: df = pd.read_csv("./data/bill_sum_data.csv")df
df = pd.read_json("./output/master_embeddings.json")

# df = pd.read_csv("./output/master_summarized.csv") # example: df = pd.read_csv("./data/bill_sum_data.csv")df
print(df)


df_sessions = df[['text', 'videoId', 'description', 'title', 'speaker', 'start', 'summary']].fillna("")
print(df_sessions)


# s is input text
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


df_sessions['text'] = df_sessions["text"].apply(lambda x: normalize_text(x))


tokenizer = tiktoken.get_encoding("cl100k_base")
df_sessions['n_tokens'] = df_sessions["text"].apply(
    lambda x: len(tokenizer.encode(x)))
df_sessions = df_sessions[df_sessions.n_tokens < 8192]
len(df_sessions)


# engine should be set to the deployment name you chose when you deployed the text-embedding-ada-002 (Version 2) model
df_sessions['ada_v2'] = df_sessions["text"].apply(lambda x: get_embedding(x, engine='text-embedding-ada-002'))

# drop the text column
# df_sessions = df_sessions.drop(columns=["text"])

# save the embeddings to a json file
df_sessions.to_json("./output/master_embeddings.json", orient="records")
