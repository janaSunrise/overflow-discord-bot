import random
import traceback
from datetime import datetime
from itertools import cycle

import discord
from discord.ext import menus
from loguru import logger

from bot.utils.utils import confirmation


class BCard:
    def __init__(self, value, colour) -> None:
        self._value = value
        self.is_ace = value == 1
        self.colour = colour

    @property
    def name(self) -> str:
        if self.is_ace:
            N = "Ace of "
        elif self._value > 10:
            N = ["Jack", "Queen", "King"][self._value - 11] + " of "
        else:
            N = f"{self._value} of "
        N += [
            "\U00002660\N{variation selector-16}",
            "\U00002663\N{variation selector-16}",
            "\U00002665\N{variation selector-16}",
            "\U00002666\N{variation selector-16}",
        ][self.colour]
        return N
        # spades, clubs, hearts, diamonds

    @property
    def value(self) -> int:
        if self._value > 10:
            return 10
        return self._value

    def tuple(self) -> tuple:
        return self._value, self.colour

    def __eq__(self, other) -> bool:
        return self._value == other._value

    def min(self) -> int:
        if self.is_ace:
            return 1
        return self.value


class BRow(list):
    def isvalid(self) -> bool:
        return self.value_min() <= 21

    def value_min(self) -> int:
        return sum([card.min() for card in self])

    def value(self) -> int:
        V = self.value_min()
        c = 0
        for card in self:
            if card.is_ace:
                c += 1
        while c:
            if V <= 11:
                V += 10
                c -= 1
            else:
                break
        return V


class Deck:
    def __init__(self, money, cost, player_id) -> None:
        self.cards = [BRow()]
        self._money = money
        self.balance = -cost
        self.cost = cost
        self.player_id = player_id

    @property
    def money(self) -> int:
        return self._money + self.balance

    def __contains__(self, card) -> int:
        return any(card in column for column in self.cards) and len(self.cards) < 3

    def __iter__(self) -> list:
        return self.cards

    def isvalid(self) -> bool:
        return any(column.isvalid() for column in self.cards) and self.money > 0

    async def add(self, card, ctx, ini=False) -> None:
        if card in self and self.cost < self.money and not ini:

            answer = confirmation(
                ctx,
                f"You have a {card.name}. Do you want to split?",
                title="Split the card",
            )

            if answer:
                return self.split(card)

        L = [i for i in range(len(self.cards)) if self.cards[i].isvalid()]
        if len(L) == 1:
            id = L[0]
        else:
            m1 = await ctx.send(
                f"You have {len(L)} rows available. In which one do you want to play ?"
            )

            def check(message) -> bool:
                if (
                    message.author == ctx.author
                    and message.channel == ctx.channel
                    and message.content.isdigit()
                ):
                    try:
                        return self.cards[int(message.content) - 1].isvalid()
                    except Exception:
                        pass
                return False

            try:
                message = await ctx.bot.wait_for("message", check=check, timeout=30)
                id = int(message.content) - 1
            except Exception:
                id = L[0]
                await ctx.send(f"Defaulting to row {id + 1}", delete_after=4)

            try:
                await m1.delete()
                await message.delete()
            except Exception:
                pass

        self.cards[id].append(card)

    def split(self, card) -> None:
        self.balance -= self.cost
        self.cards.append(BRow([card]))


