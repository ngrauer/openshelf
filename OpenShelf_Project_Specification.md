# OpenShelf — Complete Project Specification

## Document Purpose

This is the single source of truth for the OpenShelf project. It captures every architectural decision, design choice, technical specification, and scope boundary agreed upon between the development team and the project planning sessions. Any AI assistant, developer, or collaborator reading this document should be able to understand exactly what OpenShelf is, how it works, what has been built, what needs to be built, and how to build it — without any additional context.

**If a decision is not documented here, it has not been made.**

---

## 1. Project Context

### 1.1 Academic Framework

OpenShelf is being developed as a senior capstone project at the **University of Saint Joseph (USJ)** in partnership with **CGI** (a global IT and consulting firm). The project runs on a **13-week timeline** from January 21, 2026 through April 22, 2026.

**Team composition:** 5 members, including 1 Computer Science student (Noah Grauer — the technical lead responsible for the MVP).

**CGI Mentor:** Pasha Syed (Senior Consultant), checking in weekly to ensure alignment with capstone guidelines.

**Because the team includes a CS student, the project is required to deliver:**
- A working Minimum Viable Product (MVP) demonstrating at least 1 core AI capability
- A final written report covering problem definition, AI solution design, feasibility analysis, business case, and implementation roadmap
- A 15-minute strategic presentation + 5-minute Q&A at the CGI Hartford Office
- Architecture diagrams and workflow visuals
- Stakeholder analysis
- Ethical and responsible AI considerations
- Business case with at least one quantified impact estimate

### 1.2 Key Dates

| Milestone | Date | Status |
|-----------|------|--------|
| Capstone Kickoff | January 21, 2026 | Complete |
| Problem Approval | End of Week 2 (Feb 3) | Complete |
| Capstone Midpoint | End of February | Complete |
| Week 10 (Implementation Roadmap) | March 25, 2026 | Current |
| Week 11 (Content Lock — no new major content) | April 1, 2026 | Upcoming |
| Week 12 (Submission-Ready, Presentation Practice) | April 8, 2026 | Upcoming |
| Week 13 (Final Presentations at CGI Hartford) | Approx April 22, 2026 | Upcoming |

**Content lock (Week 11) means:** All substantive project content — problem definition, solution design, feasibility, business case, roadmap — must be finalized. MVP code can continue being refined through Week 12. No new conceptual work after April 1.

### 1.3 Capstone Requirements Summary

The CGI capstone requires teams to:
1. Choose a real business or industry sector
2. Identify a real-world operational problem improvable by AI
3. Design an AI-enabled solution that creates measurable business value
4. Use 1-2 primary AI techniques (not over-engineered)
5. Provide at least one quantified impact/ROI estimate
6. Use public, mock, or synthetic data (real company data not required)
7. Clearly state all assumptions
8. Address ethical and responsible AI considerations
9. Deliver a phased implementation roadmap

**What is NOT required:** Production-ready systems, live access to real systems, proprietary data, exhaustive technical detail.

**What matters most:** Clear problem definition, logical AI solution, realistic assumptions, clear reasoning over technical complexity.

---

## 2. Product Vision

### 2.1 What is OpenShelf?

OpenShelf is an **AI-powered Progressive Web App (PWA)** that serves as a **campus textbook marketplace**. It connects students who are buying textbooks with students and alumni who are selling them — all within the same university. The platform integrates intelligent search, rule-based buyer-seller matching, and an AI-powered chatbot to reduce search friction, increase textbook reuse rates, and lower student costs.

### 2.2 The Problem

College textbook costs continue to rise faster than inflation. Students spend $700+ per year on textbooks. Many textbooks are used for a single semester and then sit unused. There is no centralized, campus-wide platform that allows students to easily search for, buy, sell, or trade used textbooks within their own school. Existing options (bookstore buybacks, Amazon, Chegg, Facebook groups) are fragmented, inconvenient, and provide limited value. The result: students overpay, books go to waste, and universities fail to deliver on affordability and sustainability goals.

