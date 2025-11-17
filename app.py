import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 最初は * でOK、あとで必要に応じて絞る
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY", "CHANGE_ME")  # M5側と同じ値に

app = FastAPI(title="Sonaeru+ Ingest API")
_latest: Dict[str, Any] = {}  # 開発中はここに保持（本番はDBへ）

class Ingest(BaseModel):
    device_id: str
    temperature: float
    humidity: float
    pressure: Optional[float] = None
    ts: Optional[datetime] = None

def _auth(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

@app.get("/health")
def health():
    return {"ok": True, "server_time": datetime.utcnow().isoformat() + "Z"}

@app.post("/ingest")
def ingest(payload: Ingest, x_api_key: Optional[str] = Header(None)):
    _auth(x_api_key)
    _latest.update(payload.model_dump())
    _latest["ts_server"] = datetime.utcnow().isoformat() + "Z"
    return {"ok": True}

@app.get("/poll")
def poll(device_id: str, x_api_key: Optional[str] = Header(None)):
    _auth(x_api_key)
    return {"cmd": None, "interval": 30, "server_time": datetime.utcnow().isoformat() + "Z"}

@app.get("/latest")
def latest():
    return _latest
