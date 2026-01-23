"""
Main FastAPI app
"""
from fastapi import FastAPI
from app.api import explain

app = FastAPI(title="AI Why Did This Move? Engine")
app.include_router(explain.router)

@app.get("/")
def root():
    return {"message": "AI 'Why Did This Move?' Engine is running."}
