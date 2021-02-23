import textwrap
from datetime import datetime

from discord import Color, Embed
from discord.ext.commands import (
    Bot,
    BucketType,
    Cog,
    Context,
    group,
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

    @group(invoke_without_command=True)
    async def github(self, ctx: Context) -> None:
        """Commands to make github lookup really easy from discord."""
        await ctx.send_help(ctx.command)

    @github.command(aliases=["pullrequest", "pullrequests", "issues"])
    @cooldown(1, 5, type=BucketType.user)
    async def issue(self, ctx: Context, user: str, repository: str, issue_num: int) -> None:
        """Command to retrieve issues or PRs from a GitHub repository."""
        url = f"https://api.github.com/repos/{user}/{repository}/issues/{issue_num}"
        merge_url = f"https://api.github.com/repos/{user}/{repository}/pulls/{issue_num}"

        async with self.bot.session.get(url) as resp:
            json_data = await resp.json()

        if resp.status in BAD_RESPONSES:
            await ctx.send(f"ERROR: {BAD_RESPONSES.get(resp.status)}")
            return

        labels = [f"`{json_data['labels'][i]['name']}`" for i in range(len(json_data["labels"]))]
        assignees = len(json_data["assignees"])

        if "issues" in json_data.get("html_url"):
            issue_type = "issue"
            if json_data.get("state") == "open":
                title = "Issue Opened"
            else:
                title = "Issue Closed"

            description = textwrap.dedent(
                f"""
                🧿 **Info:**
                • Repository located at **{user}/{repository}**

                • {issue_type} state is {title}

                • Created by {json_data["user"]["login"]}

                • Has {json_data["comments"]} comments
                • Has {assignees} assignees.
                • {assignees} developers participated.

                🏷️ **Labels:**
                {"No labels" if len(labels) == 0 else " ".join(labels)}
                """
            )
        else:
            async with self.bot.session.get(merge_url) as merge:
                issue_type = "PR"
                if json_data.get("state") == "open":
                    title = "PR Opened"
                elif merge.status == 204:
                    title = "PR Merged"
                else:
                    title = "PR Closed"

                merge = await merge.json()

                description = textwrap.dedent(
                    f"""
                    🧿 **Info:**
                    • Repository located at **{user}/{repository}**

                    • {issue_type} state is {title}

                    • Created by {merge["user"]["login"]}

                    • Has {merge["comments"]} comments 
                    • Has {"no" if not merge["review_comments"] else merge["review_comments"]} reviews
                    • {merge["changed_files"]} Files changes, with {merge["commits"]} commits done.
                    • Changes contain {merge["additions"]} additions and {merge["deletions"]} deletions

                    🏷️ **Labels:**
                    {"No labels" if len(labels) == 0 else " ".join(labels)}
                    """
                )

        issue_url = json_data.get("html_url")
        resp = Embed(
            title=f"{json_data.get('title')} [#{issue_num}]",
            colour=Color.gold(),
            description=description,
            url=issue_url
        )
        resp.set_author(name="GitHub", url=issue_url)
        await ctx.send(embed=resp)

    @github.command(aliases=["repository"])
    @cooldown(1, 5, type=BucketType.user)
    async def repo(self, ctx: Context, user: str, repo: str) -> None:
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

    @github.command(aliases=["userinfo"])
    @cooldown(1, 5, type=BucketType.user)
    async def user(self, ctx: Context, user: str) -> None:
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
