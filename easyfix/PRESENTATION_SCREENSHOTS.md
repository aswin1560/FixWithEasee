# FixWithEase - Recommended Presentation Screenshots: "Program Code & Output"

This guide lists the exact screenshots to capture for your presentation slides and final project report to showcase both the user-facing output and the technical implementation.

---

## 📸 Section 1: Output / UI Screenshots

| # | Slide / Section Title | URL to Capture | How to Recreate & What to Capture |
| :-: | :--- | :--- | :--- |
| **1** | **Home Page & Directory Search** | `http://127.0.0.1:5000/` | Hero banner with search bar, popular skill badges (*Plumber*, *Electrician*, *Carpenter*), and the ₹30/month pricing callout. |
| **2** | **Free Directory & 5% Fee Calculation** | `http://127.0.0.1:5000/book/4` *(logged in as Arun)* | Booking screen showing **Base Amount ₹500** + **Platform Consulting Fee ₹25 (+5% Free Tier Fee)** = **Total ₹525.00**. |
| **3** | **Subscription Paywall (Server-Side 403)** | `http://127.0.0.1:5000/fix` *(logged in as Arun)* | The **"Subscribe to Unlock AI Features"** friendly paywall page demonstrating strict server-side access control. |
| **4** | **Pricing Page & Razorpay Checkout** | `http://127.0.0.1:5000/pricing` | Pricing tier cards showing **₹30/month** and **₹300/year** (with the *"🎁 Save ₹60 / year"* tag) and the Razorpay test modal popup. |
| **5** | **AI Natural-Language Matchmaker** | `http://127.0.0.1:5000/ai-search?q=my+kitchen+tap+is+leaking` *(logged in as Kavitha)* | The **AI Problem Diagnosis** card (Skill: Plumber, Urgency: Medium) and the **Top 5 Ranked Workers** with percentage match scores and recommendation reasons. |
| **6** | **"Fix It Yourself": Safe DIY Tutorial** | `http://127.0.0.1:5000/fix?q=leaking+tap` | The 5-step numbered tutorial for leaking tap, Tools & Materials cards, the *"🛑 Stop and Call a Pro"* warning, and YouTube video help cards. |
| **7** | **"Fix It Yourself": Risky Task Refusal** | `http://127.0.0.1:5000/fix?q=socket+sparking` | The red warning banner: **"🚫 Please Consult a Professional (Electrical Hazards)"**, showing zero DIY steps and the direct button to find licensed electricians. |
| **8** | **Admin Financial Dashboard** | `http://127.0.0.1:5000/admin` *(logged in as Admin)* | KPI metric cards displaying Total Platform Revenue, Subscription Revenue (₹30 & ₹300), 5% Consulting Fee Revenue, and the Recent Orders table. |

---

## 💻 Section 2: Program Code Snippets

Take clean IDE screenshots of these exact files and line ranges to demonstrate the project's engineering depth:

### 1. Multi-Factor Worker Ranking & Scoring Algorithm
- **File:** `services/ai_matcher.py` (lines 150–245)
- **Key Highlight:** Demonstrates how Gemini AI's diagnosis is translated into weighted scores: Skill match (50 pts), Haversine distance proximity (20 pts), Average rating (15 pts), Live availability (10 pts), and Past completed orders (5 pts).

### 2. Multi-Language Safety Guardrail & Blocklist
- **File:** `services/safety_filter.py` (lines 15–85)
- **Key Highlight:** Shows regex pattern matching for hazardous electrical, gas, geyser, structural, and chemical keywords across English, Tamil (*min saram*, *theepori*, *gas aduppu*), and Hindi (*bijli ka shock*, *gas risav*).

### 3. Server-Side Subscription Check & Route Protection
- **File:** `app.py` (lines 45–75)
- **Key Highlight:** Shows the custom `@subscription_required` decorator verifying active status and `end_date >= datetime.now()` directly on SQLite, returning HTTP 403 on violations.

### 4. Razorpay Test Mode HMAC-SHA256 Cryptographic Verification
- **File:** `services/payment_service.py` (lines 80–120)
- **Key Highlight:** Shows `hmac.new()` generating the expected SHA256 digest and `hmac.compare_digest()` preventing timing attacks before activating subscriptions.

### 5. Haversine Distance Formula
- **File:** `services/location.py` (lines 15–45)
- **Key Highlight:** Mathematical implementation calculating great-circle distance between coordinates on Earth in kilometers:
  $$a = \sin^2\left(\frac{\Delta \text{lat}}{2}\right) + \cos(\text{lat}_1)\cos(\text{lat}_2)\sin^2\left(\frac{\Delta \text{lon}}{2}\right)$$
