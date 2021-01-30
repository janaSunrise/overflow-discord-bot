import textwrap
from datetime import datetime

from discord import Color, Embed
from discord.ext.commands import (
    Bot,
    BucketType,
    Cog,
    Context,
    command,
    cooldown
)

BAD_RESPONSES = {
    404: "Issue/pull request not Found! Please enter a valid PR Number!",
    403: "Rate limit is hit! Please try again later!"
}


class Github(Cog):
    """
    Add GitHub integration to the bot.

    **This command uses the GitHub API and is limited to 1 use per 5 seconds to comply with the rules.**
    """
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(aliases=["pullrequest", "pullrequests", "issues"])
    @cooldown(1, 5, type=BucketType.user)
    async def issue(self, ctx: Context, issue_num: int, repository: str, user: str) -> None:
        """Command to retrieve issues or PRs from a GitHub repository."""
        url = f"https://api.github.com/repos/{user}/{repository}/issues/{issue_num}"
        merge_url = f"https://api.github.com/repos/{user}/{repository}/pulls/{issue_num}/merge"

        async with self.bot.session.get(url) as resp:
            json_data = await resp.json()

        if resp.status in BAD_RESPONSES:
            await ctx.send(f"ERROR: {BAD_RESPONSES.get(resp.status)}")
            return

        if "issues" in json_data.get("html_url"):
            if json_data.get("state") == "open":
                title = "Issue Opened"
            else:
                title = "Issue Closed"
        else:
            async with self.bot.session.get(merge_url) as merge:
                if json_data.get("state") == "open":
                    title = "PR Opened"
                elif merge.status == 204:
                    title = "PR Merged"
                else:
                    title = "PR Closed"

        issue_url = json_data.get("html_url")
        resp = Embed(
            title=f"{title}",
            colour=Color.gold(),
            description=textwrap.dedent(
                f"""
                Repository : **{user}/{repository}**

                Title : **{json_data.get('title')}**
                ID : **`{issue_num}`**

                Link :  [Here]({issue_url})
                """
            )
        )
        resp.set_author(name="GitHub", url=issue_url)
        await ctx.send(embed=resp)

    @command()
    @cooldown(1, 5, type=BucketType.user)
    async def ghrepo(self, ctx: Context, user: str, repo: str) -> None:
        """Show info about a given GitHub repository."""
        URL = f"https://api.github.com/repos/{user}/{repo}"

        embed = Embed(color=Color.blue())

        # Fetching the data

        async with await self.bot.session.get(f"https://api.github.com/repos/{user}/{repo}") as resp:
            response = await resp.json()

        async with await self.bot.session.get(f"https://api.github.com/repos/{user}/{repo}/languages") as resp:
            json = await resp.json()
            languages = len(json)

        if resp.status in BAD_RESPONSES:
            await ctx.send(f"ERROR: {BAD_RESPONSES.get(resp.status)}")
            return

        try:
            if response["message"]:
                await ctx.send(f"ERROR: {response['message']}")
        except KeyError:

            if response["description"] == "":
                desc = "No description provided."
            else:
                desc = response["description"]

            description = textwrap.dedent(
                f"""
                📄 **Description:**
                ```
                {desc}
                ```

                🧿 **Info:**
                • Created on {datetime.strptime(response["created_at"],"%Y-%m-%dT%H:%M:%SZ")}

                • Has been starred {response["stargazers_count"]} times.
                • Has been forked {response["forks_count"]} times.
                
                • Written in {response["language"]} among {languages} languages.
                • Uses {response["license"]["name"]}.
                
                • Use this command to fork:
                **`git clone {response["clone_url"]}`**
                """
            )

            embed.title = f"{repo} on GitHub"
            embed.url = response["html_url"]
            embed.description = description
            embed.set_thumbnail(url=response["owner"]["avatar_url"])

            await ctx.send(embed=embed)

    @command()
    @cooldown(1, 5, type=BucketType.user)
    async def ghuser(self, ctx: Context, user: str) -> None:
        """Show info about a given GitHub user."""
        embed = Embed(color=Color.blue())
        async with await self.bot.session.get(f"https://api.github.com/users/{user}") as resp:
            response = await resp.json()

        if resp.status in BAD_RESPONSES:
            await ctx.send(f"ERROR: {BAD_RESPONSES.get(resp.status)}")
            return

        try:
            if response["message"]:
                await ctx.send(f"ERROR: {response['message']}")
        except KeyError:
            description = textwrap.dedent(
                f"""
                📄 **Description:**
                • He/She is {"No Name!" if not response["name"] else response["name"]}
                ```
                {"No Bio!" if not response["bio"] else response["bio"]}
                ```

                🧿 **Info:**
                • Created on {datetime.strptime(response["created_at"],"%Y-%m-%dT%H:%M:%SZ")}

                • Owns {response["public_repos"]} repositories.

                • Has been followed by {response["followers"]} developers.
                • Loves to follow {response["following"]} developers
                
                {"" if not response["location"] else f"• Located in {response['location']}"}

                {"" if not response["company"] else f"• Works at {response['company']}"}

                🔗 **Links:**
                {"" if response["blog"] == "" else f"• Has a site or blog at {response['blog']}"}
                {
                "" if not response["twitter_username"] 
                   else f"• Twitter handle is https://twitter.com/{response['twitter_username']}"
                }
                """
            )

            embed.title = f"{user} on Github"
            embed.url = response["html_url"]
            embed.description = description
            embed.set_thumbnail(url=response["avatar_url"])

            await ctx.send(embed=embed)
