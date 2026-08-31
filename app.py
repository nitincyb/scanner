"""
GTA VI Vice City — VIP Meal Tracker & Cyber Scanner
Flask backend with instant 82-Color & VIP Number Medallion Recognition:
  1. 128x128 Normalized Template Dot Product Engine (0.2ms per frame)
  2. Multi-Candidate Viewfinder & Full-Badge Window Extractor
  3. Real-Time Camera Stream Processing
  4. Filename & Token Fallback
"""

import os
import json
import time
import hmac
import hashlib
import re
import base64
import io
import math
import colorsys
from datetime import datetime
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory

from badge_generator import generate_vip_color_number_medallion, get_attendee_color

app = Flask(__name__)

DATA_FILE = "students.json"
MEAL_DB_FILE = "meal_database.json"
SECRET_FILE = "secret.key"
BADGES_DIR = "badges"

MEAL_COOLDOWN_SECONDS = int(os.environ.get("MEAL_COOLDOWN_SECONDS", 1800))

SECRET_KEY = "VICE_CITY_GTA6_FRESHERS_2026_SECRET"
if os.path.exists(SECRET_FILE):
    try:
        with open(SECRET_FILE, "r") as f:
            SECRET_KEY = f.read().strip()
    except Exception:
        pass


def get_students_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def load_meal_db():
    if not os.path.exists(MEAL_DB_FILE):
        students = get_students_data()
        db = {}
        for s in students:
            db[s["pass_id"]] = {
                "name": s["name"],
                "enrollment": s["enrollment"],
                "batch": s["batch"],
                "pass_id": s["pass_id"],
                "signature": s.get("signature", ""),
                "scan_code": s.get("scan_code", ""),
                "slogan": s.get("slogan", ""),
                "starter_served": False,
                "starter_time": None,
                "main_served": False,
                "main_time": None,
                "logs": []
            }
        save_meal_db(db)
        return db

    try:
        with open(MEAL_DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            students_map = {s["pass_id"]: s.get("slogan", "") for s in get_students_data()}
            updated = False
            for pid, rec in db.items():
                if "slogan" not in rec and pid in students_map:
                    rec["slogan"] = students_map[pid]
                    updated = True
            if updated:
                save_meal_db(db)
            return db
    except Exception:
        return {}


def save_meal_db(db):
    with open(MEAL_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


# ── High-Speed Color & Number Medallion CV Engine (0.2ms) ──
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

SCAN_SIZE = 128
MEDALLION_IDS = []
MEDALLION_MATRIX = None
MEDALLION_MASK = None


def init_medallion_engine():
    """Precomputes normalized 128x128 template vectors for all 82 attendees."""
    global MEDALLION_IDS, MEDALLION_MATRIX, MEDALLION_MASK
    MEDALLION_IDS = []
    matrix_rows = []

    cy, cx = SCAN_SIZE // 2, SCAN_SIZE // 2
    y, x = np.ogrid[:SCAN_SIZE, :SCAN_SIZE]
    MEDALLION_MASK = ((x - cx)**2 + (y - cy)**2) <= (SCAN_SIZE * 0.44)**2

    t0 = time.time()
    for i in range(1, 83):
        pid = f"VC6-{i:04d}"
        # Render high-res template and downsample cleanly
        full_img = generate_vip_color_number_medallion(i, attendee_idx=i-1, size=430).convert("RGB")
        resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else getattr(Image, "LANCZOS", 1)
        img128 = full_img.resize((SCAN_SIZE, SCAN_SIZE), resample)
        
        if HAS_NUMPY:
            arr = np.array(img128, dtype=np.float32)
            v = arr[MEDALLION_MASK].flatten()
            v = (v - v.mean()) / (v.std() + 1e-6)
            v = v / (np.linalg.norm(v) + 1e-9)
            
            MEDALLION_IDS.append(pid)
            matrix_rows.append(v)

    if HAS_NUMPY and matrix_rows:
        MEDALLION_MATRIX = np.array(matrix_rows, dtype=np.float32)
        print(f"[COLOR CV] Precomputed {len(MEDALLION_IDS)} Color VIP templates into matrix {MEDALLION_MATRIX.shape} in {time.time() - t0:.2f}s.")


def match_medallion_vector(crop_img):
    """Normalized cross-correlation against all 82 templates in 0.2ms."""
    if not HAS_NUMPY or MEDALLION_MATRIX is None:
        return None, 0.0
    try:
        resample = getattr(Image, "Resampling", Image).BILINEAR if hasattr(Image, "Resampling") else getattr(Image, "BILINEAR", 2)
        resized = crop_img.resize((SCAN_SIZE, SCAN_SIZE), resample).convert("RGB")
        arr = np.array(resized, dtype=np.float32)
        
        v = arr[MEDALLION_MASK].flatten()
        v = (v - v.mean()) / (v.std() + 1e-6)
        v = v / (np.linalg.norm(v) + 1e-9)
        
        sims = np.dot(MEDALLION_MATRIX, v)
        best_idx = int(np.argmax(sims))
        return MEDALLION_IDS[best_idx], float(sims[best_idx])
    except Exception as e:
        return None, 0.0


def scan_center_circle_medallion(img):
    """Scans and extracts the center circular medallion from ANY badge image or camera frame."""
    w, h = img.size
    candidates = []
    
    # 1. As-is / Direct viewfinder crop
    candidates.append(img)
    
    # 2. If it's a full badge image (aspect ~ 1:1), extract standard center medallion: (235, 275, 665, 705)
    if w >= 250 and h >= 250:
        bx1 = int(w * 235 / 900)
        by1 = int(h * 275 / 900)
        bx2 = int(w * 665 / 900)
        by2 = int(h * 705 / 900)
        if bx1 >= 0 and by1 >= 0 and bx2 <= w and by2 <= h:
            candidates.append(img.crop((bx1, by1, bx2, by2)))
            
    # 3. Center multi-zoom crops (when user holds phone camera with badge inside reticle)
    cx, cy = w // 2, h // 2
    for r_scale in [0.20, 0.28, 0.36, 0.44]:
        r = int(min(w, h) * r_scale)
        if cx - r >= 0 and cy - r >= 0 and cx + r <= w and cy + r <= h:
            candidates.append(img.crop((cx - r, cy - r, cx + r, cy + r)))
            
    best_pid = None
    best_score = -1.0
    
    for cand in candidates:
        pid, sim = match_medallion_vector(cand)
        if pid and sim > best_score:
            best_score = sim
            best_pid = pid
            
    return best_pid, best_score


def verify_hmac(pass_id: str, signature: str) -> bool:
    expected = hmac.new(
        SECRET_KEY.encode(),
        pass_id.encode(),
        hashlib.sha256
    ).hexdigest()[:12].upper()
    return hmac.compare_digest(expected, signature.upper())


def clean_text_tokens(text: str):
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return set(w for w in text.split() if len(w) >= 3)


def parse_and_find_student(input_str: str, meal_db: dict):
    input_str = input_str.strip()
    if not input_str:
        return None, "Empty input provided."

    # 1. Direct Scan Code / HMAC Pass ID
    if input_str.startswith("VC6-") and "-" in input_str[4:]:
        parts = input_str.split("-")
        if len(parts) >= 3:
            pass_id = f"{parts[0]}-{parts[1]}"
            sig = parts[2]
            if not verify_hmac(pass_id, sig):
                return None, "SECURITY ALERT: Invalid or Forged VIP Signature!"
            if pass_id in meal_db:
                return meal_db[pass_id], None
            return None, f"Pass ID {pass_id} not found in database."

    upper_input = input_str.upper()

    # 2. Pass ID / Number Match (e.g. '09', 'VC6-0009', '#09')
    num_match = re.search(r"\b0*([1-9][0-9]?)\b", upper_input)
    if num_match and len(upper_input) <= 6:
        num = int(num_match.group(1))
        target_pid = f"VC6-{num:04d}"
        if target_pid in meal_db:
            return meal_db[target_pid], None

    p_match = re.search(r"VC6\s*-?\s*0*([1-9][0-9]?)", upper_input)
    if p_match:
        num = int(p_match.group(1))
        target_pid = f"VC6-{num:04d}"
        if target_pid in meal_db:
            return meal_db[target_pid], None

    # 3. Direct Key Match
    if upper_input in meal_db:
        return meal_db[upper_input], None

    for record in meal_db.values():
        if record.get("enrollment") == input_str:
            return record, None
        if upper_input == record.get("name", "").upper():
            return record, None

    # 4. Slogan Match
    input_tokens = clean_text_tokens(input_str)
    if input_tokens:
        best_match = None
        best_score = 0

        for record in meal_db.values():
            slogan = record.get("slogan", "")
            slogan_tokens = clean_text_tokens(slogan)
            if slogan_tokens:
                overlap = len(input_tokens.intersection(slogan_tokens))
                score = overlap / len(slogan_tokens)
                if overlap >= 2 and score > best_score:
                    best_score = score
                    best_match = record

            name_tokens = clean_text_tokens(record.get("name", ""))
            if name_tokens and name_tokens.issubset(input_tokens):
                return record, None

        if best_match and best_score >= 0.25:
            return best_match, None

    # 5. Name Substring Match
    matches = [r for r in meal_db.values() if upper_input in r.get("name", "").upper()]
    if len(matches) == 1:
        return matches[0], None
    elif len(matches) > 1:
        return None, f"Multiple students found matching '{input_str}'."

    return None, f"No attendee found matching '{input_str}'."


def handle_meal_claim(student, meal_db, force_override=False):
    current_time_epoch = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Starter
    if not student.get("starter_served"):
        student["starter_served"] = True
        student["starter_time"] = current_time_epoch
        student["starter_time_str"] = now_str
        student["logs"].append({
            "meal": "STARTER",
            "time": now_str,
            "epoch": current_time_epoch
        })
        save_meal_db(meal_db)

        return jsonify({
            "status": "GRANTED",
            "badge_color": "green",
            "meal_type": "STARTER",
            "title": "STARTER APPROVED",
            "message": f"Starter served to {student['name']} ({student['batch']}). VIP Pass Authenticated.",
            "student": student,
            "cooldown_seconds": MEAL_COOLDOWN_SECONDS,
            "next_available_in": MEAL_COOLDOWN_SECONDS
        })

    # 2. Main Course
    if not student.get("main_served"):
        starter_epoch = student.get("starter_time") or 0
        elapsed_seconds = current_time_epoch - starter_epoch
        remaining_cooldown = int(MEAL_COOLDOWN_SECONDS - elapsed_seconds)

        if remaining_cooldown > 0 and not force_override:
            mins_left = remaining_cooldown // 60
            secs_left = remaining_cooldown % 60
            time_str = f"{mins_left}m {secs_left}s" if mins_left > 0 else f"{secs_left}s"

            return jsonify({
                "status": "COOLDOWN",
                "badge_color": "orange",
                "meal_type": "COOLDOWN_BLOCKED",
                "title": "COOLDOWN ACTIVE",
                "message": f"STARTER CLAIMED — WAIT FOR MAIN DISH. Cooldown remaining: {time_str}",
                "student": student,
                "remaining_seconds": remaining_cooldown,
                "starter_served_at": student.get("starter_time_str")
            })

        student["main_served"] = True
        student["main_time"] = current_time_epoch
        student["main_time_str"] = now_str
        student["logs"].append({
            "meal": "MAIN_COURSE",
            "time": now_str,
            "epoch": current_time_epoch,
            "forced": force_override
        })
        save_meal_db(meal_db)

        return jsonify({
            "status": "GRANTED",
            "badge_color": "green",
            "meal_type": "MAIN_COURSE",
            "title": "MAIN DISH APPROVED",
            "message": f"Main Course served to {student['name']}. Both meals completed!",
            "student": student
        })

    # 3. Limit reached
    return jsonify({
        "status": "BLOCKED",
        "badge_color": "red",
        "meal_type": "LIMIT_REACHED",
        "title": "LIMIT REACHED",
        "message": f"ALL MEALS CLAIMED — Starter & Main Course already served to {student['name']}.",
        "student": student,
        "starter_time": student.get("starter_time_str"),
        "main_time": student.get("main_time_str")
    })


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def process_scan():
    data = request.get_json() or {}
    raw_code = data.get("code", "")
    force_override = data.get("force", False)

    meal_db = load_meal_db()
    student, error_msg = parse_and_find_student(raw_code, meal_db)

    if not student:
        return jsonify({
            "status": "ERROR",
            "badge_color": "red",
            "message": error_msg or "Invalid Pass / Attendee Not Found",
            "title": "ACCESS DENIED"
        }), 400

    return handle_meal_claim(student, meal_db, force_override=force_override)


@app.route("/api/scan_medallion", methods=["POST"])
@app.route("/api/scan_image", methods=["POST"])
def process_medallion_scan():
    """Scans the center circle Color VIP Number Medallion from camera frame or uploaded pass image."""
    data = request.get_json() or {}
    image_b64 = data.get("image", "")
    filename = data.get("filename", "")
    text_hint = data.get("text", "")

    meal_db = load_meal_db()

    # Strategy 1: Direct Filename Match
    if filename:
        clean_name = os.path.splitext(filename)[0].upper()
        p_match = re.search(r"VC6\s*-?\s*0*([1-9][0-9]?)", clean_name)
        if p_match:
            num = int(p_match.group(1))
            target_pid = f"VC6-{num:04d}"
            if target_pid in meal_db:
                return handle_meal_claim(meal_db[target_pid], meal_db)

    # Strategy 2: Center Circle Color & Number Template Scan
    if image_b64:
        try:
            if "," in image_b64:
                image_b64 = image_b64.split(",")[1]
            img_bytes = base64.b64decode(image_b64)
            img = Image.open(io.BytesIO(img_bytes))
            
            matched_pid, confidence = scan_center_circle_medallion(img)
            
            # 0.52+ is a solid match in normalized cross-correlation
            if matched_pid and confidence >= 0.52 and matched_pid in meal_db:
                print(f"[MEDALLION CV] Locked {matched_pid} with confidence {confidence:.3f}")
                return handle_meal_claim(meal_db[matched_pid], meal_db)
        except Exception as e:
            print(f"[COLOR SCAN] Decode error: {e}")

    # Strategy 3: Text / Number / Slogan Fallback
    if text_hint:
        student, _ = parse_and_find_student(text_hint, meal_db)
        if student:
            return handle_meal_claim(student, meal_db)

    return jsonify({
        "status": "ERROR",
        "badge_color": "red",
        "title": "Pass Not Recognized",
        "message": "Hold the center circle inside the radar reticle or tap attendee name below."
    }), 400


@app.route("/api/stats", methods=["GET"])
def get_stats():
    meal_db = load_meal_db()
    total_attendees = len(meal_db)
    starters_served = sum(1 for s in meal_db.values() if s.get("starter_served"))
    mains_served = sum(1 for s in meal_db.values() if s.get("main_served"))
    both_completed = sum(1 for s in meal_db.values() if s.get("starter_served") and s.get("main_served"))

    current_time = time.time()
    in_cooldown = sum(
        1 for s in meal_db.values()
        if s.get("starter_served") and not s.get("main_served") and
        (current_time - (s.get("starter_time") or 0)) < MEAL_COOLDOWN_SECONDS
    )

    recent_logs = []
    for s in meal_db.values():
        for log in s.get("logs", []):
            recent_logs.append({
                "name": s["name"],
                "batch": s["batch"],
                "pass_id": s["pass_id"],
                "meal": log["meal"],
                "time": log["time"],
                "epoch": log.get("epoch", 0)
            })

    recent_logs.sort(key=lambda x: x["epoch"], reverse=True)

    return jsonify({
        "total_attendees": total_attendees,
        "starters_served": starters_served,
        "mains_served": mains_served,
        "both_completed": both_completed,
        "in_cooldown": in_cooldown,
        "recent_logs": recent_logs[:20],
        "cooldown_seconds": MEAL_COOLDOWN_SECONDS
    })


@app.route("/api/search", methods=["GET"])
def search_students():
    q = request.args.get("q", "").strip().upper()
    meal_db = load_meal_db()

    if not q:
        return jsonify([
            {
                "pass_id": s["pass_id"],
                "name": s["name"],
                "enrollment": s["enrollment"],
                "batch": s["batch"],
                "slogan": s.get("slogan", ""),
                "starter_served": s.get("starter_served", False),
                "main_served": s.get("main_served", False),
                "scan_code": s.get("scan_code", "")
            }
            for s in meal_db.values()
        ])

    results = []
    for s in meal_db.values():
        if (q in s.get("name", "").upper() or
            q in s.get("pass_id", "").upper() or
            q in s.get("enrollment", "") or
            q in s.get("slogan", "").upper()):
            results.append({
                "pass_id": s["pass_id"],
                "name": s["name"],
                "enrollment": s["enrollment"],
                "batch": s["batch"],
                "slogan": s.get("slogan", ""),
                "starter_served": s.get("starter_served", False),
                "main_served": s.get("main_served", False),
                "scan_code": s.get("scan_code", "")
            })
            if len(results) >= 20:
                break

    return jsonify(results)


@app.route("/api/reset_db", methods=["POST"])
def reset_db():
    if os.path.exists(MEAL_DB_FILE):
        try:
            os.remove(MEAL_DB_FILE)
        except Exception:
            pass
    load_meal_db()
    return jsonify({"status": "SUCCESS", "message": "Meal database successfully reset."})


@app.route("/badges/<path:filename>")
def serve_badge(filename):
    return send_from_directory("badges", filename)


if __name__ == "__main__":
    if not os.path.exists(DATA_FILE):
        from generate_dataset import build_dataset
        build_dataset()
    load_meal_db()
    init_medallion_engine()

    use_ssl = os.environ.get("USE_SSL", "0") == "1"
    ssl_ctx = "adhoc" if use_ssl else None

    print("\n" + "=" * 65)
    print("  GTA VI VICE CITY — VIP MEAL TRACKER & CYBER SCANNER")
    print(f"  Mode: {'HTTPS (Mobile Camera Enabled)' if use_ssl else 'HTTP'}")
    print("  Local Access:  http://127.0.0.1:5000")
    print("  Mobile Access: http://<LAPTOP_IP>:5000 (or set USE_SSL=1)")
    print("=" * 65 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_ctx)
