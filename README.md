## Overflow discord bot

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://gitHub.com/janaSunrise/overflow-discord-bot/graphs/commit-activity)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](./LICENSE)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python%203.8-ffe900.svg?longCache=true&style=flat-square&colorB=00a1ff&logo=python&logoColor=88889e)](https://www.python.org/)
[![made-with-discord.py](https://img.shields.io/badge/Using-discord.py-ffde57.svg?longCache=true&style=flat-square&colorB=4584b6&logo=discord&logoColor=7289DA)](https://github.com/Rapptz/discord.py)
[![CodeFactor](https://www.codefactor.io/repository/github/janasunrise/overflow-discord-bot/badge)](https://www.codefactor.io/repository/github/janasunrise/overflow-discord-bot)
[![DeepSource](https://deepsource.io/gh/janaSunrise/overflow-discord-bot.svg/?label=active+issues&show_trend=true)](https://deepsource.io/gh/janaSunrise/overflow-discord-bot/?ref=repository-badge)

A small bot designed to help you with coding and finding and solving 
issues faster by integrating stack overflow workflow into discord and more.

### Usage
Go to any channel in discord of any server where this bot is invited, and 
invoke it using `=help`

### Developement / Contributing

If you're interested in growing this project further,
Add a .env file based on .env.example file. And add the following things:

- Grab your StackExchange key from http://stackapps.com/
- A lavalink node for the music cog
- Openweathermap API Key for the weather stuff.
- Get the nasa get at https://api.nasa.gov/
- And, the spotify credentials at https://developer.spotify.com/dashboard/

### Creating the bot on Discord

1. Create bot on Discord's [bot portal](https://discord.com/developers/applications/)
2. Make a **New Application**
3. Go to **Bot** settings and click on **Add Bot**
4. Give **Administrator** permission to bot
5. You will find your bot **TOKEN** there, it is important that you save it
6. Go to **OAuth2** and click bot, than add **Administrator** permissions
7. You can follow the link that will appear to add the bot to your discord server


## Installation

This is a guide to help you self host the Bot, and use it privately which simplifies the work, and allows you to have
a bot for yourself.

## Docker

**NOTE**: The docker is being tested and being made to worked properly. It hasn't been working perfectly yet. I advise
to use non docker steps until the docker works perfectly when deploying / running. Sorry for this inconvenience.

Docker is an easy way of containerizing and delivering your applications quickly and easily, in an 
convenient way. It's really simple to get started with this, with docker handling all the installation
and other tasks.Configure the environmental variables by renaming the `.env.example` file to `.env` with the respective 
values. Then, run `docker-compose --env-file .env up` after getting the project and config ready.

**Docker mini guide:**

- Running the bot: `docker-compose --env-file .env up`
- Stopping the bot: `docker-compose down`
- Rebuilding the bot: `docker-compose build`

### Self hosting without docker

This is a clean and neat way of hosting without using docker. You can follow this if docker doesn't work
well on your system, or it doesn't support it. Containers are resource intensive, and your PC might not
be able to do it, this is the perfect method to get started with the self-hosting.

#### Postgres

You need a postgres database configured locally to run this bot.
If you haven't done that yet, take a look at the official documentation from EDB[The company behind PG-SQL] 
[here](https://www.postgresql.org/docs/13/tutorial-install.html)

Once your done, create the databases and users accordingly, and configure it in `.env` as said in the future steps.

- Clone or fork the repository, whichever suits you better.
- Install `pipenv`, a virtual env for python. Command: **`pip install pipenv`**
- Create the virtual environment and prepare it for usage using `pipenv update`
- Configure the environmental variables by renaming the `.env.example` file to `.env` with the respective 
  values for it. If you're using heroku or other platforms that have option for external environmental
  variables, use that instead of `.env`
- Configure the options and settings available in `config.py` inside the Bot module, according to your
  preferences.
- Run the server using `pipenv run start`

## Contributing

Contributions, issues and feature requests are welcome. After cloning & setting up project locally, you 
can just submit a PR to this repo and it will be deployed once it's accepted. The contributing file can be 
found 
[here](https://github.com/janaSunrise/overflow-discord-bot/blob/main/CONTRIBUTING.md).

⚠️ It’s good to have descriptive commit messages, or PR titles so that other contributors can understand about your 
commit or the PR Created. Read [conventional commits](https://www.conventionalcommits.org/en/v1.0.0-beta.3/) 
before making the commit message.

## Show your support

We love people's support in growing and improving. Be sure to leave a ⭐️ if you like the project and 
also be sure to contribute, if you're interested!


<div align="center">
Made by Sunrit Jana with <3
</div>
