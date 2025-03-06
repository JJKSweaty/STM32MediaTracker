import pygetwindow as gw
import psutil
from pycaw.pycaw import AudioUtilities
import socketio
import eventlet
import eventlet.wsgi
import threading
import pyautogui
import pythoncom

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)



title_data = None
artist_data = None
album_data = None
artwork_data = {}
connected_clients = {}  
@sio.event
def connect(sid, environ):
    print(f"Connected: {sid}")
    print("Connected to client")    
    connected_clients[sid] = True 
    sio.emit('my_response', {'msg': 'Hello from server'}, to=sid)

@sio.event
def disconnect(sid):
    print(f"Disconnected: {sid}")
    print("Disconnected from client")
    if sid in connected_clients:
        del connected_clients[sid]

@sio.event
def sendTitle(sid, data):
    global title_data
    title_data = data
    print(f"Received Title: {title_data}")

@sio.event
def sendArtist(sid, data):
    global artist_data
    artist_data = data
    print(f"Received Artist: {artist_data}")

@sio.event
def sendAlbum(sid, data):
    global album_data
    album_data = data
    print(f"Received Album: {album_data}")

@sio.event
def sendArtwork(sid, data):
    global artwork_data
    artwork_data = data
    print(f"Received Artwork: {artwork_data}")



@sio.event
def send_play(sid):
    print("Emitting 'command' with 'play'")
    sio.emit('command', "play", to=sid)
    print(f"Emit finished {sid}")
    
def send_pause():
    sio.emit('command', 'pause')
    
def send_next():
    sio.emit('command', 'next')
    control_media('next')

def send_previous():
    sio.emit('command', 'previous')
    control_media('previous')

def control_media(command):
    try:
        pythoncom.CoInitialize()
        sessions = AudioUtilities.GetAllSessions() 
        for session in sessions:
            if session.Process and session.Process.name().lower() in ["spotify.exe", "chrome.exe", "vlc.exe", "windowsmedia.exe", "brave.exe"]:
                if command == 'play':
                    send_play()
                elif command == 'pause':
                    send_pause()
                elif command == 'next':
                    pyautogui.press('right')  
                elif command == 'previous':
                    pyautogui.press('left')
        pythoncom.CoInitialize()
    except Exception as e:
        print(f"Error controlling media: {str(e)}")

def get_media_title():
    try:
        pythoncom.CoInitialize()
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in ["spotify.exe","chrome.exe","vlc.exe","windowsmedia.exe","brave.exe"]:
                return session.Process.name()
        return "No media playing"
    except Exception as e:
        return f"Error: {str(e)}"


def print_stored_metadata():
    print("\n--- Stored Metadata ---")
    print(f"Title: {title_data}")
    print(f"Artist: {artist_data}")
    print(f"Album: {album_data}")
    print(f"Artwork: {artwork_data}")
    print("-----------------------\n")


def handle_user_input():
    print("Press 1 to play, 2 to pause, 3 to next, 4 to previous, 5 to get media title, 6 to show stored metadata, 7 to exit")
    
    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if choice == 1:
                send_play(connected_clients[0])
            elif choice == 2:
                send_pause()
            elif choice == 3:
                send_next()
            elif choice == 4:
                send_previous()
            elif choice == 5:
                disconnect()
            elif choice == 6:
                print_stored_metadata()  
            elif choice == 7:
                break
            else:
                print("Invalid choice")
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

input_thread = threading.Thread(target=handle_user_input)
input_thread.daemon = True
input_thread.start()
pythoncom.CoInitialize()
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8080)), app)
