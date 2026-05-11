"""
main.py

Purpose:
Main FastAPI application entry point.

This acts as the Enterprise AI Governance Gateway.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.agent_routes import router as agent_router
from api.routes.tool_routes import router as tool_router
from api.routes.event_routes import router as event_router
from api.routes.metrics_routes import router as metrics_router
from api.routes.governance_routes import router as governance_router


app = FastAPI(
    title="Insurance AI Control Tower",
    description=(
        "Enterprise Agentic AI Governance Platform "
        "for Insurance & Reinsurance"
    ),
    version="1.0.0",
)


# -------------------------------------------------------------------
# CORS Configuration
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Root Endpoint
# -------------------------------------------------------------------

@app.get("/")
def root():
    """
    Root API endpoint.
    """

    return {
        "application": "Insurance AI Control Tower",
        "status": "running",
        "environment": "local_demo",
    }


# -------------------------------------------------------------------
# Health Check Endpoint
# -------------------------------------------------------------------

@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Used for:
    - monitoring
    - uptime checks
    - deployment validation
    """

    return {
        "status": "healthy",
        "service": "enterprise_ai_gateway",
    }

# Register API routers
app.include_router(agent_router)
app.include_router(tool_router)
app.include_router(event_router)
app.include_router(metrics_router)
app.include_router(governance_router)