import json, colorsys
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

def get_attendee_solid_color(idx, total=82):
    # 82 pure solid distinct vibrant colors across 360 degrees
    hue = (idx % total) / float(total)
    r, g, b = colorsys.hsv_to_rgb(hue, 0.88, 0.96)
    return (int(r * 255), int(g * 255), int(b * 255))

def generate_solid_color_medallion(pass_num, attendee_idx=0, size=430):
    scale = 2
    S = size * scale
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    r_disc = S // 2 - 14 * scale

    # Pure Solid Color Filled Circle (NO gradient, NO complex texture)
    solid_color = get_attendee_solid_color(attendee_idx)
    
    # Outer crisp ring border
    draw.ellipse([cx - r_disc, cy - r_disc, cx + r_disc, cy + r_disc], fill=solid_color + (255,), outline=(10, 15, 30, 255), width=6 * scale)

    # Giant Bold High-Contrast Number (e.g. '09', '79') in center
    num_str = f'{pass_num:02d}'
    num_font = get_font(['C:/Windows/Fonts/IMPACT.TTF', 'C:/Windows/Fonts/ARIALBD.TTF'], 150 * scale)
    bbox_num = draw.textbbox((0, 0), num_str, font=num_font)
    nw = bbox_num[2] - bbox_num[0]
    nh = bbox_num[3] - bbox_num[1]
    
    nx = cx - nw // 2
    ny = cy - nh // 2 - 10 * scale
    
    # Crisp Dark 3D Shadow + Solid Pure White Number
    draw.text((nx + 6 * scale, ny + 6 * scale), num_str, font=num_font, fill=(10, 15, 30, 240))
    draw.text((nx + 3 * scale, ny + 3 * scale), num_str, font=num_font, fill=(0, 0, 0, 200))
    draw.text((nx, ny), num_str, font=num_font, fill=(255, 255, 255, 255))

    # VIP Text Label under number
    lbl_font = get_font(['C:/Windows/Fonts/SEGOEUIB.TTF', 'C:/Windows/Fonts/ARIALBD.TTF'], 28 * scale)
    lbl = f'VIP #{pass_num:02d}'
    bbox_lbl = draw.textbbox((0, 0), lbl, font=lbl_font)
    lw = bbox_lbl[2] - bbox_lbl[0]
    lx = cx - lw // 2
    ly = cy + nh // 2 + 10 * scale
    
    draw.text((lx + 2 * scale, ly + 2 * scale), lbl, font=lbl_font, fill=(10, 15, 30, 220))
    draw.text((lx, ly), lbl, font=lbl_font, fill=(255, 255, 255, 255))

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
        
        medallion = generate_solid_color_medallion(pass_num, attendee_idx=i, size=430)
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
        
        img.save(f'scratch_solid_{s["pass_id"]}.png')

print('Generated scratch_solid_VC6-0009.png and scratch_solid_VC6-0079.png')
