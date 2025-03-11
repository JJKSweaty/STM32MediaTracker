import pythoncom
from pycaw.pycaw import AudioUtilities
import os
from dotenv import load_dotenv
import requests
import json
import base64
import webbrowser
import urllib.parse
load_dotenv()
code=""

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
def get_media_title():
    """ Detect active media player process """
    try:
        pythoncom.CoInitialize()
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in [
                "spotify.exe", "chrome.exe", "vlc.exe", "windowsmedia.exe", "brave.exe"
            ]:
                return session.Process.name()
        return "No media playing"
    except Exception as e:
        return f"Error: {str(e)}"

def Auth():
    encoded_redirect_uri = urllib.parse.quote(REDIRECT_URI, safe='')
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={encoded_redirect_uri}&scope=user-read-playback-state"
    webbrowser.open(auth_url)
