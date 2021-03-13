import os
import re

# ---- About bot section ----
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "=")

branding = "Overflow bot"
creator = "Sunrit Jana"
devs = [711194921683648523, 372063179557175297]

# ---- Config settings section ----
# -- Database config --
DATABASE = {
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "hostname": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}
# Syntax: "postgresql+asyncpg://<user>:<password>@<hostname>/<dbname>"
DATABASE_CONN = (
    f"postgresql+asyncpg://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['hostname']}"
    f"/{DATABASE['database']}"
)

# -- Logger configuration --
log_file = "logs/bot.log"
log_level = "INFO"
log_format = (
    "<green>{time:YYYY-MM-DD hh:mm:ss}</green> | <level>{level: <8}</level> | "
    "<cyan>{name: <18}</cyan> | <level>{message}</level>"
)
log_file_size = "400 MB"

# -- Music --
nodes = {
    "MAIN": {
        "host": os.getenv("LAVALINK_HOST"),
        "port": os.getenv("LAVALINK_PORT"),
        "rest_uri": "http://"
        + os.getenv("LAVALINK_HOST")
        + ":"
        + os.getenv("LAVALINK_PORT"),
        "password": os.getenv("LAVALINK_PASSWORD"),
        "identifier": "MAIN",
        "region": "us_central",
    },
    "NODE_1": {
        "host": "144.172.71.88",
        "port": 2444,
        "rest_uri": "http://144.172.71.88:2444",
        "password": "youshallnotpass",
        "identifier": "NODE_1",
        "region": "us_central",
    },
}

# -- Spotify --
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# -- 8ball response --
BALL_REPLIES = {
    "positive": [
        "Yep.",
        "Absolutely!",
        "Can do!",
        "Affirmative!",
        "Yeah okay.",
        "Sure.",
        "Sure thing!",
        "You're the boss!",
        "Okay.",
        "No problem.",
        "I got you.",
        "Alright.",
        "You got it!",
        "ROGER THAT",
        "Of course!",
        "Aye aye, cap'n!",
        "I'll allow it.",
        "Yea, for sure!",
    ],
    "negative": [
        "Noooooo!!",
        "Nope.",
        "I'm sorry Dave, I'm afraid I can't do that.",
        "I don't think so.",
        "Not gonna happen.",
        "Out of the question.",
        "Huh? No.",
        "Nah.",
        "Naw.",
        "Not likely.",
        "No way, José.",
        "Not in a million years.",
        "Fat chance.",
        "Certainly not.",
        "NEGATORY.",
        "Nuh-uh.",
        "Not in my house!",
    ],
    "error": [
        "Please don't do that.",
        "You have to stop.",
        "Do you mind?",
        "In the future, don't do that.",
        "That was a mistake.",
        "You blew it.",
        "You're bad at computers.",
        "Are you trying to kill me?",
        "Noooooo!!",
        "I can't believe you've done this",
    ],
}

# -- Search --
basic_search_categories = [
    "web",
    "videos",
    "music",
    "files",
    "images",
    "it",
    "maps",
]

# -- Study --
RESPONSES = {
    200: True,
    301: "Switching to a different endpoint",
    400: "Bad Request",
    401: "Not Authenticated",
    404: "The resource you tried to access wasn't found on the server.",
    403: "The resource you’re trying to access is forbidden — you don’t have the right permissions to see it.",
}


# ---- Cogs resource section ----
WEATHER_ICONS = {
    "wind": "https://cdn.discordapp.com/attachments/728569086174298112/735550169222873118/windy.png",
    "rain": "https://cdn.discordapp.com/attachments/728569086174298112/735550164458274947/raining.png",
    "sun": "https://cdn.discordapp.com/attachments/728569086174298112/735550167859593306/sunny.png",
    "cloud": "https://cdn.discordapp.com/attachments/728569086174298112/735550159781494865/cloudy.png",
    "partly": "https://cdn.discordapp.com/attachments/728569086174298112/735550162721701979/partly.png",
    "snow": "https://cdn.discordapp.com/attachments/728569086174298112/735550166563684474/snowy.png",
}

# -- Swear filter --
with open("bot/assets/filter_words.txt", "r") as f:
    filter_words = f.readlines()

REGEXP = ""
for filter_word in filter_words:
    filter_word = filter_word.replace("\n", "")
    REGEXP += f"{filter_word}|"
REGEXP = REGEXP[:-1]

filter_words = re.compile(REGEXP, re.I)

