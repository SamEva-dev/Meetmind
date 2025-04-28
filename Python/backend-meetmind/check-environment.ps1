Write-Host " Vérification de l'environnement pour MeetMind..." -ForegroundColor Cyan

# Fonction pour vérifier si une commande existe
function CommandExists {
    param (
        [string]$Command
    )
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Vérifier Python
if (CommandExists -Command "python") {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python détecté : $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python non détecté !" -ForegroundColor Red
}

# Vérifier Pip
if (CommandExists -Command "pip") {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ Pip détecté : $pipVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Pip non détecté !" -ForegroundColor Red
}

# Vérifier FFMPEG
if (CommandExists -Command "ffmpeg") {
    $ffmpegVersion = ffmpeg -version | Select-String "ffmpeg version"
    Write-Host "✅ FFMPEG détecté : $($ffmpegVersion.Line)" -ForegroundColor Green
} else {
    Write-Host "❌ FFMPEG non détecté !" -ForegroundColor Red
}

# Vérifier installation FastAPI
try {
    $fastapiVersion = pip show fastapi 2>&1
    if ($fastapiVersion -match "Name: fastapi") {
        Write-Host "✅ FastAPI est installé." -ForegroundColor Green
    } else {
        Write-Host "❌ FastAPI n'est pas installé !" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ FastAPI non détecté !" -ForegroundColor Red
}

# Vérifier installation Uvicorn
try {
    $uvicornVersion = pip show uvicorn 2>&1
    if ($uvicornVersion -match "Name: uvicorn") {
        Write-Host "✅ Uvicorn est installé." -ForegroundColor Green
    } else {
        Write-Host "❌ Uvicorn n'est pas installé !" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Uvicorn non détecté !" -ForegroundColor Red
}

Write-Host "`n🎯 Vérification terminée." -ForegroundColor Yellow
