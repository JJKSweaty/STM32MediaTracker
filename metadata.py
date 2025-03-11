from main import socketio, connected_clients
import requests
def send_command(command):
    print(f"[SENDING COMMAND via API]: {command}")
    try:
        res = requests.post("http://localhost:8080/send_command", json={"command": command})
        if res.ok:
            print("[COMMAND SENT SUCCESSFULLY]")
        else:
            print("[SERVER ERROR]:", res.status_code, res.text)
    except Exception as e:
        print("[ ERROR SENDING COMMAND]:", str(e))

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
