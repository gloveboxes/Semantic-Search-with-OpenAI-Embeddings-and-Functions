# Semantic Search with OpenAI Embeddings

## Overview

Solution takes over 100 hours of conference transcriptions with the objective of making the transcriptions semantic searchable.

1. generate_master_csv.py: Cleans up the vtt transcripts, strips out vtt metadata, splits large blocks of text into chunks to fall inside of OpenAI token limits for embeddings.
All the session metadata and transcripts are saved to the master.csv file
1. generate_session_embedding.ipynb: loads the master.csv file into a pandas dataframe and calls OpenAI Embeddings to generate vectors for each session transcript.
The pandas dataframe is then saved to master_embeddings.csv
1. vector_search.py: loads the master_embeddings.csv into a pandas dataframe and prompts user for a query. The query is vectorized, then cosine_similarity used to find "nearest neighbor" for the query against the vectorized session transcripts.
1. vector_service.py: FastAPI service that loads the master_embeddings.csv into a pandas dataframe and exposes a REST API to query the vectorized session transcripts.
1. search.py: A simple PySimpleGUI app that prompts the user for a query and calls the vector_service.py REST API to find the "nearest neighbor" for the query against the vectorized session transcripts.

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

        Once the Vector Search Service starts, you should see output similar to the following.

        ```text
        INFO:     Started server process [18560]
        INFO:     Waiting for application startup.
        INFO:     Application startup complete.
        INFO:     Uvicorn running on http://0.0.0.0:5500 (Press CTRL+C to quit)
        ```

9. View the Swagger Docs for the Vector Search Service.

    1. Open a browser and navigate to `http://localhost:5500/docs`.
    2. Select the **GET** button.
    3. Select the **Try it out** button.
    4. Set the **query** parameter to `vs code`.
    5. Set the **top_n** parameter to `1`.
    6. Select the **Execute** button.
    7. Scroll down to the **Response Body** section. You should see output similar to the following.

        ```json
        [
            {
                "videoId": "0gZO79pGBow",
                "description": "VS Code is hot, there's no doubt about it being an utterly amazing editor, but I ask you, are you using it to its full potential? Let's go on a journey together and look to unlock the real power that you can get out of VS Code. Whether it's with shortcuts or extensions, environment standardisation and remote development, collaboration to integrations, there's so many things to uncover that can take you from a user to a pro in no time.\\n\\nThis session will leave you itching to get back into your editor and code up a storm on that next piece of work.\\n\\nNo experience necessary\\n45 mins\\nCore/Non Technical Skills\\nAaron is a Developer Advocate at Microsoft. Having spent 15 years doing web development he's seen it all, from browser wars, the rise of AJAX and the fall of 20 JavaScript frameworks (and that was just yesterday!). Always tinkering with something new he explores crazy ideas like writing your own implementation of numbers in .NET, creating IoC in JavaScript or implementing tic-tac-toe using git commits.",
                "title": "Unleash the Power of VS Code",
                "speaker": "Aaron Powell",
                "similarities": 0.8550920247945629
            }
        ]
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

    > **Note:** You can pass the host and port of the Vector Search Service as a command line argument. For example, to connect to a Vector Search Service running on `http://rpi44:5500`, run `python3 search.py http://rpi44:5500`.

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
