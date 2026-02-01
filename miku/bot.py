import hikari
import lightbulb

from miku.config import TOKEN
from miku.listeners import beam, pinterest

intents = hikari.Intents.GUILDS | hikari.Intents.GUILD_MESSAGES | hikari.Intents.MESSAGE_CONTENT
bot = hikari.GatewayBot(token=TOKEN, intents=intents)
client = lightbulb.client_from_app(bot)

bot.subscribe(hikari.StartingEvent, client.start)

beam.register(bot)
pinterest.register(bot)

bot.run()