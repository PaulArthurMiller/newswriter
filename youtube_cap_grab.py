# The script for grabbing YouTube transcripts

# App to download YouTube transcripts for city council meetings, then
# pass them on to an OpenAI model to produce news stories for online posting

from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        if transcript_list:
            print("Transcript acquired!")
        else:
            print("No transcript acquired!")
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        print("Text joined!")
    except:
        print("Unable to join text.")
    
    print("Cleaning text.")
    # Remove simple timestamps
    cleaned_text = re.sub(r"\[\d{2}:\d{2}:\d{2}\]", "", transcript_text)
    cleaned_text = re.sub(r"\[\d{2}:\d{2}\]", "", cleaned_text)

    # Remove SRT caption format timestamps
    cleaned_text = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", "", cleaned_text)

    # Remove interjections (ums, ahs, and uhs)
    cleaned_text = re.sub(r"^um$", "", cleaned_text)
    cleaned_text = re.sub(r"^ah$", "", cleaned_text)
    cleaned_text = re.sub(r"^uh$", "", cleaned_text)

    # Remove extra spaces caused by the removal
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    print("Text cleaned!")
    print(cleaned_text[:50])
    return cleaned_text
    