### 2.3 The Vision

OpenShelf is designed to **plug into existing student portals** (Blackboard, Canvas, etc.) as a new tab. Every university gets its own instance — USJ, UCF, UMiami would each have their own version of OpenShelf with their own student body, course catalog, and listings. The tool is architected as a **plug-and-play product** that any campus can adopt. Effectiveness scales with campus size (larger student body = more supply, more demand, better matching).

**For the MVP:** OpenShelf is a **standalone web app** that is described as LMS-integrable. Mocked screenshots will show where it would appear inside Blackboard/Canvas. No actual LTI/LMS integration is built.

### 2.4 Positioning

OpenShelf **complements** the campus bookstore and academic center — it does not replace them. It provides a peer-to-peer layer where students and alumni can exchange textbooks alongside institutional resources. The long-term vision includes other course materials (lab manuals, clickers, notes), but **MVP scope is strictly textbooks**.

### 2.5 Business Model

- **Primary model:** Sold to universities as an institutional tool (university-funded)
- **Future model:** Small transaction fee when in-app payments are implemented
- No in-app payment processing for MVP

### 2.6 Stakeholders

| Stakeholder | Role | Impact |
|-------------|------|--------|
| Students | Primary users (both buyers and sellers) | Lower costs, easier access, trusted peer marketplace |
| Faculty | Impacted when students lack materials | Better student preparedness |
| University Admins | Institutional stakeholders | Affordability, sustainability, student success metrics |
| Alumni | Supply-side stakeholders | Donate or sell older textbooks back into the campus ecosystem, verified via previous .edu accounts |

---

## 3. User Experience

### 3.1 Dashboard Design

**Unified dashboard with role-switching** — not separate buyer/seller dashboards. Every user is potentially both a buyer and a seller. The dashboard has a persistent toggle/tab system:

- **Shopping View:** Shows enrolled courses, available textbook listings per course, search/filter tools, and the AI chatbot
- **My Listings View:** Shows the user active listings, incoming offers, listing analytics (views, inquiries)
- **Shared elements:** Notification center, messaging inbox, account settings

For alumni who are only selling, they simply do not use the shopping tab. Their course enrollments show as completed/historical, and the listings tab is their primary workspace.

### 3.2 Buyer Journey

1. Student logs into OpenShelf via school credentials (SSO or .edu email signup)
2. Presented with a personalized dashboard showing their enrolled courses
3. Each course shows available textbook listings and other study materials
4. AI chatbot is available in the bottom-right corner for conversational search (e.g., "find me the CS 301 textbook under $30 in good condition")
5. Student can sort/filter results by quality, price, seller availability, and other criteria
6. When they find a book, they press a button that sends an AI-generated first message/offer to the seller (agentic workflow)
7. Seller receives a push notification
8. If seller accepts, a private in-app chat opens to negotiate and arrange the exchange (campus meetup or paid delivery)

### 3.3 Seller Journey

1. Student or alum logs into OpenShelf via school credentials
2. Navigates to My Listings / sell flow
3. AI assists with listing creation — manual ISBN entry, or automated lookup via API (Google Books, ISBNdb) if available for that book
4. AI provides a price recommendation based on condition, edition, and market data
5. Book is listed and uploaded to the database
6. The matching engine connects the listing to buyers enrolled in courses requiring that textbook
7. When a buyer expresses interest, seller gets a push notification
8. If seller accepts the inquiry, private chat opens to arrange exchange
9. At semester end, AI sends resale prompts nudging students to list their books

### 3.4 Transaction Model

- **MVP:** No in-app payment processing. Transactions are facilitated through campus meetups and direct exchanges
- **Future:** In-app payments with a small transaction fee
- **Book-for-book swaps:** Secondary feature, not in MVP but acknowledged in the roadmap

### 3.5 Trust and Safety

