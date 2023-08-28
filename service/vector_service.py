
''' app to search through the session data using the vector embeddings'''
# https://github.com/gloveboxes/OpenAI-Whisper-Transcriber-Sample/blob/master/server/main.py

from typing import Any
import os
import openai
import pandas as pd
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


# load the session data from csv file
df_sessions = pd.read_csv('../master_embeddings.csv')
# convert the embedding column from string to list
df_sessions['ada_v2'] = df_sessions['ada_v2'].apply(lambda x: eval(x))

# {'videoId': 'LK-3YtMIel8', 'description': 'Women make up 31% of...anisation.', 'title': 'Attraction and reten...en in tech', 'speaker': 'Donna Edwards', 'similarities': 0.8331244588766407}


class Session(BaseModel):
    videoId: str
    description: str
    title: str
    speaker: str
    similarities: float


@app.get("/search", status_code=200, response_model=list[Session])
async def create_upload_file(query: str, top_n: int = 6) -> Any:
    '''search the documents using the user query and return the top_n results'''

    embedding = get_embedding(
        query,
        # engine should be set to the deployment name you chose when you deployed the text-embedding-ada-002 (Version 2) model
        engine="text-embedding-ada-002"
    )

    df_sessions["similarities"] = df_sessions.ada_v2.apply(
        lambda x: cosine_similarity(x, embedding))

    res = (
        df_sessions.sort_values("similarities", ascending=False)
        .drop_duplicates("title")
        .head(top_n)
        .drop(columns=["ada_v2"])
        .drop(columns=["n_tokens"])
        .fillna("")
    ).to_dict('records')

    return res

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5500)
