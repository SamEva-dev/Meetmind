# RUn this first : Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Write-Host " Lancement du serveur MeetMind (FastAPI)..." -ForegroundColor Cyan

# Activer venv
& .\venv\Scripts\Activate.ps1

# Lancer uvicorn via Python
python -m uvicorn main:app --reload --host 127.0.0.1 --port 5000
