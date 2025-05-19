import websocket
import threading
import time

def on_message(ws, message):
    print("[WebSocket] Received:", message)

def on_error(ws, error):
    print("[WebSocket] Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("[WebSocket] Connection closed.")

def on_open(ws):
    print("[WebSocket] Connection opened. Waiting for notifications...")

def run_websocket():
    ws = websocket.WebSocketApp(
        "ws://localhost:8000/ws/notifications/",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    print("Connecting to ws://localhost:8000/ws/notifications/ ...")
    run_websocket()