- **.edu email verification** for all accounts
- **University SSO** integration
- **Alumni verification** via previous .edu accounts
- **Ratings and reviews** system for users after transactions
- **Campus-only marketplace** (inherent trust layer — everyone is verified as part of the institution)

---

## 4. AI Architecture

### 4.1 Primary AI Techniques

OpenShelf uses **two primary AI approaches**, deliberately scoped to be practical rather than over-engineered:

#### 4.1.1 Rule-Based Matching and Recommendation Engine

**Not a trained ML model.** A structured rules engine that matches buyers to sellers based on weighted signals:

| Signal | Description |
|--------|-------------|
| ISBN / Edition | Exact match on book identifier |
| Course Number and Professor | Matches listing to courses requiring that textbook |
| Book Condition | Filters by buyer condition preference |
| Price Sensitivity | Ranks by proximity to buyer budget |
| Timing and Availability | Prioritizes currently available listings, considers semester timing |

The matching engine runs when a buyer views their course dashboard and produces a ranked list of recommended listings. It also runs in reverse — when a seller lists a book, the engine identifies enrolled buyers and can trigger notifications.

**Rationale for rule-based over ML:** An ML model is overkill for this problem at MVP scale. A rules engine is explainable, debuggable, and does not require training data that does not exist yet. The system can be upgraded to ML in the future as transaction data accumulates.

#### 4.1.2 NLP Chatbot via RAG and Ollama

This is the **flagship AI feature** and the one that will be demoed live.

**Architecture:**
- **LLM:** Ollama running locally on a Linux server. Model: **Qwen 3 8B** (if GPU is available) or a 3B-class model like Qwen 2.5 3B (if CPU-only or faster inference is needed for demo)
- **RAG Pipeline:** Retrieval-Augmented Generation grounding the chatbot in real platform data
- **Vector Store:** ChromaDB (Python-native, lightweight, runs locally, integrates with FastAPI)
- **Embedding Model:** To be selected (options: sentence-transformers, Ollama built-in embeddings)

**RAG Pipeline Flow:**
1. User asks a question in the chatbot
2. Question is converted to a vector embedding
3. ChromaDB is searched for the most relevant chunks of data (textbook listings, course info, platform FAQs, pricing guidance, bookstore comparisons)
4. Retrieved chunks are injected into the LLM context/system prompt
5. LLM generates a response grounded in real data, preventing hallucinations

**Chatbot Knowledge Base (to be embedded in ChromaDB):**
- Current textbook listings and their metadata
- Course catalog and required textbooks
- Platform FAQs (how to list, how to buy, how to message, how to leave a review, etc.)
- Pricing guidance (average prices by condition, how AI pricing recommendations work)
- Bookstore comparison data (why OpenShelf is cheaper than alternatives)
- Guardrail content (what the chatbot should and should not do)

#### 4.1.3 Supporting AI Capabilities

- **Agentic Messaging:** When a buyer wants to contact a seller, the AI generates a pre-written first message/offer and sends it on the buyer behalf. Subsequent messages are manual real-time chat. For MVP v1, this is mocked with templates.
- **AI-Assisted Listing Creation:** The AI helps sellers fill in book details, suggests pricing, and streamlines the listing process.
- **Push Notifications:** Match alerts, incoming offers, end-of-semester resale reminders. For MVP, these are in-app notification indicators (actual phone/email push is a future feature).
- **End-of-Semester Resale Prompts:** AI nudges students to list their textbooks when the semester is ending.

---

## 5. Technical Architecture

### 5.1 Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | React + Tailwind CSS | PWA (web-first, mobile-adaptive) |
| Backend | Python FastAPI | REST API, business logic, AI orchestration |
| Database (MVP v1) | SQLite | Self-contained, demo-only, controlled entirely in Python | Provide schema and create statements |
| ORM | SQLAlchemy | Connects FastAPI to both SQLite (v1) and MySQL (v2) |
| AI/LLM | Ollama (local) | Qwen 3 8B or 3B-class model |
| Vector Store | ChromaDB | RAG retrieval for chatbot grounding |
| Real-time Chat | WebSockets | Via FastAPI WebSocket support |
| Auth | Dual | University SSO + standalone .edu email signup | #should be able to be toggled on and off for demo
| Password Hashing | bcrypt | Industry standard | #should be able to be toggled on and off for demo
| Hosting | Linux Apache web server | Local or deployed |
| Encryption | At rest + in transit | TLS/HTTPS on FastAPI; | #should be able to be toggled on or off for demo

