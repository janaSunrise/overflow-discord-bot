from itertools import cycle

from discord import Embed, Member, Message
from discord.ext import menus


class Connect4(menus.Menu):
    def __init__(self, *players, **kwargs) -> None:
        super().__init__(**kwargs)
        self.winner = None
        self.id_dict = {players[i].id: i + 1 for i in range(len(players))}
        self.ids = cycle(list(self.id_dict))
        self.players = players
        self.next = next(self.ids)
        self.status = [":black_large_square:",
                       ":green_circle:", ":red_circle:"]
        self.state = [[0 for _ in range(6)] for __ in range(7)]

    def reaction_check(self, payload) -> bool:
        if payload.message_id != self.message.id:
            return False

        return payload.user_id == self.next and payload.emoji in self.buttons

    def get_embed(self) -> Embed:
        return Embed(
            description="\n".join(
                [
                    "".join([self.status[column[5 - i]]
                            for column in self.state])
                    for i in range(6)
                ]
            )
        )

    async def send_initial_message(self, ctx, channel) -> Message:
        return await ctx.send(embed=self.get_embed())

    async def action(self, n, payload) -> None:
        if 0 not in self.state[n]:
            return
        self.next = next(self.ids)
        ID = self.id_dict[payload.user_id]
        self.state[n][self.state[n].index(0)] = ID
        await self.embed_updating()
        check = self.check(ID)
        if check:
            self.winner = self.players[ID - 1]
            self.stop()

    def check(self, id) -> bool:
        S = str(id) + 3 * f", {id}"
        if any(S in str(x) for x in self.state):
            return True
        for i in range(6):
            if S in str([column[i] for column in self.state]):
                return True
        for i in range(3):
            L, L2, L3, L4 = [], [], [], []
            for c in range(4 + i):
                L.append(self.state[3 + i - c][c])
                L2.append(self.state[3 + i - c][5 - c])
                L3.append(self.state[3 - i + c][c])
                L4.append(self.state[3 - i + c][5 - c])
            if any(S in str(column) for column in (L, L2, L3, L4)):
                return True
        return False

    async def embed_updating(self) -> None:
        await self.message.edit(embed=self.get_embed())

    @menus.button("1\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_1(self, payload) -> None:
        await self.action(0, payload)

    @menus.button("2\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_2(self, payload) -> None:
        await self.action(1, payload)

    @menus.button("3\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_3(self, payload) -> None:
        await self.action(2, payload)

    @menus.button("4\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_4(self, payload) -> None:
        await self.action(3, payload)

    @menus.button("5\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_5(self, payload) -> None:
        await self.action(4, payload)

    @menus.button("6\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_6(self, payload) -> None:
        await self.action(5, payload)

    @menus.button("7\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_7(self, payload) -> None:
        await self.action(6, payload)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload) -> None:
        self.stop()

    async def prompt(self, ctx) -> Member:
        await self.start(ctx, wait=True)
        return self.winner
