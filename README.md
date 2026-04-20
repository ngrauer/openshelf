# OpenShelf MVP v1 — Backend Proof of Concept

## Overview

OpenShelf is an AI-powered campus textbook marketplace. This is **MVP v1** — a backend proof of concept built to demonstrate that all core systems work: normalized database, CRUD operations, rule-based matching engine, AI price recommendations, messaging, reviews, and JWT authentication.

**Purpose:** Demo to CGI mentor (Pasha) via Zoom. Walk through FastAPI Swagger UI to show data flowing correctly across all endpoints.

---

## Quick Start

### 1. Install Dependencies

```bash
# Recommended: use a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Seed the Database

```bash
python seed.py
```

This creates `openshelf.db` (SQLite) and populates it with:
- 1 university (USJ)
- 10 users (8 students + 2 alumni)
- 8 courses across departments
- 15 textbooks with real ISBNs and retail prices
- 15 course-textbook mappings
- 24 student enrollments
- 20 active listings with AI-recommended prices
- 7 messages (sample conversations)
- 4 reviews
- 5 notifications

### 3. Start the Server

```bash
python main.py
```

Server runs at `http://localhost:8000`

### 4. Open Swagger UI

Navigate to **http://localhost:8000/docs** in your browser.

---

## Demo Walkthrough \\

Use the Swagger UI to demonstrate each system. Here's a suggested order:

### Step 1: Health Check
- `GET /` — shows the app is running

### Step 2: Authentication
- `POST /auth/login` — login with `noah.grauer@usj.edu` / `openshelf123`
- Copy the `access_token` from the response
- Click the **Authorize** button (lock icon, top right of Swagger), paste the token
- `GET /auth/me` — confirms authenticated user

### Step 3: Browse Courses & Textbooks
- `GET /courses/?university_id=1&semester=Spring 2026` — see all 8 courses
- `GET /courses/1/textbooks` — see required textbooks for CS 301
- `GET /courses/user/1/enrollments` — see Noah's 4 enrolled courses
- `GET /textbooks/?title=algorithm` — search textbooks by title

### Step 4: Search Listings
- `GET /listings/` — see all 20 active listings with seller and textbook details
- `GET /listings/?course_id=1` — filter listings for CS 301 textbooks only
- `GET /listings/?min_price=20&max_price=50` — price range filter
- `GET /listings/?condition=good` — condition filter
- `GET /listings/1` — get a single listing with full details

### Step 5: AI Price Recommendation
- `POST /listings/ai-price` — body: `{"textbook_id": 1, "condition": "good"}`
- Shows recommended price, reasoning, savings vs retail
- Try different conditions to see pricing logic adjust

### Step 6: Matching Engine (Core AI Feature)
- `POST /matches/generate/1` — run the matching engine for Noah (user_id=1)
- Returns scored, ranked listings matching Noah's enrolled courses
- Each match shows score (0-100), listing details, seller info
- `GET /matches/1` — retrieve existing matches

### Step 7: Messaging
- `POST /messages/` — send a message (requires auth): `{"receiver_id": 9, "listing_id": 1, "content": "Is this still available?", "is_agentic": true}`
- `GET /messages/conversation/1/9` — see conversation thread between Noah and Alex
- `GET /messages/inbox/1` — see Noah's full inbox

### Step 8: Reviews & Reputation
- `GET /reviews/user/9` — see reviews for Alex (seller)
- `GET /reviews/user/9/profile` — see Alex's profile with average rating and stats

### Step 9: Notifications
- `GET /notifications/1` — see Noah's notifications
- `PUT /notifications/1/read` — mark a notification as read

---

## Demo Login Credentials

| User | Email | Role | Use Case |
|------|-------|------|----------|
| Noah Grauer | noah.grauer@usj.edu | Student | Primary buyer persona |
| Emily Chen | emily.chen@usj.edu | Student | Buyer + seller |
| Alex Martinez | alex.martinez@usj.edu | Alumni | Primary seller persona |
| Rachel Nguyen | rachel.nguyen@usj.edu | Alumni | Seller |

**Password for all accounts:** `openshelf123`

---

## Project Structure

```
openshelf-mvp-v1/
├── main.py                          # FastAPI app entry point
├── seed.py                          # Database seeder with mock data
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── app/
│   ├── __init__.py
│   ├── config.py                    # App settings, JWT config, DB URL
│   ├── database.py                  # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py                # All ORM models (10 tables)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py          # JWT + bcrypt authentication
│   │   └── matching_engine.py       # Rule-based matching + AI pricing
│   └── routers/
│       ├── __init__.py
│       ├── auth.py                  # POST /auth/register, /login, GET /me
│       ├── courses.py               # GET /courses, /{id}/textbooks, enrollments
│       ├── textbooks.py             # GET /textbooks, search, by ISBN
│       ├── listings.py              # CRUD + search/filter + AI price
│       ├── matching.py              # POST generate matches, GET matches
│       ├── messages.py              # POST send, GET conversation, inbox
│       ├── reviews.py               # POST review, GET user reviews + profile
│       └── notifications.py         # GET notifications, PUT mark read
└── docs/
    └── ARCHITECTURE.md              # System architecture documentation
```

---

## Database Schema (10 Normalized Tables)

