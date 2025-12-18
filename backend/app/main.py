"""
FastAPI Application with History tracking
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Certificate Verification API",
    description="AI-powered verification with history tracking",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from app.api import routes, history

app.include_router(routes.router, prefix="/api/v1", tags=["verification"])
app.include_router(history.router, prefix="/api/v1/history", tags=["history"])

@app.get("/")
async def root():
    return {
        "message": "Certificate Verification API v2.0",
        "features": ["OCR", "Forensics", "Verification", "History"],
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
