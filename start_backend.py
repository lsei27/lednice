#!/usr/bin/env python3
import os
import sys
import subprocess

def install_requirements():
    print("📦 Instaluji Python závislosti...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
        print("✅ Závislosti byly úspěšně nainstalovány")
    except subprocess.CalledProcessError as e:
        print(f"❌ Chyba při instalaci závislostí: {e}")
        return False
    return True

def start_backend():
    print("🚀 Spouštím backend server...")
    try:
        os.chdir("backend")
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Backend server byl zastaven")
    except Exception as e:
        print(f"❌ Chyba při spouštění backend serveru: {e}")

def main():
    print("🍳 Fridge Recipe App - Backend")
    print("=" * 40)
    
    if not os.path.exists("backend/requirements.txt"):
        print("❌ Soubor backend/requirements.txt nebyl nalezen")
        return
    
    if not install_requirements():
        return
    
    start_backend()

if __name__ == "__main__":
    main() 