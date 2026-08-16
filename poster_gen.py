# poster_gen.py
from PIL import Image, ImageDraw, ImageFont
import os

def create_movie_poster(title, subtitle, rating, year, duration, genres, description, output_path):
    try:
        img = Image.new('RGB', (600, 900), color=(15, 15, 25))
        draw = ImageDraw.Draw(img)
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            font_title = font_sub = font_small = ImageFont.load_default()
        draw.text((30, 60), title.upper(), fill=(255,255,255), font=font_title)
        draw.text((30, 130), subtitle if subtitle else "MOVIE", fill=(200,200,200), font=font_sub)
        info_parts = []
        if year: info_parts.append(str(year))
        if rating: info_parts.append(f"{rating}★")
        if duration: info_parts.append(duration)
        info_text = "  •  ".join(info_parts) if info_parts else "2026  •  7.9★  •  2H25M"
        draw.text((30, 200), info_text, fill=(255,215,0), font=font_small)
        genres_str = " / ".join(genres[:3]) if genres and isinstance(genres, list) else "Action / Drama"
        draw.text((30, 250), genres_str, fill=(180,180,255), font=font_small)
        if description:
            desc_lines = wrap_text(description, 35)
            y = 320
            for line in desc_lines[:6]:
                draw.text((30, y), line, fill=(220,220,220), font=font_small)
                y += 28
        draw.text((30, 850), "〽️ Powered by @Backupsk01", fill=(100,100,120), font=font_small)
        img.save(output_path)
        return output_path
    except Exception as e:
        print(f"Poster generation error: {e}")
        return None

def wrap_text(text, width):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if len(current + w) < width:
            current += w + " "
        else:
            lines.append(current.strip())
            current = w + " "
    if current:
        lines.append(current.strip())
    return lines
