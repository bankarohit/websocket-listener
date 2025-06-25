from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
