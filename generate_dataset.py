"""
GTA VI Vice City — Attendee Dataset Generator
Generates students.json with HMAC-signed pass IDs and batch-specific unique slogans.
"""

import json
import hmac
import hashlib
import os

SECRET_KEY = "VICE_CITY_GTA6_FRESHERS_2026_SECRET"
SECRET_FILE = "secret.key"

SENIOR_SLOGANS_33 = [
    "Ek saal nikaal liya, ab juniors ko bina wajah gyaan dene ka haq hai.",
    "Party humne organize ki hai, toh VIP treatment toh hamara banta hai boss.",
    "Placement ki tension kal dekhenge, aaj senior swag 200% on hai.",
    "Juniors ke cringe dance moves judge karne ka alag hi maza hai.",
    "1st year walo ko lagta hai hum padhte hain, hume pata hai hum kya karte hain.",
    "Attendance 40% hai par party presence 100% mandatory hai.",
    "Backlog ke dukh ko Vice City ke neon lights me bhula raha hoon.",
    "Senior ban gaye par abhi bhi assignment submission se 5 min pehle banta hai.",
    "Ek saal me hostel mess ne itna dard diya ki ab party me sukoon mila.",
    "Formal blazer isliye pehna taaki lag sake placement lagne wali hai.",
    "Juniors se izzat mangna padta hai, khana haq se chheenna padta hai.",
    "Seniorhood ka pehla niyam: Buffet me juniors ko line me lagao.",
    "Hostel me 1 saal bina nahaye survive karne ka medal milna chahiye.",
    "CGPA girta gaya par senior wala attitude badhta gaya.",
    "Last year hum fresher the, aaj hum hi boundary decide karte hain.",
    "Juniors bol rahe the 'Bhaiya treat do', humne bola 'Party me aao'.",
    "Viva me blank hone ka 1 saal ka solid experience hai mere paas.",
    "Hum seniors hain, hum DJ wale ko order dete hain request nahi.",
    "College life ka sach: 1st year me sapne, 2nd year me sirf survival.",
    "Proxy lagane ki PhD ho chuki hai, kisi junior ko coaching chahiye?",
    "Syllabus kabhi complete nahi hua par party list hamesha ready rahi.",
    "Juniors ko bolte hain 'Padh lo', khud raat 3 baje reels scroll karte hain.",
    "Stage pe jaake mic pakadne ka confidence sirf 2nd year me aata hai.",
    "Dost bole kal submission hai, maine bola aaj Vice City ki raat hai.",
    "1st year ki innocence kho chuki hai, ab sirf pro jugad chalega.",
    "Formal shoes me pair dukh rahe hain par attitude zero compromise.",
    "Canteen wale bhaiya se udhaar lene me ab koi sharm nahi aati.",
    "Juniors humse impress hone aaye hain, hum buffet se impress ho rahe hain.",
    "Ek saal purana blazer, naya swag, wahi purane dost.",
    "Assignment copy karne ka speed light ki speed se bhi fast hai.",
    "Subah 9 baje lab me neend aati hai, raat 12 baje full energy.",
    "Freshers party me aaye hain apna 1 saal ka trauma celebrate karne.",
    "Hostel warden se ladne ka 1 saal ka experience bolta hai!"
]

