import os
import json
import time
import hmac
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

DATA_FILE = "students.json"
MEAL_DB_FILE = "meal_database.json"
SECRET_FILE = "secret.key"

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
            return json.load(f)
    except Exception:
        return {}


def save_meal_db(db):
    with open(MEAL_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def verify_hmac(pass_id: str, signature: str) -> bool:
    expected = hmac.new(
        SECRET_KEY.encode(),
        pass_id.encode(),
        hashlib.sha256
    ).hexdigest()[:12].upper()
    return hmac.compare_digest(expected, signature.upper())


def parse_and_find_student(input_str: str, meal_db: dict):
    input_str = input_str.strip()
    if not input_str:
        return None, "Empty input provided."

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
    if upper_input in meal_db:
        return meal_db[upper_input], None

    for record in meal_db.values():
        if record.get("enrollment") == input_str:
            return record, None

    matches = []
    for record in meal_db.values():
        if upper_input == record.get("name", "").upper():
            return record, None
        if upper_input in record.get("name", "").upper():
            matches.append(record)

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
            "message": f"Starter meal served to {student['name']} ({student['batch']}). Cooldown activated.",
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
def process_scan_image():
    data = request.get_json() or {}
    text_content = data.get("text", "").strip()
    filename = data.get("filename", "").strip()

    meal_db = load_meal_db()

    # 1. Filename match (e.g. VC6-0009.png)
    if filename:
        clean_name = os.path.splitext(filename)[0].upper()
        if clean_name in meal_db:
            return handle_meal_claim(meal_db[clean_name], meal_db, force_override=False)

    # 2. Text match
    if text_content:
        student, _ = parse_and_find_student(text_content, meal_db)
        if student:
            return handle_meal_claim(student, meal_db, force_override=False)

    return jsonify({
        "status": "ERROR",
        "badge_color": "red",
        "title": "Pass Not Recognized",
        "message": "Could not identify attendee pass from image. Try another image or search manually."
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
        # Return all attendees if no query (for local caching)
        return jsonify([
            {
                "pass_id": s["pass_id"],
                "name": s["name"],
                "enrollment": s["enrollment"],
                "batch": s["batch"],
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
            q in s.get("enrollment", "")):
            results.append({
                "pass_id": s["pass_id"],
                "name": s["name"],
                "enrollment": s["enrollment"],
                "batch": s["batch"],
                "starter_served": s.get("starter_served", False),
                "main_served": s.get("main_served", False),
                "scan_code": s.get("scan_code", "")
            })
            if len(results) >= 15:
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

    use_ssl = os.environ.get("USE_SSL", "0") == "1"
    ssl_ctx = "adhoc" if use_ssl else None

    print("\n" + "=" * 65)
    print("  GTA VI VICE CITY — VIP MEAL TRACKER & CYBER SCANNER")
    print(f"  Mode: {'HTTPS (Mobile Camera Enabled)' if use_ssl else 'HTTP'}")
    print("  Local Access:  http://127.0.0.1:5000")
    print("  Mobile Access: http://<LAPTOP_IP>:5000 (or set USE_SSL=1)")
    print("=" * 65 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_ctx)
