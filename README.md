## Overflow bot

A small bot designed to help you with coding and finding and solving 
issues faster by integrating stack overflow workflow into discord.

### Usage

Go to any channel in discord of any server where this bot is invited, and 
invoke it using `=help`

### Developement / Contributing

If you're interested in growing this project further,
Add a .env file based on .env.example file. Grab your StackExchange key 
from http://stackapps.com/

### Creating the bot on Discord

1. Create bot on Discord's [bot portal](https://discord.com/developers/applications/)
2. Make a **New Application**
3. Go to **Bot** settings and click on **Add Bot**
4. Give **Administrator** permission to bot
5. You will find your bot **TOKEN** there, it is important that you save it
6. Go to **OAuth2** and click bot, than add **Administrator** permissions
7. You can follow the link that will appear to add the bot to your discord server

### Running bot

1. Clone the repository (or fork it if you want to make changes)
2. Install **pipenv** `pip install pipenv`
3. Build the virtual enviroment from Pipfile.lock `pipenv sync`
4. Add a .env file based on .env.example file. Grab your StackExchange key from http://stackapps.com/
6. Run the bot `pipenv run start`

### Features planned:

- [x] Stackoverflow search.
- [ ] Music.
- [ ] Hacker news.
- [ ] Scheduled hacker news on guild basis.
- [ ] Code execution.

### Credits

Credits for the code execution and the API requests goes to [Engineer Man](https://github.com/engineer-man)
and [his repo](https://github.com/engineer-man/piston) for safe code eval without any issues.

Made by Sunrit Jana with <3
