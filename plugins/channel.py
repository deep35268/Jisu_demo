import re
import hashlib
import asyncio
import os
import tempfile
from info import *
from utils import *
from pyrogram import Client, filters, enums
from database.users_chats_db import db
from database.ia_filterdb import save_file, unpack_new_file_id
import aiohttp
from typing import Optional
from collections import defaultdict

CAPTION_LANGUAGES = [
    "Bhojpuri", "Hindi", "Bengali", "Tamil", "English", "Bangla",
    "Telugu", "Malayalam", "Kannada", "Marathi", "Punjabi", "Bengoli",
    "Gujrati", "Korean", "Gujarati", "Spanish", "French", "German",
    "Chinese", "Arabic", "Portuguese", "Russian", "Japanese", "Odia",
    "Assamese", "Urdu"
]

UPDATE_CAPTION = """<b>𝖭𝖤𝖶 {} 𝖠𝖣𝖣𝖤𝖣 ✅</b>

🎬 <b>{} {}</b>
🔰 <b>Quality:</b> {}
🎧 <b>Audio:</b> {}

<b>✨ Telegram Files ✨</b>

{}

<blockquote>〽️ Powered by @Backupsk01</b></blockquote>"""

notified_movies = set()
movie_files = defaultdict(list)
POST_DELAY = 10
processing_movies = set()
media_filter = filters.document | filters.video | filters.audio

# -------------------------------------------------------------------
# HANDLER FOR NEW FILES
# -------------------------------------------------------------------
@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    bot_id = bot.me.id
    media = getattr(message, message.media.value, None)
    if media.mime_type in ["video/mp4", "video/x-matroska", "document/mp4"]:
        media.file_type = message.media.value
        media.caption = message.caption
        success_sts = await save_file(media)
        if success_sts == "suc" and await db.get_send_movie_update_status(bot_id):
            file_id, file_ref = unpack_new_file_id(media.file_id)
            await queue_movie_file(bot, media)

# -------------------------------------------------------------------
# QUEUE SYSTEM
# -------------------------------------------------------------------
async def queue_movie_file(bot, media):
    file_name = None
    try:
        file_name = await movie_name_format(media.file_name)
        caption = await movie_name_format(media.caption)
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None
        season_match = re.search(r"(?i)(?:s|season)0*(\d{1,2})", caption) or re.search(
            r"(?i)(?:s|season)0*(\d{1,2})", file_name
        )
        if year:
            file_name = file_name[: file_name.find(year) + 4]
        elif season_match:
            season = season_match.group(1)
            file_name = file_name[: file_name.find(season) + 1]
        
        quality = await get_qualities(caption) or "HDRip"
        jisshuquality = await Jisshu_qualities(caption, media.file_name) or "720p"
        language = (
            ", ".join([lang for lang in CAPTION_LANGUAGES if lang.lower() in caption.lower()])
            or "Not Idea"
        )
        file_size_str = format_file_size(media.file_size)
        file_id, file_ref = unpack_new_file_id(media.file_id)
        
        movie_files[file_name].append({
            "quality": quality,
            "jisshuquality": jisshuquality,
            "file_id": file_id,
            "file_size": file_size_str,
            "caption": caption,
            "language": language,
            "year": year,
        })
        
        if file_name in processing_movies:
            return
        processing_movies.add(file_name)
        
        await asyncio.sleep(POST_DELAY)
        if file_name in movie_files:
            await send_movie_update(bot, file_name, movie_files[file_name])
            del movie_files[file_name]
            
    except Exception as e:
        print(f"Error in queue_movie_file: {e}")
        if file_name and file_name in processing_movies:
            processing_movies.remove(file_name)
        await bot.send_message(LOG_CHANNEL, f"❌ queue_movie_file Error: {e}")
    finally:
        if file_name and file_name in processing_movies:
            processing_movies.remove(file_name)

