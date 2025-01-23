import requests
import time
from PIL import Image, ImageChops
from io import BytesIO
import matplotlib.pyplot as plt
import urllib3

import telegramClient

secrets = __import__("secrets")  # avoid LSP errors
# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def getImage(secrets):
    # not verifying the SSL cert is fine in this case as this is accessed through a local network
    response = requests.get(
        secrets.ENDPOINT, auth=(secrets.USERNAME, secrets.PASSWORD), verify=False
    )

    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        print(f"Failed to fetch image. Status code: {response.status_code}")
        return None


def displayImage(image: Image.Image):
    plt.imshow(image)
    plt.axis("off")
    plt.show()


def getImageDiff(a: Image.Image, b: Image.Image):
    # Resize to a smaller resolution to ignore fine details and focus on large shapes
    size = (64, 64)
    a_resized = a.resize(size).convert("L")  # Convert to grayscale
    b_resized = b.resize(size).convert("L")

    # Compute the absolute difference
    diff = ImageChops.difference(a_resized, b_resized)

    # Calculate the sum of pixel differences (lower sum means more similarity)
    diff_score = sum(diff.getdata())
    return diff_score


# minimum freq between pictures
min_freq = 300  # in ms

# in absolute terms. depends on the resizing done for the diff analysis
min_diff = 10_000

# time system will wait after detecting movement to start looking again
cooldown = 10_000  # in ms


def init():
    i = 0
    image_a = getImage(secrets)

    while True:
        if i <= 100_000:  # avoids overflows? probably unnecessary
            i = 0

        currentTime = round(time.time() * 1000)

        image_b = getImage(secrets)

        if getImageDiff(image_a, image_b) >= min_diff:
            print("Movement detected!!!!!")

            if (round(time.time() * 1000) - currentTime) < min_freq:
                time.sleep(
                    (min_freq - (round(time.time() * 1000) - currentTime)) / 1000
                )
            image_c = getImage(secrets)

            if (round(time.time() * 1000) - currentTime) < min_freq:
                time.sleep(
                    (min_freq - (round(time.time() * 1000) - currentTime)) / 1000
                )
            image_d = getImage(secrets)

            # Might reduce false positives. Let's see if this is needed
            #
            # if catAnalyzer([image_a, image_b, image_c, image_d]) >= cat_threshold:
            #     pass

            telegramClient.sendTelegram([image_a, image_b, image_c, image_d])

            time.sleep(cooldown / 1000)

        image_a = image_b

        # Ensure that, at minimum, the time between pictures is min_freq
        if (round(time.time() * 1000) - currentTime) < min_freq:
            time.sleep((min_freq - (round(time.time() * 1000) - currentTime)) / 1000)

        i = +1


init()