```
universities ─┬─→ users ──────┬─→ enrollments ←── courses ──→ course_textbooks ←── textbooks
              │               ├─→ listings ────────────────────────────────────────────┘
              │               ├─→ messages
              │               ├─→ reviews
              │               └─→ notifications
              └─→ courses
```

### Tables & Relationships
| Table | Purpose | Key Relationships |
|-------|---------|-------------------|
| universities | Campus instances | Has many users, courses |
| users | Students + alumni | Belongs to university; has enrollments, listings, messages, reviews |
| courses | Course catalog | Belongs to university; has textbooks (via course_textbooks), enrollments |
| textbooks | Canonical book records | Has listings, linked to courses via course_textbooks |
| course_textbooks | Many-to-many: courses ↔ textbooks | Includes is_required flag |
| enrollments | Many-to-many: users ↔ courses | Unique per (user, course, semester) |
| listings | Books for sale | Belongs to seller (user) and textbook; has matches, messages, reviews |
| matches | Buyer-listing connections | Scored by matching engine; links buyer to listing |
| messages | Buyer-seller communication | Between two users, optionally about a listing |
| reviews | Seller reputation | Reviewer → reviewed user, tied to a listing |
| notifications | User alerts | Match alerts, offers, messages, resale reminders |

---

## API Endpoints (28 Total)

### Authentication (3)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register with .edu email |
| POST | /auth/login | Login → JWT token |
| GET | /auth/me | Get current user (auth required) |

### Courses (4)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /courses/ | List courses (filter: university, semester) |
| GET | /courses/{id} | Get single course |
| GET | /courses/{id}/textbooks | Course with required textbooks |
| GET | /courses/user/{id}/enrollments | User's enrolled courses |

### Textbooks (3)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /textbooks/ | Search textbooks (isbn, title, author) |
| GET | /textbooks/{id} | Get by ID |
| GET | /textbooks/isbn/{isbn} | Get by ISBN |

### Listings (6)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /listings/ | Create listing (auth required) |
| GET | /listings/ | Search/filter (course, ISBN, title, price, condition) |
| GET | /listings/{id} | Get listing with seller + textbook details |
| PUT | /listings/{id} | Update listing (owner only) |
| DELETE | /listings/{id} | Remove listing (owner only) |
| POST | /listings/ai-price | AI price recommendation |

### Matching (2)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /matches/generate/{user_id} | Run matching engine for buyer |
| GET | /matches/{user_id} | Get existing matches |

### Messages (3)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /messages/ | Send message (auth required) |
| GET | /messages/conversation/{uid}/{other_uid} | Conversation thread |
| GET | /messages/inbox/{uid} | User's full inbox |

### Reviews (3)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /reviews/ | Submit review (auth required) |
| GET | /reviews/user/{uid} | Reviews for a user |
| GET | /reviews/user/{uid}/profile | User profile with stats |

### Notifications (3)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /notifications/{uid} | Get user notifications |
| PUT | /notifications/{id}/read | Mark one as read |
| PUT | /notifications/user/{uid}/read-all | Mark all as read |

### Health (2)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | App info |
| GET | /health | Health check |

---

## Matching Engine — How It Works

The rule-based matching engine connects buyers to relevant listings based on their course enrollments. It is **not** a trained ML model — this is intentional. A rules-based approach is explainable, debuggable, and appropriate for MVP scope.

### Matching Flow
1. Get buyer's enrolled courses
2. Find required textbooks for those courses (via course_textbooks table)
3. Find active listings for those textbooks (excluding buyer's own listings)
4. Score each listing on a 0–100 scale

### Scoring Criteria
| Factor | Points | Logic |
|--------|--------|-------|
| Course/ISBN match | 40 | Required — listing must be for a needed textbook |
| Condition | 0–20 | New=20, Like New=18, Good=15, Fair=10, Poor=5 |
| Price vs. Retail | 0–25 | ≤30% of retail=25, ≤50%=20, ≤70%=15, ≤85%=10, >85%=5 |
| Recency | 0–15 | Newer listings score higher |

### AI Price Recommendation
When a seller creates a listing, the system recommends a price based on:
1. **Retail MSRP** of the textbook (from catalog)
2. **Condition multiplier** (New=85%, Like New=70%, Good=55%, Fair=40%, Poor=25%)
3. **Market adjustment** — blends condition-based price (60%) with average of existing listings (40%)

---

## Security

| Feature | Implementation |
|---------|---------------|
| Password storage | bcrypt hash (never stored in plaintext) |
| Authentication | JWT Bearer tokens (24h expiry for demo) |
| Auth enforcement | Protected endpoints require valid token |

**Note:** MVP uses SQLite for self-contained demo. Will migrate to mysql in a future build.

---

## What This MVP Does NOT Include

These are scoped for **MVP v2** (April 2026):
- Frontend UI (React + Tailwind PWA)
- AI Chatbot (Ollama + RAG + ChromaDB)
- WebSocket real-time chat
- Push notifications
- University SSO authentication (mocked)
- LMS/Blackboard integration (mocked through screenshots)

## Future Ideas

These are not scoped for MVP use but can be implemented
-online hosting via apache web server
-MySQL with encryption at rest and HTTPS/TLS in transit.

---

## Troubleshooting

**Port 8000 already in use:**
```bash
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8001)"
```

**Database issues — reset everything:**
```bash
rm openshelf.db
python seed.py
python main.py
```

**Import errors:**
Make sure you're in the `openshelf-mvp-v1/` directory when running commands.
