#!/usr/bin/env python3
"""
Simple HTTP server for the Nike 3D Experience
Serves files with proper CORS headers for GLB models
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow GLB loading
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print("="*50)
        print(f"🚀 Nike 3D Experience Server Started!")
        print("="*50)
        print(f"\n📍 Open these URLs in your browser:\n")
        print(f"  Main Viewer:  http://localhost:{PORT}/nike-viewer.html")
        print(f"  Chat Demo:    http://localhost:{PORT}/chat.html")
        print(f"  Test Page:    http://localhost:{PORT}/test.html")
        print(f"  Simple Test:  http://localhost:{PORT}/simple-test.html")
        print(f"\n✨ Press Ctrl+C to stop the server\n")
        print("="*50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")
