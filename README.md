# Embeddings_vector_search

## Overview

Solution takes over 100 hours of conference transcripts with the objective of vectorizing and making semantic searchable.

1. generate_master_csv.py: Cleans up the vtt transcripts, strips out vtt metadata, splits large blocks of text into chunks to fall inside of OpenAI token limits for embeddings.
All the session metadata and transcripts are saved to the master.csv file
1. generate_session_embedding.ipynb: loads the master.csv file into a pandas dataframe and calls OpenAI Embeddedings to generate vectors for each session transcript.
The pandas dataframe is then saved to master_embeddings.csv
1. vector_search.py: loads the master_embeddings.csv into a pandas dataframe and prompts user for a quesy. The query is vectorised, then cosine_similarity used to find "nearest neighbour" for the query against the vectorised session transcripts.

## References

1. [OpenAI Guide to Embeddings](https://platform.openai.com/docs/guides/embeddings)
1. [Azure OpenAI Service REST API reference](https://learn.microsoft.com/azure/ai-services/openai/reference)
1. [Tutorial: Explore Azure OpenAI Service embeddings and document search](https://learn.microsoft.com/azure/ai-services/openai/tutorials/embeddings?tabs=command-line)
1. [Understanding vector search - excellent YT video on embeddings, highly recommended](https://www.youtube.com/watch?v=xzHhZh7F25I)
1. [Hugging face Embeddings leaderboard](https://huggingface.co/blog/mteb)