### 5.2 Database Schema (Normalized, with PK/FK)

**All tables use proper primary keys, foreign keys, and normalization.**

#### universities
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(255) | NOT NULL |
| domain | VARCHAR(255) | NOT NULL, UNIQUE (e.g., usj.edu) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

#### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| email | VARCHAR(255) | NOT NULL, UNIQUE |
| hashed_password | VARCHAR(255) | NOT NULL (bcrypt) |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| role | ENUM student or alumni | NOT NULL |
| university_id | INT | FK to universities.id |
| is_verified | BOOLEAN | DEFAULT FALSE |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

#### courses
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| course_code | VARCHAR(20) | NOT NULL (e.g., CS301) |
| course_name | VARCHAR(255) | NOT NULL |
| professor | VARCHAR(255) | nullable |
| semester | VARCHAR(20) | NOT NULL (e.g., Spring 2026) |
| university_id | INT | FK to universities.id |

#### textbooks
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| isbn | VARCHAR(13) | NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| author | VARCHAR(255) | NOT NULL |
| edition | VARCHAR(50) | nullable |
| publisher | VARCHAR(255) | nullable |
| retail_price | DECIMAL(10,2) | bookstore MSRP for comparison |

#### course_textbooks
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| course_id | INT | FK to courses.id |
| textbook_id | INT | FK to textbooks.id |
| is_required | BOOLEAN | DEFAULT TRUE |
| UNIQUE | | (course_id, textbook_id) |

#### enrollments
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| user_id | INT | FK to users.id |
| course_id | INT | FK to courses.id |
| semester | VARCHAR(20) | NOT NULL |
| UNIQUE | | (user_id, course_id, semester) |

#### listings
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| seller_id | INT | FK to users.id |
| textbook_id | INT | FK to textbooks.id |
| condition | ENUM new, like_new, good, fair, poor | NOT NULL |
| price | DECIMAL(10,2) | NOT NULL |
| ai_recommended_price | DECIMAL(10,2) | nullable |
| description | TEXT | nullable |
| status | ENUM active, pending, sold, removed | DEFAULT active |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | ON UPDATE CURRENT_TIMESTAMP |

#### matches
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| listing_id | INT | FK to listings.id |
| buyer_id | INT | FK to users.id |
| match_score | DECIMAL(5,2) | NOT NULL (0-100) |
| is_notified | BOOLEAN | DEFAULT FALSE |
| matched_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

#### conversations
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| listing_id | INT | FK to listings.id |
| buyer_id | INT | FK to users.id |
| seller_id | INT | FK to users.id |
| status | ENUM pending, active, completed, cancelled | DEFAULT pending |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

#### messages
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| conversation_id | INT | FK to conversations.id |
| sender_id | INT | FK to users.id |
| content | TEXT | NOT NULL |
| is_agentic | BOOLEAN | DEFAULT FALSE |
| read_at | DATETIME | NULLABLE |
| sent_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

#### notifications
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| user_id | INT | FK to users.id |
| type | ENUM match, offer, message, resale_reminder, system | NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| body | TEXT | nullable |
| is_read | BOOLEAN | DEFAULT FALSE |
| reference_id | INT | NULLABLE (polymorphic reference to listing, conversation, etc.) |
| reference_type | VARCHAR(50) | NULLABLE |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

