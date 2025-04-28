import logging
import os

# Create a "logs" folder if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/meetmind.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()  # also output to console
    ]
)

logger = logging.getLogger("MeetMind")
