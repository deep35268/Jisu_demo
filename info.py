import re
from os import environ
from Script import script

id_pattern = re.compile(r"^.\d+$")


def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


# Main
SESSION = environ.get("SESSION", "Media_search")
API_ID = int(environ.get("API_ID", "25625749"))
API_HASH = environ.get("API_HASH", "1b4a47426f1189e4c406057be9735e3b")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
PORT = environ.get("PORT", "8082")

# Owners
ADMINS = [
    int(admin) if id_pattern.search(admin) else admin
    for admin in environ.get("ADMINS", "6467566398").split()
]
OWNER_USERNAME = environ.get(
    "OWNER_USERNAME", "Deep2213k"
)  # without @ or https://t.me/
USERNAME = environ.get("USERNAME", "Deep2213k")  # ADMIN USERNAME

# Database Channel
CHANNELS = [
    int(ch) if id_pattern.search(ch) else ch
    for ch in environ.get("CHANNELS", "-1003954712996").split()
]

# 🆕 **BIN_CHANNEL (Streaming/Download ਲਈ ਜ਼ਰੂਰੀ)**
BIN_CHANNEL = int(environ.get("BIN_CHANNEL", "-1002160542554"))

# ForceSub Channel & Log Channels
AUTH_CHANNEL = int(environ.get("AUTH_CHANNEL", "-1002545890634"))
AUTH_REQ_CHANNEL = int(environ.get("AUTH_REQ_CHANNEL", "-1002290453638"))
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1002427494480"))
LOG_API_CHANNEL = int(environ.get("LOG_API_CHANNEL", "-1002427494480"))
LOG_VR_CHANNEL = int(environ.get("LOG_VR_CHANNEL", "-1002160542554"))

# MongoDB
DATABASE_URI = environ.get("DATABASE_URI", "mongodb+srv://xewena6452:OFhJE1WmM2wG10xs@cluster0.gvum06n.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = environ.get("DATABASE_NAME", "Cluster0")

# Files index database url
FILES_DATABASE = environ.get("FILES_DATABASE", "mongodb+srv://xewena6452:OFhJE1WmM2wG10xs@cluster0.gvum06n.mongodb.net/?retryWrites=true&w=majority")
COLLECTION_NAME = environ.get("COLLECTION_NAME", "jisshu")

# Other Channel's
SUPPORT_GROUP = int(environ.get("SUPPORT_GROUP", "-1002216002151"))
DELETE_CHANNELS = int(environ.get("DELETE_CHANNELS", "-1002479259622"))
request_channel = environ.get("REQUEST_CHANNEL", "-1002290453638")
REQUEST_CHANNEL = (
    int(request_channel)
    if request_channel and id_pattern.search(request_channel)
    else None
)
MOVIE_UPDATE_CHANNEL = int(environ.get("MOVIE_UPDATE_CHANNEL", "-1002677282300"))

# Added Link Here Not Id
SUPPORT_CHAT = environ.get("SUPPORT_CHAT", "https://t.me/Ownersupport")
MOVIE_GROUP_LINK = environ.get("MOVIE_GROUP_LINK", "https://t.me/Moviesrequst01")

# Verification
IS_VERIFY = is_enabled("IS_VERIFY", True)
# ---------------------------------------------------------------
TUTORIAL = environ.get("TUTORIAL", "https://t.me/HOWTO61")
TUTORIAL_2 = environ.get("TUTORIAL_2", "https://t.me/HOWTO61")
TUTORIAL_3 = environ.get("TUTORIAL_3", "https://t.me/HOWTO61")
VERIFY_IMG = environ.get(
    "VERIFY_IMG", "https://graph.org/file/1669ab9af68eaa62c3ca4.jpg"
)
SHORTENER_API = environ.get("SHORTENER_API", "7709a824575640328a543091da04875a63be6d95")
SHORTENER_WEBSITE = environ.get("SHORTENER_WEBSITE", "shortxlinks.com")
SHORTENER_API2 = environ.get(
    "SHORTENER_API2", "7709a824575640328a543091da04875a63be6d95"
)
SHORTENER_WEBSITE2 = environ.get("SHORTENER_WEBSITE2", "shortxlinks.com")
SHORTENER_API3 = environ.get(
    "SHORTENER_API3", "7709a824575640328a543091da04875a63be6d95"
)
SHORTENER_WEBSITE3 = environ.get("SHORTENER_WEBSITE3", "shortxlinks.com")
TWO_VERIFY_GAP = int(environ.get("TWO_VERIFY_GAP", "75600"))
THREE_VERIFY_GAP = int(environ.get("THREE_VERIFY_GAP", "75900"))

# Language & Quality & Season & Year
LANGUAGES = [
    "hindi",
    "english",
    "telugu",
    "tamil",
    "kannada",
    "malayalam",
    "bengali",
    "marathi",
    "gujarati",
    "punjabi",
    "marathi",
]
QUALITIES = [
    "HdRip",
    "web-dl",
    "bluray",
    "hdr",
    "fhd",
    "240p",
    "360p",
    "480p",
    "540p",
    "720p",
    "960p",
    "1080p",
    "1440p",
    "2K",
    "2160p",
    "4k",
    "5K",
    "8K",
]
YEARS = [f"{i}" for i in range(2025, 2002, -1)]
SEASONS = [f"season {i}" for i in range(1, 23)]

# Pictures And Reaction
START_IMG = (
    environ.get(
        "START_IMG",
        "https://telegra.ph/file/5ed708a888f16dd039358.jpg",
    )
).split()
FORCESUB_IMG = environ.get("FORCESUB_IMG", "https://i.ibb.co/ZNC1Hnb/ad3f2c88a8f2.jpg")
REFER_PICS = (environ.get("REFER_PICS", "https://envs.sh/PSI.jpg")).split()
PAYPICS = (
    environ.get("PAYPICS", "https://iili.io/KQ4BhIS.md.jpg")
).split()
SUBSCRIPTION = environ.get(
    "SUBSCRIPTION", "https://i.imgur.com/f7rjBLp.jpeg"
)
REACTIONS = ["👀", "😱", "🔥", "😍", "🎉", "🥰", "😇", "⚡"]


# Other Funtions
FILE_AUTO_DEL_TIMER = int(environ.get("FILE_AUTO_DEL_TIMER", "300"))
AUTO_FILTER = is_enabled("AUTO_FILTER", True)
IS_PM_SEARCH = is_enabled("IS_PM_SEARCH", True)
IS_SEND_MOVIE_UPDATE = is_enabled(
    "IS_SEND_MOVIE_UPDATE", True
)  # Don't Change It ( If You Want To Turn It On Then Turn It On By Commands) We Suggest You To Make It Turn Off If You Are Indexing Files First Time.
MAX_BTN = int(environ.get("MAX_BTN", "8"))
AUTO_DELETE = is_enabled("AUTO_DELETE", True)
DELETE_TIME = int(environ.get("DELETE_TIME", 1200))
IMDB = is_enabled("IMDB", False)
FILE_CAPTION = environ.get("FILE_CAPTION", f"{script.FILE_CAPTION}")
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
LONG_IMDB_DESCRIPTION = is_enabled("LONG_IMDB_DESCRIPTION", False)
PROTECT_CONTENT = is_enabled("PROTECT_CONTENT", False)
SPELL_CHECK = is_enabled("SPELL_CHECK", True)
LINK_MODE = is_enabled("LINK_MODE", True)
TMDB_API_KEY = environ.get("TMDB_API_KEY", "e6449037b5c9edb30f0e4b92c3789429")

# Online Streaming And Download
STREAM_MODE = bool(environ.get("STREAM_MODE", True))  # Set True or Flase

MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get("SLEEP_THRESHOLD", "60"))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if "DYNO" in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False

