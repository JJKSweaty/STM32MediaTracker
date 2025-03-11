import threading
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Store Connected Clients and Metadata
connected_clients = {}
title_data = ""
artist_data = ""
album_data = ""
artwork_data = ""

@socketio.on("connect")
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

def get_metadata():
    return {
        "title": title_data,
        "artist": artist_data,
        "album": album_data,
        "artwork": artwork_data
    }

def handle_user_input():
    from metadata import send_play, send_pause, send_next, send_previous, print_stored_metadata

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
                if metadata["title"]:
                    print_stored_metadata(metadata)
                else:
                    print("[STORED METADATA]: No metadata stored yet.")
            elif choice == "7":
                print("[EXIT] Stopping user input loop.")
                break
            else:
                print("[ERROR] Invalid choice.")
        except Exception as e:
            print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=handle_user_input, daemon=True).start()
    print("[SERVER RUNNING] Flask-SocketIO on port 8080...")
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
