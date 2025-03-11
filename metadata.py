from main import socketio, connected_clients

def send_command(command):
    """ Sends command to the connected client """
    print(f"[🚀 SENDING COMMAND]: {command}")
    for sid in connected_clients.keys():
        socketio.emit("command", command, room=sid)

def print_stored_metadata(metadata):
    """ Prints the stored metadata from main.py """
    print("\n--- [📀 STORED METADATA] ---")
    print(f"Title: {metadata['title']}")
    print(f"Artist: {metadata['artist']}")
    print(f"Album: {metadata['album']}")
    print(f"Artwork: {metadata['artwork']}")
    print("----------------------------\n")

def send_play(): send_command("play")
def send_pause(): send_command("pause")
def send_next(): send_command("next")
def send_previous(): send_command("previous")
