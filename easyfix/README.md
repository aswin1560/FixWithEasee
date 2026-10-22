# FixWithEase (AI-Powered Local Skill Connect)

**FixWithEase** is an AI-driven web application that connects local skilled service professionals (plumbers, electricians, carpenters, painters, and appliance technicians) with nearby homeowners. The platform features subscription tiers, Gemini AI-powered natural-language matching, a strict hazard-blocking "Fix It Yourself" DIY assistant, Razorpay test mode payments, and real-time Haversine geolocation proximity scoring.

---

## 🌟 Key Features

### 1. Free Tier (Manual Directory)
- **Keyword & Filter Search:** Browse workers by category (*Plumber, Electrician, Carpenter, Painter, AC Repair, Appliance Repair*) or Chennai neighborhoods (*Adyar, T. Nagar, Velachery, Anna Nagar, Porur, Guindy*).
- **Worker Cards:** Shows verified badges, experience, star rating, availability status (`🟢 Available` / `🔴 Busy`), and Haversine distance in kilometers.
- **5% Platform Consulting Fee:** A 5% platform consulting fee is automatically added to bookings placed by free users.

### 2. Subscriber Tier (₹30/month or ₹300/year)
- **AI-Powered Problem Matcher:** Customers describe their household issue in plain everyday words (e.g., *"my kitchen tap is leaking"*, *"fan not working"*). Google Gemini AI diagnoses the required skill, assesses urgency, checks hazards, and scores/ranks the top 5 nearest technicians.
- **"Fix It Yourself" (DIY Assistant):** Step-by-step numbered tutorials, tools needed, completion times, and curated YouTube video help for safe household fixes.
- **0% Consulting Fee:** Subscribers enjoy a 100% waiver on all order booking fees.
- **Server-Side Protection:** Subscriptions are verified on the server before unlocking any AI route; unauthorized requests receive an HTTP 403 paywall.

### 3. Safety Guardrail & Hazard Blocklist
- Enforces strict safety protocols: **NEVER teaches hazardous DIY work**.
- **Blocked Categories:** Electrical wiring, sockets, switchboards, MCB/fuse, gas (LPG) lines, water heaters/geysers, structural wall-cutting, roofing/heights, and toxic chemicals.
- **Multi-Language Detection:** Regex patterns detect keywords in English, Tamil (*min saram*, *theepori*, *current shock*, *gas aduppu*), and Hindi (*bijli ka shock*, *gas risav*).
- **Automatic Referral:** When a hazard is detected, step generation is halted, a red warning banner is displayed, and the customer is offered matching licensed professionals.

### 4. Payments & Administration
- **Razorpay TEST Mode:** Supports ₹30/month and ₹300/year checkout with server-side HMAC-SHA256 cryptographic signature validation.
- **Yearly Plan Savings:** Highlights the ₹60/year savings (2 months free).
- **Admin Financial Dashboard (`/admin`):** Tracks total platform revenue, subscription revenue breakdown, 5% consulting fee revenue, and live order records.
- **Reviews & Ratings:** Customers can mark completed orders and submit 1–5 star reviews, automatically recalculating the technician's average rating.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite (clean, standard SQL schema easily portable to MySQL)
- **AI Integration:** Google Gemini API (`gemini-1.5-flash` with resilient heuristic fallback)
- **Payments:** Razorpay Python SDK (TEST mode)
- **Location:** Browser Geolocation API + Spherical Haversine Distance Formula
- **Frontend:** HTML5, CSS3 (mobile-responsive with flexbox/grid), Vanilla JavaScript (no external frameworks)

---

## 📁 Project Directory Structure

```text
easyfix/
│
├── app.py                      # Flask main entry point & route controllers
├── vercel.json                 # Vercel serverless deployment routing config
├── .gitignore                  # Git ignore rules (secrets, cache, venv)
├── .env.example                # Environment variables template
├── .env                        # Local configuration file (gitignored)
├── requirements.txt            # Python dependencies
├── database.db                 # SQLite database file (starter seed data)
├── init_db.py                  # Database schema initialization script
├── seed_db.py                  # Seeds 20 Chennai workers & sample users
├── README.md                   # Project documentation
├── DEMO_SCRIPT.md              # Live demonstration & viva walkthrough
├── PRESENTATION_SCREENSHOTS.md # Slide screenshot recommendations
│
├── api/                        # Vercel Serverless Function entry point
│   └── index.py                # WSGI handler for Vercel Python runtime
│
├── models/                     # SQLite query helper modules
│   ├── __init__.py
│   ├── db.py                   # Connection factory with Row mapping
│   ├── user.py                 # User authentication & password hashing
│   ├── worker.py               # Worker queries & SQL LIKE search
│   ├── subscription.py         # Server-side is_subscribed() validation
│   ├── order.py                # Orders management & revenue stats
│   └── review.py               # Ratings submission & average calculation
│
├── services/                   # Business logic & external services
│   ├── __init__.py
│   ├── ai_matcher.py           # Gemini AI problem intake & worker scoring
│   ├── safety_filter.py        # Multi-language hazard keyword blocklist
│   ├── diy_tutor.py            # DIY tutorial generator & video help
│   ├── payment_service.py      # Razorpay order creation & signature check
│   └── location.py             # Haversine distance formula implementation
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Mobile-responsive navbar & footer
│   ├── index.html              # Landing page
│   ├── workers.html            # Directory search with filters
│   ├── book.html               # Booking form with live 5% fee preview
│   ├── order_detail.html       # Order status, billing & review form
│   ├── my_orders.html          # Customer bookings history
│   ├── ai_search.html          # Plain-words AI problem matcher
│   ├── fix.html                # Fix It Yourself DIY tutorial page
│   ├── pricing.html            # Pricing plans & Razorpay modal
│   ├── login.html              # Login with one-click test credentials
│   ├── register.html           # Customer & worker registration
│   ├── admin.html              # Admin financial & revenue dashboard
│   └── subscription_required.html # 403 Forbidden paywall
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Custom responsive styles & animations
│   └── js/
│       └── main.js             # Mobile nav toggle & alert dismissers
│
└── tests/                      # Automated unit test suites (47 tests)
    ├── __init__.py
    ├── test_phase1.py          # Setup & home page tests
    ├── test_phase2.py          # Database models & seed counts
    ├── test_phase3.py          # Auth & 403 subscription protection
    ├── test_phase4.py          # Directory search & 5% fee logic
    ├── test_phase5.py          # Gemini AI matcher & worker ranking
    ├── test_phase6.py          # Safety blocklist & DIY tutorials
    ├── test_phase7.py          # Razorpay signature & revenue metrics
    └── test_phase8.py          # Order reviews, ratings & mobile layout
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Clone / Open Directory
Open PowerShell or your terminal in the project directory:
```powershell
cd c:\Users\Aswin.R.J\Desktop\easyfix
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
*(Optionally add your Google Gemini API key or Razorpay test credentials into `.env`).*

