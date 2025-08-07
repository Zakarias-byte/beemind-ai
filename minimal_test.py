#!/usr/bin/env python3
"""
Minimal test to isolate the API problem
"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Minimal Test API")

class TestInput(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Minimal API is working!"}

@app.post("/test")
def test_endpoint(input_data: TestInput):
    return {"received": input_data.message, "status": "success"}

if __name__ == "__main__":
    print("🧪 Starting minimal test API...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
