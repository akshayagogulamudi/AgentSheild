"""FastAPI application entry point for AgentShield AI Backend."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, seed_demo_data
from routes import health, policies, events, gateway, approvals

# Initialize database
init_db()
seed_demo_data()

# Create FastAPI app
app = FastAPI(
    title="AgentShield AI Backend",
    description="Intelligent security gateway for AI agents",
    version="0.1.0"
)

# Configure CORS - allow frontend on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route handlers
app.include_router(health.router)
app.include_router(policies.router)
app.include_router(events.router)
app.include_router(gateway.router)
app.include_router(approvals.router)
from routes import agent
app.include_router(agent.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AgentShield AI Backend API",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
