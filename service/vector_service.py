
''' app to search through the session data using the vector embeddings'''
# https://github.com/gloveboxes/OpenAI-Whisper-Transcriber-Sample/blob/master/server/main.py


import os
import openai
import pandas as pd
from typing import List
from pydantic import BaseModel
from openai.embeddings_utils import get_embedding, cosine_similarity
from fastapi import FastAPI, UploadFile, Response, status, Request
import uvicorn

app = FastAPI()

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

openai.api_type = "azure"
openai.api_key = API_KEY
openai.api_base = RESOURCE_ENDPOINT
openai.api_version = "2023-05-15"


# load the session data from json file
df_sessions = pd.read_json('../prep/output/master_embeddings.json')


class Session(BaseModel):
    videoId: str
    start: str
    speaker: str
    title: str
    description: str
    # text: str
    summary: str
    similarities: float

# https://fastapi.tiangolo.com/tutorial/response-model/#__tabbed_1_3 Compatible with Python 3.6+


@app.get("/search", status_code=200)
async def create_upload_file(query: str, top_n: int = 6, dedup: bool = True) -> List[Session]:
    '''search the documents using the user query and return the top_n results'''

    embedding = get_embedding(
        query,
        # engine should be set to the deployment name you chose when you deployed the text-embedding-ada-002 (Version 2) model
        engine="text-embedding-ada-002"
    )

    df_sessions["similarities"] = df_sessions.ada_v2.apply(
        lambda x: cosine_similarity(x, embedding))

    # df_metadata["similarities"] = df_metadata.ada_v2.apply(
    #     lambda x: cosine_similarity(x, embedding))

    # df_merged = pd.concat([df_metadata, df_sessions])

    df_merged = df_sessions

    if dedup:
        res = (
            df_merged.sort_values("similarities", ascending=False)
            .drop_duplicates("videoId")
        )
    else:
        res = df_merged.sort_values("similarities", ascending=False)

    res = (
        res.head(top_n)
        .drop(columns=["ada_v2"])
        .drop(columns=["n_tokens"])
        .drop(columns=["text"])
        .fillna("")
    ).to_dict('records')

    return res

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5500)
