"""
GTA VI / Vice City — VIP Party Badge Generator (Asymmetrical Palm Orientation)
- Square Borderless Badge (900x900)
- Clean Pure White Background
- 2 Miami Palm Trees with DIFFERENT Orientations & Natural Curvatures:
  * Left Palm: Taller, sweeping gentle S-curve with high arching fronds
  * Right Palm: Unique graceful outward-inward bow with distinct dynamic frond spread
- Top: Ultra-Sharp Crystal Clear GTA Vice City Cursive Name & Year in Vibrant Royal Blue
- Center: Cyber Sonic Pulse Medallion layered ON TOP of the palm fronds
- Bottom: 82 UNIQUE Batch-Tailored Brutal & Hilarious Party Slogans in Clean Dark Glass Capsule
"""

from PIL import Image, ImageDraw, ImageFont
import hashlib
import math
import os
import json

BADGE_SIZE = 900
BADGES_DIR = "badges"

WHITE = (255, 255, 255)
CRYSTAL_ROYAL_BLUE = (0, 90, 230)
CRISP_SHADOW_NAVY = (5, 20, 60)
SOLID_BLACK = (10, 15, 30, 255)

# 33 UNIQUE Senior (2nd Year) Jokes
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

# 49 UNIQUE Junior (1st Year) Jokes
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


def get_font(path_candidates, size):
    for path in path_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def get_cursive_font(size):
    return get_font([
        "C:/Windows/Fonts/RAGE.TTF",
        "C:/Windows/Fonts/BRUSHSCI.TTF",
        "C:/Windows/Fonts/MISTRAL.TTF",
        "C:/Windows/Fonts/FORTE.TTF",
    ], size)


def get_sans_font(size):
    return get_font([
        "C:/Windows/Fonts/SEGOEUIB.TTF",
        "C:/Windows/Fonts/ARIALBD.TTF",
        "C:/Windows/Fonts/CALIBRIB.TTF",
        "C:/Windows/Fonts/VERDANAB.TTF",
    ], size)


def get_gta_pbp_gradient(t):
    """Vice City sunset gradient: Cyan (0,210,255) -> Blue (125,20,220) -> Pink (255,20,160)"""
    if t < 0.5:
        st = t / 0.5
        r = int(0 * (1 - st) + 125 * st)
        g = int(210 * (1 - st) + 20 * st)
        b = int(255 * (1 - st) + 220 * st)
    else:
        st = (t - 0.5) / 0.5
        r = int(125 * (1 - st) + 255 * st)
        g = int(20 * (1 - st) + 20 * st)
        b = int(220 * (1 - st) + 160 * st)
    return (r, g, b)


def generate_left_palm(w=440, h=680):
    """Left Tree: Taller, graceful arching S-curve with high-spread foliage."""
    scale = 2
    W, H = w * scale, h * scale
    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)

    base_x = w * 0.30 * scale
    base_y = H - 2
    trunk_h = H * 0.76

    trunk_l, trunk_r = [], []
    for i in range(121):
        t = i / 120
        y = base_y - t * trunk_h
        cx = base_x + (math.sin(t * 1.35) * (w * 0.28 * scale))
        r = (23 * scale) * (1.0 - t * 0.60)
        trunk_l.append((cx - r, y))
        trunk_r.insert(0, (cx + r, y))

    draw.polygon(trunk_l + trunk_r, fill=255)
    top_x, top_y = (trunk_l[-1][0] + trunk_r[0][0]) / 2, trunk_l[-1][1]

    for ox, oy in [(-9, -4), (9, -5), (-4, 8), (11, 6), (0, -7)]:
        r = 13 * scale
        draw.ellipse(
            [top_x + ox * scale - r, top_y + oy * scale - r,
             top_x + ox * scale + r, top_y + oy * scale + r],
            fill=255,
        )

    # Distinct left foliage
    fronds = [
        (-195, 0.56, 0.35, 1.25),
        (-170, 0.66, 0.30, 1.15),
        (-145, 0.75, 0.25, 1.05),
        (-120, 0.78, 0.20, 0.95),
        (-95, 0.80, 0.15, 0.90),
        (-70, 0.76, 0.20, 0.95),
        (-45, 0.70, 0.25, 1.05),
        (-20, 0.62, 0.30, 1.15),
        (5, 0.50, 0.35, 1.25),
        (-155, 0.46, 0.44, 0.85),
        (-115, 0.52, 0.38, 0.78),
        (-75, 0.52, 0.38, 0.78),
        (-35, 0.44, 0.44, 0.85),
    ]

    for ang, flen_ratio, arch, sag in fronds:
        flen = w * scale * flen_ratio
        rad = math.radians(ang)
        spine = []
        for s in range(32):
            st = s / 31.0
            sx = top_x + st * flen * math.cos(rad)
            sy = top_y + st * flen * math.sin(rad) * arch + (st**2.1) * flen * 0.44 * sag
            spine.append((sx, sy))
        for k in range(1, len(spine) - 1):
            st = k / len(spine)
            px, py = spine[k]
            dx = spine[k + 1][0] - spine[k - 1][0]
            dy = spine[k + 1][1] - spine[k - 1][1]
            tangent = math.atan2(dy, dx)
            leaf_w = math.sin(st * math.pi) * (w * 0.19 * scale) + 3 * scale
            for side in [-1, 1]:
                la = tangent + side * (1.28 - st * 0.25)
                tip_x = px + leaf_w * math.cos(la)
                tip_y = py + leaf_w * math.sin(la) + (st**1.8) * 12 * scale
                draw.polygon(
                    [(px, py), (tip_x, tip_y), (px + dx * 0.5, py + dy * 0.5)],
                    fill=255,
                )
        for k in range(len(spine) - 1):
            w_line = max(2 * scale, int((1 - k / len(spine)) * 5 * scale))
            draw.line([spine[k], spine[k + 1]], fill=255, width=w_line)

    grad_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad_img)
    for y in range(H):
        t = y / H
        c = get_gta_pbp_gradient(t)
        gdraw.line([(0, y), (W, y)], fill=(c[0], c[1], c[2], 255))

    grad_img.putalpha(mask)
    resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else getattr(Image, "LANCZOS", 1)
    return grad_img.resize((w, h), resample)


