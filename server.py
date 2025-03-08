import pygetwindow as gw
import psutil
from pycaw.pycaw import AudioUtilities
import socketio
import eventlet
import eventlet.wsgi
import threading
import pyautogui
import pythoncom
import time

# Socket.IO server setup
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

connected_sids = []
connected_clients = {}

# Metadata storage
title_data = None
artist_data = None
album_data = None
artwork_data = {}

@sio.event
def connect(sid, environ):
    print(f"[CONNECTED] Client: {sid}")
    connected_sids.append(sid)
    connected_clients[sid] = True
    sio.emit('my_response', {'msg': 'Hello from server'}, to=sid)

@sio.event
def disconnect(sid):
    print(f"[DISCONNECTED] Client: {sid}")
    if sid in connected_sids:
        connected_sids.remove(sid)
    if sid in connected_clients:
        del connected_clients[sid]

@sio.event
def sendTitle(sid, data):
    global title_data
    title_data = data
    print(f"📀 Title: {title_data}")

@sio.event
def sendArtist(sid, data):
    global artist_data
    artist_data = data
    print(f"🎤 Artist: {artist_data}")

@sio.event
def sendAlbum(sid, data):
    global album_data
    album_data = data
    print(f"📀 Album: {album_data}")

@sio.event
def sendArtwork(sid, data):
    global artwork_data
    artwork_data = data
    print(f"🖼️ Artwork Received")

def emit_command(command):
    """Send command to all connected clients"""
    for sid in connected_sids:
        print(f"📡 Sending '{command}' to {sid}")
        sio.emit('command', command, to=sid)

def get_media_title():
    """Detect active media player process"""
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

def print_stored_metadata():
    """Prints stored media metadata"""
    print("\n--- Stored Metadata ---")
    print(f"🎵 Title: {title_data}")
    print(f"🎤 Artist: {artist_data}")
    print(f"📀 Album: {album_data}")
    print(f"🖼️ Artwork: {artwork_data}")
    print("-----------------------\n")

def run_server():
    """Runs the Socket.IO server"""
    print("[SERVER] Running on port 8080...")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8080)), app)

def command_input_thread():
    """Handles user commands asynchronously"""
    commands = {
        "1": "play",
        "2": "pause",
        "3": "next",
        "4": "previous",
        "6": "metadata",
        "7": "exit"
    }
    while True:
        print("\nOptions: 1: Play, 2: Pause, 3: Next, 4: Previous, 6: Metadata, 7: Exit")
        choice = input("\nChoice: ").strip()
        if choice in commands:
            if choice == "6":
                print_stored_metadata()
            elif choice == "7":
                print("[EXIT] Stopping command input...")
                break
            else:
                emit_command(commands[choice])
        else:
            print("[ERROR] Invalid choice!")

if __name__ == '__main__':
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Start input handling in a separate thread
    input_thread = threading.Thread(target=command_input_thread, daemon=True)
    input_thread.start()

    # Keep the script running
    while True:
        time.sleep(1)
