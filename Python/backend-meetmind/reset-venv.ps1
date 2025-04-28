# RUn this first : Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Write-Host " Réinitialisation de l'environnement virtuel MeetMind..." -ForegroundColor Cyan

# Supprimer venv existant
if (Test-Path "venv") {
    Write-Host " Suppression de l'ancien venv..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
} else {
    Write-Host " Aucun venv existant à supprimer." -ForegroundColor Gray
}

# Créer un nouveau venv
Write-Host " Création d'un nouvel environnement virtuel..." -ForegroundColor Cyan
python -m venv venv

# Activer le venv
Write-Host " Activation du nouvel environnement virtuel..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Mise à jour de pip
Write-Host " Mise à jour de pip..." -ForegroundColor Cyan
pip install --upgrade pip

# Installation des dépendances
if (Test-Path "requirements.txt") {
    Write-Host " Installation des dépendances depuis requirements.txt..." -ForegroundColor Cyan
    pip install -r requirements.txt
} else {
    Write-Host " requirements.txt non trouvé !" -ForegroundColor Red
}

Write-Host " Environnement MeetMind prêt !" -ForegroundColor Green
