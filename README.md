# OpenShelf MVP v2 — AI-Powered Campus Textbook Marketplace

## Overview

OpenShelf is an AI-powered campus textbook marketplace connecting student buyers with alumni and peer sellers. **MVP v2** ships a full-stack application: a React + Tailwind frontend served alongside a FastAPI backend, with real-time WebSocket chat, an AI chatbot assistant, image uploads, and a significantly expanded dataset.

**Purpose:** Live demo for CGI Hartford presentation (April 2026). The app runs end-to-end — login, browse listings, message a seller, and interact with the OpenShelf AI assistant — all without leaving the browser.

---

## What's New in v2

| Feature | v1 | v2 |
|---------|----|----|
| Frontend UI | None (Swagger only) | React + Tailwind PWA |
| Real-time chat | REST polling | WebSocket (`/ws/chat/{id}`) |
| AI Chatbot | — | OpenShelf assistant (`/chat`) |
| Conversations | Direct messages | Structured conversation model |
| Agentic messaging | — | Auto-generated buyer opener |
| Image uploads | — | `/uploads` (JPG/PNG/GIF/WebP, 5 MB max) |
| Seller listings view | — | Dedicated seller dashboard page |
| Seed data | 10 users, 20 listings | 22 users, 41 listings |

---

## Quick Start

### 1. Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Seed the Database

```bash
# from the backend/ directory
python seed.py
```

This creates `openshelf.db` (SQLite) and populates it with:
- 1 university (University of Saint Joseph)
- 22 users (18 students + 4 alumni)
- 16 courses across departments
- 30 textbooks with real ISBNs, retail prices, and Open Library cover images
- 29 course-textbook mappings
- 56 student enrollments
- 41 active listings with AI-recommended prices
- 7 conversations with 19 messages
- 10 reviews
- 14 notifications

### 3. Start the Backend

```bash
# from the backend/ directory
python main.py
```

Server runs at `http://localhost:8000`

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## Demo Login Credentials

| User | Email | Role | Use Case |
|------|-------|------|----------|
| Noah Grauer | noah.grauer@usj.edu | Student | Primary buyer + has 1 listing |
| Alex Martinez | alex.martinez@usj.edu | Alumni | Primary seller (6 listings) |
| Emily Chen | emily.chen@usj.edu | Student | Buyer + seller |
| Rachel Nguyen | rachel.nguyen@usj.edu | Alumni | Seller |

**Password for all accounts:** `openshelf123`

---

## Project Structure

```
openshelf-mvp-v1/
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── seed.py                          # Database seeder with mock data
│   ├── requirements.txt
│   ├── uploads/                         # Uploaded listing images
│   └── app/
│       ├── config.py                    # Settings, JWT config, DB URL
│       ├── database.py                  # SQLAlchemy engine + session
│       ├── models/
│       │   └── models.py                # All ORM models (11 tables)
│       ├── schemas/
│       │   └── schemas.py               # Pydantic request/response schemas
│       ├── services/
│       │   ├── auth_service.py          # JWT + bcrypt authentication
│       │   ├── matching_engine.py       # Rule-based matching + AI pricing
│       │   ├── chatbot_service.py       # OpenShelf assistant logic
│       │   ├── chatbot_prompt.py        # Prompt templates for the chatbot
│       │   └── messaging_service.py     # Agentic first-message generation
│       └── routers/
│           ├── auth.py                  # /auth — register, login, me
│           ├── courses.py               # /courses
│           ├── textbooks.py             # /textbooks
│           ├── listings.py              # /listings — CRUD + AI price
│           ├── matching.py              # /matches — matching engine
│           ├── conversations.py         # /conversations — structured chat
│           ├── messages.py              # /messages — legacy compat shim
│           ├── chat.py                  # /chat — AI chatbot endpoint
│           ├── websocket.py             # /ws/chat/{id} — real-time chat
│           ├── uploads.py               # /uploads — image upload
│           ├── reviews.py               # /reviews
│           └── notifications.py         # /notifications
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── App.jsx
        ├── contexts/
        │   └── AuthContext.jsx           # JWT auth state + login/logout
        ├── hooks/
        │   └── useChatSocket.js          # WebSocket hook for real-time chat
        ├── lib/
        │   ├── api.js                    # Axios client + API helpers
        │   └── utils.js
        ├── components/
        │   ├── DashboardLayout.jsx       # Sidebar + nav shell
        │   ├── ListingCard.jsx           # Listing preview card
        │   ├── ChatbotWidget.jsx         # Floating AI assistant widget
        │   ├── NotificationBell.jsx      # Notification dropdown
        │   └── AuthRoute.jsx             # Protected route wrapper
        └── pages/
            ├── LoginPage.jsx
            ├── RegisterPage.jsx
            ├── DashboardPage.jsx         # Matched listings for enrolled courses
            ├── ShoppingView.jsx          # Browse + filter all listings
            ├── ListingDetailPage.jsx     # Single listing + contact seller
            ├── MyListingsView.jsx        # Buyer's active conversations
            ├── SellerListingsPage.jsx    # Seller's own listings management
            ├── MessagesView.jsx          # Real-time conversation view
            └── UserProfilePage.jsx       # Profile + review history
```

