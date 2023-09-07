# This script will process the transcripts
# First it will bucket up all the transcripts into 5 minute segments
# Next it will call OpenAI ChatGPT to summarize each 5 minute segment
# Finally, it will create embeddings for each 5 minute segment

# set the folder environment variable where the transcripts are located
$env:TRANSCRIPT_FOLDER = "the_ai_show_transcripts"

# echo the TRANSCRIPT_FOLDER environment variable
Write-Output $env:TRANSCRIPT_FOLDER

python3 transcriptions_get_all.py -f $env:TRANSCRIPT_FOLDER
python3 transcription_speaker_info.py -f $env:TRANSCRIPT_FOLDER
python3 transcriptions_bucket.py -f $env:TRANSCRIPT_FOLDER
python3 openai_summarize_transcripts.py
python3 openai_create_embeddings.py
