# FixWithEase - Presentation & Live Demo Script

This demo script is designed for live project demonstrations and viva examinations. Follow the three scenarios below in order to demonstrate all project features smoothly.

---

## ⚡ Quick Test Credentials Reference
All seeded demo accounts use the standard password: `Password123!`

| Role / Scenario | Email Address | Password | Key Notes |
| :--- | :--- | :--- | :--- |
| **Free Customer (Arun)** | `customer.free@example.com` | `Password123!` | No active subscription. Manual directory search only; +5% fee added. |
| **Subscribed Customer (Kavitha)** | `customer.sub@example.com` | `Password123!` | Active Monthly Plan (⭐ Pro). Full AI Matchmaker & Fix It Yourself unlocked; 0% fee. |
| **Platform Administrator** | `admin@example.com` | `Password123!` | Access to the financial dashboard (subscription & consulting fee revenues). |
| **Sample Worker (Murugan S)** | `murugan.plumber@example.com` | `Password123!` | Verified Plumber in T. Nagar, Chennai (4.9★ rating). |

> 💡 **Tip:** On the [Login Page](http://127.0.0.1:5000/login), you can click any of the **⚡ One-Click Demo Login** buttons to auto-fill credentials instantly!

---

## 🎬 Scenario A: Free User Manual Search & 5% Consulting Fee

### Goal:
Demonstrate how an unsubscribed user browses the directory like traditional search and incurs the 5% platform consulting fee when booking a technician.

### Step-by-Step Flow:
1. **Login as Free User**:
   - Go to `http://127.0.0.1:5000/login`.
   - Click **"Login as Free User (Arun)"** &rarr; Click **Log In**.
   - Notice: The navbar shows *Hi, Arun Kumar* without the Pro badge.
2. **Browse Worker Directory (Manual Search)**:
   - Click **"Find Workers"** in the navigation bar.
   - Filter by skill: Select **"Plumber"** and click **Filter**.
   - Show the worker cards: Point out worker names, verified badges (`✓`), distance in kilometers (calculated via Haversine formula), and live availability (`🟢 Available`).
3. **Attempt to Access Premium Features (Demonstrating Server-Side 403 Paywall)**:
   - Click **"🤖 AI Matcher"** or **"Fix It Yourself"** in the navbar.
   - Show the examiner the **HTTP 403 Forbidden** paywall page: *"Subscribe to Unlock AI Features"*. Explain that this restriction is strictly enforced on the server.
4. **Book a Worker & Point Out the 5% Fee**:
   - Return to **Find Workers** and click **"Book Now"** on **Murugan S** (Plumber).
   - Enter Problem Description: `"Kitchen pipe is dripping under the sink"`.
   - Base Service Estimate: Enter `₹500.00`.
   - **Highlight the Price Breakdown**:
     - Base Amount: `₹500.00`
     - Platform Consulting Fee: **`+₹25.00 (+5% Free Tier Fee)`**
     - Total Amount: **`₹525.00`**
   - Click **"Confirm & Start Order"**.
   - Show the resulting **Order Summary** page showing the stored 5% fee and status `🟡 Booking Pending`.

---

## 🤖 Scenario B: Subscribed User Plain-Words AI Matchmaker

### Goal:
Demonstrate how an active subscriber types a problem in natural everyday language, and Gemini AI analyzes the issue, diagnoses urgency and risk, and scores/ranks local technicians.

### Step-by-Step Flow:
1. **Login as Subscribed User**:
   - Click **Logout**, then go to `http://127.0.0.1:5000/login`.
   - Click **"Login as Subscribed User (Kavitha)"** &rarr; Click **Log In**.
   - Notice: The navbar now shows the green **⭐ Pro** badge.
2. **Open the AI Matcher**:
   - Click **"🤖 AI Matcher"** in the navbar (or visit `http://127.0.0.1:5000/ai-search`).
3. **Run Query 1 (Plumbing)**:
   - Click the chip: **💧 "my kitchen tap is leaking"** (or type it in).
   - Click **"✨ Find Best Matching Workers"**.
   - Point out:
     - **AI Diagnosis Box**: Required Skill: **Plumber**, Urgency: **Medium**, Safety: **Standard Task**.
     - **Top 5 AI-Ranked Workers**: Worker `#1` has a 90%+ match score with recommendation reason: e.g. `"Plumber, 1.1 km away, 4.7 rating, Available Now"`.
4. **Run Query 2 (Electrical)**:
   - Type: `"fan not working and switch is loose"`.
   - Notice: Gemini identifies Required Skill: **Electrician** and ranks local electricians (e.g. *Karthik Raja* at 0.0 km).
5. **Run Query 3 (Carpentry)**:
   - Type: `"need a wooden dining table repaired"`.
   - Notice: Gemini identifies Required Skill: **Carpenter** and surfaces carpentry specialists.
6. **Book Worker with 0% Fee (Subscriber Perk)**:
   - Click **"Book This Worker"** on the #1 result.
   - Enter Base Amount: `₹500.00`.
   - **Highlight the Price Breakdown**:
     - Base Amount: `₹500.00`
     - Platform Consulting Fee: **`₹0.00 (0% Subscriber Perk - Waived)`**
     - Total Amount: **`₹500.00`**
     - Note the green banner: *"⭐ Subscriber Benefit: You saved 5% consulting fee on this booking!"*
   - Click **"Confirm & Start Order"**.

---

## 🛠️ Scenario C: "Fix It Yourself" (Safe DIY vs. Risky Refusal)

### Goal:
Demonstrate the core safety rule: Safe minor problems receive step-by-step tutorials and YouTube video help, while risky problems (electrical, gas, geysers) are strictly refused and referred to professionals.

### Step-by-Step Flow:
1. **Open Fix It Yourself**:
   - While logged in as Kavitha (Subscriber), click **"Fix It Yourself"** in the navbar.
2. **Test Case 1: Safe Problem ("leaking tap")**:
   - Click the quick chip **"💧 leaking tap"** &rarr; Click **"🛠️ Get Step-by-Step Tutorial"**.
   - **Show the Generated Guide**:
     - Title: *"Fixing a Leaking or Dripping Water Tap"* (⏱️ 15-25 mins, Difficulty: Easy).
     - **Tools Needed**: Adjustable wrench, screwdriver, rag.
     - **Materials Needed**: Replacement rubber washer, Teflon tape.
     - **5 Numbered Steps**: From shutting off the main valve to reassembling.
     - **Safety Guardrail**: Show the warning box: *"🛑 Stop and Call a Professional If..."*
     - **Video Help**: Show the 2–3 curated YouTube tutorial links.
     - **Worker Fallback**: Show the button at the bottom: *"👨‍🔧 Still Not Fixed? Find a Worker"*.
3. **Test Case 2: Hazardous Problem ("socket sparking" - Electrical Hazard)**:
   - In the input box, click the red chip **"⚡ socket sparking"** &rarr; Click **"Get Step-by-Step Tutorial"**.
   - **Demonstrate the Refusal**:
     - Explain to the examiner: **No DIY steps are generated** because electricity carries electrocution and fire hazards.
     - Show the red warning banner: **"🚫 Please Consult a Professional (Electrical Hazards)"**.
     - Point out the safety explanation.
     - Click the red button: **"🔍 Find Verified Professionals for 'socket sparking'"** &rarr; It seamlessly redirects to the AI Matcher with top local electricians already ranked!
4. **Test Case 3: Other Risky Tests**:
   - Try typing **"gas smell in kitchen"** or **"geyser not heating"**.
   - Confirm that both are immediately blocked and refused by the safety blocklist.

---

## 💰 Bonus Admin Demonstration: Financial Metrics
1. Log in as **`admin@example.com`** (Password: `Password123!`).
2. Click **"⚙️ Admin"** in the navbar.
3. Show the examiner:
   - **Total Platform Revenue**: Sum of subscriptions + 5% consulting fees.
   - **Subscription Revenue**: ₹30 monthly and ₹300 yearly counts.
   - **Consulting Fee Revenue**: Total 5% fees collected from free users.
   - **Recent Orders Table**: Clear breakdown showing which orders were charged 5% vs 0%.
