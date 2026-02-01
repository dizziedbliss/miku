import hikari
import random

MIKU_GIFS = [
    "https://c.tenor.com/06N8oWCu3KgAAAAd/tenor.gif",
    "https://c.tenor.com/UcpzfXzOr0MAAAAd/tenor.gif",
    "https://c.tenor.com/Q_Tc4WD1nnsAAAAd/tenor.gif",
]

async def on_message(event: hikari.MessageCreateEvent) -> None:
    if not event.is_human:
        return
    content = (event.content or "").lower()
    if "miku miku" in content:
        embed = hikari.Embed(
            title="BEEEEAAAAAMMMMMMM!!!",
            color=0x39C5BB
        )
        embed.set_image(random.choice(MIKU_GIFS))
        await event.message.respond(embed=embed)

def register(bot: hikari.GatewayBot) -> None:
    bot.subscribe(hikari.MessageCreateEvent, on_message)