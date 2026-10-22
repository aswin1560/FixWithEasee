"""
DIY Tutorial Service (Fix It Yourself)
Generates safe, numbered step-by-step DIY home maintenance tutorials,
tools needed, time needed, 'stop and call a professional if...' warning,
and curated YouTube video links.

Safety Rule: NEVER generates steps if the problem is risky.
"""

import os
import re
import json
import urllib.parse
from services.safety_filter import check_safety_blocklist

# Pre-crafted safe guides for common household repairs (offline fallback)
SAFE_PRESET_GUIDES = {
    "leaking tap": {
        "title": "Fixing a Leaking or Dripping Water Tap",
        "time_needed": "15 - 25 minutes",
        "difficulty": "Easy",
        "tools_needed": ["Adjustable Wrench / Spanner", "Flathead Screwdriver", "Old Rag or Towel"],
        "materials_needed": ["Replacement Rubber Washer (correct size)", "Teflon Thread Seal Tape"],
        "steps": [
            {
                "step_number": 1,
                "title": "Shut Off the Water Supply",
                "instruction": "Locate the isolation valve under the sink or turn off the main water valve to prevent flooding while you work. Open the tap to drain any remaining water."
            },
            {
                "step_number": 2,
                "title": "Remove the Tap Handle",
                "instruction": "Use a small flathead screwdriver to gently pry off the decorative cap (hot/cold indicator) on top of the tap handle. Unscrew the hidden screw underneath and pull off the handle."
            },
            {
                "step_number": 3,
                "title": "Unscrew the Valve Spindle",
                "instruction": "Use an adjustable wrench to loosen the brass tap valve spindle by turning counter-clockwise. Carefully lift the spindle out of the tap body."
            },
            {
                "step_number": 4,
                "title": "Inspect & Replace the Washer",
                "instruction": "Look at the rubber washer at the base of the spindle. If it is cracked, worn, or deformed, remove the small securing nut, replace it with a fresh washer, and tighten gently."
            },
            {
                "step_number": 5,
                "title": "Wrap Teflon Tape and Reassemble",
                "instruction": "Wrap 2-3 layers of Teflon tape clockwise around the spindle threads. Screw the spindle back in, reinstall the handle, turn the main water valve back on, and check for leaks."
            }
        ],
        "stop_warning": "Stop immediately and call a licensed plumber if the brass spindle is seized/corroded, if the valve seat is deeply scored, or if water continues to leak after replacing the washer."
    },

    "loose door hinge": {
        "title": "Tightening and Repairing a Loose Door Hinge",
        "time_needed": "10 - 15 minutes",
        "difficulty": "Easy",
        "tools_needed": ["Phillips Screwdriver", "Wooden Toothpicks or Matchsticks", "Wood Glue / PVA Glue"],
        "materials_needed": ["Longer Wood Screws (1.5 - 2 inches) if stripped"],
        "steps": [
            {
                "step_number": 1,
                "title": "Support the Door",
                "instruction": "Place a doorstop, folded cardboard, or a wooden wedge under the open door so the weight is supported and does not stress the remaining hinges."
            },
            {
                "step_number": 2,
                "title": "Tighten the Existing Screws",
                "instruction": "Using a manual Phillips screwdriver, gently tighten each screw on the door frame and door leaf. Do not overtighten with a power drill to avoid stripping the wood."
            },
            {
                "step_number": 3,
                "title": "Fix Stripped Screw Holes",
                "instruction": "If a screw spins loosely without gripping, remove it. Dip 2-3 wooden toothpicks or matchsticks in wood glue and push them deeply into the screw hole. Snap off the excess flush with the surface."
            },
            {
                "step_number": 4,
                "title": "Drive the Screws Firmly",
                "instruction": "Reinsert the screw into the packed hole. The toothpicks provide fresh wood fiber for the screw threads to bite into. Alternatively, use a longer 2-inch wood screw that reaches the wall stud."
            },
            {
                "step_number": 5,
                "title": "Test Door Swing",
                "instruction": "Remove the wedge and swing the door open and shut several times to ensure it swings smoothly without sagging or scraping the floor."
            }
        ],
        "stop_warning": "Stop and consult a carpenter if the wooden frame is rotted, the door jamb is cracked through, or the door itself is severely warped."
    },

    "clogged sink": {
        "title": "Clearing a Slow or Clogged Sink Drain (Non-Chemical)",
        "time_needed": "15 - 20 minutes",
        "difficulty": "Easy",
        "tools_needed": ["Cup Plunger", "Small Bucket or Basin", "Rubber Gloves"],
        "materials_needed": ["Baking Soda (1/2 cup)", "White Vinegar (1/2 cup)", "Hot Water (1 kettle)"],
        "steps": [
            {
                "step_number": 1,
                "title": "Clear Standing Water & Debris",
                "instruction": "Remove any visible food scraps, hair, or debris from the strainer. Scoop out most standing water leaving just 2 inches around the drain to seal the plunger."
            },
            {
                "step_number": 2,
                "title": "Block the Overflow Hole",
                "instruction": "If your sink has an overflow opening near the rim, seal it tightly with a damp rag or piece of duct tape to ensure suction."
            },
            {
                "step_number": 3,
                "title": "Plunge with Firm Downward Pressure",
                "instruction": "Place the rubber cup of the plunger squarely over the drain. Push down and pull up vigorously 6 to 10 times in quick succession. Break the seal quickly to pull the clog free."
            },
            {
                "step_number": 4,
                "title": "Baking Soda & Vinegar Flush",
                "instruction": "Pour 1/2 cup of baking soda directly into the drain, followed by 1/2 cup of vinegar. Allow the fizzing action to break down organic slime for 10 minutes."
            },
            {
                "step_number": 5,
                "title": "Flush with Boiling Water",
                "instruction": "Slowly pour a full kettle of hot water down the drain to flush away loosened residue. Run the tap to confirm normal drainage."
            }
        ],
        "stop_warning": "Stop immediately and call a plumber if dirty water backs up into adjacent drains or toilets, or if multiple drains in the house are simultaneously blocked (indicating a main sewer clog). NEVER pour caustic drain acid if you have already plunged."
    }
}


