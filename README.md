# 🌴 GTA VI VICE CITY — VIP MEAL TRACKER & BADGE SYSTEM

A complete, standalone Python & Flask web system designed for the **Freshers Party 2026** (Vice City / GTA VI synthwave neon theme).

---

## 🚀 3-Step Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Dataset & VIP Badges
```bash
# Step 2a: Generate student database with cryptographic signatures
python generate_dataset.py

# Step 2b: Generate all individual printable VIP passes (saved to /badges)
python badge_generator.py
```

### 3. Launch Flask Scanner Server
```bash
python app.py
```
- Open on host laptop: `http://localhost:5000`
- Access on mobile smartphones over local Wi-Fi / Hotspot: `http://<YOUR_LAPTOP_IP>:5000`

---

## 🍽️ 2-Course Meal Allocation Rules

Every attendee is entitled to **exactly 2 plates**:
1. **Scan 1 (Starter):** Marks Starter as **SERVED**, logs timestamp, activates 30-minute cooldown timer. Status: `STARTER APPROVED` (Green).
2. **Scan 2 (Before Cooldown):** System blocks claim with status: `STARTER CLAIMED — WAIT FOR MAIN DISH` (Orange).
3. **Scan 2 (After Cooldown):** Marks Main Course as **SERVED**, logs timestamp. Status: `MAIN DISH APPROVED` (Green).
4. **Scan 3+ (Both Claimed):** System blocks redemption with status: `ALL MEALS CLAIMED — LIMIT REACHED` (Red).

*(Staff emergency override button is available directly on the scanner UI if manual clearance is required).*

---

## 🔒 Security & VIP Badge Design

- **Anti-Forging HMAC Security:** Passes are cryptographically signed with HMAC-SHA256 (`VC6-<ID>-<HASH>`). Generic QR scanners cannot forge or tamper with passes.
- **Vice City Synthwave Aesthetics:** Hot Pink (`#FF007F`), Neon Cyan (`#00F0FF`), Deep Violet (`#150524`), neon palm tree silhouettes, and CRT scan lines.
- **Audio Feedback:** Web Audio synthesizer provides retro 80s arcade sound chimes on successful scans, warning warbles on cooldowns, and error buzzers on denials.
- **Fast-Track Emergency Search:** Instant typeahead search box to claim meals by Student Name, Enrollment Number, or Pass ID if camera scanning is unavailable.

---

## 📂 File Structure

```
├── app.py                  # Main Flask web application & scanning API
├── generate_dataset.py     # Parses attendees and generates students.json with HMAC
├── badge_generator.py      # Generates custom Vice City VIP passes to /badges
├── requirements.txt        # Flask, Pillow, qrcode
├── students.json           # Populated attendee dataset (82 students)
├── meal_database.json      # Persistent live meal consumption records
├── secret.key              # Cryptographic HMAC verification key
├── templates/
│   └── index.html          # Mobile scanner interface with camera & live stats
└── badges/                 # Generated PNG VIP badge passes
```
