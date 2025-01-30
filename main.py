import requests
import time
from PIL import Image, ImageChops
from io import BytesIO
import urllib3
import datetime

import telegramClient

secrets = __import__("secrets")  # avoid LSP errors
# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def getImage():
    # not verifying the SSL cert is fine in this case as this is accessed through a local network
    response = requests.get(
        secrets.ENDPOINT, auth=(secrets.USERNAME, secrets.PASSWORD), verify=False
    )

    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        print(f"Failed to fetch image. Status code: {response.status_code}")
        return None


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
min_freq = 350  # in ms

# in absolute terms. depends on the resizing done for the diff analysis
min_diff = 30_000

# time system will wait after detecting movement to start looking again
cooldown = 10_000  # in ms


# Number of photos that will get taken after a movement is detected
num_photos_after_detection = 5

# cooldown after detection
min_freq_detection = 350


def mainLoop():
    image_b = getImage()

    while True:
        currentTime = round(time.time() * 1000)

        image_a = getImage()

        try:
            diff = getImageDiff(image_a, image_b)
        except OSError as e:
            diff = 0
            print(
                f"OS Error!!!!!!! {datetime.datetime.now().strftime('%A, %H:%M:%S')} \n {e}"
            )
        if diff >= min_diff:
            print(f"Movement {datetime.datetime.now().strftime('%A, %H:%M:%S')}")

            image_arr = [image_a, image_b]

            for _ in range(num_photos_after_detection):
                if (round(time.time() * 1000) - currentTime) < min_freq_detection:
                    time.sleep(
                        (min_freq_detection - (round(time.time() * 1000) - currentTime))
                        / 1000
                    )
                image_arr.append(getImage())

            telegramClient.sendTelegramPictures(
                image_arr,
                text=f"Diff:{diff}, Time:{datetime.datetime.now().strftime('%A, %H:%M:%S')}",
            )

            if (round(time.time() * 1000) - currentTime) < cooldown:
                time.sleep(
                    (cooldown - (round(time.time() * 1000) - currentTime)) / 1000
                )

        # Ensure that, at minimum, the time between pictures is min_freq
        if (round(time.time() * 1000) - currentTime) < min_freq:
            time.sleep((min_freq - (round(time.time() * 1000) - currentTime)) / 1000)

        image_b = image_a
        image_a = None


print(f"Started. Time:{datetime.datetime.now().strftime('%A, %H:%M:%S')}")


if __name__ == "__main__":
    while True:
        try:
            mainLoop()
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
        ) as e:
            print(f"Connection Error: {e}")
            time.sleep(30)
