# -------------------------------------------------------------
# constants.py
# This module defines global constants and configuration values used throughout the rhythm game.
# It includes screen settings, note movement parameters, key mappings, and projection matrix parameters.

# Constants:
# - Screen dimensions
# - Line and judgment zone settings
# - Perspective projection settings (FOV, near/far planes)
# - Note physics (velocity, spawn depth)
# - Key mappings for input handling
# - TIME_AT_JUDGMENT: precomputed time it takes for a note to reach the judgment line

# Used by multiple components such as note spawning, movement logic, and rendering.
# -------------------------------------------------------------

import pygame
import numpy as np

# Screen Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Line Settings
LINE_SPACING = 2.5
NUM_LINES = 7
JUDGMENT = 17

# Matrix Constants
FOV = np.radians(60)
NEAR_PLANE = 0.1
FAR_PLANE = 1

# Note Settings
Z_VELOCITY = 20
START_Z = 100

# Keybinds
COLUMN_KEYS = {
    pygame.K_s: 6,
    pygame.K_d: 5,
    pygame.K_f: 4,
    pygame.K_j: 3,
    pygame.K_k: 2,
    pygame.K_l: 1,
}

TIME_AT_JUDGMENT = (START_Z - JUDGMENT)/(Z_VELOCITY) # Time notes hit judgment line based on distanced travelled and velocity

