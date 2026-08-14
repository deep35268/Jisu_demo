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

# 🆕 Import the poster generator
from poster_gen import create_movie_poster

CAPTION_LANGUAGES = [
    "Bhojpuri",
    "Hindi",
    "Bengali",
    "Tamil",
    "English",
    "Bangla",
    "Telugu",
    "Malayalam",
    "Kannada",
    "Marathi",
    "Punjabi",
    "Bengoli",
    "Gujrati",
    "Korean",
    "Gujarati",
    "Spanish",
    "French",
    "German",
    "Chinese",
    "Arabic",
    "Portuguese",
    "Russian",
    "Japanese",
    "Odia",
    "Assamese",
    "Urdu",
]

UPDATE_CAPTION = """<b>𝖭𝖤𝖶 {} 𝖠𝖣𝖣𝖤𝖣 ✅</b>

🎬 <b>{} {}</b>
🔰 <b>Quality:</b> {}
🎧 <b>Audio:</b> {}

<b>✨ Telegram Files ✨</b>

{}

<blockquote>〽️ Powered by @Backupsk01</b></blockquote>"""

QUALITY_CAPTION = """📦 {} : {}\n"""

notified_movies = set()
movie_files = defaultdict(list)
POST_DELAY = 10
processing_movies = set()

media_filter = filters.document | filters.video | filters.audio


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


async def queue_movie_file(bot, media):
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
            ", ".join(
                [lang for lang in CAPTION_LANGUAGES if lang.lower() in caption.lower()]
            )
            or "Not Idea"
        )
        file_size_str = format_file_size(media.file_size)
        file_id, file_ref = unpack_new_file_id(media.file_id)
        movie_files[file_name].append(
            {
                "quality": quality,
                "jisshuquality": jisshuquality,
                "file_id": file_id,
                "file_size": file_size_str,
                "caption": caption,
                "language": language,
                "year": year,
            }
        )
        if file_name in processing_movies:
            return
        processing_movies.add(file_name)
        try:
            await asyncio.sleep(POST_DELAY)
            if file_name in movie_files:
                await send_movie_update(bot, file_name, movie_files[file_name])
                del movie_files[file_name]
        finally:
            processing_movies.remove(file_name)
    except Exception as e:
        print(f"Error in queue_movie_file: {e}")
        if file_name in processing_movies:
            processing_movies.remove(file_name)
        await bot.send_message(LOG_CHANNEL, f"Failed to send movie update. Error - {e}'\n\n<blockquote>If you don’t understand this error, you can ask in our support group: @Jisshu_support.</blockquote>")