# -- Reddit config --
# -- Subreddit config --
subreddits_list = {
    "memes": (
        "ComedyCemetery",
        "dankmemes",
        "DeepFriedMemes",
        "funny",
        "meirl",
        "memes",
        "wholesomememes",
    ),
    "funny": (
        "BeAmazed",
        "blackmagicfuckery",
        "cursedimages",
        "fakehistoryporn",
        "gifsthatkeepongiving",
        "hmmm",
        "mildlyinteresting",
        "MurderedByWords",
        "nevertellmetheodds",
        "nostalgia",
        "OldSchoolCool",
        "reactiongifs",
        "Unexpected",
        "WatchPeopleDieInside",
    ),
    "aww": (
        "AnimalsBeingJerks",
        "guineapigs",
        "NatureIsFuckingLit",
        "natureismetal",
        "Rabbits",
        "StartledCats",
        "WhatsWrongWithYourDog",
    ),
    "nsfw": (
        "2busty2hide",
        "amateur",
        "AsiansGoneWild",
        "Ass",
        "BigAsses",
        "BigBoobsGW",
        "boobies",
        "boobs",
        "breakingtheseal",
        "breastenvy",
        "BustyPetite",
        "camsluts",
        "collegesluts",
        "cumsluts",
        "curvy",
        "dirtysmall",
        "fauxbait",
        "funwithfriends",
        "GirlsFinishingTheJob",
        "godpussy",
        "goneerotic",
        "gonewild",
        "gonewild18",
        "gonewild30plus",
        "gonewildcouples",
        "gonewildcurvy",
        "GoneWildScrubs",
        "gwcumsluts",
        "gwpublic",
        "hairypussy",
        "holdthemoan",
        "hotwife",
        "hugeboobs",
        "impressedbycum",
        "indiansgonewild",
        "innie",
        "iWantToFuckHer",
        "LabiaGW",
        "lactation",
        "latinasgw",
        "LegalTeens",
        "legalteens",
        "legs",
        "milf",
        "mycleavage",
        "nipples",
        "nsfw",
        "nsfw_amateurs",
        "NSFW_GIF",
        "NSFW_GIFS",
        "NSFW_HTML5",
        "NSFW_Snapchat",
        "OnOff",
        "peegonewild",
        "petite",
        "PetiteGoneWild",
        "pokies",
        "pussy",
        "ratemynudebody",
        "RealGirls",
        "realgirls",
        "realmoms",
        "SexyTummies",
        "SlimThick",
        "slutwife",
        "snapleaks",
        "stacked",
        "stockings",
        "streamersgonewild",
        "thick",
        "tightshorts",
        "tits",
        "wetfetish",
        "wifesharing",
        "workgonewild",
        "wouldyoufuckmywife",
        "yogapants",
    ),
    "sci": (
        "askscience",
        "Physics",
        "shittyrobots",
        "chemicalreactiongifs",
        "chemistry",
        "nasa",
        "EverythingScience",
        "spaceporn",
    ),
}

