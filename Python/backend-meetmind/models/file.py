from pydantic import BaseModel
from datetime import datetime

class FileInfo(BaseModel):
    file_name: str
    file_path: str
    date: datetime
    type: str  # audio | transcript | summary