class Blackjack(menus.Menu):
    def __init__(self, players, money_dict, cost, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ids = cycle([player.id for player in players])
        self.index = cycle([i for i in range(len(players))])
        self.next = next(self.ids)
        self.next_index = next(self.index)

        self.player_dict = {player.id: player for player in players}
        self.money_dict = money_dict
        self.cost = cost

    def reaction_check(self, payload) -> bool:
        if payload.message_id != self.message.id:
            return False

        return payload.user_id == self.next and payload.emoji in self.buttons

    @property
    def card(self) -> BCard:
        random.shuffle(self.cards)
        return self.cards.pop()

    async def new_game(self) -> None:
        self.cards = [
            BCard(i + 1, j) for i in range(13) for j in range(4) for _ in range(6)
        ]
        self.players = [Deck(self.money_dict[i], self.cost, i)
                        for i in self.money_dict]
        self.dealer = BRow()
        self.dealer.append(self.card)
        for i in range(len(self.players)):
            for _ in range(2):
                await self.players[i].add(self.card, None, True)
        self.next_card = self.card

    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(title=f"The bet is fixed at {self.cost}")
        embed.add_field(
            name="Dealer :",
            value=", ".join([card.name for card in self.dealer]),
            inline=False,
        )

        for player in self.players:
            embed.add_field(
                name=f"{self.player_dict[player.player_id].display_name} ({player.money} GP)",
                value="\n".join(
                    [", ".join([card.name for card in row])
                     for row in player.cards]
                ),
                inline=False,
            )
        return embed

    async def send_initial_message(self, ctx, channel) -> discord.Message:
        return await ctx.send(
            self.player_dict[self.next].mention, embed=self.generate_embed()
        )

    async def update_embed(self, new_turn=False) -> None:
        if new_turn:
            self.next = next(self.ids)
            self.next_index = next(self.index)
            if self.next_index == 0:
                return await self.result()
        else:
            self.next_card = self.card

        await self.message.edit(
            content=self.player_dict[self.next].mention, embed=self.generate_embed(
            )
        )

    async def result(self) -> None:
        while self.dealer.value() < 17:
            self.dealer.append(self.card)

        embed = discord.Embed()

        if not self.dealer.isvalid():
            n = "Busted"
            V = 0
        elif len(self.dealer) == 2 and self.dealer.value() == 21:
            n = "Blackjack"
            V = 22
        else:
            V = self.dealer.value()
            n = f"{V} points"

        n += f" : {', '.join([card.name for card in self.dealer])}"
        embed.add_field(name="Dealer", value=n, inline=False)

        for player in self.players:
            n = []
            if (
                player.cards[0].value() == 21
                and len(player.cards) == 1
                and len(player.cards[0]) == 2
            ):
                n.append(
                    f"Blackjack : {', '.join([card.name for card in player.cards[0]])}"
                )
                if V == 22:
                    player.balance += self.cost
                else:
                    player.balance += round(2.5 * self.cost)
            else:
                for row in player.cards:
                    if row.isvalid():
                        n.append(
                            f"{row.value()} points : {', '.join([card.name for card in row])}"
                        )
                        if row.value() == V:
                            player.balance += self.cost
                        elif row.value() > V:
                            player.balance += 2 * self.cost
                    else:
                        n.append(
                            f"Busted : {', '.join([card.name for card in row])}")
            embed.add_field(
                name=f"{self.player_dict[player.player_id]} : {player.money} GP",
                value="\n".join(n),
                inline=False,
            )
        await self.message.edit(content=None, embed=embed)
        self.stop()

    @menus.button("\U00002795")
    async def action(self, payload) -> None:
        await self.players[self.next_index].add(self.next_card, self.ctx)
        await self.update_embed(not self.players[self.next_index].isvalid())

    @menus.button("\U0000274c")
    async def next_turn(self, payload) -> None:
        await self.update_embed(True)

    async def prompt(self, ctx) -> dict:
        await self.new_game()
        await self.start(ctx, wait=True)
        return {P.player_id: P.balance for P in self.players}


class Blackjack_players(menus.Menu):
    def __init__(self, author, author_money, cost, **kwargs) -> None:
        super().__init__(**kwargs)
        self.players = [author]
        self.money_dict = {author.id: author_money}
        self.cost = cost
        self.current_state = 0

    def reaction_check(self, payload) -> bool:
        return (
            payload.message_id == self.message.id
            and payload.user_id != self.bot.user.id
        )

    async def update(self, payload) -> None:
        button = self.buttons[payload.emoji]
        if not self._running:
            return

        try:
            if button.lock:
                async with self._lock:
                    if self._running:
                        await button(self, payload)
            else:
                await button(self, payload)
        except Exception as error:
            embed = discord.Embed(color=0xFF0000)
            embed.set_author(
                name=str(self.ctx.author), icon_url=str(self.ctx.author.avatar_url)
            )
            message = f"{self.ctx.author.id} caused an error in blackjack. | {type(error).__name__} : {error}"

            if self.ctx.guild:
                message += (
                    f"\nin {self.ctx.guild} ({self.ctx.guild.id})\n   in {self.ctx.channel.name} "
                    f"({self.ctx.channel.id})"
                )
            elif isinstance(self.ctx.channel, discord.DMChannel):
                message += f"\nin a Private Channel ({self.ctx.channel.id})"
            else:
                message += (
                    f"\nin the Group {self.ctx.channel.name} ({self.ctx.channel.id})"
                )

            tb = "".join(traceback.format_tb(error.__traceback__))
            message += f"```\n{tb}```"

            logger.error(message)

    async def send_initial_message(self, ctx, channel) -> discord.Message:
        self.time = 120
        return await ctx.send(embed=self.get_embed())

    async def updater(self) -> None:
        self.time -= 5
        await self.message.edit(embed=self.get_embed())
        if self.time == 0:
            self.stop()

    def get_embed(self) -> discord.Embed:
        r = "\n -"
        ini = (
            "Check the command's help for the rules. React with :white_check_mark: to join, :track_next: to begin "
            "the game\n\n"
        )
        return discord.Embed(
            title=f"Come play blackjack ! Initial bet is {self.cost}. ({self.time} seconds left)",
            description=f"{ini}Current players :\n -{r.join([player.mention for player in self.players])}",
        )

    @menus.button("\U00002705")
    async def adder(self, payload) -> None:
        member = self.ctx.guild.get_member(payload.user_id)
        if member in self.players:
            self.players.remove(member)
            del self.money_dict[payload.user_id]
        else:
            self.money_dict[payload.user_id] = 100
            self.players.append(member)

    @menus.button("\U000023ed\N{variation selector-16}")
    async def skipper(self, payload) -> None:
        self.time = 5
        self.current_state = -1
        await self.updater()

    async def prompt(self, ctx) -> tuple:
        await self.start(ctx, wait=True)
        return self.players, self.money_dict

    def stop(self) -> None:
        self.current_state = -1
        super().stop()
