import hikari
from miku.config import PREFIX  # e.g., "miku "

async def on_message(event: hikari.MessageCreateEvent) -> None:
    if not event.is_human or not event.content:
        return
    
    if not event.content.startswith(PREFIX):
        return
    
    args = event.content[len(PREFIX):].strip().split(" ")
    commandName = args.pop(0).lower()

    if not event.guild_id:
        return

    if commandName == "join":        

        voice_state = event.app.cache.get_voice_state(event.guild_id, event.author.id)
        
        if not voice_state or not voice_state.channel_id:
            await event.message.respond("JOIN A VOICE CHANNEL MF! (*in vocaloid voice lol*)")
            return

        await event.app.update_voice_state(event.guild_id, voice_state.channel_id)
        
        await event.message.respond(
            f"Joining your voice channel FOREVER (until u tell me to leave by using `{PREFIX}leave`): {voice_state.channel_id}"
        )
        
    if commandName == "leave":

        await event.app.update_voice_state(event.guild_id, None)
        
        await event.message.respond(
            f"Leaving your voice channel FOREVER (until u tell me to join by using `{PREFIX}join`)"
        )
