import json
from PIL import Image, ImageDraw, ImageFont
from badge_generator import (
    BADGE_SIZE, SOLID_BLACK, CRYSTAL_ROYAL_BLUE, CRISP_SHADOW_NAVY,
    generate_left_palm, generate_right_palm, get_cursive_font, get_sans_font
)

def get_font(path_candidates, size):
    for path in path_candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def get_attendee_gradient(idx):
    palettes = [
        ((0, 229, 255), (157, 78, 221)),   # Cyan -> Purple
        ((255, 0, 127), (123, 44, 191)),   # Hot Pink -> Violet
        ((255, 183, 3), (251, 86, 7)),     # Gold -> Orange
        ((0, 245, 212), (0, 187, 249)),    # Turquoise -> Sky Blue
        ((255, 77, 109), (201, 24, 74)),   # Tropical Coral -> Crimson
        ((114, 9, 183), (247, 37, 133)),   # Deep Indigo -> Neon Pink
        ((76, 201, 240), (67, 97, 238)),   # Electric Blue -> Cobalt
        ((56, 176, 0), (0, 114, 0)),       # Neon Emerald
    ]
    return palettes[idx % len(palettes)]

def generate_vip_color_number_medallion(pass_num, attendee_idx=0, size=430):
    scale = 2
    S = size * scale
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    r_disc = S // 2 - 20 * scale

    # Outer Neon Glowing Cyber Rings
    draw.ellipse([cx - r_disc, cy - r_disc, cx + r_disc, cy + r_disc], fill=(10, 15, 30, 255), outline=(0, 229, 255, 255), width=7 * scale)
    draw.ellipse([cx - r_disc + 7 * scale, cy - r_disc + 7 * scale, cx + r_disc - 7 * scale, cy + r_disc - 7 * scale], outline=(255, 0, 127, 255), width=4 * scale)

    # Inner Colored Disc with Gradient / Radial Shading
    c1, c2 = get_attendee_gradient(attendee_idx)
    inner_r = r_disc - 16 * scale
    
    disc_img = Image.new('RGBA', (inner_r * 2, inner_r * 2), (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(disc_img)
    for rad in range(inner_r, 0, -2):
        t = rad / inner_r
        r = int(12 * t + c1[0] * (1 - t) * 0.9)
        g = int(18 * t + c1[1] * (1 - t) * 0.9)
        b = int(32 * t + c1[2] * (1 - t) * 0.9)
        ddraw.ellipse([inner_r - rad, inner_r - rad, inner_r + rad, inner_r + rad], fill=(r, g, b, 255))
        
    img.paste(disc_img, (cx - inner_r, cy - inner_r), disc_img)
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], outline=(0, 229, 255, 255), width=2 * scale)

    # Top VIP Badge Header
    label_font = get_font(['C:/Windows/Fonts/SEGOEUIB.TTF', 'C:/Windows/Fonts/ARIALBD.TTF'], 26 * scale)
    lbl = 'VIP ACCESS'
    bbox_lbl = draw.textbbox((0, 0), lbl, font=label_font)
    lw = bbox_lbl[2] - bbox_lbl[0]
    draw.text((cx - lw // 2, cy - inner_r + 34 * scale), lbl, font=label_font, fill=(0, 229, 255, 255))

    # Giant Bold High-Contrast Number (e.g. '09', '79')
    num_str = f'{pass_num:02d}'
    num_font = get_font(['C:/Windows/Fonts/IMPACT.TTF', 'C:/Windows/Fonts/ARIALBD.TTF'], 138 * scale)
    bbox_num = draw.textbbox((0, 0), num_str, font=num_font)
    nw = bbox_num[2] - bbox_num[0]
    nh = bbox_num[3] - bbox_num[1]
    
    nx = cx - nw // 2
    ny = cy - nh // 2 + 10 * scale
    
    # 3D Shadow + Solid Pure White Digits
    draw.text((nx + 6 * scale, ny + 6 * scale), num_str, font=num_font, fill=(0, 0, 0, 240))
    draw.text((nx + 3 * scale, ny + 3 * scale), num_str, font=num_font, fill=(255, 0, 127, 255))
    draw.text((nx, ny), num_str, font=num_font, fill=(255, 255, 255, 255))

    # Bottom Sub-Tag: 'PASS #09'
    sub_font = get_font(['C:/Windows/Fonts/SEGOEUIB.TTF', 'C:/Windows/Fonts/ARIALBD.TTF'], 24 * scale)
    sub_lbl = f'PASS #{pass_num:02d}'
    bbox_sub = draw.textbbox((0, 0), sub_lbl, font=sub_font)
    sw = bbox_sub[2] - bbox_sub[0]
    draw.text((cx - sw // 2, cy + inner_r - 50 * scale), sub_lbl, font=sub_font, fill=(255, 0, 127, 255))

    return img.resize((size, size), Image.Resampling.LANCZOS)

with open('students.json', encoding='utf-8') as f:
    students = json.load(f)

left_palm = generate_left_palm(440, 680)
right_palm = generate_right_palm(440, 680)

for i, s in enumerate(students):
    if s['pass_id'] in ['VC6-0009', 'VC6-0079']:
        pass_num = int(s['pass_id'].split('-')[1])
        img = Image.new('RGBA', (BADGE_SIZE, BADGE_SIZE), (255, 255, 255, 255))
        img.paste(left_palm, (-20, BADGE_SIZE - left_palm.height + 25), left_palm)
        img.paste(right_palm, (BADGE_SIZE - right_palm.width + 15, BADGE_SIZE - right_palm.height + 25), right_palm)
        
        medallion = generate_vip_color_number_medallion(pass_num, attendee_idx=i, size=430)
        img.paste(medallion, (235, 275), medallion)
        
        draw = ImageDraw.Draw(img)
        name_raw = s['name']
        name_text = name_raw.title() if name_raw.isupper() else name_raw
        name_font = get_cursive_font(110)
        year_font = get_cursive_font(76)
        
        bbox_n = draw.textbbox((0, 0), name_text, font=name_font)
        nw = bbox_n[2] - bbox_n[0]
        nx = (BADGE_SIZE - nw) // 2
        ny = 38
        draw.text((nx + 4, ny + 4), name_text, font=name_font, fill=CRISP_SHADOW_NAVY)
        draw.text((nx + 2, ny + 2), name_text, font=name_font, fill=(0, 45, 130))
        draw.text((nx, ny), name_text, font=name_font, fill=CRYSTAL_ROYAL_BLUE)
        
        bbox_y = draw.textbbox((0, 0), s['batch'], font=year_font)
        yw = bbox_y[2] - bbox_y[0]
        yx = (BADGE_SIZE - yw) // 2
        yy = ny + (bbox_n[3] - bbox_n[1]) + 2
        draw.text((yx + 4, yy + 4), s['batch'], font=year_font, fill=CRISP_SHADOW_NAVY)
        draw.text((yx + 2, yy + 2), s['batch'], font=year_font, fill=(0, 45, 130))
        draw.text((yx, yy), s['batch'], font=year_font, fill=CRYSTAL_ROYAL_BLUE)
        
        pass_id_str = s['pass_id']
        quote_font = get_sans_font(21)
        slog = s.get('slogan', '')
        full_bottom_text = f'“ {slog} ”   •   {pass_id_str}'
        bbox_q = draw.textbbox((0, 0), full_bottom_text, font=quote_font)
        qw = bbox_q[2] - bbox_q[0]
        qh = bbox_q[3] - bbox_q[1]
        qx = (BADGE_SIZE - qw) // 2
        qy = BADGE_SIZE - 82
        
        pad_x, pad_y = 24, 10
        pill_box = [qx - pad_x, qy - pad_y, qx + qw + pad_x, qy + qh + pad_y]
        draw.rounded_rectangle(pill_box, radius=14, fill=SOLID_BLACK, outline=(0, 229, 255, 255), width=2)
        draw.text((qx, qy), full_bottom_text, font=quote_font, fill=(255, 255, 255, 255))
        
        img.save(f'scratch_color_{s["pass_id"]}.png')

print('Generated scratch_color_VC6-0009.png and scratch_color_VC6-0079.png')