async def send_movie_update(bot, file_name, files):
    try:
        if file_name in notified_movies:
            return
        notified_movies.add(file_name)

        imdb_data = await get_imdb(file_name)
        title = imdb_data.get("title", file_name)
        year_match = re.search(r"\b(19|20)\d{2}\b", file_name)
        year = year_match.group(0) if year_match else None
        kind = imdb_data.get("kind", "").strip().upper().replace(" ", "_") if imdb_data else ""
        if kind == "TV_SERIES":
           kind = "SERIES"
        languages = set()
        for file in files:
            if file["language"] != "Not Idea":
                languages.update(file["language"].split(", "))
        language = ", ".join(sorted(languages)) or "Not Idea"

        # ---------- QUALITY AND BUTTONS LOGIC (your existing code) ----------
        episode_pattern = re.compile(r"S(\d{1,2})E(\d{1,2})", re.IGNORECASE)
        combined_pattern = re.compile(r"S(\d{1,2})\s*E(\d{1,2})[-~]E?(\d{1,2})", re.IGNORECASE)
        episode_map = defaultdict(dict)
        combined_links = []

        for file in files:
            caption = file["caption"]
            quality = file.get("jisshuquality") or file.get("quality") or "Unknown"
            size = file["file_size"]
            file_id = file['file_id']
            match = episode_pattern.search(caption)
            combined_match = combined_pattern.search(caption)

            if match:
                ep = f"S{int(match.group(1)):02d}E{int(match.group(2)):02d}"
                episode_map[ep][quality] = file
            elif combined_match:
                season = f"S{int(combined_match.group(1)):02d}"
                ep_range = f"E{int(combined_match.group(2)):02d}-{int(combined_match.group(3)):02d}"
                ep = f"{season}{ep_range}"
                combined_links.append(f"📦 {ep} ({quality}) : <a href='https://t.me/{temp.U_NAME}?start=file_0_{file_id}'>{size}</a>")
            elif re.search(r"complete|completed|batch|combined", caption, re.IGNORECASE):
                combined_links.append(f"📦 ({quality}) : <a href='https://t.me/{temp.U_NAME}?start=file_0_{file_id}'>{size}</a>")

        quality_text = ""

        for ep, qualities in sorted(episode_map.items()):
            parts = []
            for quality in sorted(qualities.keys()):
                f = qualities[quality]
                link = f"<a href='https://t.me/{temp.U_NAME}?start=file_0_{f['file_id']}'>{quality}</a>"
                parts.append(link)
            joined = " - ".join(parts)
            quality_text += f"📦 {ep} : {joined}\n"

        if combined_links:
            quality_text += "\n<b>COMBiNED</b> ✅\n\n"
            quality_text += "\n".join(combined_links) + "\n"
            
        if not quality_text:
            quality_groups = defaultdict(list)
            for file in files:
                quality = file.get("jisshuquality") or file.get("quality") or "Unknown"
                quality_groups[quality].append(file)

            for quality, q_files in sorted(quality_groups.items()):
                links = [f"<a href='https://t.me/{temp.U_NAME}?start=file_0_{f['file_id']}'>{f['file_size']}</a>" for f in q_files]
                line = f"📦 {quality} : " + " | ".join(links)
                quality_text += line + "\n"

        movie_update_channel = await db.movies_update_channel_id()
        if not movie_update_channel:
            movie_update_channel = MOVIE_UPDATE_CHANNEL

        # ✅ FIX: PEER_ID_INVALID Error
        try:
            await bot.get_chat(movie_update_channel)
        except Exception as e:
            print(f"Chat {movie_update_channel} not accessible: {e}")
            return

        # ============================================================
        # 🆕 GENERATE CUSTOM POSTER INSTEAD OF FETCHING FROM EXTERNAL API
        # ============================================================
        try:
            # Extract necessary details from imdb_data or fallback
            rating = imdb_data.get("rating") if imdb_data else None
            year_val = year or files[0].get("year")
            genres_list = imdb_data.get("genres") if imdb_data else []
            duration = imdb_data.get("runtime") if imdb_data else "2H25M"
            plot = imdb_data.get("plot") if imdb_data else None

            # If genres list is empty, use some default or leave empty
            if not genres_list:
                genres_list = ["Action", "Drama"]

            # Create a temporary file for the poster
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                poster_path = tmp.name

            # Generate the poster using our function
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
            image_url = poster_path   # use generated image
            print(f"✅ Custom poster generated: {poster_path}")

        except Exception as e:
            print(f"❌ Poster generation failed: {e}")
            # Fallback to default poster
            image_url = "https://te.legra.ph/file/88d845b4f8a024a71465d.jpg"

        full_caption = UPDATE_CAPTION.format(kind, title, year, files[0]['quality'], language, quality_text)

        # Send the photo with the generated poster
        await bot.send_photo(
            chat_id=movie_update_channel,
            photo=image_url,
            caption=full_caption,
            parse_mode=enums.ParseMode.HTML
        )

        # Clean up temporary file if it was created
        if image_url and image_url != "https://te.legra.ph/file/88d845b4f8a024a71465d.jpg":
            try:
                os.remove(image_url)
                print(f"🗑️ Temporary poster deleted: {image_url}")
            except:
                pass

    except Exception as e:
        print('Failed to send movie update. Error - ', e)
        await bot.send_message(LOG_CHANNEL, f"Failed to send movie update. Error - {e}'\n\n<blockquote>If you don’t understand this error, you can ask in our support group: @Jisshu_support.</blockquote>")


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
            "rating": imdb.get("rating"),         # 🆕
            "genres": imdb.get("genres"),         # 🆕
            "runtime": imdb.get("runtime"),       # 🆕
            "plot": imdb.get("plot"),             # 🆕
            "url": imdb.get("url"),
        }
    except Exception as e:
        print(f"IMDB fetch error: {e}")
        return {}

# The rest functions (fetch_movie_poster, generate_unique_id, get_qualities, Jisshu_qualities, movie_name_format, format_file_size) remain unchanged.
# We remove fetch_movie_poster as we no longer use it, but keep it if needed for fallback.
# For cleanliness, we can keep it but we are not calling it.
