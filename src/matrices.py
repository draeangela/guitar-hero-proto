# -------------------------------------------------------------------
# matrices.py
#
# Defines all projection matrices and conversions
# Includes model, view, world, and projection matrices
# -------------------------------------------------------------------
import numpy as np
from src.constants import *

# LOCAL --> WORLD
def create_model_matrix(trans_x, trans_y, trans_z):
    """
    Return a model matrix to translate an object in world space.
    """
    return np.array([
        [1, 0, 0, trans_x],
        [0, 1, 0, trans_y],
        [0, 0, 1, trans_z],
        [0, 0, 0, 1]
    ])

# WORLD --> VIEW
def create_view_matrix():
    """
    Return a view matrix to translate an object in view space.
    """
    pitch = np.radians(20)
    cos_p = np.cos(pitch)
    sin_p = np.sin(pitch)
    
    rot_x = np.array([
        [1, 0, 0, 0],
        [0, cos_p, -sin_p, 0],
        [0, sin_p,  cos_p, 0],
        [0, 0, 0, 1]
    ])
    
    trans = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, -13],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    return rot_x @ trans

# VIEW --> CLIP (PERSPECTIVE)
def create_perspective_matrix():
    """
    Return a view perspective to translate an object in clip space.
    """
    n = NEAR_PLANE
    f = FAR_PLANE
    fov = FOV
    aspect = SCREEN_WIDTH / SCREEN_HEIGHT

    return np.array([
        [1 / (aspect * np.tan(fov / 2)), 0, 0, 0],
        [0, 1 / (np.tan(fov / 2)), 0, 0],
        [0, 0, -(f + n) / (f - n), -(2 * f * n) / (f - n)],
        [0, 0, -1, 0]
    ])

def world_to_screen(world_coord):
    """
    Convert a point from world coordinates to 2D screen coordinates.
    """
    world_to_clip = create_perspective_matrix() @ create_view_matrix()
    world_coord_h = np.append(world_coord, 1)

    clip_coord = world_to_clip @ world_coord_h

    # Reject point if it's behind the camera (z < 0) or w == 0
    if clip_coord[3] == 0 or clip_coord[2] > 0:
        return None

    ndc = clip_coord[:3] / clip_coord[3]

    # Reject if NDCs are out of range or invalid
    if not np.all(np.isfinite(ndc)) or np.any(np.abs(ndc) > 10):
        return None

    return convert_to_screen(ndc[0], ndc[1], ndc[2])

# Convert to screen coordinates
def convert_to_screen(x, y, z):
    """
    Convert normalized device coordinates to 2D screen space.
    """
    x_screen = ((x + 1) / 2) * SCREEN_WIDTH 
    y_screen = ((y - 1) / 2) * SCREEN_HEIGHT

    return x_screen, y_screen