# -------------------------------------------------------------------
# SEND UPDATE WITH GENERATED POSTER
# -------------------------------------------------------------------
async def send_movie_update(bot, file_name, files):
    try:
        if file_name in notified_movies:
            return
        notified_movies.add(file_name)

        # Get bot's own username for links (instead of temp.U_NAME)
        bot_username = (await bot.get_me()).username
        if not bot_username:
            bot_username = "YourBotUsername"  # fallback

        # IMDB data
        imdb_data = await get_imdb(file_name)
        title = imdb_data.get("title", file_name)
        year_match = re.search(r"\b(19|20)\d{2}\b", file_name)
        year = year_match.group(0) if year_match else None
        kind = imdb_data.get("kind", "").strip().upper().replace(" ", "_") if imdb_data else ""
        if kind == "TV_SERIES":
            kind = "SERIES"
        
        languages = set()
        for f in files:
            if f["language"] != "Not Idea":
                languages.update(f["language"].split(", "))
        language = ", ".join(sorted(languages)) or "Not Idea"

        # Build quality/episode links
        episode_pattern = re.compile(r"S(\d{1,2})E(\d{1,2})", re.IGNORECASE)
        combined_pattern = re.compile(r"S(\d{1,2})\s*E(\d{1,2})[-~]E?(\d{1,2})", re.IGNORECASE)
        episode_map = defaultdict(dict)
        combined_links = []

        for f in files:
            caption_text = f["caption"]
            quality = f.get("jisshuquality") or f.get("quality") or "Unknown"
            size = f["file_size"]
            file_id = f['file_id']
            link = f"<a href='https://t.me/{bot_username}?start=file_0_{file_id}'>{size}</a>"
            
            match = episode_pattern.search(caption_text)
            combined_match = combined_pattern.search(caption_text)
            
            if match:
                ep = f"S{int(match.group(1)):02d}E{int(match.group(2)):02d}"
                episode_map[ep][quality] = f
            elif combined_match:
                season = f"S{int(combined_match.group(1)):02d}"
                ep_range = f"E{int(combined_match.group(2)):02d}-{int(combined_match.group(3)):02d}"
                ep = f"{season}{ep_range}"
                combined_links.append(f"📦 {ep} ({quality}) : {link}")
            elif re.search(r"complete|completed|batch|combined", caption_text, re.IGNORECASE):
                combined_links.append(f"📦 ({quality}) : {link}")

        quality_text = ""
        for ep, qualities in sorted(episode_map.items()):
            parts = []
            for q in sorted(qualities.keys()):
                f = qualities[q]
                link = f"<a href='https://t.me/{bot_username}?start=file_0_{f['file_id']}'>{q}</a>"
                parts.append(link)
            quality_text += f"📦 {ep} : " + " - ".join(parts) + "\n"

        if combined_links:
            quality_text += "\n<b>COMBiNED</b> ✅\n\n" + "\n".join(combined_links) + "\n"

        if not quality_text:
            quality_groups = defaultdict(list)
            for f in files:
                q = f.get("jisshuquality") or f.get("quality") or "Unknown"
                quality_groups[q].append(f)
            for q, q_files in sorted(quality_groups.items()):
                links = [
                    f"<a href='https://t.me/{bot_username}?start=file_0_{f['file_id']}'>{f['file_size']}</a>"
                    for f in q_files
                ]
                quality_text += f"📦 {q} : " + " | ".join(links) + "\n"

        # Get target channel
        movie_update_channel = await db.movies_update_channel_id()
        if not movie_update_channel:
            movie_update_channel = MOVIE_UPDATE_CHANNEL

        # Validate channel
        try:
            await bot.get_chat(movie_update_channel)
        except Exception as e:
            print(f"Chat {movie_update_channel} not accessible: {e}")
            await bot.send_message(LOG_CHANNEL, f"❌ Channel invalid: {e}")
            return

        # ============================================================
        # GENERATE CUSTOM POSTER (using poster_gen)
        # ============================================================
        poster_path = None
        try:
            rating = imdb_data.get("rating") if imdb_data else None
            year_val = year or files[0].get("year")
            genres_list = imdb_data.get("genres") if imdb_data else ["Action", "Drama"]
            duration = imdb_data.get("runtime") if imdb_data else "2H25M"
            plot = imdb_data.get("plot") if imdb_data else None

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                poster_path = tmp.name

            # Generate poster
            create_movie_poster(
                title=title,
                subtitle=kind if kind else "MOVIE",
                rating=rating,
                year=year_val,
                duration=duration,
                genres=genres_list,
                description=plot,
                output_path=poster_path,
            )
            image_url = poster_path
            print(f"✅ Custom poster generated: {poster_path}")

        except Exception as e:
            print(f"❌ Poster generation failed: {e}")
            # Fallback to default image
            image_url = "https://te.legra.ph/file/88d845b4f8a024a71465d.jpg"

        # Build and send caption
        full_caption = UPDATE_CAPTION.format(
            kind, title, year or "",
            files[0]['quality'], language, quality_text
        )

        await bot.send_photo(
            chat_id=movie_update_channel,
            photo=image_url,
            caption=full_caption,
            parse_mode=enums.ParseMode.HTML
        )

        # Cleanup temporary poster file
        if poster_path and os.path.exists(poster_path):
            try:
                os.remove(poster_path)
                print(f"🗑️ Temporary poster deleted: {poster_path}")
            except:
                pass

    except Exception as e:
        print('Failed to send movie update:', e)
        await bot.send_message(LOG_CHANNEL, f"❌ send_movie_update Error: {e}")

