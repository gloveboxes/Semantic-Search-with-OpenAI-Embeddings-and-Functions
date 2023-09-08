# This script will process the transcripts
# First it will bucket up all the transcripts into 5 minute segments
# Next it will call OpenAI ChatGPT to summarize each 5 minute segment
# Finally, it will create embeddings for each 5 minute segment

# set the folder environment variable where the transcripts are located
$env:TRANSCRIPT_FOLDER = "transcripts_the_ai_show"

# echo the TRANSCRIPT_FOLDER environment variable
Write-Output $env:TRANSCRIPT_FOLDER

# make directory for the transcripts
New-Item -ItemType Directory -Force -Path $env:TRANSCRIPT_FOLDER

python3 transcript_download.py -f $env:TRANSCRIPT_FOLDER
python3 transcriptions_enrich_speaker.py -f $env:TRANSCRIPT_FOLDER
python3 transcriptions_enrich_bucket.py -f $env:TRANSCRIPT_FOLDER
python3 transcriptions_enrich_summaries.py
python3 transcriptions_enrich_embeddings.py
