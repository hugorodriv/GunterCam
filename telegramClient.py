import telegram
import asyncio
from io import BytesIO

secrets = __import__("secrets")  # avoid LSP errors


def sendTelegramPictures(image_arr, text):
    bot = telegram.Bot(secrets.TELEGRAM_TOKEN)

    async def send_message():
        media_group = []
        for image in image_arr:
            bio = BytesIO()
            bio.name = "image.jpg"
            image.save(bio, "JPEG")
            bio.seek(0)
            media_group.append(telegram.InputMediaPhoto(media=bio, caption=text))

        try:
            await asyncio.wait_for(
                bot.send_media_group(
                    chat_id=secrets.TELEGRAM_GROUP_ID, media=media_group
                ),
                timeout=60,
            )
        except (telegram.error.TimedOut, asyncio.TimeoutError):
            print("Telegram request timed out but may have been sent.")

    asyncio.run(send_message())


def sendTelegramGif(gif_buffer, text):
    bot = telegram.Bot(secrets.TELEGRAM_TOKEN)

    async def send_message():
        try:
            gif_buffer.name = "animation.gif"  # Set a name for the file
            await asyncio.wait_for(
                bot.send_animation(
                    chat_id=secrets.TELEGRAM_GROUP_ID,
                    animation=gif_buffer,
                    caption=text,
                ),
                timeout=60,
            )
        except (telegram.error.TimedOut, asyncio.TimeoutError):
            print("Telegram request timed out but image may have been sent.")

    asyncio.run(send_message())


if __name__ == "__main__":
    pass
