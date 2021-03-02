import json
import typing as t
from contextlib import suppress

import discord


async def file_uploader(attachments: list) -> t.Optional[str]:
    file_list_json = []

    for attachment in attachments:
        try:
            content = await attachment.read()
            value = content.decode("utf-8")
        except (discord.NotFound, ConnectionError):
            continue

        file_list_json.append(
            {
                "name": attachment.filename,
                "content": {"format": "text", "value": value},
            }
        )

    if len(file_list_json) == 0:
        return

    payload = {
        "name": "Overflow paste service.",
        "description": "Overflow file sec cog.",
        "files": file_list_json,
    }

    with suppress(discord.NotFound, ConnectionError):
        response = await self.bot.session.post(
            "https://api.paste.gg/v1/pastes",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )

    if response.status != 201:
        return

    key = (await response.json())["result"]["id"]
    return f"https://www.paste.gg/{key}"
