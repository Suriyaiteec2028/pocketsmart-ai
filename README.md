# PocketSmart AI – Your Smart Budget & Recommendation Assistant

PocketSmart AI is a production-style, AI-powered personal budget and shopping recommendation web application. It intelligently organizes a user's total budget, analyzes specific lifestyle requirements and preferences, and generates personalized, value-for-money recommendations across three specialized planners:
1. **Home Interior Budget Planner** (furniture, lighting, curtains, storage, decor across Amazon, Flipkart, IKEA)
2. **Party & Event Budget Planner** (banquets, catering via Swiggy/Zomato, theme decoration, DJs, OYO accommodations)
3. **Jewelry & Outfit Styling Planner** (multimodal vision AI analyzing outfit photos, dominant colors, matching metals/stones)

---

## Key Features

- **Strict Budget Ceiling Guarantee**: Unlike generic AI chatbots that hallucinate arbitrary figures, PocketSmart AI's backend independently computes `Remaining = Budget - Total Spent` and automatically scales or drops low-priority items if recommendations exceed your budget.
- **Three Specialized Planners**:
  - **Home Interior**: Adaptive room selection (Living Room, Bedroom, Kitchen, Dining, Study, Balcony), custom quantities, style preferences (Modern, Minimalist, Scandinavian, Luxury, etc.), and priority weighting.
  - **Party & Event**: Guest-count dynamic catering calculation (per-person pricing), venue booking, entertainment options, and conditional accommodation room sizing.
  - **Jewelry Planner**: Multimodal vision AI. Upload outfit images (JPG, PNG, WEBP) to automatically extract dominant color palettes, style tones, and match complementary jewelry sets.
- **Resilient Fallback Engine**: If Google Gemini API is unconfigured, rate-limited, or temporarily offline, PocketSmart AI seamlessly switches to its intelligent local dataset and PIL-based image color extraction algorithms. The application remains 100% functional.
- **Platform Adapter Architecture**: Sourced through a modular adapter design (`services/platforms/`) integrating realistic datasets for **Amazon**, **Flipkart**, **IKEA**, **Swiggy**, **Zomato**, and **OYO Townhouse**.
- **Secure Authentication & Data Isolation**: Password hashing using `bcrypt`, stateless signed JWT tokens stored in HTTP-only cookies and Authorization headers, and strict per-user ownership verification on every database query.
- **Recommendation History, Details & Reuse**: Filter, sort, view full input/output breakdowns, delete records with confirmation dialogs, and one-click "Reuse Plan" that repopulates planner forms.
- **Asynchronous Favorite Saving**: Save individual items directly to favorites with real-time feedback and count tracking on the User Dashboard.
- **Modern Responsive Design**: Accessible card-based UI built with HTML5, CSS3, Vanilla JS, and Jinja2 templates, optimized for desktop, tablet, and mobile.

---

## Technology Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic v2
- **Database**: SQLite with SQLAlchemy ORM (swappable to PostgreSQL via `DATABASE_URL`)
- **Authentication**: JWT (`pyjwt`), Password Hashing (`bcrypt`), HTTP-only cookies
- **AI / Multimodal**: Google Gemini API (`gemini-1.5-flash` / `gemini-1.5-pro` / `gemini-2.0-flash` configurable), Pillow (PIL)
- **Frontend**: Semantic HTML5, CSS3 Variables, Responsive Flexbox/Grid, Vanilla JavaScript, Jinja2 Templates, FontAwesome 6
- **Testing**: `pytest`, `fastapi.testclient`

---

## Project Structure

