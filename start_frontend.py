#!/usr/bin/env python3
import os
import sys
import subprocess
import webbrowser
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_frontend_server():
    try:
        os.chdir("frontend")
        port = 8000
        server = HTTPServer(('localhost', port), CustomHTTPRequestHandler)
        
        print(f"🌐 Frontend server běží na http://localhost:{port}")
        print("📱 Otevřete prohlížeč a nahrajte fotografii ledničky")
        print("🛑 Pro zastavení stiskněte Ctrl+C")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend server byl zastaven")
    except Exception as e:
        print(f"❌ Chyba při spouštění frontend serveru: {e}")

def open_browser():
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:8000')
    except Exception as e:
        print(f"⚠️  Nepodařilo se otevřít prohlížeč: {e}")
        print("🌐 Otevřete manuálně: http://localhost:8000")

def main():
    print("🍳 Fridge Recipe App - Frontend")
    print("=" * 40)
    
    if not os.path.exists("frontend/index.html"):
        print("❌ Frontend soubory nebyly nalezeny")
        print("📁 Zkontrolujte, zda existuje složka frontend/")
        return
    
    server_thread = threading.Thread(target=start_frontend_server)
    server_thread.daemon = True
    server_thread.start()
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Aplikace byla ukončena")

if __name__ == "__main__":
    main() 