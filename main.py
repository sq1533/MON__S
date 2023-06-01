from typing import Union
from fastapi import FastAPI
from Alam import alamcheck

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}