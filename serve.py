"""Starts Hear on this computer and prints the address to open on your phone.
Double-click "Start Hear.command" (Mac) or "Start Hear.bat" (Windows), or run: python3 serve.py
"""
import http.server
import os
import socket
import socketserver
import webbrowser

PORT = 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


ip = lan_ip()
print()
print("Hear is running.")
print(f"  On this computer:            http://localhost:{PORT}")
print(f"  On your phone (same Wi-Fi):  http://{ip}:{PORT}")
print()
print("Leave this window open while you use the app. Press Ctrl+C to stop.")
print()
webbrowser.open(f"http://localhost:{PORT}")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), Quiet) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
