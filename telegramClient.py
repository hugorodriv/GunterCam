import matplotlib.pyplot as plt


def sendTelegram(image_arr):
    fig, axs = plt.subplots(2, 2)

    for i, ax in enumerate(axs.flat):
        ax.imshow(image_arr[i])  # Display image from the array
        ax.axis("off")

    plt.tight_layout()  # Makes the layout tight
    plt.show()
