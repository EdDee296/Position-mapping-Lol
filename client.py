import websocket
import time

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection established")

if __name__ == "__main__":
    # Connect to the WebSocket server
    server_address = "ws://localhost:8080/ws"
    print(f"Connecting to {server_address}...")
    
    # Create a WebSocket connection
    ws = websocket.WebSocketApp(
        server_address,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Start the connection in a blocking call
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if ws.sock and ws.sock.connected:
            ws.close()
