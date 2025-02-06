# Configuration file. Values will be applied after restarting docker container (or pgrogram in general)


# minimum freq between pictures
min_freq = 200  # in ms

# Min difference between pictures (to detect motion)
# % range (0.0, 1.0)
min_diff = 0.05

# time system will wait after detecting movement to start looking again
cooldown = 10_000  # in ms

# Number of photos that will be part of the GIF (+2 extra at the beggining from the detection phase)
num_photos_after_detection = 1