nsfw_subreddits_list = {
    "fourk": [
        "HighResNSFW",
        "UHDnsfw",
        "nsfw_hd",
        "NSFW_Wallpapers",
        "closeup"
    ],
    "ahegao": [
        "AhegaoGirls",
        "RealAhegao",
        "EyeRollOrgasm",
        "MouthWideOpen",
        "O_Faces"
    ],
    "ass": [
        "ass",
        "pawg",
        "AssholeBehindThong",
        "girlsinyogapants",
        "girlsinleggings",
        "bigasses",
        "asshole",
        "AssOnTheGlass",
        "TheUnderbun",
        "asstastic",
        "booty",
        "AssReveal",
        "beautifulbutt",
        "Mooning",
        "BestBooties",
        "brunetteass",
        "assinthong",
        "paag",
        "asstastic",
        "GodBooty",
        "Underbun",
        "datass",
        "ILikeLittleButts",
        "datgap"
    ],
    "anal": [
        "MasterOfAnal",
        "analgonewild",
        "anal",
        "buttsex",
        "buttsthatgrip",
        "AnalGW",
        "analinsertions",
        "AnalGW",
        "assholegonewild"
    ],
    "bdsm": [
        "BDSMGW",
        "bdsm",
        "ropeart",
        "shibari"
    ],
    "blowjob": [
        "blowjobsandwich",
        "Blowjobs",
        "BlowjobGifs",
        "BlowjobEyeContact",
        "blowbang",
        "AsianBlowjobs",
        "SuckingItDry",
        "OralCreampie",
        "SwordSwallowers"
    ],
    "boobs": [
        "boobs",
        "TheHangingBoobs",
        "bigboobs",
        "BigBoobsGW",
        "hugeboobs",
        "pokies",
        "ghostnipples",
        "PiercedNSFW",
        "piercedtits",
        "PerfectTits",
        "BestTits",
        "Boobies",
        "JustOneBoob",
        "tits",
        "naturaltitties",
        "smallboobs",
        "Nipples",
        "homegrowntits",
        "TheUnderboob",
        "BiggerThanYouThought",
        "fortyfivefiftyfive",
        "Stacked",
        "BigBoobsGonewild",
        "AreolasGW",
        "TittyDrop",
        "Titties",
        "Boobies",
        "boobbounce",
        "TinyTits",
        "cleavage",
        "BoobsBetweenArms",
        "BustyNaturals",
        "burstingout"
    ],
    "cunnilingus": [
        "cunnilingus",
        "CunnilingusSelfie",
        "Hegoesdown"
    ],
    "bottomless": [
        "upskirt",
        "Bottomless",
        "nopanties",
        "Pantiesdown"
    ],
    "cumshots": [
        "OralCreampie",
        "cumfetish",
        "cumontongue",
        "cumshots",
        "CumshotSelfies",
        "facialcumshots",
        "pulsatingcumshots",
        "gwcumsluts",
        "ImpresssedByCum",
        "GirlsFinishingTheJob",
        "amateurcumsluts",
        "unexpectedcum",
        "bodyshots",
        "ContainTheLoad",
        "bodyshots"
    ],
    "dick": [
        "DickPics4Freedom",
        "mangonewild",
        "MassiveCock",
        "penis",
        "cock",
        "ThickDick"
    ],
    "doublepenetration": [
        "doublepenetration",
        "dp_porn",
        "Technical_DP"
    ],
    "deepthroat": [
        "DeepThroatTears",
        "deepthroat",
        "SwordSwallowers"
    ],
    "gay": [
        "gayporn",
        "ladybonersgw",
        "mangonewild"
    ],
    "group": [
        "GroupOfNudeGirls",
        "GroupOfNudeMILFs",
        "groupsex"
    ],
    "hentai": [
        "hentai",
        "thick_hentai",
        "HQHentai",
        "AnimeBooty",
        "thighdeology",
        "ecchigifs",
        "nsfwanimegifs",
        "oppai_gif"
    ],
    "lesbian": [
        "lesbians",
        "HDLesbianGifs",
        "amateurlesbians",
        "Lesbian_gifs"
    ],
    "milf": [
        "amateur_milfs",
        "GroupOfNudeMILFs",
        "ChocolateMilf",
        "milf",
        "Milfie",
        "hairymilfs",
        "HotAsianMilfs",
        "HotMILFs",
        "MILFs",
        "maturemilf",
        "puremilf",
        "amateur_milfs"
    ],
    "public": [
        "RealPublicNudity",
        "FlashingAndFlaunting",
        "FlashingGirls",
        "PublicFlashing",
        "Unashamed",
        "NudeInPublic",
        "publicplug",
        "casualnudity"
    ],
    "rule34": [
        "rule34",
        "rule34cartoons",
        "Rule_34",
        "Rule34LoL",
        "AvatarPorn",
        "Overwatch_Porn",
        "Rule34Overwatch",
        "WesternHentai"
    ],
    "thigh": [
        "Thighs",
        "ThickThighs",
        "thighhighs",
        "Thigh",
        "leggingsgonewild"
    ],
    "trap": [
        "Transex",
        "DeliciousTraps",
        "traps",
        "trapgifs",
        "GoneWildTrans",
        "SexyShemales",
        "Shemales",
        "shemale_gifs",
        "Shemales",
        "ShemalesParadise",
        "Shemale_Big_Cock",
        "ShemaleGalleries"
    ],
    "wild": [
        "gonewild",
        "GWNerdy",
        "dirtysmall",
        "MyCalvins",
        "AsiansGoneWild",
        "GoneWildSmiles",
        "gonewildcurvy",
        "BigBoobsGonewild",
        "gonewildcouples",
        "gonewildcolor",
        "PetiteGoneWild",
        "GWCouples",
        "BigBoobsGW",
        "altgonewild",
        "LabiaGW",
        "UnderwearGW",
        "JustTheTop",
        "TallGoneWild",
        "LingerieGW",
        "Swingersgw",
        "workgonewild"
    ],
    "redhead": [
        "redheadxxx",
        "redheads",
        "ginger",
        "FireBush",
        "FreckledRedheads",
        "redhead",
        "thesluttyginger",
        "RedheadGifs"
    ]
}