JUNIOR_SLOGANS_49 = [
    "College dream Bollywood movie jaisa tha, par schedule engineering ban gaya.",
    "Senior ko 'Bhaiya' bolun ya 'Sir', isi confusion me 1 month nikal gaya.",
    "Outfit 5000 ka liya taaki freshers party me hero wali entry mile.",
    "Abhi tak campus ke saare classroom ke raaste bhi yaad nahi huye.",
    "Hostel mess ka pehla bite khate hi ghar ki yaad aa gayi thi.",
    "8 AM lecture me zinda pahunchna hi hamara sabse bada achievement hai.",
    "Intro dene se zyada darr attendance register dekh ke lagta hai.",
    "Seniors bole 'Intro do', humne bola 'Pehle party enjoy karne do'.",
    "Class me first bench se last bench ka safar 1 hafte me poora ho gaya.",
    "College aane se pehle socha tha chill hoga, yahan roz lab viva hai.",
    "Freshers party me full swag, kal se phir wahi 75% attendance ka rona.",
    "Dress pe itna kharcha kiya ki agle 2 mahine canteen me udhaar chalega.",
    "Hostel ke room me pehli baar jhadu lagate waqt rona aa gaya tha.",
    "Senior se eye contact bacha ke DJ floor pe aag lagane aaya hoon.",
    "Abhi tak syllabus ka pehla page bhi nahi khula par party look 10/10.",
    "College fest me aane ka sapna tha, freshers party me VIP ban gaya.",
    "Professors ke naam yaad nahi hain par campus ke saare crush yaad hain.",
    "Ghar pe bola tha engineering easy hai, yahan assignment ne rulaya hai.",
    "Hostel me Maggie bana ke khane wale aaj VIP buffet explore karenge.",
    "1st semester me hi samajh aa gaya ki school life kitni achhi thi.",
    "Photographer bhaiya meri single photos lo, DP update karni hai.",
    "Naagin dance ka plan nahi tha par DJ wale ne majboor kar diya.",
    "CR banne ka sapna tha, pehle assignment me hi resign karne ka man hua.",
    "Senior bole 'Koi problem ho toh batana', humne bola 'Attendance dilwa do'.",
    "High school se nikle toh laga azaadi mili, yahan submission deadline mil gayi.",
    "Formal wear me chalna itna mushkil hai jaise coding me bug dhundhna.",
    "Canteen me pehli baar samosa khate hi realise hua paise bachane honge.",
    "Instagram stories 50 daalunga, college walon ko pata chalna chahiye.",
    "Pehla semester hai, party me energy 100% aur marks ki koi chinta nahi.",
    "Hostel me roommates ke saath pehli ladai Maggi ke share par hui thi.",
    "Sir ne bola tha 'You are the future', par abhi sirf buffet ka future dikh raha hai.",
    "Freshers title mile na mile, best dressed ka confidence poora hai.",
    "College group me 500 messages hain par kaam ka ek bhi nahi.",
    "Subah uthne ke 4 alarm bajte hain, fir bhi 8:05 pe daudte huye aate hain.",
    "Senior bhaiya se tips lene aaya tha, unhone bola 'Hum khud jugad pe hain'.",
    "Ghar ke khane ki kadar hostel aane ke 3 din baad samajh aayi.",
    "Nayi notebooks khareedi thi sundar banayenge, ab rough book ban chuki hai.",
    "Party me no shy mode, freshers hain toh full dhamaka banta hai!",
    "Orientation me socha tha top karenge, ab bas pass hona goal hai.",
    "Selfie angle test karne me hi aadha ghanta nikal gaya!",
    "Mess wale uncle ko laga hum chup rahenge, hum freshers party me aagaye.",
    "Bhai blazer me pocket kahan hai, mobile rakhne me struggle ho raha hai.",
    "Attendance policy sun ke pehli baar dil me thoda dard hua tha.",
    "1st Year ka swag: Har nayi cheez pe over-excited hona!",
    "Hostel ke bathroom ki line se bachke party me time pe pahunch gaya.",
    "College crush ko party me dekha, ab agle 4 saal motivation set hai.",
    "Library me AC ke liye baithe the, padhai ka koi lena dena nahi tha.",
    "Freshers party me aake laga ab officially college life shuru ho gayi!",
    "Duniya chahe idhar ki udhar ho jaye, aaj ki raat full enjoy karenge!"
]

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
    return hmac.new(
        SECRET_KEY.encode(),
        pass_id.encode(),
        hashlib.sha256,
    ).hexdigest()[:12].upper()


def build_dataset():
    students = []
    counter = 1

    for i, (name, enrollment) in enumerate(STUDENTS_2ND_YEAR):
        pass_id = f"VC6-{counter:04d}"
        sig = generate_hmac(pass_id)
        slogan = SENIOR_SLOGANS_33[i % len(SENIOR_SLOGANS_33)]
        students.append({
            "pass_id": pass_id,
            "name": name,
            "enrollment": enrollment,
            "batch": "2nd Year",
            "slogan": slogan,
            "signature": sig,
            "scan_code": f"{pass_id}-{sig}",
        })
        counter += 1

    for i, (name, enrollment) in enumerate(STUDENTS_1ST_YEAR):
        pass_id = f"VC6-{counter:04d}"
        sig = generate_hmac(pass_id)
        slogan = JUNIOR_SLOGANS_49[i % len(JUNIOR_SLOGANS_49)]
        students.append({
            "pass_id": pass_id,
            "name": name,
            "enrollment": enrollment,
            "batch": "1st Year",
            "slogan": slogan,
            "signature": sig,
            "scan_code": f"{pass_id}-{sig}",
        })
        counter += 1

    with open("students.json", "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(students)} students in students.json with batch slogans!")
    return students


if __name__ == "__main__":
    build_dataset()
