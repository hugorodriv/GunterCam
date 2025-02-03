#!/bin/bash

docker buildx create --use
docker buildx inspect --bootstrap

# Build the image
docker buildx build --platform linux/arm/v7 -t guntercam --output type=docker .

# Save image to file
docker save -o guntercam.tar guntercam