def generate_right_palm(w=420, h=640):
    """Right Tree: Different height, slightly sharper inward lean, different frond angles & canopy silhouette."""
    scale = 2
    W, H = w * scale, h * scale
    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)

    base_x = w * 0.72 * scale
    base_y = H - 2
    trunk_h = H * 0.72

    trunk_l, trunk_r = [], []
    for i in range(121):
        t = i / 120
        y = base_y - t * trunk_h
        # Different wave curvature (t^1.1 power curvature instead of pure sine)
        cx = base_x - (math.pow(t, 1.15) * (w * 0.26 * scale))
        r = (21 * scale) * (1.0 - t * 0.58)
        trunk_l.append((cx - r, y))
        trunk_r.insert(0, (cx + r, y))

    draw.polygon(trunk_l + trunk_r, fill=255)
    top_x, top_y = (trunk_l[-1][0] + trunk_r[0][0]) / 2, trunk_l[-1][1]

    for ox, oy in [(-7, -5), (8, -3), (-5, 7), (9, 7), (0, -8)]:
        r = 12 * scale
        draw.ellipse(
            [top_x + ox * scale - r, top_y + oy * scale - r,
             top_x + ox * scale + r, top_y + oy * scale + r],
            fill=255,
        )

    # Distinct right foliage (different angles, lengths and sag ratios)
    fronds = [
        (-185, 0.52, 0.38, 1.15),
        (-160, 0.60, 0.32, 1.05),
        (-135, 0.68, 0.28, 0.98),
        (-110, 0.74, 0.22, 0.88),
        (-85, 0.76, 0.18, 0.84),
        (-60, 0.74, 0.22, 0.88),
        (-35, 0.68, 0.28, 0.98),
        (-10, 0.60, 0.32, 1.05),
        (15, 0.52, 0.38, 1.15),
        (-145, 0.42, 0.40, 0.82),
        (-105, 0.48, 0.35, 0.75),
        (-65, 0.48, 0.35, 0.75),
        (-25, 0.42, 0.40, 0.82),
    ]

    for ang, flen_ratio, arch, sag in fronds:
        flen = w * scale * flen_ratio
        rad = math.radians(ang)
        spine = []
        for s in range(32):
            st = s / 31.0
            sx = top_x + st * flen * math.cos(rad)
            sy = top_y + st * flen * math.sin(rad) * arch + (st**2.1) * flen * 0.42 * sag
            spine.append((sx, sy))
        for k in range(1, len(spine) - 1):
            st = k / len(spine)
            px, py = spine[k]
            dx = spine[k + 1][0] - spine[k - 1][0]
            dy = spine[k + 1][1] - spine[k - 1][1]
            tangent = math.atan2(dy, dx)
            leaf_w = math.sin(st * math.pi) * (w * 0.17 * scale) + 3 * scale
            for side in [-1, 1]:
                la = tangent + side * (1.28 - st * 0.25)
                tip_x = px + leaf_w * math.cos(la)
                tip_y = py + leaf_w * math.sin(la) + (st**1.8) * 11 * scale
                draw.polygon(
                    [(px, py), (tip_x, tip_y), (px + dx * 0.5, py + dy * 0.5)],
                    fill=255,
                )
        for k in range(len(spine) - 1):
            w_line = max(2 * scale, int((1 - k / len(spine)) * 5 * scale))
            draw.line([spine[k], spine[k + 1]], fill=255, width=w_line)

    grad_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad_img)
    for y in range(H):
        t = y / H
        c = get_gta_pbp_gradient(t)
        gdraw.line([(0, y), (W, y)], fill=(c[0], c[1], c[2], 255))

    grad_img.putalpha(mask)
    resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else getattr(Image, "LANCZOS", 1)
    return grad_img.resize((w, h), resample)