#### reviews
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| reviewer_id | INT | FK to users.id |
| reviewed_user_id | INT | FK to users.id |
| listing_id | INT | FK to listings.id |
| rating | INT | NOT NULL, CHECK (1-5) |
| comment | TEXT | nullable |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| UNIQUE | | (reviewer_id, listing_id) |

### 5.3 API Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user with .edu email |
| POST | /api/auth/login | Login, returns JWT token |
| GET | /api/auth/me | Get current user profile |

#### Courses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/courses | Get all courses (filterable by semester, university) |
| GET | /api/courses/{id} | Get course details with required textbooks |
| GET | /api/courses/{id}/textbooks | Get required textbooks for a course |
| GET | /api/users/me/courses | Get current user enrolled courses |

#### Textbooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/textbooks | Search textbooks (by ISBN, title, author) |
| GET | /api/textbooks/{id} | Get textbook details |
| GET | /api/textbooks/{id}/listings | Get all active listings for a textbook |

#### Listings
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/listings | Create a new listing (with AI price recommendation) |
| GET | /api/listings | Search/filter listings (course, ISBN, price range, condition) |
| GET | /api/listings/{id} | Get listing details |
| PUT | /api/listings/{id} | Update a listing |
| DELETE | /api/listings/{id} | Remove a listing (soft delete to status removed) |
| GET | /api/users/me/listings | Get current user listings |

#### Matching
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/matches/recommendations | Get recommended listings for buyer based on enrolled courses |
| GET | /api/matches/buyers/{listing_id} | Get potential buyers for a listing (seller-side) |

#### Messaging
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/conversations | Start a conversation about a listing (sends agentic first message) |
| GET | /api/conversations | Get all conversations for current user |
| GET | /api/conversations/{id}/messages | Get messages in a conversation |
| POST | /api/conversations/{id}/messages | Send a message |
| WebSocket | /ws/chat/{conversation_id} | Real-time chat connection |

#### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/notifications | Get current user notifications |
| PUT | /api/notifications/{id}/read | Mark notification as read |
| PUT | /api/notifications/read-all | Mark all notifications as read |

#### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/reviews | Submit a review after a transaction |
| GET | /api/users/{id}/reviews | Get reviews for a user |

#### AI / Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/chat | Send a message to the AI chatbot, get response |
| GET | /api/ai/price-recommendation | Get AI price recommendation for a textbook listing |

### 5.4 Security
# this section should be limited for the purpose of the demo. we want to demonstrate idea, not enterprise readiness.
- **Passwords:** Hashed with bcrypt (never stored in plaintext)
- **Authentication:** JWT tokens for API access
- **Encryption in transit:** TLS/HTTPS on all connections
- **Encryption at rest:** MySQL native encryption at rest for MVP v2; noted architecturally for MVP v1
- **.edu email verification:** Required for account activation
- **Authorization:** Users can only modify their own listings, messages, and profile
- **Input validation:** All API inputs validated via Pydantic models (FastAPI native validation)

---

## 6. MVP Versioning Strategy

### 6.1 MVP v1 — Backend Proof of Concept (This is what we have now)

**Due:** March 25, 2026

**Purpose:** Demonstrate to CGI mentor Pasha that the core backend systems work. Presented via Zoom screen-share.

**Format:** Python project run locally. Demonstrated via FastAPI built-in Swagger UI (/docs) — interactive, clean, shows a real working API. Optionally, a very simple HTML page hitting the API.

| Aspect | MVP v1 Spec |
|--------|-------------|
| Database | SQLite (self-contained, no external server needed) |
| ORM | SQLAlchemy |
| Backend | FastAPI |
| Frontend | Swagger UI (/docs) or minimal HTML |
| Auth | bcrypt password hashing, JWT tokens |
| AI Chatbot | NOT included |
| RAG / Ollama | NOT included |
| WebSockets | NOT included |
| Push Notifications | NOT included |
| Real-time Chat | NOT included |

