# Transcription data prep

The transcription data prep scripts download YouTube video transcripts and prepare them for use with the Semantic Search with OpenAI Embeddings and Functions sample.

The transcription data prep scripts have been tested on the latest releases Windows 11, macOS Ventura and Ubuntu 20.04 (and above).

## Create required Azure OpenAI Service resources

1. Create an Azure OpenAI Service resource.
2. Deploy the following models:
   - `text-embedding-ada-002` version `2` or greater, named `text-embedding-ada-002`
   - `gpt-35-turbo` version `0613` or greater, named `gpt-35-turbo`

## Environment variables

The following environment variables are required to run the YouTube transcription data prep scripts.

## Required software

- [Python 3.8](https://www.python.org/downloads/) or greater

### On Windows

Recommend adding the variables to your `user` environment variables. 
`Windows Start` > `Edit the system environment variables` > `Environment Variables` > `User variables` for <user> > `New`.

```text
AZURE_OPENAI_API_KEY  \<your Azure OpenAI Service API key>
AZURE_OPENAI_ENDPOINT \<your Azure OpenAI Service endpoint>
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME \<your Azure OpenAI Service model deployment name>
AZURE_OPENAI_GPT_DEPLOYMENT_NAME \< your Azure OpenAI gpt-35-turbo (or above) model deployment name>
GOOGLE_DEVELOPER_API_KEY = \<your Google developer API key>
``````

<!-- You can add the environment variables to your PowerShell profile.

```powershell
$env:AZURE_OPENAI_API_KEY = "<your Azure OpenAI Service API key>"
$env:AZURE_OPENAI_ENDPOINT = "<your Azure OpenAI Service endpoint>"
$env:AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = "<your Azure OpenAI Service model deployment name>"
$env:AZURE_OPENAI_GPT_DEPLOYMENT_NAME \< your Azure OpenAI gpt-35-turbo (or above) model deployment name>
$env:GOOGLE_DEVELOPER_API_KEY = "<your Google developer API key>"
``` -->

### On Linux and macOS

Recommend adding the following exports to your `~/.bashrc` or `~/.zshrc` file.

```bash
export AZURE_OPENAI_API_KEY=<your Azure OpenAI Service API key>
export AZURE_OPENAI_ENDPOINT=<your Azure OpenAI Service endpoint>
export AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=<your Azure OpenAI Service model deployment name>
export AZURE_OPENAI_GPT_DEPLOYMENT_NAME \< your Azure OpenAI gpt-35-turbo (or above) model deployment name>
export GOOGLE_DEVELOPER_API_KEY=<your Google developer API key>
```

## Set up Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Install the required Python libraries

1. Install the [git client](https://git-scm.com/downloads) if it's not already installed.
1. From a `Terminal` window, clone the Semantic Search with OpenAI Embeddings and Functions sample to your preferred repo folder.
    ```bash
    git clone https://github.com/gloveboxes/semanic-search-openai-embeddings-functions.git
    ```
1. Navigate to the `data_prep` folder.
   ```bash
   cd semanic-search-openai-embeddings-functions/data_prep
   ```
1. Create a Python virtual environment.

    On Windows:

    ```powershell
    python -m venv .venv
    ```
    On macOS and Linux:

    ```bash
    python3 -m venv .venv
    ```
2. Activate the Python virtual environment.
   
   On Windows:
   ```powershell
   .venv\Scripts\activate
   ```
   On macOS and Linux:
   ```bash
   source .venv/bin/activate
   ```
3. Install the required libraries.

   On windows:

   ```powershell
   pip install -r requirements.txt
   ```

   On macOS and Linux:

   ```bash
   pip3 install -r requirements.txt
   ```

## Run the YouTube transcription data prep scripts

### On windows

```powershell
.\transcripts_prepare.ps1
```

### On macOS and Linux

```bash
./transcripts_prepare.sh
```
