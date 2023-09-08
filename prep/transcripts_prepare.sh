#!/bin/bash

# This script will process the transcripts
# 1. Download the transcripts from YouTube
# 2. Enrich the transcripts with speaker information
# 3. Enrich the transcripts into 5 minute buckets
# 4. Enrich the transcripts with with OpenAI ChatGPT summaries
# 5. Enrich the transcripts with embeddings


export TRANSCRIPT_FOLDER=transcripts_the_ai_show

mkdir -p $TRANSCRIPT_FOLDER

python3 transcript_download.py -f $TRANSCRIPT_FOLDER
python3 transcript_enrich_speaker.py -f $TRANSCRIPT_FOLDER
python3 transcript_enrich_bucket.py -f $TRANSCRIPT_FOLDER
python3 transcript_enrich_summaries.py
python3 transcript_enrich_embeddings.py