**What MVP v1 must demonstrate:**
1. FastAPI server runs and serves endpoints
2. SQLite database with mock data pre-loaded on startup
3. Working API endpoints for: user registration/login, creating a listing, searching/filtering listings by course/ISBN/price/condition, getting matched recommendations for a buyer based on enrolled courses, sending a message between buyer and seller, getting an AI price recommendation (rule-based)
4. The rule-based matching engine returning ranked results when given a student course list
5. Mock data that tells a coherent story (realistic courses, books, users, prices at USJ)

**What MVP v1 does NOT need:**
- No frontend UI (Swagger is sufficient)
- No chatbot
- No WebSockets
- No push notifications
- No Ollama/RAG
- No real authentication flow (basic JWT is fine)
- Does not need to be perfect — needs to work

**Mock Data for MVP v1:**
- 1 university (USJ, domain: usj.edu)
- 5-8 courses with professors (Spring 2026 semester)
- 10-15 textbooks with realistic ISBNs, titles, authors, editions, retail prices
- 6-10 mock users (mix of students and alumni)
- Student enrollments linking users to courses
- Course-textbook requirements linking courses to required books
- 10-20 active listings at varying prices and conditions
- A few completed conversations with messages
- A few reviews

### 6.2 MVP v2 — Full Working Prototype (This is what we need to work on)

**Due:** By April 22, 2026 (Presentation Day)

**Purpose:** Full working prototype for the CGI final presentation. This is what gets demoed live and walked through in the UI. Must support live navigation — if a CGI evaluator asks to see a specific flow, the presenter can do it live.

| Aspect | MVP v2 Spec |
|--------|-------------|
| Database | SQLite with schema and create statements to be manually added to a mysql db |
| ORM | SQLAlchemy |
| Backend | FastAPI |
| Frontend | React + Tailwind CSS PWA |
| Auth | University SSO + .edu email signup, JWT, bcrypt, toggled on and off for demo |
| AI Chatbot | REAL — Ollama + RAG via ChromaDB |
| Matching Engine | Rule-based, fully functional |
| Real-time Chat | WebSockets via FastAPI |
| Notifications | In-app notification indicators |
| Agentic Messaging | Mocked with templates (not live LLM generation) |

**What is fully working in MVP v2:**
- React + Tailwind PWA frontend with unified dashboard (Shopping + My Listings views)
- Authentication flow (SSO + .edu email)
- Course-aware dashboard showing enrolled courses and available textbooks
- Search, sort, and filter functionality across listings
- AI chatbot (bottom-right corner) — real, powered by Ollama + RAG, grounded in listings, courses, FAQs, pricing, bookstore comparisons
- AI-assisted listing creation with price recommendation
- Rule-based matching engine surfacing recommended books to buyers
- Private in-app messaging via WebSocket
- In-app notification indicators

**What is mocked but functional-looking in MVP v2:**
- Agentic first-message generation (pre-built templates simulating AI-generated outreach)
- Push notifications to phone/email (in-app visual indicators only)
- Student enrollment data (synthetic but realistic)
- Course metadata and syllabi (synthetic)
- Textbook metadata (synthetic)
- LMS/Blackboard integration (mocked screenshots showing OpenShelf as a portal tab)

**What is NOT in MVP v2:**
- Actual LMS/Blackboard integration
- Real payment processing
- Book-for-book swap logic
- Actual phone/email push notifications
- Real university data
- ISBN barcode scanning (manual entry + automated API lookup where available)

---

## 7. Data Strategy

### 7.1 Data Sources

All data for both MVP versions is **synthetic/mock**. This is explicitly permitted by the CGI capstone guidelines.

| Data Type | Source | Notes |
|-----------|--------|-------|
| Universities | Mock | USJ as pilot, with schema supporting multi-campus |
| Users | Mock | 25-30+ synthetic student/alumni profiles |
| Courses | Mock | Based on realistic USJ-style course codes and names |
| Syllabi / Course-Textbook Links | Mock | Synthetic mapping of courses to required textbooks |
| Textbooks | Mock | Realistic ISBNs, titles, authors, editions, retail prices |
| Listings | Mock | Varying prices, conditions, and statuses |
| Transactions and Messages | Mock | Pre-populated for demo storytelling |
| Reviews | Mock | Sample ratings and comments |