def build_youtube_links(problem_text):
    """Generates 2-3 helpful YouTube tutorial search links for the problem."""
    clean_query = re.sub(r"[^\w\s]", "", problem_text).strip()
    encoded_1 = urllib.parse.quote_plus(f"how to fix {clean_query} tutorial")
    encoded_2 = urllib.parse.quote_plus(f"{clean_query} DIY repair guide")
    encoded_3 = urllib.parse.quote_plus(f"fix {clean_query} step by step")

    return [
        {
            "title": f"Watch: How to Fix {clean_query.title()} (Tutorial)",
            "url": f"https://www.youtube.com/results?search_query={encoded_1}"
        },
        {
            "title": f"Watch: DIY Step-by-Step {clean_query.title()} Guide",
            "url": f"https://www.youtube.com/results?search_query={encoded_2}"
        },
        {
            "title": f"Watch: Quick Fix for {clean_query.title()}",
            "url": f"https://www.youtube.com/results?search_query={encoded_3}"
        }
    ]


def get_diy_tutorial(problem_text):
    """
    Main entry point for Fix It Yourself.
    1. First checks the keyword safety filter.
    2. If risky: immediately returns { "is_risky": True, "category": ..., "warning": ... }.
    3. If safe: queries Gemini AI (or pre-crafted safe guides) for a complete tutorial.
    """
    if not problem_text:
        return {"error": "Problem description is required."}

    # Step 1: Pre-AI Safety Blocklist check
    is_risky, category, warning = check_safety_blocklist(problem_text)
    if is_risky:
        return {
            "is_risky": True,
            "category": category,
            "warning": warning,
            "message": "This task involves hazardous conditions and cannot be safely repaired as a DIY project. Please consult a licensed professional."
        }

    # Step 2: Safe task -> check preset guides or query Gemini
    normalized = problem_text.lower()
    for key, guide in SAFE_PRESET_GUIDES.items():
        if key in normalized:
            result = dict(guide)
            result["is_risky"] = False
            result["youtube_links"] = build_youtube_links(problem_text)
            result["source"] = "preset"
            return result

    # Check Gemini API for other safe tasks
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key and api_key != "your_gemini_api_key_here":
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
You are an expert home repair safety instructor.
The user wants DIY guidance for: "{problem_text}".

