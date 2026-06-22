import subprocess
import sys
import time

def start_services():
    print("🚀 Démarrage des services...")

    
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"]
    )
    print("✅ Backend FastAPI lancé sur http://127.0.0.1:8000")

    
    time.sleep(2)

    
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/ui/app_ui.py"]
    )
    print("✅ Frontend Streamlit lancé sur http://localhost:8501")

    try:
        
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        
        print("\n🛑 Arrêt des services en cours...")
        backend_process.terminate()
        frontend_process.terminate()
        print("💡 Tous les services ont été arrêtés.")

if __name__ == "__main__":
    start_services()