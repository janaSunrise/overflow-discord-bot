import os

# ---- About bot section ----
COMMAND_PREFIX = "="

creator = "Sunrit Jana"
devs = [711194921683648523, 372063179557175297]

# ---- Config settings section ----

# -- Music --
nodes = {
    'MAIN': {
        'host': os.getenv("LAVALINK_HOST"),
        'port': os.getenv("LAVALINK_PORT"),
        'rest_uri': "http://" + os.getenv("LAVALINK_HOST") + ":" + os.getenv("LAVALINK_PORT"),
        'password': os.getenv("LAVALINK_PASSWORD"),
        'identifier': 'MAIN',
        'region': 'us_central'
    },
    "SUBNODE": {
        "host": "144.172.71.88",
        "port": 2444,
        "rest_uri": "http://144.172.71.88:2444",
        "password": "youshallnotpass",
        "identifier": "MAIN",
        "region": "us_central",
    }
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
    ]
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
    "snow": "https://cdn.discordapp.com/attachments/728569086174298112/735550166563684474/snowy.png"
}