FIRST SAFETY CHECK:
If this task involves electrical wiring, sockets, MCB, switchboards, gas lines, water heaters/geysers, wall cutting, roofs, heights, fire or chemicals, YOU MUST REFUSE IT by returning:
{{"is_risky": true, "reason": "Hazardous work requires a licensed professional."}}

If and ONLY IF it is completely safe for an untrained homeowner, return a raw JSON object (no markdown, no backticks):
{{
  "is_risky": false,
  "title": "<Concise Tutorial Title>",
  "time_needed": "<e.g. 15-20 minutes>",
  "difficulty": "<Easy | Moderate>",
  "tools_needed": ["<tool 1>", "<tool 2>"],
  "materials_needed": ["<material 1>", "<material 2>"],
  "steps": [
    {{"step_number": 1, "title": "<Step 1 Title>", "instruction": "<Clear instruction>"}},
    {{"step_number": 2, "title": "<Step 2 Title>", "instruction": "<Clear instruction>"}}
  ],
  "stop_warning": "<Explicit warning explaining when to stop immediately and call a professional>"
}}
"""
            response = model.generate_content(prompt)
            cleaned = re.sub(r"^```(?:json)?\s*", "", response.text.strip(), flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned).strip()
            data = json.loads(cleaned)

            if data.get("is_risky"):
                return {
                    "is_risky": True,
                    "category": "High Risk Problem",
                    "warning": data.get("reason", "This task is unsafe for DIY repair."),
                    "message": "This task involves hazardous conditions. Please consult a licensed professional."
                }

            data["youtube_links"] = build_youtube_links(problem_text)
            data["source"] = "gemini_ai"
            return data

        except Exception:
            pass

    # Generic safe fallback guide
    clean_title = problem_text.strip().capitalize()
    return {
        "is_risky": False,
        "title": f"Safe DIY Inspection Guide: {clean_title}",
        "time_needed": "15 - 20 minutes",
        "difficulty": "Easy",
        "tools_needed": ["Basic Hand Screwdriver", "Flashlight", "Cleaning Cloth", "Protective Gloves"],
        "materials_needed": ["Cleaning Solution", "Lubricating Spray (WD-40 if moving parts)"],
        "steps": [
            {
                "step_number": 1,
                "title": "Clear and Inspect the Area",
                "instruction": f"Clear a safe, well-lit workspace around the item. Inspect the mechanism carefully for visible loose screws, misaligned parts, or grime buildup."
            },
            {
                "step_number": 2,
                "title": "Clean Away Debris and Buildup",
                "instruction": "Wipe down any dust, rust, or residue that may be jamming or hindering smooth movement."
            },
            {
                "step_number": 3,
                "title": "Tighten Fasteners and Align Parts",
                "instruction": "Using hand tools only, gently tighten any loose mounting bolts or screws. Ensure components seat evenly."
            },
            {
                "step_number": 4,
                "title": "Test Operation",
                "instruction": "Test the function gently. If it operates smoothly without abnormal friction or noise, the minor fix is complete."
            }
        ],
        "stop_warning": "Stop immediately and call a skilled professional if parts are cracked, under mechanical tension, or if the problem persists after basic tightening.",
        "youtube_links": build_youtube_links(problem_text),
        "source": "general_safe_fallback"
    }
