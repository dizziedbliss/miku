import re
import hikari
import logging

from miku.extractor.pinterest import extract_pinterest_video

logger = logging.getLogger(__name__)


PIN_REGEX = re.compile(r"https?://(?:www\.)?pinterest\.com/pin/[^\s<]+|https?://pin\.it/[^\s<]+")


async def on_message(event: hikari.MessageCreateEvent) -> None:
    if not event.is_human:
        logger.debug(f"Ignoring non-human message from {event.message.author}")
        return

    logger.debug(f"Checking message content: {event.message.content}")
    pin_urls = PIN_REGEX.findall(event.message.content)
    if not pin_urls:
        logger.debug("No Pinterest link found in message")
        return
    
    logger.info(f"Found {len(pin_urls)} Pinterest link(s): {pin_urls}")
    
    # Extract media from all links
    media_urls = []
    for pin_url in pin_urls:
        media_url = await extract_pinterest_video(pin_url)
        logger.info(f"Extracted media URL from {pin_url}: {media_url}")
        if media_url:
            media_urls.append(media_url)
    
    if not media_urls:
        logger.warning(f"Failed to extract any media URLs")
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

        # Extract text without the Pinterest links
        text_content = event.message.content
        for pin_url in pin_urls:
            text_content = text_content.replace(pin_url, "")
        text_content = text_content.strip()
        logger.debug(f"Extracted text: {text_content}")
        
        # Combine text with the media links
        media_links = "\n".join([f"[.]({url})" for url in media_urls])
        message_content = f"{text_content}\n{media_links}" if text_content else media_links

        await event.app.rest.execute_webhook(
            webhook=webhook,
            token=webhook.token,
            content=message_content,
            username=event.message.author.username,
            avatar_url=event.message.author.make_avatar_url(),
            user_mentions=True,
        )
        logger.info(f"Webhook executed successfully with {len(media_urls)} media URL(s)")

        await event.app.rest.delete_webhook(webhook)
        logger.debug("Webhook deleted successfully")
    except Exception as e:
        logger.error(f"Error executing webhook: {e}", exc_info=True)


def register(bot: hikari.GatewayBot) -> None:
    bot.subscribe(hikari.MessageCreateEvent, on_message)