# -------------------------------------------------------------------
# IMDB DATA FETCH
# -------------------------------------------------------------------
async def get_imdb(file_name):
    try:
        formatted_name = await movie_name_format(file_name)
        imdb = await get_poster(formatted_name)
        if not imdb:
            return {}
        return {
            "title": imdb.get("title", formatted_name),
            "kind": imdb.get("kind", "Movie"),
            "year": imdb.get("year"),
            "rating": imdb.get("rating"),
            "genres": imdb.get("genres"),
            "runtime": imdb.get("runtime"),
            "plot": imdb.get("plot"),
            "url": imdb.get("url"),
        }
    except Exception as e:
        print(f"IMDB fetch error: {e}")
        return {}

# -------------------------------------------------------------------
# HELPER FUNCTIONS (unchanged)
# -------------------------------------------------------------------
async def get_qualities(text):
    qualities = [
        "480p", "720p", "720p HEVC", "1080p", "ORG", "org",
        "hdcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip",
        "camrip", "WEB-DL", "CAMRip", "hdtc", "predvd",
        "DVDscr", "dvdscr", "dvdrip", "HDTC", "dvdscreen", "HDTS", "hdts"
    ]
    found = [q for q in qualities if q.lower() in text.lower()]
    return ", ".join(found) or "HDRip"

async def Jisshu_qualities(text, file_name):
    qualities = ["480p", "720p", "720p HEVC", "1080p", "1080p HEVC", "2160p"]
    combined = (text.lower() + " " + file_name.lower()).strip()
    if "hevc" in combined:
        for q in qualities:
            if "HEVC" in q and q.split()[0].lower() in combined:
                return q
    for q in qualities:
        if "HEVC" not in q and q.lower() in combined:
            return q
    return "720p"

async def movie_name_format(file_name):
    filename = re.sub(
        r"http\S+", "",
        re.sub(r"@\w+|#\w+", "", file_name)
        .replace("_", " ")
        .replace("[", "").replace("]", "")
        .replace("(", "").replace(")", "")
        .replace("{", "").replace("}", "")
        .replace(".", " ")
        .replace("@", "")
        .replace(":", "").replace(";", "")
        .replace("'", "").replace("-", "").replace("!", "")
    ).strip()
    return filename

def format_file_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def generate_unique_id(movie_name):
    return hashlib.md5(movie_name.encode("utf-8")).hexdigest()[:5]
