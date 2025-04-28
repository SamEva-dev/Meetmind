Write-Host "Préparation de l'environnement MeetMind..." -ForegroundColor Cyan

# Créer un venv s'il n'existe pas déjà
if (!(Test-Path -Path "venv")) {
    python -m venv venv
    Write-Host " Environnement virtuel créé." -ForegroundColor Green
} else {
    Write-Host " Environnement virtuel déjà existant." -ForegroundColor Yellow
}

# Activer le venv
Write-Host " Activation de l'environnement virtuel..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Mettre à jour pip
Write-Host " Mise à jour de pip..." -ForegroundColor Cyan
pip install --upgrade pip

# Installer requirements.txt
if (Test-Path -Path "requirements.txt") {
    Write-Host " Installation des dépendances..." -ForegroundColor Cyan
    pip install -r requirements.txt
} else {
    Write-Host " requirements.txt introuvable !" -ForegroundColor Red
}

Write-Host " Environnement prêt pour MeetMind !" -ForegroundColor Green
