import re
import hikari
import logging

from miku.extractor.pinterest import extract_pinterest_video

logger = logging.getLogger(__name__)


PIN_REGEX = re.compile(r"https?://(www\.)?pinterest\.com/pin/\S+|https?://pin\.it/\S+")


async def on_message(event: hikari.MessageCreateEvent) -> None:
    if not event.is_human:
        logger.debug(f"Ignoring non-human message from {event.message.author}")
        return

    logger.debug(f"Checking message content: {event.message.content}")
    match = PIN_REGEX.search(event.message.content)
    if not match:
        logger.debug("No Pinterest link found in message")
        return

    pin_url = match.group(0)
    logger.info(f"Found Pinterest link: {pin_url}")
    
    video_url = await extract_pinterest_video(pin_url)
    logger.info(f"Extracted video URL: {video_url}")
    if not video_url:
        logger.warning(f"Failed to extract video URL from {pin_url}")
        return

    try:
        await event.message.delete()
        logger.debug("Original message deleted successfully")
    except hikari.ForbiddenError as e:
        logger.error(f"Permission denied when deleting message: {e}")
        return
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        return

    try:
        webhook = await event.app.rest.create_webhook(
            channel=event.message.channel_id,
            name=event.message.author.username,
        )
        logger.debug(f"Webhook created: {webhook.id}")

        # Extract text without the Pinterest link
        text_content = event.message.content.replace(pin_url, "").strip()
        logger.debug(f"Extracted text: {text_content}")
        
        # Combine text with the media link
        message_content = f"{text_content}\n[‎ ]({video_url})" if text_content else f"[.]({video_url})"

        await event.app.rest.execute_webhook(
            webhook=webhook,
            token=webhook.token,
            content=message_content,
            username=event.message.author.username,
            avatar_url=event.message.author.make_avatar_url(),
            user_mentions=True,
        )
        logger.info(f"Webhook executed successfully with video: {video_url}")

        await event.app.rest.delete_webhook(webhook)
        logger.debug("Webhook deleted successfully")
    except Exception as e:
        logger.error(f"Error executing webhook: {e}", exc_info=True)


def register(bot: hikari.GatewayBot) -> None:
    bot.subscribe(hikari.MessageCreateEvent, on_message)
