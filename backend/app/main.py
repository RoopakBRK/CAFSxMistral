"""
FastAPI Application - Certificate Verification with Mistral OCR
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Certificate Verification API",
    description="AI-powered certificate verification with Mistral OCR",
    version="2.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from app.api import routes
app.include_router(routes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Certificate Verification API v2.0",
        "ocr_engine": "Mistral OCR",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "ocr": "mistral"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
