import threading
import asyncio
from flask import Flask, request
from flask_socketio import SocketIO
import pyautogui
import pythoncom
from pycaw.pycaw import AudioUtilities

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Store Connected Clients
connected_clients = {}

# Store Media Metadata
title_data = None
artist_data = None
album_data = None
artwork_data = {}

# ✅ Handle Client Connection
@socketio.on("connect")
def handle_connect():
    sid = request.sid
    print(f"[✅ CONNECTED] Client {sid}")
    connected_clients[sid] = True
    socketio.emit("my_response", {"msg": "Hello from server"}, to=sid)

# ✅ Handle Client Disconnection
@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    print(f"[❌ DISCONNECTED] Client {sid}")
    connected_clients.pop(sid, None)

# ✅ Handle Metadata Updates
@socketio.on("sendTitle")
def receive_title(data):
    global title_data
    title_data = data
    print(f"[📡 RECEIVED TITLE]: {title_data}")

@socketio.on("sendArtist")
def receive_artist(data):
    global artist_data
    artist_data = data
    print(f"[📡 RECEIVED ARTIST]: {artist_data}")

@socketio.on("sendAlbum")
def receive_album(data):
    global album_data
    album_data = data
    print(f"[📡 RECEIVED ALBUM]: {album_data}")

@socketio.on("sendArtwork")
def receive_artwork(data):
    global artwork_data
    artwork_data = data
    print(f"[📡 RECEIVED ARTWORK]: {artwork_data}")

# ✅ Emit Commands to All Clients
def send_command(command):
    print(f"[🚀 SENDING COMMAND]: {command}")
    for sid in connected_clients.keys():
        socketio.emit("command", command, to=sid)

def send_play(): send_command("play")
def send_pause(): send_command("pause")
def send_next(): send_command("next")
def send_previous(): send_command("previous")

# ✅ Handle OS-Level Media Controls via Pycaw
def control_media(command):
    try:
        pythoncom.CoInitialize()
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in ["spotify.exe", "chrome.exe", "vlc.exe", "windowsmedia.exe", "brave.exe"]:
                if command == "play":
                    send_play()
                elif command == "pause":
                    send_pause()
                elif command == "next":
                    pyautogui.press("right")  
                elif command == "previous":
                    pyautogui.press("left")
        pythoncom.CoUninitialize()
    except Exception as e:
        print(f"[❌ ERROR] Media Control Failed: {str(e)}")

# ✅ Get Active Media Player
def get_media_title():
    try:
        pythoncom.CoInitialize()
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in ["spotify.exe", "chrome.exe", "vlc.exe", "windowsmedia.exe", "brave.exe"]:
                return session.Process.name()
        return "No media playing"
    except Exception as e:
        return f"[❌ ERROR] {str(e)}"

# ✅ Print Stored Metadata
def print_stored_metadata():
    print("\n--- [📀 STORED METADATA] ---")
    print(f"Title: {title_data}")
    print(f"Artist: {artist_data}")
    print(f"Album: {album_data}")
    print(f"Artwork: {artwork_data}")
    print("----------------------------\n")

# ✅ Handle User Input for Manual Commands
def handle_user_input():
    print("\n[🎮 CONTROL PANEL]")
    print("Type '1' to Play, '2' to Pause, '3' Next, '4' Previous")
    print("Type '5' for Media Title, '6' to Show Metadata, '7' to Exit\n")

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
                print(f"[🎵 ACTIVE MEDIA]: {get_media_title()}")
            elif choice == "6":
                print_stored_metadata()
            elif choice == "7":
                print("[❌ EXIT] Stopping user input loop.")
                break
            else:
                print("[⚠️ ERROR] Invalid choice.")
        except Exception as e:
            print(f"[❌ ERROR] {str(e)}")

# ✅ Start Flask-SocketIO Server
if __name__ == "__main__":
    threading.Thread(target=handle_user_input, daemon=True).start()
    print("[🚀 SERVER RUNNING] Flask-SocketIO on port 8080...")
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
