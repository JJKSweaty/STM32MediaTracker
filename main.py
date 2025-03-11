import threading
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
import os
import base64
from dotenv import load_dotenv
import requests
import json
import webbrowser
import urllib.parse
load_dotenv()
pending_command = None

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
connected_clients = {}
title_data = ""
artist_data = ""
album_data = ""
artwork_data = ""
client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded = base64.b64encode(client_creds.encode()).decode()
@app.route("/callback")
def callback():
    codes=request.args.get("code")
    if(codes): 
     print(f"[CALLBACK] Received code: {codes}")
    else:
        return "Error: No code received"
    response = requests.post("https://accounts.spotify.com/api/token", headers={"Authorization": "Basic "+encoded}, data={"grant_type":"authorization_code","code":codes,"redirect_uri":REDIRECT_URI})
    tokens = response.json()
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=3)
    return "Authorization successful. You can close this window."


@socketio.event("connect")
def handle_connect():
    print(f"[CONNECTED] Client connected")
    connected_clients["client"] = True  
    socketio.emit("my_response", {"msg": "Hello from server"})

@socketio.on("disconnect")
def handle_disconnect():
    print(f"[DISCONNECTED] Client disconnected")
    connected_clients.pop("client", None)

@socketio.on("sendTitle")
def receive_title(data):
    global title_data
    title_data = data
    print(f"[RECEIVED TITLE]: {title_data}")

@socketio.on("sendArtist")
def receive_artist(data):
    global artist_data
    artist_data = data
    print(f"[RECEIVED ARTIST]: {artist_data}")

@socketio.on("sendAlbum")
def receive_album(data):
    global album_data
    album_data = data
    print(f"[RECEIVED ALBUM]: {album_data}")

@socketio.on("sendArtwork")
def receive_artwork(data):
    global artwork_data
    artwork_data = data
    print(f"[RECEIVED ARTWORK]: {artwork_data}")

@app.route("/send_command", methods=["POST"])
def set_command():
    global pending_command
    data = request.json
    command = data.get("command")
    if command in ["play", "pause", "next", "previous"]:
        print(f"[🚀 COMMAND SET BY USER]: {command}")
        pending_command = command
        return jsonify({"status": "command set", "command": command})
    return jsonify({"error": "invalid command"}), 400

@app.route("/get_command", methods=["GET"])
def get_command():
    global pending_command
    if pending_command:
        cmd = pending_command
        pending_command = None  # Clear it after sending
        return jsonify({"command": cmd})
    return jsonify({"command": None})
def get_metadata():
    return {
        "title": title_data,
        "artist": artist_data,
        "album": album_data,
        "artwork": artwork_data
    }

def handle_user_input():
    from metadata import send_play, send_pause, send_next, send_previous, print_stored_metadata
    from control_media import Auth, getProfile

    print("\n[CONTROL PANEL]")
    print("Type '1' to Play, '2' to Pause, '3' Next, '4' Previous")
    print("Type '5' for Metadata, '6' to Show Stored Metadata, '7' to Exit\n")

    while True:
        try:
            choice = input("> ").strip()
            if choice == "1":
                send_play()
            elif choice == "2":
                send_pause()
            elif choice == "3":
                send_next()
            elif choice == "4":
                send_previous()
            elif choice == "5":
                print(f"[ACTIVE METADATA]: {get_metadata()}")
            elif choice == "6":
                metadata = get_metadata()
                getProfile()
                if metadata["title"]:
                    print_stored_metadata(metadata)
                else:
                    print("[STORED METADATA]: No metadata stored yet.")
            elif choice == "7":
                print("[EXIT] Stopping user input loop.")
                break
            elif choice == "8":
                Auth()
            else:
                print("[ERROR] Invalid choice.")
        except Exception as e:
            print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=handle_user_input, daemon=True).start()
    print("[SERVER RUNNING] Flask-SocketIO on port 8080...")
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