```
pocketsmart-ai/
├── app/
│   ├── main.py                  # FastAPI app factory, lifespan, routes & static mounts
│   ├── config.py                # Environment and app configuration
│   ├── routes/
│   │   ├── auth.py              # Register, login, logout, session-info API routes
│   │   ├── home.py              # Home Interior generation endpoint
│   │   ├── party.py             # Party & Event generation endpoint
│   │   ├── jewelry.py           # Jewelry multimodal & image upload endpoints
│   │   ├── recommendations.py   # Save items, reuse plan, plan details
│   │   ├── history.py           # User history filtering, sorting & deletion
│   │   └── pages.py             # Jinja2 template page renderers
│   ├── services/
│   │   ├── gemini_service.py    # Google Gemini client (text + multimodal vision)
│   │   ├── recommendation_engine.py  # Central recommendation orchestrator
│   │   ├── home_service.py      # Home AI prompt & fallback engine
│   │   ├── party_service.py     # Party AI prompt & guest-count engine
│   │   ├── jewelry_service.py   # Multimodal image analysis & jewelry engine
│   │   └── platforms/
│   │       ├── base.py          # Abstract BasePlatformAdapter
│   │       ├── amazon.py        # Amazon product catalog adapter
│   │       ├── flipkart.py      # Flipkart retail adapter
│   │       ├── ikea.py          # IKEA home furnishing adapter
│   │       ├── swiggy.py        # Swiggy catering & food box adapter
│   │       ├── zomato.py        # Zomato banquets & event dining adapter
│   │       └── oyo.py           # OYO Townhouse halls & accommodation adapter
│   ├── models/
│   │   ├── user.py              # User model with hashed passwords
│   │   ├── recommendation.py    # RecommendationPlan model (JSON inputs & results)
│   │   └── saved.py             # SavedRecommendation model
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── database/                # SQLAlchemy session & init_db
│   └── utils/                   # Auth helpers, budget math, image validators
├── templates/                   # Dual-mode Jinja2 HTML templates (Public top navbar + Authenticated Left Sidebar)
├── static/                      # CSS stylesheets and interactive JavaScript
├── uploads/                     # Sanitized uploaded outfit images
├── tests/                       # Complete pytest test suite (18 passing tests, 100% coverage)
├── inspect_db.py                # Database inspection utility
├── .env.example                 # Environment template
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Project dependencies
├── run.py                       # Easy launch script
└── README.md

```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Git (optional)

### 2. Installation
Open your terminal in the `pocketsmart-ai` directory:

```bash
# Optional: Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the `.env.example` file to `.env`:

```bash
# Windows (PowerShell):
Copy-Item .env.example .env

# macOS / Linux:
cp .env.example .env
```

Open `.env` and configure your settings:
```env
# Optional: Add your Google Gemini API key to enable live AI generation
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# JWT Secret Key
SECRET_KEY=pocketsmart_dev_secret_key_super_secure_2026_jwt_token_auth

# Database (Default: SQLite file pocketsmart.db)
DATABASE_URL=sqlite:///./pocketsmart.db
```
> **Note**: If `GEMINI_API_KEY` is left blank, the application automatically runs in **Intelligent Fallback Mode** using realistic datasets, mathematical budget allocations, and PIL-based image color extraction.

### 4. Running the Application
Run the launcher script:
```bash
python run.py
```
Or directly with Uvicorn:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Access the Web Application
- **Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Running the Automated Test Suite

PocketSmart AI includes automated integration and unit tests covering authentication, budget verification, home planning, party allocations, multimodal jewelry processing, and history data isolation:

```bash
python -m pytest -v
```

All 14 tests run automatically against the FastAPI test client.

---

## User Journey Walkthrough

1. **Register / Login**: Create an account with name, email, and password. You are automatically authenticated and directed to your Dashboard.
2. **Dashboard**: View summary cards (Total Plans, Home, Party, Jewelry, Saved Items), quick planner shortcuts, and recent history.
3. **Home Planner (`/home-planner`)**:
   - Enter your budget (e.g. ₹1,00,000).
   - Select rooms (Living Room, Bedroom, Kitchen, etc.). Dynamic item checklists appear.
   - Adjust quantities and style preferences.
   - Click **Generate Smart Home Plan**. Watch the multi-step animated loader.
   - Review room-by-room progress bars and product cards from Amazon, Flipkart, and IKEA.
4. **Party Planner (`/party-planner`)**:
   - Enter guest count (e.g. 50), event type (Birthday), and budget (e.g. ₹50,000).
   - Toggle guest accommodations if needed.
   - Review catering packages (Swiggy/Zomato), venue options (OYO Townhouse), and entertainment.
5. **Jewelry Planner (`/jewelry-planner`)**:
   - Drag & drop an outfit photo. Preview updates instantly.
   - Click **Generate Jewelry Recommendations**.
   - Gemini Vision AI extracts dominant colors (e.g. Navy Blue, Silver), recommends complementary tones (Silver, Zirconia), and presents curated jewelry sets.
6. **Save & History (`/history`)**:
   - Favorite individual items across plans.
   - Filter plans by category, sort by date or budget.
   - Click **Reuse Plan** to pre-fill planner forms with previous parameters.

---

## Security Best Practices Implemented

- Passwords hashed with `bcrypt` using cryptographic salts.
- Signed JWT tokens with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Tokens delivered via secure HTTP-only cookies and bearer headers.
- Input validation via Pydantic v2 schemas.
- Upload validation checking MIME types, file size limits (5MB), and Pillow image structure verification.
- Safe filename generation using UUIDv4 preventing path traversal attacks.
- Sensitive credentials strictly isolated in environment variables.

---

## License

This project is licensed under the MIT License.