### 7.2 Chatbot Knowledge Base (for ChromaDB in MVP v2)

The following content will be authored and embedded into the vector store:

1. **Platform FAQs** — How to create an account, list a book, search for books, message a seller, leave a review, etc.
2. **Pricing Guidance** — How AI price recommendations work, average prices by condition, tips for pricing competitively
3. **Bookstore Comparison Data** — Why OpenShelf is cheaper than campus bookstore, Amazon, Chegg; sample price comparisons
4. **Guardrail Content** — What the chatbot should and should not do, response boundaries, escalation paths
5. **Live Database Content** — Current listings, course data, and availability (queried dynamically via RAG retrieval)

A template for this knowledge base will be developed separately and refined by the team.

---

## 8. Presentation Strategy

### 8.1 Format

- **15 minutes** presentation + **5 minutes** Q&A (20 minutes total)
- All 5 team members actively participate
- Slides are visual and concise — detailed content belongs in the written report
- Live MVP walkthrough included (not just slides)

### 8.2 Narrative Arc

The presentation follows the story of a student:

A new student arrives on campus and gets hit with $700 in required textbooks across all their classes. They do not want to go without the materials, but the price is too high to justify buying them all new. They search online — Amazon, Chegg, Facebook groups — but cannot find affordable, convenient options from their own campus. They are stuck in a lose-lose decision: overpay or go without.

**OpenShelf is the resolution.** The presentation traces the arc from problem to current-state workflow to solution to AI capabilities to live demo to business impact to feasibility to roadmap to responsible AI to closing.

### 8.3 Required Presentation Sections (per CGI Guidelines)

1. **Problem and Context** — Industry context, specific problem, why it matters, who is impacted
2. **Current-State Workflow** — How it works today (before AI), key steps, where bottlenecks occur. Use workflow diagrams.
3. **Making the Problem Measurable** — Metrics, indicators, data assumptions
4. **AI Solution Concept** — Overview, 1-2 AI techniques, how AI fits the workflow, inputs/outputs/interactions
5. **Target Outcomes, Business Value and ROI** — Target outcomes, success metrics, at least one quantified estimate, value proposition, high-level ROI discussion
6. **Feasibility, ROI Assumptions and Risks** — Data feasibility, integration considerations, operating environment, key assumptions, risks and mitigations
7. **Implementation Roadmap** — Phased rollout, resources, timeline and milestones
8. **Technical Deliverable** — Walk through / demonstrate the MVP (for CS teams)
9. **Responsible AI Considerations** — Ethical, privacy, bias considerations and mitigations
10. **Closing Summary** — Restate problem, summarize solution and value, expected ROI, one clear takeaway

---

## 9. KPIs and Success Metrics

### 9.1 Financial Impact
- Average textbook spending reduction per student per semester (target: 20-30% vs. buying new)
- Resale recovery rate (what percentage of book value does a seller recover)
- Reduction in new textbook purchases campus-wide

### 9.2 Access and Efficiency
- Time-to-find: Average time from needing a book to finding a listing (target: reduce by 50%+)
- Percentage of students with required textbooks by Week 1 of classes
- Listing-to-sale conversion rate
- Average days from listing to purchase

### 9.3 Platform Engagement
- Seller participation rate (percentage of eligible students listing at least one book)
- Platform adoption rate per semester
- Chatbot resolution rate (percentage of queries resolved without human intervention)
- Buyer satisfaction score (post-transaction survey)

### 9.4 Sustainability
- Textbook reuse rate (percentage of textbooks that cycle through 2+ owners)
- Volume of books diverted from landfill/waste
- Reduction in unused textbook volume per semester

### 9.5 Operational
- Cost-per-transaction for the university
- System uptime and reliability
- Average chatbot response time

---

