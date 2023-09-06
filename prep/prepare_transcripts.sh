#!/bin/bash

# This script will process the transcripts
# First it will bucket up all the transcripts into 5 minute segments
# Next it will call OpenAI ChatGPT to summarize each 5 minute segment
# Finally, it will create embeddings for each 5 minute segment

python3 transcriptions_bucket.py
python3 openai_summarize_transcripts.py
python3 openai_create_embeddings.py