def generate_cyber_radial_medallion(scan_code, size=430):
    scale = 2
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    r_outer = S // 2 - 10
    r_disc = r_outer - 28

    glow_colors = [
        (255, 10, 160, 255),
        (0, 215, 255, 255),
        (160, 20, 240, 255),
        (0, 180, 255, 255),
    ]
    for i in range(16):
        r = r_outer - i * 2
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=glow_colors[i % len(glow_colors)],
            width=3,
        )

    disc_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(disc_mask).ellipse(
        [cx - r_disc, cy - r_disc, cx + r_disc, cy + r_disc], fill=255
    )

    disc_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dldraw = ImageDraw.Draw(disc_layer)
    for y in range(int(cy - r_disc), int(cy)):
        t = (y - (cy - r_disc)) / r_disc
        c = get_gta_pbp_gradient(t)
        dldraw.line(
            [(cx - r_disc - 5, y), (cx + r_disc + 5, y)],
            fill=(c[0], c[1], c[2], 255),
        )
    dldraw.rectangle(
        [cx - r_disc - 5, cy, cx + r_disc + 5, cy + r_disc + 5],
        fill=SOLID_BLACK,
    )
    disc_layer.putalpha(disc_mask)
    img.paste(disc_layer, (0, 0), disc_layer)

    draw.line(
        [(cx - r_disc + 6, cy), (cx + r_disc - 6, cy)],
        fill=(0, 235, 255, 255),
        width=5,
    )

    hash_bytes = hashlib.sha256(scan_code.encode("utf-8")).digest()
    num_rays = 48
    for i in range(num_rays):
        angle = (i / num_rays) * 2 * math.pi
        val = hash_bytes[i % len(hash_bytes)]
        ray_len = (r_disc * 0.35) + (val / 255.0) * (r_disc * 0.52)

        t_col = (math.sin(angle) + 1) / 2
        rgb = get_gta_pbp_gradient(t_col)

        x1 = cx + math.cos(angle) * (r_disc * 0.22)
        y1 = cy + math.sin(angle) * (r_disc * 0.22)
        x2 = cx + math.cos(angle) * ray_len
        y2 = cy + math.sin(angle) * ray_len

        draw.line([(x1, y1), (x2, y2)], fill=(rgb[0], rgb[1], rgb[2], 230), width=4)
        draw.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=(255, 255, 255, 255))

    draw.ellipse(
        [cx - r_disc * 0.20, cy - r_disc * 0.20, cx + r_disc * 0.20, cy + r_disc * 0.20],
        fill=(15, 23, 42, 255),
        outline=(0, 235, 255, 255),
        width=4,
    )
    draw.ellipse(
        [cx - r_disc * 0.08, cy - r_disc * 0.08, cx + r_disc * 0.08, cy + r_disc * 0.08],
        fill=(255, 10, 160, 255),
    )

    draw.ellipse(
        [cx - r_disc, cy - r_disc, cx + r_disc, cy + r_disc],
        outline=(255, 215, 40, 255),
        width=5,
    )

    resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else getattr(Image, "LANCZOS", 1)
    return img.resize((size, size), resample)


