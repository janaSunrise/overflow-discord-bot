import os

# ---- About bot section ----
creator = "Sunrit Jana"
devs = [711194921683648523, 372063179557175297]

COMMAND_PREFIX = "="

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
    'BACKUP': {
        'host': 'katrina.qub.io',
        'port': 2333,
        'rest_uri': 'http://katrina.qub.io:2333',
        'password': 'terribleconsequences',
        'identifier': 'BACKUP',
        'region': 'us_central'
    }
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
