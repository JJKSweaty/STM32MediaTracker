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

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
encoded = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
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

def getProfile():
        authorized_req()
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        access_token = tokens["access_token"]
        response = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code == 200:
            data = response.json()
        print(json.dumps(data, indent=3))

# Using this function to check if the token is still valid
def authorized_req():
    state=False
    while state==False:
        if not os.path.exists("tokens.json"):
            print("Error: No token.json file found")
            Auth()
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        access_token = tokens["access_token"]
        # using a random spotify req to test if it needs to refreshed
        response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code == 200:
            state=True
            return state
        else:
            refresh()
            state=True
    return state

# It will refresh the token if its expired
def refresh():
    tokens=load_tokens()
    refresh_token = tokens["refresh_token"]
    response = requests.post("https://accounts.spotify.com/api/token", headers={"Authorization": "Basic "+encoded}, data={"grant_type":"refresh_token","refresh_token":refresh_token})
    # if valid api req then update the tokens
    if (response.status_code == 200):
        new_tokens = response.json()
        # checking if the refresh token is being sent in the response
        if "refresh_token" not in new_tokens:
            new_tokens["refresh_token"] = refresh_token
        save_tokens(new_tokens)
    # If even the refresh token is expired then reauthenticate the user
    else:
        print("Error: Could not refresh token")
        Auth()

def load_tokens():
    if not os.path.exists("tokens.json"):
        print("Error: No token.json file found")
        Auth()
    with open("tokens.json", "r") as f:
        return json.load(f)
    
def save_tokens(tokens):
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=3)