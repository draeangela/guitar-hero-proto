# -------------------------------------------------------------
# column_highlighter.py
# 
# Handles visual highlighting of columns when keys are pressed
# in the Guitar Hero-style rhythm game. Highlights are shown as
# semi-transparent rectangles over the active columns.
# -------------------------------------------------------------
from constants import *
from shapes import Quad
from matrices import world_to_screen

class ColumnHighlighter:
    def __init__(self):
        self.active_columns = set()

    def press_key(self, key):
        """Register a key press by adding its column to the active set."""
        if key in COLUMN_KEYS:
            self.active_columns.add(COLUMN_KEYS[key])

    def release_key(self, key):
        """Unregister a key release by removing its column from the active set."""
        if key in COLUMN_KEYS:
            self.active_columns.discard(COLUMN_KEYS[key])

    def draw(self, screen):
        """Draw highlights for all currently active columns."""
        for column in self.active_columns:
            self.draw_column_highlight(screen, column)

    def draw_column_highlight(self, screen, column):
        """Render a semi-transparent white rectangle over the given column."""
        highlight = Quad(column)
        highlight.color = (255, 255, 255, 60)  # Alpha channel

        # Define 3D vertices of the column highlight
        highlight.vertices_3D = np.array([
            np.array([5, 0, START_Z]), 
            np.array([5 - LINE_SPACING, 0, START_Z]),
            np.array([5 - LINE_SPACING, 0, 10]),
            np.array([5, 0, 10]),
        ])

        # Shift the quad to the correct column using X-offset
        x_offset = (column - (NUM_LINES + 3) / 2) * LINE_SPACING
        highlight.vertices_3D[:, 0] += x_offset  

        # Convert vertices to 2D
        verts_2D = [
            world_to_screen(np.array(highlight.vertices_3D[0])),
            world_to_screen(np.array(highlight.vertices_3D[1])),
            world_to_screen(np.array(highlight.vertices_3D[2])),
            world_to_screen(np.array(highlight.vertices_3D[3]))
        ]

        # Make opaque
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(temp_surface, highlight.color, verts_2D)
        screen.blit(temp_surface, (0, 0))

    