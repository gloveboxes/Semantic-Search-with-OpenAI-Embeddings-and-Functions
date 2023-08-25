# Embeddings_vector_search

1. generate_master_csv.py: Cleans up the vtt transcripts, strips out vtt metadata, splits large blocks of text into chunks to fall inside of OpenAI token limits for embeddings.
All the session metadata and transcripts are saved to the master.csv file
1. generate_session_embedding.ipynb: loads the master.csv file into a pandas dataframe and calls OpenAI Embeddedings to generate vectors for each session transcript.
The pandas dataframe is then saved to master_embeddings.csv
1. vector_search.py: loads the master_embeddings.csv into a pandas dataframe and prompts user for a quesy. The query is vectorised, then cosine_similarity used to find "nearest neighbour" for the quesry against the vectorised session transcripts.