def create_badge(student, slogan_text, left_palm, right_palm):
    img = Image.new("RGBA", (BADGE_SIZE, BADGE_SIZE), (255, 255, 255, 255))

    # 1. TWO Asymmetrical Miami Palm Trees with different orientation & curvatures
    img.paste(left_palm, (-20, BADGE_SIZE - left_palm.height + 25), left_palm)
    img.paste(
        right_palm,
        (BADGE_SIZE - right_palm.width + 15, BADGE_SIZE - right_palm.height + 25),
        right_palm,
    )

    # 2. CENTER: Cyber Sonic Medallion (Layered ON TOP of palm fronds)
    medallion_size = 430
    medallion = generate_cyber_radial_medallion(
        student["scan_code"], size=medallion_size
    )
    mx = (BADGE_SIZE - medallion_size) // 2
    my = 275
    img.paste(medallion, (mx, my), medallion)

    draw = ImageDraw.Draw(img)

    # 3. TOP: Student Name & Year (Crystal Clear High-Definition GTA Vice City Cursive)
    name_raw = student["name"]
    name_text = name_raw.title() if name_raw.isupper() else name_raw
    year_text = student["batch"]

    if len(name_text) > 22:
        name_size = 98
    elif len(name_text) > 16:
        name_size = 110
    else:
        name_size = 122

    name_font = get_cursive_font(name_size)
    year_font = get_cursive_font(76)

    # Name at Top
    bbox_n = draw.textbbox((0, 0), name_text, font=name_font)
    nw = bbox_n[2] - bbox_n[0]
    nx = (BADGE_SIZE - nw) // 2
    ny = 38

    # Ultra-crisp 3D shadow
    draw.text((nx + 4, ny + 4), name_text, font=name_font, fill=CRISP_SHADOW_NAVY)
    draw.text((nx + 2, ny + 2), name_text, font=name_font, fill=(0, 45, 130))
    draw.text((nx, ny), name_text, font=name_font, fill=CRYSTAL_ROYAL_BLUE)

    # Year at Top (under Name)
    bbox_y = draw.textbbox((0, 0), year_text, font=year_font)
    yw = bbox_y[2] - bbox_y[0]
    yx = (BADGE_SIZE - yw) // 2
    yy = ny + (bbox_n[3] - bbox_n[1]) + 6

    draw.text((yx + 3, yy + 3), year_text, font=year_font, fill=CRISP_SHADOW_NAVY)
    draw.text((yx + 1, yy + 1), year_text, font=year_font, fill=(0, 45, 130))
    draw.text((yx, yy), year_text, font=year_font, fill=CRYSTAL_ROYAL_BLUE)

    # 4. BOTTOM: UNIQUE Brutal & Funny Slogan + Crisp Pass ID
    pass_id_str = student["pass_id"]
    quote_font = get_sans_font(21)
    full_bottom_text = f"“ {slogan_text} ”   •   {pass_id_str}"
    bbox_q = draw.textbbox((0, 0), full_bottom_text, font=quote_font)
    qw = bbox_q[2] - bbox_q[0]
    qx = (BADGE_SIZE - qw) // 2
    qy = BADGE_SIZE - 74

    pad_x, pad_y = 18, 9
    # Dark glassmorphism capsule with clean border
    draw.rounded_rectangle(
        [qx - pad_x, qy - pad_y, qx + qw + pad_x, qy + (bbox_q[3] - bbox_q[1]) + pad_y],
        radius=14,
        fill=(15, 23, 42, 245),
        outline=(0, 229, 255, 220),
        width=2
    )

    draw.text((qx, qy), full_bottom_text, font=quote_font, fill=(248, 250, 252, 255))

    return img.convert("RGB")


def generate_all_badges():
    os.makedirs(BADGES_DIR, exist_ok=True)
    print("Generating passes with distinct asymmetrical palm tree orientations...")
    left_palm = generate_left_palm(w=440, h=680)
    right_palm = generate_right_palm(w=420, h=640)

    with open("students.json", "r", encoding="utf-8") as f:
        students = json.load(f)

    senior_idx = 0
    junior_idx = 0

    for i, student in enumerate(students):
        is_senior = (student.get("batch") == "2nd Year")
        if is_senior:
            slogan = SENIOR_SLOGANS_33[senior_idx % len(SENIOR_SLOGANS_33)]
            senior_idx += 1
            cat = "Senior"
        else:
            slogan = JUNIOR_SLOGANS_49[junior_idx % len(JUNIOR_SLOGANS_49)]
            junior_idx += 1
            cat = "Junior"

        badge = create_badge(student, slogan, left_palm, right_palm)
        fname = f"{student['pass_id']}.png"
        filepath = os.path.join(BADGES_DIR, fname)
        badge.save(filepath, quality=98)
        print(f"  [OK] {fname} -> {student['name']} ({student['batch']} / {cat}) | Slogan: \"{slogan}\"")

    print(f"\n[SUCCESS] Generated all {len(students)} passes with distinct asymmetrical palms -> {BADGES_DIR}/")


if __name__ == "__main__":
    generate_all_badges()
