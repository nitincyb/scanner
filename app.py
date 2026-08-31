"""
GTA VI Vice City — VIP Meal Tracker & Cyber Scanner
Flask backend with robust multi-strategy badge matching:
  1. Perceptual Image Hash (pHash) matching on full badge
  2. Filename-based pass ID extraction
  3. Text/slogan/name matching
  4. Direct scan code / HMAC verification
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
from datetime import datetime
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory

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


# ── Perceptual Hash (pHash) Image Fingerprint Engine ──
# Instead of matching just the center circle, we compute a perceptual hash
# of the FULL badge image. pHash is robust to scaling, minor rotation,
# brightness changes, and JPEG compression — perfect for camera scans.

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

BADGE_PHASHES = {}  # pass_id -> phash_bits (list of 0/1, length 256)
BADGE_COLOR_SIGS = {}  # pass_id -> color signature tuple


def compute_phash(img, hash_size=16):
    """Compute a perceptual hash of an image.
    
    1. Convert to grayscale
    2. Resize to (hash_size+1) x hash_size
    3. Compute horizontal gradient (difference hash variant)
    4. Return binary hash as list of bits
    
    This is robust to scaling, brightness, contrast, and minor geometric changes.
    """
    try:
        gray = img.convert("L")
        resized = gray.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(resized.getdata())
        
        bits = []
        for row in range(hash_size):
            for col in range(hash_size):
                idx = row * (hash_size + 1) + col
                bits.append(1 if pixels[idx] < pixels[idx + 1] else 0)
        
        return bits
    except Exception:
        return None


def compute_color_signature(img):
    """Compute a color histogram signature of the badge.
    
    Extracts color distribution in HSV space focusing on the unique
    elements (name text color position, slogan text, medallion rays).
    Returns a tuple of histogram bin values.
    """
    try:
        # Sample from key regions of the badge
        w, h = img.size
        rgb = img.convert("RGB")
        
        # Region 1: Top area (name text region) - top 25%
        top_region = rgb.crop((0, 0, w, int(h * 0.25)))
        # Region 2: Center area (medallion) - middle 40%
        center_region = rgb.crop((int(w * 0.2), int(h * 0.25), int(w * 0.8), int(h * 0.75)))
        # Region 3: Bottom area (slogan) - bottom 15%
        bottom_region = rgb.crop((0, int(h * 0.85), w, h))
        
        def region_histogram(region, bins=8):
            """Get a simplified color histogram for a region."""
            small = region.resize((32, 32), Image.Resampling.LANCZOS)
            pixels = list(small.getdata())
            hist = [0] * (bins * 3)  # R, G, B each with 'bins' buckets
            for r, g, b in pixels:
                hist[r * bins // 256] += 1
                hist[bins + g * bins // 256] += 1
                hist[bins * 2 + b * bins // 256] += 1
            total = len(pixels)
            return tuple(h / total for h in hist)
        
        sig = region_histogram(top_region) + region_histogram(center_region) + region_histogram(bottom_region)
        return sig
    except Exception:
        return None


def hamming_distance(hash1, hash2):
    """Count the number of differing bits between two hashes."""
    return sum(a != b for a, b in zip(hash1, hash2))


def cosine_similarity_sigs(sig1, sig2):
    """Compute cosine similarity between two color signatures."""
    dot = sum(a * b for a, b in zip(sig1, sig2))
    norm1 = math.sqrt(sum(a * a for a in sig1))
    norm2 = math.sqrt(sum(b * b for b in sig2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def init_badge_fingerprints():
    """Pre-compute perceptual hashes and color signatures for all 82 badge images."""
    global BADGE_PHASHES, BADGE_COLOR_SIGS
    BADGE_PHASHES = {}
    BADGE_COLOR_SIGS = {}
    
    if not os.path.exists(BADGES_DIR):
        return
    
    for fname in os.listdir(BADGES_DIR):
        if fname.endswith(".png"):
            pid = os.path.splitext(fname)[0]
            fpath = os.path.join(BADGES_DIR, fname)
            try:
                img = Image.open(fpath)
                
                # Compute pHash
                phash = compute_phash(img)
                if phash is not None:
                    BADGE_PHASHES[pid] = phash
                
                # Compute color signature
                csig = compute_color_signature(img)
                if csig is not None:
                    BADGE_COLOR_SIGS[pid] = csig
                    
            except Exception:
                pass
    
    print(f"[INIT] Loaded {len(BADGE_PHASHES)} pHash fingerprints + {len(BADGE_COLOR_SIGS)} color signatures.")


def match_badge_image(img):
    """Match an uploaded/scanned badge image against all 82 stored badges.
    
    Uses a combined score from:
    1. Perceptual Hash (pHash) hamming distance — structural similarity
    2. Color signature cosine similarity — color distribution match
    
    Returns (best_pass_id, confidence_score) or (None, 0.0)
    """
    query_phash = compute_phash(img)
    query_csig = compute_color_signature(img)
    
    if query_phash is None and query_csig is None:
        return None, 0.0
    
    best_pid = None
    best_combined_score = -1.0
    
    for pid in set(list(BADGE_PHASHES.keys()) + list(BADGE_COLOR_SIGS.keys())):
        phash_score = 0.0
        color_score = 0.0
        
        # pHash similarity (convert hamming distance to similarity)
        if query_phash and pid in BADGE_PHASHES:
            dist = hamming_distance(query_phash, BADGE_PHASHES[pid])
            max_dist = len(query_phash)  # 256 bits
            phash_score = 1.0 - (dist / max_dist)
        
        # Color signature similarity
        if query_csig and pid in BADGE_COLOR_SIGS:
            color_score = cosine_similarity_sigs(query_csig, BADGE_COLOR_SIGS[pid])
        
        # Combined weighted score (pHash is more structural, color adds differentiation)
        combined = phash_score * 0.55 + color_score * 0.45
        
        if combined > best_combined_score:
            best_combined_score = combined
            best_pid = pid
    
    return best_pid, best_combined_score


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

    # 2. Pass ID Regex Match
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
            "message": f"Starter served to {student['name']} ({student['batch']}). Badge Authenticated.",
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


@app.route("/api/scan_image", methods=["POST"])
def process_image_scan():
    """Scans a badge image using perceptual hash + color signature matching.
    
    Accepts:
    - image: base64-encoded image data (from camera frame or file upload)
    - filename: original filename (used for pass ID extraction)
    - text: any OCR-extracted text hint from client-side
    
    Matching pipeline:
    1. Filename-based pass ID extraction (most reliable for file uploads)
    2. Perceptual hash + color signature image matching
    3. Text/slogan/name fallback matching
    """
    data = request.get_json() or {}
    image_b64 = data.get("image", "")
    filename = data.get("filename", "")
    text_hint = data.get("text", "")

    meal_db = load_meal_db()

    # Strategy 1: Filename Match (most reliable for file uploads)
    if filename:
        clean_name = os.path.splitext(filename)[0].upper()
        p_match = re.search(r"VC6\s*-?\s*0*([1-9][0-9]?)", clean_name)
        if p_match:
            num = int(p_match.group(1))
            target_pid = f"VC6-{num:04d}"
            if target_pid in meal_db:
                return handle_meal_claim(meal_db[target_pid], meal_db)

    # Strategy 2: Perceptual Hash + Color Signature Image Matching
    if image_b64:
        try:
            if "," in image_b64:
                image_b64 = image_b64.split(",")[1]
            img_bytes = base64.b64decode(image_b64)
            img = Image.open(io.BytesIO(img_bytes))
            
            matched_pid, confidence = match_badge_image(img)
            
            if matched_pid and confidence >= 0.60 and matched_pid in meal_db:
                return handle_meal_claim(meal_db[matched_pid], meal_db)
        except Exception as e:
            print(f"[SCAN] Image decode error: {e}")

    # Strategy 3: Text / Slogan / Name Match
    if text_hint:
        student, _ = parse_and_find_student(text_hint, meal_db)
        if student:
            return handle_meal_claim(student, meal_db)

    return jsonify({
        "status": "ERROR",
        "badge_color": "red",
        "title": "Badge Not Recognized",
        "message": "Could not match this badge. Try uploading a clearer image or use the attendee search below."
    }), 400


# Keep the old endpoint name for backward compatibility
@app.route("/api/scan_medallion", methods=["POST"])
def process_medallion_scan():
    """Backward-compatible alias for scan_image."""
    return process_image_scan()


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
    init_badge_fingerprints()

    use_ssl = os.environ.get("USE_SSL", "0") == "1"
    ssl_ctx = "adhoc" if use_ssl else None

    print("\n" + "=" * 65)
    print("  GTA VI VICE CITY — VIP MEAL TRACKER & CYBER SCANNER")
    print(f"  Mode: {'HTTPS (Mobile Camera Enabled)' if use_ssl else 'HTTP'}")
    print("  Local Access:  http://127.0.0.1:5000")
    print("  Mobile Access: http://<LAPTOP_IP>:5000 (or set USE_SSL=1)")
    print("=" * 65 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_ctx)
