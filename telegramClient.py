from PIL import Image
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

        result = await bot.sendMediaGroup(
            chat_id=secrets.TELEGRAM_GROUP_ID, media=media_group
        )

    asyncio.run(send_message())


if __name__ == "__main__":
    print("test")

    # generate test images
    #

    test_arr = []
    test_arr.append(Image.new("RGB", (300, 200), (255, 0, 0)))
    test_arr.append(Image.new("RGB", (300, 200), (0, 255, 0)))
    test_arr.append(Image.new("RGB", (300, 200), (0, 0, 255)))
    test_arr.append(Image.new("RGB", (300, 200), (255, 255, 0)))

    sendTelegramPictures(test_arr, "testRun")
