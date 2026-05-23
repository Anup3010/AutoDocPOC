"""
AutoDoc POC - Sample FastAPI CRUD Application
This is the project being auto-documented.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crud_app.api import users, items
from crud_app.services.db_service import init_db

app = FastAPI(
    title="AutoDoc Sample CRUD API",
    description="A sample CRUD API for AutoDoc POC demonstration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize in-memory database
init_db()

# Register routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])


@app.get("/health", tags=["Health"])
def health_check():
    """Check if the API is running."""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
