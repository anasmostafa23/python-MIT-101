import os
import requests

def summarize_text(text, ngrokUrl):
    """Send text to the external summarization service and return the summary."""
    if(not ngrokUrl):
        ngrokUrl = os.getenv('NGROK_URL') 

    print('Passed ngrokUrl: ', ngrokUrl)
    
    payload = {"text": text}
    response = requests.post(f"{ngrokUrl}/summarize", json=payload)
    
    if response.status_code == 200:
        return response.json().get("summary", "No summary provided.")
    else:
        raise RuntimeError(f"Summarization failed: {response.status_code} - {response.text}")