## 10. Implementation Roadmap (for CGI Presentation)

### Phase 1: Pilot (Months 1-3)
- Deploy at USJ as single-campus pilot
- Synthetic data seeded, real student accounts onboarded
- Core features: listings, search, matching, chatbot, messaging
- Monitor adoption, gather feedback

### Phase 2: Refinement (Months 4-6)
- Iterate on UI/UX based on student feedback
- Tune matching algorithm weights based on transaction data
- Expand chatbot knowledge base
- Introduce in-app payments
- Add book-for-book swap feature

### Phase 3: Scale (Months 7-12)
- Multi-campus rollout (plug-and-play architecture)
- LMS integration (Blackboard, Canvas LTI)
- Expand to other course materials (lab manuals, clickers, etc.)
- Alumni network expansion
- University partnership program

---

## 11. Risks and Mitigations

| Risk | Category | Mitigation |
|------|----------|------------|
| Low student participation / cold-start problem | Adoption | Seed with alumni donations, partner with student orgs, integrate with course registration |
| Competition from Amazon, Chegg, bookstores | Market | Campus-only trust, university backing, AI-powered convenience, no shipping delays |
| Data privacy / student information security | Legal/Ethical | .edu verification, encryption at rest and in transit, FERPA compliance considerations |
| Chatbot hallucinations or bad recommendations | Technical | RAG grounding in real data, guardrails, human fallback |
| Listings become stale or inaccurate | Operational | Automated semester-end cleanup, listing expiration, seller nudges |
| Publisher resistance to textbook resale | Legal | First-sale doctrine protects resale of physical books; platform facilitates, does not sell |
| Low long-term engagement | Adoption | End-of-semester resale prompts, integration with course registration, gamification |

---

## 12. Responsible AI Considerations

- **Bias:** Price recommendation algorithm must not disadvantage sellers based on any demographic factors. Matching engine should be transparent and auditable.
- **Privacy:** Student enrollment data, purchase history, and messaging content must be protected. FERPA considerations for educational records.
- **Transparency:** Users should know when they are interacting with AI (chatbot clearly labeled, agentic messages disclosed).
- **Data minimization:** Collect only what is needed for the platform to function.
- **Human oversight:** AI assists and recommends — humans make final decisions on pricing, purchasing, and exchanges.
- **Fairness in recommendations:** Matching should prioritize relevance, not seller profit or platform metrics.

---

## 13. Open Decisions and Future Considerations

These items have been acknowledged but not yet finalized:

- Specific Ollama model selection (Qwen 3 8B vs. 3B-class) — depends on server hardware
- Embedding model for RAG pipeline
- Exact ChromaDB schema and chunking strategy
- ISBN automated lookup API selection (Google Books vs. ISBNdb vs. Open Library)
- Detailed ROI calculations and quantified estimates (needed before content lock)
- Written report draft (all sections)
- Architecture diagram (visual)
- Chatbot knowledge base template content
- Mocked LMS integration screenshots

---

## 14. File Inventory

### CGI Framework Documents (Read-Only Reference)
- 6012448.pdf — 13-Week Capstone Project Roadmap
- 6012099.pdf — 2026 USJ x CGI Capstone Project Guidelines (full)
- 2026_USJ_Capstone_Kickoff_Deck.pdf — Kickoff presentation including Lean/Agile/DevOps methodology
- Capstone_Presentation_Guidelines_20.txt — Detailed presentation requirements and section breakdown

### OpenShelf Project Documents
- Problem_and_Context.pdf — Problem definition, stakeholders, AI integration overview
- OpenShelf_Pitch_Deck.pdf — 12-slide pitch deck with mockups, PESTEL, SWOT
- AIPowered_Campus_Textbook_Marketplace.pdf — PESTEL and SWOT analysis deep dive
- AI-Enabled_Solution_Overview.docx — AI solution overview, workflow comparison, system I/O

---

*Last updated: March 25, 2026*
*Version: 1.0*
