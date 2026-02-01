import aiohttp
import json
import logging
import re

logger = logging.getLogger(__name__)

async def extract_pinterest_video(pin_url: str) -> str | None:
    try:
        logger.debug(f"Extracting content from: {pin_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(pin_url, headers=headers, allow_redirects=True) as res:
                logger.debug(f"Response status: {res.status}")
                html = await res.text()
                logger.debug(f"HTML length received: {len(html)} characters")

        # Try to find video_list first (old method)
        idx = html.find('"video_list"')
        if idx != -1:
            logger.debug(f"'video_list' found at index: {idx}")
            snippet = html[idx:idx + 3000]
            
            try:
                json_str = "{" + snippet.split("{", 1)[1].rsplit("}", 1)[0] + "}"
                logger.debug(f"JSON string: {json_str[:300]}...")
                data = json.loads(json_str)
                logger.debug(f"Parsed JSON keys: {list(data.keys())}")
                
                video_url = data["V_720P"]["url"]
                logger.info(f"Successfully extracted video URL: {video_url}")
                return video_url
            except (KeyError, json.JSONDecodeError, IndexError) as e:
                logger.warning(f"Failed to extract from video_list: {e}")
        
        # Try alternative: look for direct video URLs in the HTML
        logger.debug("Trying alternative extraction methods...")
        
        # Pattern 1: Look for mp4 URLs
        mp4_pattern = r'"(https://[^"]*\.mp4[^"]*)"'
        mp4_matches = re.findall(mp4_pattern, html)
        if mp4_matches:
            video_url = mp4_matches[0]
            logger.info(f"Found MP4 URL via regex: {video_url}")
            return video_url
        
        # Pattern 2: Look for video in JSON-LD or other structured data
        json_ld_pattern = r'"contentUrl":\s*"(https://[^"]*video[^"]*)"'
        json_ld_matches = re.findall(json_ld_pattern, html)
        if json_ld_matches:
            video_url = json_ld_matches[0]
            logger.info(f"Found video via JSON-LD: {video_url}")
            return video_url
        
        # Pattern 3: Look for "videoSource" or similar
        video_src_pattern = r'"[^"]*video[^"]*":\s*"(https://[^"]*)"'
        video_src_matches = re.findall(video_src_pattern, html)
        if video_src_matches:
            for url in video_src_matches:
                if "mp4" in url or "video" in url:
                    logger.info(f"Found video URL: {url}")
                    return url
        
        # If no video found, try to extract image
        logger.debug("No video found, trying to extract image...")
        
        # Pattern 4: Look for high-quality images from pinimg
        image_pattern = r'"(https://[^"]*pinimg\.com/[^"]*\.jpg[^"]*)"'
        image_matches = re.findall(image_pattern, html)
        if image_matches:
            # Filter for larger image sizes (avoid thumbnails)
            for url in image_matches:
                if "236x" not in url and "100x100" not in url:
                    logger.info(f"Found image URL: {url}")
                    return url
        
        # Pattern 5: Look for any image URL
        image_pattern2 = r'"image":\s*"(https://[^"]*)"'
        image_matches2 = re.findall(image_pattern2, html)
        if image_matches2:
            image_url = image_matches2[0]
            logger.info(f"Found image via JSON: {image_url}")
            return image_url
        
        logger.warning(f"Could not find video or image URL in any format for {pin_url}")
        logger.debug(f"Sample HTML: {html[:1000]}...")
        return None
        
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching Pinterest link: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in extract_pinterest_video: {e}", exc_info=True)
        return None
