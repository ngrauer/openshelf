"""
OpenShelf MVP v2 — Application Configuration
"""
import os

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./openshelf.db")

# --- JWT Authentication ---
SECRET_KEY = os.getenv("SECRET_KEY", "openshelf-dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours for demo convenience

# --- AI Chatbot (Claude Haiku) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- Application ---
APP_TITLE = "OpenShelf API"
APP_DESCRIPTION = """
**OpenShelf** — AI-Powered Campus Textbook Marketplace

Backend proof-of-concept demonstrating:
- Normalized relational schema (users, courses, textbooks, listings, matches, messages, reviews)
- Rule-based matching engine connecting buyers to sellers by course enrollment
- AI price recommendation engine (rule-based)
- AI chatbot with RAG-powered responses (Claude Haiku)
- Full CRUD for listings, messaging, and reviews
- JWT authentication with bcrypt password hashing
"""
APP_VERSION = "2.0.0-mvp2"
