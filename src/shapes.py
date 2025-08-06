# -------------------------------------------------------------------
# visuals.py
#
# Handles all drawing and rendering logic 
# Includes projection of world coordinates to screen, visualizing game
# elements like lanes, notes, the judgment line, and UI elements.
# -------------------------------------------------------------------
import pygame
import sys
from src.constants import *
from src.matrices import create_model_matrix, create_view_matrix, create_perspective_matrix, convert_to_screen, world_to_screen
import numpy as np

def define_line_positions():
    """
    Define the start and end positions (in world coordinates) of the vertical
    lines that represent playable columns.
    
    Returns:
        (start_world_coords, end_world_coords): Two lists of 3D points.
    """
    line_x_coords = []
    for i in range(NUM_LINES):
        offset = (i - NUM_LINES // 2) * LINE_SPACING
        x = offset
        line_x_coords.append(x)
    
    start_world_coords = []
    end_world_coords = []

    # Coordinates for line in WORLD coordinates
    for i in range (len(line_x_coords)):
        start_world_coords.append(np.array([line_x_coords[i], 0, 10])) # Hardcoded values
        end_world_coords.append(np.array([line_x_coords[i], 0, 300]))
    
    return start_world_coords, end_world_coords

def draw_lines(screen):
    """
    Draw vertical guide lines for each column on the screen.
    """
    start_world_coords, end_world_coords = define_line_positions()

    for start, end in zip(start_world_coords, end_world_coords):
        # Convert to screen space
        start_screen = world_to_screen(start)
        end_screen = world_to_screen(end)

        # Draw line on screen
        pygame.draw.line(screen, (255, 255, 255), start_screen, end_screen)

# Quad class with moving vertices to visually represent notes
class Quad:
    def __init__ (self, column, length = 1.5):
        self.column = column
        self.color = (0, 0, 0)

        vertices_3D = np.array([
            np.array([5, 0, START_Z]), 
            np.array([5 - LINE_SPACING, 0, START_Z]),
            np.array([5 - LINE_SPACING, 0, START_Z - length]),
            np.array([5, 0, START_Z - length])
        ])

        x_offset = (column - (NUM_LINES + 3) / 2) * LINE_SPACING
        self.vertices_3D = vertices_3D.copy()
        self.vertices_3D[:, 0] += x_offset  # Shift x-coordinates

        color_map = {
            1: (235, 103, 2),
            2: (2, 235, 231),
            3: (235, 2, 126),
            4: (56, 2, 235),
            5: (45, 235, 2),
        }
        self.color = color_map.get(column, (235, 216, 2))

    def get_testing_z(self):
        """Return the Z-depth of the bottom face of the quad."""
        return self.vertices_3D[2][2]

def draw_judgment(screen):
    """
    Draw the red horizontal judgment zone where notes should be hit.
    """
    start_front_3D = np.array([-20, 0, JUDGMENT + 1.5])
    end_front_3D = np.array([20, 0, JUDGMENT + 1.5])
    start_back_3D = np.array([-20, 0, JUDGMENT])
    end_back_3D = np.array([20, 0, JUDGMENT])

    start_front_2D = world_to_screen(start_front_3D)
    end_front_2D = world_to_screen(end_front_3D)
    start_back_2D = world_to_screen(start_back_3D)
    end_back_2D = world_to_screen(end_back_3D)


    pygame.draw.line(screen, (255, 0, 0), start_front_2D, end_front_2D)
    pygame.draw.line(screen, (255, 0, 0), start_back_2D, end_back_2D)

def draw_column_labels(screen, font):
    """
    Draw labeled key boxes (S, D, F, J, K, L) at the bottom of the screen.
    """
    # Map to map column numbers to keyboard keys
    column_to_key = {
        1: 'S',
        2: 'D',
        3: 'F',
        4: 'J',
        5: 'K',
        6: 'L'
    }
    
    # Size and position parameters
    box_size = 40
    spacing = 125  # Reduced spacing between boxes
    corner_radius = 8
    y_position = SCREEN_HEIGHT - box_size - 20  # Position from bottom of screen
    
    # Calculate the total width of all boxes with spacing
    total_width = spacing * (len(column_to_key) - 1) + box_size
    
    # Calculate starting x position to center the group
    start_x = (SCREEN_WIDTH - total_width) // 2
    
    for i, (column, key) in enumerate(column_to_key.items()):
        # Calculate x position with fixed spacing
        x_position = start_x + i * spacing
        
        # Create rectangle for the key
        rect = pygame.Rect(x_position, y_position, box_size, box_size)
        
        # Draw rounded rectangle (white background)
        pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=corner_radius)
        
        # Render the key text in black
        text_surface = font.render(key, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def draw_title_screen(screen):
    """Render the title screen with instructions and start prompt."""
    title_font = pygame.font.SysFont(None, 64)
    subtitle_font = pygame.font.SysFont(None, 28)

    # Draw black background
    screen.fill((0, 0, 0))
        
    # Calculate center positioning with better spacing
    center_y = SCREEN_HEIGHT // 2
    title_y = center_y - 150  # Move title up from center
        
    # Draw title
    title_surface = title_font.render("NOTE RUSH", True, (255, 255, 255))
    title_rect = title_surface.get_rect(centerx=SCREEN_WIDTH//2, 
                                           centery=title_y)
    screen.blit(title_surface, title_rect)
        
    # Draw instructions
    instructions = [
        "How to Play:",
        "1. Press S, D, F, J, K, L to hit notes as they reach the red judgment zone",
        "2.Hold keys for long notes",
        "3. Score points for accurate timing",
        "",
        "PRESS ANY KEY TO START"
    ]
        
    # Start instructions below the title with appropriate spacing
    y_offset = title_y + 70
    for line in instructions:
        if line == "PRESS ANY KEY TO START":
            # Add some space before the start prompt
            y_offset += 30
            text_surface = subtitle_font.render(line, True, (255, 0, 0))
        else:
            text_surface = subtitle_font.render(line, True, (255, 255, 255))
            
        text_rect = text_surface.get_rect(centerx=SCREEN_WIDTH//2, 
                                             top=y_offset)
        screen.blit(text_surface, text_rect)
        y_offset += 40