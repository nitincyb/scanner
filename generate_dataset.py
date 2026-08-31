"""
GTA VI Vice City — Attendee Dataset Generator
Generates students.json with HMAC-signed pass IDs.
"""

import json
import hmac
import hashlib
import os

# ── Secret key for HMAC signing (persisted for verification) ──
SECRET_KEY = "VICE_CITY_GTA6_FRESHERS_2026_SECRET"
SECRET_FILE = "secret.key"

STUDENTS_2ND_YEAR = [
    ("R GEET NAG SARDHAK", "25003111016031016"),
    ("Himanshu Singh", "25003111016031021"),
    ("Kapileshwar Gonewad", "25003111016031024"),
    ("Riyan Rajak", "25003111016031040"),
    ("Harshit", "25003111016031020"),
    ("Hariom Singh", "25003111016031017"),
    ("Mohammad Irfan", "25003111016031027"),
    ("Hrishika Singh", "25003111016031064"),
    ("Nitin Mali", "25003111016031060"),
    ("Mukund Kundan", "25003111016031028"),
    ("Bhumika Bharti", "25003111016031058"),
    ("Chandrima Majumdar", "25003111016031010"),
    ("Shivanshu", "25003111016031048"),
    ("Rixika Agarwal", "25003111016031039"),
    ("Swini Singh", "25003111016031053"),
    ("Sidhant Raj", "25003111016031051"),
    ("Aman Dubey", "25003111016031005"),
    ("Chandra Prakash Suthar", "25003111016031009"),
    ("Navneet Singh", "25003111016031030"),
    ("Charvi", "25003111016031011"),
    ("Saumya Mishra", "25003111016031044"),
    ("Shreyashee Gupta", "25003111016031049"),
    ("Ayushman Dutta", "25003111016031008"),
    ("Pratham Bhardwaj", "25003111016031036"),
    ("Saksham Sharma", "25003111016031061"),
    ("Palak", "25003111016031035"),
    ("Mahi Shashi", "25003111016031026"),
    ("Harshit Ram", "26003111062042006"),
    ("Shivansh Sahajpal", "25003111016031047"),
    ("Sakshi Phulwari", "25003111016031042"),
    ("Sakshi Priya", "25003111016031062"),
    ("Sneha Maity", "25003111016031063"),
    ("Shubham Kumar Gupta", "25003111016031050"),
]

STUDENTS_1ST_YEAR = [
    ("Ritabrata Ghosh", "26003111016031054"),
    ("Jiya Patel", "26003111016031019"),
    ("Bedabrata Taraphdar", "26003111016031010"),
    ("Devin Laliyawala", "26003111016031014"),
    ("Aaryan Agrawal", "26003111016031001"),
    ("Jaineel Vaidya", "26003111016031018"),
    ("Devanshi A Kawaiya", "26003111016031013"),
    ("Nitya Chaudhary", "26003111016031032"),
    ("Mayank Poriya", "26003111016031029"),
    ("Siddhangana Bain", "26003111016031045"),
    ("Siddhi Khadgi", "26003111016031046"),
    ("Mridul Patil", "26003111016031057"),
    ("Yash Pratap", "26003111016031051"),
    ("Anand Shankar", "26003111016031007"),
    ("Harsh Joshi", "26003111016031020"),
    ("Shauryasahajpal", "26003111016031043"),
    ("Samridhi Kumari", "26003111016031041"),
    ("Nitya Raghuwanshi", "26003111016031059"),
    ("Surbhi Kumari", "26003111016031048"),
    ("Jahnavi Prasad", "26003111016031017"),
    ("Varad Gupta", "26003111016031050"),
    ("Akshu Pareek", "26003111016031006"),
    ("Dhatri Chawla", "26003111016031015"),
    ("Yug Desai", "26003111016031052"),
    ("Anshu Pareek", "26003111016031008"),
    ("Katyayni Sharma", "26003111016031023"),
    ("Ishaan Singh", "26003111016031016"),
    ("Aashi Srivastava", "26003111016031002"),
    ("Riti Patel", "26003111016031039"),
    ("Prerit Kishan", "26003111016031037"),
    ("Karunya Varma", "26003111016031022"),
    ("Navachaithanya M", "26003111016031031"),
    ("Prasoon", "26003111016031011"),
    ("Kemal Sha", "26003111016031025"),
    ("Om Kasurkar", "26003111016031033"),
    ("Pavitra Kapadiya", "26003111015031035"),
    ("Arsh ArpitKumar Chav", "26003111016031009"),
    ("Patil Vaibhav", "26003111016031055"),
    ("Maitreyi Sharma", "26003111016031053"),
    ("PULKIT UPADHYAY", "26003111016031038"),
    ("Ajad", "26003111016031005"),
    ("Deepak Kumar", "26003111016031012"),
    ("Lakshay", "26003111016031026"),
    ("Pankaj Kumar Ranwa", "26003111016031034"),
    ("Madhav Patidar", "26003111016031028"),
    ("Pratyush", "26003111016031036"),
    ("Vamsi", "26003111016031027"),
    ("Saurabh Kumar", "26003111016031042"),
    ("Adarsh Pratap Singh", "26003111016031004"),
]


def generate_hmac(pass_id: str) -> str:
    """Generate HMAC-SHA256 signature for a pass ID."""
    return hmac.new(
        SECRET_KEY.encode(),
        pass_id.encode(),
        hashlib.sha256,
    ).hexdigest()[:12].upper()


def build_dataset():
    students = []
    counter = 1

    for name, enrollment in STUDENTS_2ND_YEAR:
        pass_id = f"VC6-{counter:04d}"
        sig = generate_hmac(pass_id)
        students.append({
            "name": name,
            "enrollment": enrollment,
            "batch": "2nd Year",
            "pass_id": pass_id,
            "signature": sig,
            "scan_code": f"{pass_id}-{sig}",
        })
        counter += 1

    for name, enrollment in STUDENTS_1ST_YEAR:
        pass_id = f"VC6-{counter:04d}"
        sig = generate_hmac(pass_id)
        students.append({
            "name": name,
            "enrollment": enrollment,
            "batch": "1st Year",
            "pass_id": pass_id,
            "signature": sig,
            "scan_code": f"{pass_id}-{sig}",
        })
        counter += 1

    # Persist the secret alongside the data
    with open(SECRET_FILE, "w", encoding="utf-8") as f:
        f.write(SECRET_KEY)

    with open("students.json", "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2, ensure_ascii=False)

    print(f"[OK] Generated {len(students)} student records -> students.json")
    print(f"[OK] Secret key saved -> {SECRET_FILE}")
    return students


if __name__ == "__main__":
    build_dataset()