---

## Key Features

### React Frontend
A Vite-built React app styled with Tailwind CSS. JWT tokens are stored in context and passed as Authorization headers on every API call. The app is organized around a persistent sidebar layout with protected routes — unauthenticated users are redirected to login.

### Real-Time WebSocket Chat
Buyers and sellers communicate through persistent WebSocket connections:

```
ws://localhost:8000/ws/chat/{conversation_id}?token=<jwt>
```

The in-process connection manager broadcasts messages to all active sockets in a conversation. Notifications are created for the other participant on every send. The conversation status auto-upgrades from `pending` → `active` on the seller's first reply.

### AI Chatbot Assistant
The OpenShelf assistant (`POST /chat`) is auth-gated and identity-aware — it knows which courses the caller is enrolled in and uses that context to personalize responses (e.g., "find me the CS 301 book" filters by the user's actual enrollments).

### Agentic Messaging
When a buyer starts a conversation without providing an initial message, the backend auto-generates a natural opener on their behalf using their name, the textbook title, and the seller's name. Buyers can override this with their own message.

### Image Uploads
Sellers can attach photos to listings via `POST /uploads`. The endpoint accepts JPG, JPEG, PNG, GIF, and WebP files up to 5 MB and returns a URL path served statically by FastAPI.

### Conversations Model
A structured `Conversation` resource links a buyer, seller, and listing. This replaces the v1 direct-message model:

- `POST /conversations` — start or resume a conversation about a listing
- `GET /conversations` — inbox view (sorted by most recent activity, with unread counts)
- `GET /conversations/{id}` — full thread (marks incoming messages as read)
- `POST /conversations/{id}/messages` — append a message via REST (alternative to WebSocket)

---

## API Endpoints

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
| GET | /textbooks/ | Search (isbn, title, author) |
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

### Conversations (5)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /conversations/ | Start or resume a conversation |
| GET | /conversations/ | Inbox (auth required) |
| GET | /conversations/{id} | Full thread + mark read |
| GET | /conversations/{id}/messages | Message list (no read marking) |
| POST | /conversations/{id}/messages | Send a message via REST |

### WebSocket (1)
| Protocol | Endpoint | Description |
|----------|----------|-------------|
| WS | /ws/chat/{conversation_id}?token= | Real-time chat |

### Chatbot (1)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /chat/ | Send message to OpenShelf assistant (auth required) |

### Uploads (1)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /uploads/ | Upload listing image (JPG/PNG/GIF/WebP, max 5 MB) |

### Reviews (3)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /reviews/ | Submit review (auth required) |
| GET | /reviews/user/{uid} | Reviews for a user |
| GET | /reviews/user/{uid}/profile | Profile with average rating + stats |

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

The rule-based matching engine connects buyers to relevant listings based on their enrolled courses. It is not a trained ML model — this is intentional. A rules-based approach is explainable, debuggable, and appropriate for MVP scope.

### Matching Flow
1. Get buyer's enrolled courses
2. Find required textbooks for those courses (via `course_textbooks` table)
3. Find active listings for those textbooks (excluding the buyer's own listings)
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
3. **Market adjustment** — blends condition-based price (60%) with the average of existing listings (40%)

---

## Database Schema (11 Normalized Tables)

```
universities ─┬─→ users ──────┬─→ enrollments ←── courses ──→ course_textbooks ←── textbooks
              │               ├─→ listings ────────────────────────────────────────────┘
              │               ├─→ conversations (buyer + seller)
              │               ├─→ messages ←── conversations
              │               ├─→ reviews
              │               └─→ notifications
              └─→ courses
```

---

## Security

| Feature | Implementation |
|---------|---------------|
| Password storage | bcrypt hash (never stored in plaintext) |
| Authentication | JWT Bearer tokens (24h expiry for demo) |
| WebSocket auth | JWT via `?token=` query param |
| Auth enforcement | Protected endpoints require valid token |

**Note:** MVP uses SQLite for self-contained demo. Will migrate to MySQL in a future build.

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
Make sure you're running commands from inside the `backend/` directory.

---

## Future Work

- Online hosting via Apache or cloud provider
- MySQL with encryption at rest and HTTPS/TLS in transit
- University SSO / LMS integration (currently mocked)
- RAG-based chatbot using Ollama + ChromaDB
- Push notifications (mobile PWA)
