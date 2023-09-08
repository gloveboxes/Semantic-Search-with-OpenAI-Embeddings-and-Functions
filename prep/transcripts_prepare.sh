#!/bin/bash

# This script will process the transcripts
# First it will bucket up all the transcripts into 5 minute segments
# Next it will call OpenAI ChatGPT to summarize each 5 minute segment
# Finally, it will create embeddings for each 5 minute segment

export TRANSCRIPT_FOLDER=transcripts_the_ai_show

mkdir -p $TRANSCRIPT_FOLDER

python3 transcript_download.py -f $TRANSCRIPT_FOLDER
python3 transcript_enrich_speaker.py -f $TRANSCRIPT_FOLDER
python3 transcript_enrich_bucket.py -f $TRANSCRIPT_FOLDER
python3 transcript_enrich_summaries.py
python3 transcript_enrich_embeddings.py