### 5. Initialize and Seed the Database
```powershell
python seed_db.py
```
This sets up all 5 tables and populates **20 skilled workers** across Chennai, sample customer accounts, and initial reviews.

### 6. Run the Flask Web Application
```powershell
python app.py
```
The server will start at: **http://127.0.0.1:5000**

---

## 🧪 Running Automated Tests

Run the complete test suite across all 8 phases:
```powershell
python -m unittest discover tests
```
*(All 50 unit tests will execute and pass).*

---

## 👥 Demo Accounts (Password: `Password123!`)

| User | Email | Role | Features Unlocked |
| :--- | :--- | :--- | :--- |
| **Kavitha Raman** | `customer.sub@example.com` | Customer (Subscribed) | Full AI Matchmaker, Fix It Yourself DIY, 0% Fee |
| **Arun Kumar** | `customer.free@example.com` | Customer (Free) | Manual Directory Search, 5% Consulting Fee |
| **Admin Manager** | `admin@example.com` | Admin | Financial Dashboard (`/admin`), Revenue Stats |
| **Murugan S** | `murugan.plumber@example.com` | Worker | Plumber in T. Nagar (4.9★ rating) |

*(Use the one-click demo buttons on `/login` to auto-fill any account).*

---

## 🚀 Deployment Guide: GitHub & Vercel

### Step 1: Upload Project to GitHub

#### Option A: Using the Git CLI
1. Open PowerShell or Command Prompt inside the project directory:
   ```bash
   cd c:\Users\Aswin.R.J\Desktop\easyfix
   ```
2. Initialize git and commit your files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: FixWithEase full-stack AI platform"
   git branch -M main
   ```
3. Create a new repository on [GitHub](https://github.com/new) named `fixwithease`.
4. Link and push to GitHub:
   ```bash
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/fixwithease.git
   git push -u origin main
   ```

#### Option B: Using GitHub Desktop or Web Upload
1. Open **[GitHub Desktop](https://desktop.github.com/)** and select **File -> Add Local Repository...** pointing to `easyfix`.
2. Click **Publish repository** to GitHub.
3. *Alternatively*, on [GitHub.com](https://github.com), create a new repository, click **Upload an existing file**, drag and drop the files, and click **Commit changes**.

---

### Step 2: Deploy to Vercel (One-Click)

FixWithEase is configured with `vercel.json` and `api/index.py` for direct serverless deployment:

1. Go to **[Vercel](https://vercel.com/)** and sign in with your GitHub account.
2. On your Vercel Dashboard, click **Add New...** ➜ **Project**.
3. Locate your `fixwithease` repository and click **Import**.
4. In the **Configure Project** screen:
   - **Framework Preset:** Leave as *Other* (detected automatically via `vercel.json`).
   - **Root Directory:** `./`
5. Expand **Environment Variables** and add the following keys:
   | Key | Value | Description |
   | :--- | :--- | :--- |
   | `SECRET_KEY` | *(any random string)* | Required for Flask session security |
   | `GEMINI_API_KEY` | *(your Gemini API key)* | Optional/Recommended (free at aistudio.google.com) |
   | `RAZORPAY_KEY_ID` | `rzp_test_demo123` | Optional test key |
   | `RAZORPAY_KEY_SECRET` | `secret_demo123` | Optional test secret |
6. Click **Deploy**.
7. In ~30–45 seconds, Vercel will complete the build and assign you a live HTTPS URL (e.g., `https://fixwithease.vercel.app`)!

> 💡 **How SQLite Works on Vercel:**  
> Vercel functions execute in an ephemeral container where the project folder is read-only. `models/db.py` automatically detects the Vercel environment and initializes the SQLite database inside `/tmp/database.db`, pre-seeding all 20 Chennai workers and demo accounts so your live web app works seamlessly for evaluators and visitors without any setup.
