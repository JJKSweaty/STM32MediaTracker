import pythoncom
from pycaw.pycaw import AudioUtilities
import os
from dotenv import load_dotenv
load_dotenv()

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
