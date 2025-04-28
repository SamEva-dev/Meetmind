import logging
import os


# Créer un dossier "logs" si pas encore existant
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/meetmind.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()  # Continue d'afficher dans la console
    ]
)

logger = logging.getLogger("MeetMind")
