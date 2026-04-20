# OpenShelf MVP v2 — Remaining Tasks

Snapshot after Phase C (frontend) completed. Backend and UI are end-to-end
functional against the template chatbot; Phase B swaps real Ollama in behind
the stable `/chat/` contract, and Phase D is polish for the CGI presentation.

---

## Phase B — Ollama + RAG chatbot

The chat endpoint (`POST /chat/`) and widget (`ChatbotWidget.jsx`) already
work against `app/services/chatbot_service.py`'s template fallback. Phase B
replaces the template with a real Ollama call + retrieval, keeping the
template as the graceful fallback.

### B1 — Ollama client wrapper
- New `app/services/ollama_client.py` with a thin async client.
- Env vars: `OLLAMA_HOST` (default `http://localhost:11434`), `OLLAMA_MODEL`
  (default `llama3.2`).
- Functions: `is_available()` (quick health ping with short timeout),
  `generate(prompt, system=None, temperature=0.2) -> str`.
- On any network or decode error, raise a custom `OllamaUnavailable`
  exception — never swallow silently.

### B2 — RAG retrieval layer
- New `app/services/rag_retriever.py`.
- Build context by querying the existing SQLite data:
  - user's enrolled courses + required textbooks
  - active listings for those textbooks (title, condition, price, seller)
  - user's own listings (so the bot can answer "what am I selling?")
  - canned FAQ entries (hard-coded dict for now)
- Return a `List[ChatSource]` that matches the existing schema so the
  frontend's sources display keeps working.
- Keep it deterministic and fast — no embeddings yet, just SQL joins.
  Embedding-based retrieval is a stretch goal.

### B3 — Wire chatbot_service to Ollama
- In `chatbot_service.generate_chat_response`:
  1. Call `rag_retriever.retrieve(db, user, request.message)` → sources.
  2. Build a prompt: system instructions + serialized sources + history + message.
  3. Try `ollama_client.generate(prompt)`. On success, return the response
     with `model=<OLLAMA_MODEL>` and the same sources.
  4. On `OllamaUnavailable`, fall back to the existing template path and
     return with `model="template"`.
- The frontend already renders the `model` badge, so fallback vs. live is
  visually obvious during the demo.

### B4 — Prompt design
- System prompt should:
  - Establish the assistant as the OpenShelf campus textbook helper.
  - Forbid hallucinating listings that aren't in the retrieved context.
  - Require citing sources by title when relevant.
  - Keep responses under ~120 words.
- Test manually with all five intents the template routes (greeting, howto,
  pricing, listing, default) and confirm answers are grounded.

### B5 — Integration tests
- Add `tests/test_chat_endpoint.py` (new) that:
  - monkeypatches `ollama_client.generate` to raise `OllamaUnavailable` and
    confirms the template fallback path runs.
  - monkeypatches it to return a canned string and confirms the response
    and sources flow through.
- Keep the existing chatbot_service template tests passing unchanged.

### B6 — Docs
- Update `README.md` with:
  - How to install Ollama + pull the default model.
  - Env vars for the wrapper.
  - How to verify fallback works (`OLLAMA_HOST=http://127.0.0.1:1` to force it).

---

## Phase D — Presentation polish *(deprioritized)*

Noah flagged that the presentation date is flexible and the app itself is
the priority. These are nice-to-haves, not blockers for the CGI demo.

### D1 — Dashboard landing animation
- Subtle fade-in on the Shopping grid + match cards so the first load feels
  intentional rather than "it popped in."
- Use tailwindcss-animate utilities — the dep is already installed.

### D2 — Empty state illustrations
- Replace the plain "No listings match your filters" / "No conversations
  yet" blocks with a small illustration + CTA.
- Candidate: lucide icons at `h-12 w-12` + a suggested action button.

### D3 — Demo seed refresh
- `seed.py` currently has a canonical buyer persona. For the presentation,
  ensure the seed produces:
  - at least 3 visible matches on Noah's dashboard
  - 2 existing conversations (one unread)
  - 1 notification of each type (message, match, review)
- Idempotent reseed script so we can reset state right before the demo.

### D4 — Presentation script / talking points doc
- New `docs/demo_script.md` with:
  - 5-minute walkthrough order (login → shopping → matches → contact seller
    → live message arriving → my listings → AI price → chatbot).
  - Fallback plan if Ollama or the WebSocket dies mid-demo.

### D5 — Production deploy notes
- Noah plans to host on his personal web server. Add `docs/deploy.md`:
  - How to build the frontend (`npm run build` → `dist/`) and point FastAPI
    at it as a static mount.
  - Reverse proxy config sketch for `/ws` WebSocket passthrough.
  - Env var checklist (`OLLAMA_HOST`, `SECRET_KEY`, `DATABASE_URL`).

---

## Known gaps / follow-ups surfaced during Phase C

Not worth their own phase, but worth remembering:

- **`GET /listings/` has no `seller_id` filter.** My Listings filters
  client-side today. If seed data ever grows, add `?seller_id=` to the
  backend router and thread it through `listingsApi.list`.
- **`RegisterPage` hardcodes `university_id = 1`.** There's no
  `/universities/` endpoint yet. When multi-school lands, add the router
  and swap the constant for a dropdown.
- **Reconnecting WebSocket.** `useChatSocket` intentionally doesn't retry.
  If the demo ever loses the socket mid-thread, revisit.
- **Inbox polling at 10s.** Works for the demo, but the right answer is a
  second, lightweight WebSocket channel (`/ws/inbox/:user_id`) that pushes
  unread-count deltas. Deferred.
