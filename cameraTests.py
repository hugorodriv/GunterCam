from main import getImage
import time
import datetime
import matplotlib.pyplot as plt
from PIL import Image, ImageChops
import cv2
import numpy as np

# minimum freq between pictures
min_freq = 350  # in ms

# in absolute terms. depends on the resizing done for the diff analysis
min_diff = 30_000

# time system will wait after detecting movement to start looking again
cooldown = 10_000  # in ms


image_b = getImage()


def displayImages(img1, img2, text):
    # Create figure and grid
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(8, 6))

    # Display first image
    axes[0, 0].imshow(img1, cmap="grey")
    axes[0, 0].axis("off")
    axes[0, 0].set_title("Image 1")

    # Display second image
    axes[0, 1].imshow(img2, cmap="grey")
    axes[0, 1].axis("off")
    axes[0, 1].set_title("Image 2")

    # Display text
    axes[1, 0].axis("off")
    axes[1, 1].axis("off")
    axes[1, 0].text(
        1,
        0.5,
        text,
        fontsize=14,
        ha="center",
        va="center",
        transform=axes[1, 0].transAxes,
    )

    plt.tight_layout()
    plt.show()


# def getImageDiff(a: Image.Image, b: Image.Image):
#     # Resize to a smaller resolution to ignore fine details and focus on large shapes
#     size = (128, 128)
#     a_resized = a.resize(size).convert("L")  # Convert to grayscale
#     b_resized = b.resize(size).convert("L")
#
#
#     a_resized.het
#
#     # Compute the absolute difference
#     diff = ImageChops.difference(a_resized, b_resized)
#
#     # Calculate the sum of pixel differences (lower sum means more similarity)
#     diff_score = sum(diff.getdata())
#     return diff_score, a_resized, b_resized


# deepseekr1


def getImageDiff_deep(a: Image.Image, b: Image.Image):
    # Resize to a smaller resolution to ignore fine details and focus on large shapes
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

    # Convert the cleaned difference image back to PIL format for visualization
    diff_cleaned_pil = Image.fromarray(diff_cleaned)

    return diff_score


def getImageDiff_open(a: Image.Image, b: Image.Image):
    # Resize to a smaller resolution to ignore fine details and focus on large shapes
    size = (128, 128)
    a_resized = a.resize(size).convert("L")  # Convert to grayscale
    b_resized = b.resize(size).convert("L")

    # Convert to numpy arrays for OpenCV operations
    a_np = np.array(a_resized)
    b_np = np.array(b_resized)

    # Compute the absolute difference
    diff = cv2.absdiff(a_np, b_np)

    # Apply a binary threshold to eliminate small differences (e.g., lighting changes)
    _, thresh_diff = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

    # Find contours to detect the shape of the moving object
    contours, _ = cv2.findContours(
        thresh_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Calculate the total area of all contours (as a measure of movement)
    diff_score = sum(cv2.contourArea(c) for c in contours)

    # normalize score
    total_area = size[0] * size[1]
    diff_score = diff_score / total_area
    return diff_score


while True:
    currentTime = round(time.time() * 1000)

    image_a = getImage()

    # Ensure that, at minimum, the time between pictures is min_freq
    if (round(time.time() * 1000) - currentTime) < min_freq:
        time.sleep((min_freq - (round(time.time() * 1000) - currentTime)) / 1000)

    open = getImageDiff_open(image_a, image_b)
    deep = getImageDiff_deep(image_a, image_b)
    text = f"Open:{open} Deep:{deep}"

    print(text)
    # displayImages(image_a, image_b, text)

    image_b = image_a
    image_a = None

    i = +1
