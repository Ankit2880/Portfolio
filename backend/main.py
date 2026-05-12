import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Database Configuration ---
# Reads DATABASE_URL from environment; falls back to local SQLite for development.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./portfolio.db")

# SQLAlchemy needs the postgres dialect for asyncpg / psycopg2
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---
class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas ---
class MessageCreate(BaseModel):
    name: str
    email: EmailStr
    message: str

# --- CORS Origins ---
# Set ALLOWED_ORIGINS env var to a comma-separated list of production domains.
# Example: "https://yourportfolio.com,https://www.yourportfolio.com"
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()] or [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1",
]

# --- FastAPI Initialization ---
app = FastAPI(
    title="Ankit Verma's Portfolio API",
    description="Backend for handling contact forms.",
    version="1.0.0",
    # Hide docs in production unless DEBUG flag is set
    docs_url="/docs" if os.environ.get("DEBUG") else None,
    redoc_url="/redoc" if os.environ.get("DEBUG") else None,
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# --- DB Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.get("/api/ping")
def ping():
    """Health check endpoint."""
    return {"status": "ok", "message": "Portfolio API is live!"}

@app.post("/api/contact", status_code=201)
def submit_contact(msg: MessageCreate, request: Request, db: Session = Depends(get_db)):
    """Handle contact form submissions."""
    try:
        new_msg = ContactMessage(
            name=msg.name,
            email=msg.email,
            message=msg.message,
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        logger.info("New contact from %s <%s>", msg.name, msg.email)
        return {"success": True, "message": "Message received! I'll get back to you soon."}
    except Exception as exc:
        logger.exception("Error saving contact message")
        raise HTTPException(status_code=500, detail="Internal server error") from exc

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not found"})

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
