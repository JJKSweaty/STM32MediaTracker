import socketio
import eventlet
import time

# Create a Socket.IO server
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"[CONNECTED] {sid}")

@sio.event
def disconnect(sid):
    print(f"[DISCONNECTED] {sid}")

def send_test_command():
    while True:
        print("[SERVER] Sending 'play' command...")
        sio.emit("command", "play")  # Send 'play' command to clients
        time.sleep(5)  # Send every 5 seconds

# Start the test server
if __name__ == "__main__":
    eventlet.spawn(send_test_command)
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 8000)), app)
