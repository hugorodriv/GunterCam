import requests
import time
from PIL import Image
from io import BytesIO
import urllib3
import datetime
import numpy as np
import cv2
import io

import telegramClient
import config

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
    size = (128, 128)
    a_resized = a.resize(size).convert("L")  # Convert to grayscale
    b_resized = b.resize(size).convert("L")

    # Convert PIL images to NumPy arrays for OpenCV processing
    a_np = np.array(a_resized)
    b_np = np.array(b_resized)

    # Compute the absolute difference
    diff = cv2.absdiff(a_np, b_np)

    # Apply a threshold to ignore small differences (e.g., lighting changes)
    _, diff_thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Apply morphological operations to remove noise and fill gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    diff_cleaned = cv2.morphologyEx(diff_thresh, cv2.MORPH_OPEN, kernel)
    diff_cleaned = cv2.morphologyEx(diff_cleaned, cv2.MORPH_CLOSE, kernel)

    # Find contours of the detected differences
    contours, _ = cv2.findContours(
        diff_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Calculate the total area of differences
    diff_area = 0
    for contour in contours:
        diff_area += cv2.contourArea(contour)

    # Normalize the difference score by the total image area
    total_area = size[0] * size[1]
    diff_score = diff_area / total_area

    return diff_score


def createGif(img_arr, duration=300):
    buffer = io.BytesIO()
    img_arr[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=img_arr[1:],
        loop=0,
        optimize=False,
        duration=duration,
    )
    buffer.seek(0)
    return buffer


def mainLoop():
    image_b = getImage()

    while True:
        currentTime = round(time.time() * 1000)
        image_a = getImage()

        try:
            diff = getImageDiff(image_a, image_b)
        except OSError as e:
            # diff1 = 0
            diff = 0
            print(
                f"OS Error!!!!!!! {datetime.datetime.now().strftime('%A, %H:%M:%S')} \n {e}"
            )

        if diff >= config.min_diff:
            print(f"Movement {datetime.datetime.now().strftime('%A, %H:%M:%S')}")
            print(f"Diff: {diff:.2f}")

            image_arr = [image_b, image_a]

            for _ in range(config.num_photos_after_detection):
                if (round(time.time() * 1000) - currentTime) < config.min_freq:
                    time.sleep(
                        (config.min_freq - (round(time.time() * 1000) - currentTime))
                        / 1000
                    )
                image_arr.append(getImage())

            gif_buffer = createGif(image_arr)
            telegramClient.sendTelegramGif(
                gif_buffer,
                text=f"Diff:{diff:.2f} Time:{datetime.datetime.now().strftime('%A, %H:%M:%S')}",
            )

            if (round(time.time() * 1000) - currentTime) < config.cooldown:
                time.sleep(
                    (config.cooldown - (round(time.time() * 1000) - currentTime)) / 1000
                )

            # It has been 30s, update image a again
            image_a = getImage()

        # Ensure that, at minimum, the time between pictures is min_freq
        if (round(time.time() * 1000) - currentTime) < config.min_freq:
            time.sleep(
                (config.min_freq - (round(time.time() * 1000) - currentTime)) / 1000
            )

        image_b = image_a


if __name__ == "__main__":
    print(f"Started. Time:{datetime.datetime.now().strftime('%A, %H:%M:%S')}")
    while True:
        try:
            mainLoop()
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
        ) as e:
            print(f"Connection Error: {e}")
            time.sleep(30)
