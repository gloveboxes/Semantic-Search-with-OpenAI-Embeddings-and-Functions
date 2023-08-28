# Embeddings_vector_search

## Overview

Solution takes over 100 hours of conference transcriptions with the objective of making the transcriptions semantic searchable.

1. generate_master_csv.py: Cleans up the vtt transcripts, strips out vtt metadata, splits large blocks of text into chunks to fall inside of OpenAI token limits for embeddings.
All the session metadata and transcripts are saved to the master.csv file
1. generate_session_embedding.ipynb: loads the master.csv file into a pandas dataframe and calls OpenAI Embeddedings to generate vectors for each session transcript.
The pandas dataframe is then saved to master_embeddings.csv
1. vector_search.py: loads the master_embeddings.csv into a pandas dataframe and prompts user for a quesy. The query is vectorised, then cosine_similarity used to find "nearest neighbour" for the query against the vectorised session transcripts.

## Create a Vector Search Endpoint

1. Clone the Whisper Transcriber Sample to your preferred repo folder.

    ```bash
    git clone https://github.com/gloveboxes/Embeddings_vector_search.git
    ```

2. Navigate to the `service` folder.

    ```bash
    cd Embeddings_vector_search/service
    ```

3. Create a Python virtual environment.

   on Windows

    ```pwsh
    python -m venv .embeddings_venv
    ```

    on macOS and Linux

    ```bash
    python3 -m venv .embeddings_venv
    ```

5. Activate the Python virtual environment.

    on Windows

    ```pwsh
    .\.whisper-venv\Scripts\activate
    ```

    on macOS and Linux

    ```bash
    source .whisper-venv/bin/activate
    ```

5. Install the required Python libraries.

    ```bash
    pip3 install -r requirements.txt
    ```

6.   Start the Vector Search Service. From the command line, run:

        ```bash
        uvicorn vector_service:app --port 5500 --host 0.0.0.0
        ```

        Once the Whisper Transcriber Service starts, you should see output similar to the following.

        ```text
        INFO:     Started server process [18560]
        INFO:     Waiting for application startup.
        INFO:     Application startup complete.
        INFO:     Uvicorn running on http://0.0.0.0:5500 (Press CTRL+C to quit)
        ```

## Start the Vector Search Client

1. Navigate to the `client` folder.

    ```bash
    cd Embeddings_vector_search/client
    ```

1. Create a Python virtual environment.

    ```bash
    python3 -m venv .embeddings_venv
    ```

1. Activate the Python virtual environment.

    ```bash
    source .embeddings_venv/bin/activate
    ```

1. Install the required Python libraries.

    ```bash
    pip3 install -r requirements.txt
    ```

1. Start the Vector Search Client. From the command line, run:

    ```bash
    python3 vector_search.py
    ```

1. Enter a query and press enter.

    ```text
    Enter a query:  sessions about solution architecture
    ```


## References

1. [OpenAI Guide to Embeddings](https://platform.openai.com/docs/guides/embeddings)
1. [Azure OpenAI Service REST API reference](https://learn.microsoft.com/azure/ai-services/openai/reference)
1. [Tutorial: Explore Azure OpenAI Service embeddings and document search](https://learn.microsoft.com/azure/ai-services/openai/tutorials/embeddings?tabs=command-line)
1. [Understanding vector search - excellent YT video on embeddings, highly recommended](https://www.youtube.com/watch?v=xzHhZh7F25I)
1. [Hugging face Embeddings leaderboard](https://huggingface.co/blog/mteb)