# 🔴 **ਸਭ ਤੋਂ ਜ਼ਰੂਰੀ ਬਦਲਾਅ - URL ਨੂੰ ਆਪਣੇ Render App URL ਨਾਲ ਬਦਲੋ**
URL = environ.get("URL", "https://your-render-app-name.onrender.com/")  # ⚠️ "your-render-app-name" ਨੂੰ ਆਪਣੇ Render App ਦੇ ਨਾਮ ਨਾਲ ਬਦਲੋ

# Commands
admin_cmds = [
    "/add_premium - Add A User To Premium",
    "/premium_users - View All Premium Users",
    "/remove_premium - Remove A User's Premium Status",
    "/add_redeem - Generate A Redeem Code",
    "/refresh - Refresh Free Trail",
    "/set_muc - Set Movie Update Channel",
    "/pm_search_on - Enable PM Search",
    "/pm_search_off - Disable PM Search",
    "/set_ads - Set Advertisements",
    "/del_ads - Delete Advertisements",
    "/setlist - Set Top Trending List",
    "/clearlist - Clear Top Trending List",
    "/verify_id - Verification Off ID",
    "/index - Index Files",
    "/send - Send Message To A User",
    "/leave - Leave A Group Or Channel",
    "/ban - Ban A User",
    "/unban - Unban A User",
    "/broadcast - Broadcast Message",
    "/grp_broadcast - Broadcast Messages To Groups",
    "/delreq - Delete Join Request",
    "/channel - List Of Database Channels",
    "/del_file - Delete A Specific File",
    "/delete - Delete A File(By Reply)",
    "/deletefiles - Delete Multiple Files",
    "/deleteall - Delete All Files",
]

cmds = [
    {"start": "Start The Bot"},
    {"most": "Get Most Searches Button List"},
    {"trend": "Get Top Trending Button List"},
    {"mostlist": "Show Most Searches List"},
    {"trendlist": "𝖦𝖾𝗍 𝖳𝗈𝗉 𝖳𝗋𝖾𝗇𝖽𝗂𝗇𝗀 𝖡𝗎𝗍𝗍𝗈𝗇 𝖫𝗂𝗌t"},
    {"plan": "Check Available Premium Membership Plans"},
    {"myplan": "Check Your Currunt Plan"},
    {"refer": "To Refer Your Friend And Get Premium"},
    {"stats": "Check My Database"},
    {"id": "Get Telegram Id"},
    {"font": "To Generate Cool Fonts"},
    {"details": "Check Group Details"},
    {"settings": "Change Bot Setting"},
    {"grp_cmds": "Check Group Commands"},
    {"admin_cmds": "Bot Admin Commands"},
]
