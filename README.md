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

4. Activate the Python virtual environment.

    on Windows

    ```pwsh
    .\.embeddings_venv\Scripts\activate
    ```

    on macOS and Linux

    ```bash
    source .embeddings_venv/bin/activate
    ```

5. Install the required Python libraries.

    ```bash
    pip3 install -r requirements.txt
    ```

6. Create an Azure OpenAI Service Resource
   
   1. [Create and deploy an Azure OpenAI Service resource](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource?pivots=web-portal)
   2. [Deploy the text-embedding-ada-002 (Version 2) model](https://learn.microsoft.com/azure/ai-services/openai/tutorials/embeddings?tabs=command-line). Name the deployment `text-embedding-ada-002`.

7. Export the following environment variables.

    1. Open the Azure portal and navigate to the Azure OpenAI Service resource you created.
    2. Select **Keys and Endpoint**.
    3. Open a terminal window.
    4. Export the Azure OpenAI Service API key and endpoint to the environment variables.

        On Windows

        ```pwsh
        $env:AZURE_OPENAI_API_KEY="<your Azure OpenAI API key>"
        $env:AZURE_OPENAI_ENDPOINT="<your Azure OpenAI Endpoint>"
        ```

        On macOS and Linux

        ```bash
        export AZURE_OPENAI_API_KEY=<your Azure OpenAI API key>
        export AZURE_OPENAI_ENDPOINT=<your Azure OpenAI Endpoint>
        ```

    5. **Don't** close the terminal window. You will need it in the next step.

8.   Start the Vector Search Service. From the command line, run:

        From the command line opened in the previous step, run:

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
    .\.embeddings_venv\Scripts\activate
    ```

    on macOS and Linux

    ```bash
    source .embeddings_venv/bin/activate
    ```

1. Install the required Python libraries.

    ```bash
    pip3 install -r requirements.txt
    ```

    On Ubuntu, you may need to install tkinter.

    ```bash
    sudo apt-get install python3-tk
    ```

1. Start the Vector Search Client. From the command line, run:

    ```bash
    python3 search.py
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
