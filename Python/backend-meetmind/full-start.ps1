Write-Host "🚀 Démarrage complet de MeetMind..." -ForegroundColor Cyan

# S'assurer qu'on est bien dans backend-meetmind/
if (!(Test-Path "requirements.txt")) {
    Write-Host "❌ Vous n'êtes pas dans le dossier backend-meetmind !" -ForegroundColor Red
    exit
}

# Étape 1 : Reset venv
Write-Host "♻️ Réinitialisation de l'environnement virtuel..." -ForegroundColor Yellow
.\reset-venv.ps1

# Étape 2 : Lancer le serveur API
Write-Host "🚀 Lancement du serveur MeetMind..." -ForegroundColor Green
.\run-meetmind-api.ps1
