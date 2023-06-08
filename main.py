from typing import Optional
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"Welcome Home"}

@app.get("/MOS")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}