# -------------------------------------------------------------------
# notes.py
#
# Defines the Note classes
# Includes ShortNote and LongNote, which inherit from a base Note class.
# Handles note behavior, rendering, movement, and hit detection logic.
# -------------------------------------------------------------------
import pygame 
from constants import *
from matrices import world_to_screen
from shapes import Quad

print ("hello")
# Base Note class
class Note:
    def __init__(self, column):
        """Initialize a note in the specified column."""
        self.column = column
        self.hit = False
        self.object = Quad(self.column)
   
    def update(self, dt):
        """Update the note's 3D position and project it to 2D screen space."""
        self.object.vertices_3D[:, 2] -= Z_VELOCITY * dt

        # Only project valid points
        verts_2D = []
        for v in self.object.vertices_3D:
            screen_pos = world_to_screen(v)
            if screen_pos is None:
                self.object.vertices_2D = None
                return
            verts_2D.append(screen_pos)

        self.object.vertices_2D = np.array(verts_2D)

    def draw(self, screen):
        """Render the note on screen with its outline."""
        if self.object.vertices_2D is None:
            return

        v2d = self.object.vertices_2D
        if np.all(v2d[:, 1] > SCREEN_HEIGHT): # Color black when off the screen
            color = (0, 0, 0)
        else:
            color = self.object.color

        pygame.draw.polygon(screen, color, v2d)
        pygame.draw.lines(screen, (255, 255, 255), True, v2d, 1)

# ShortNote class
class ShortNote(Note):
    def __init__(self, column):
        """Create a short (tap) note in the specified column."""
        super().__init__(column)

# LongNote 
class LongNote(Note):
    def __init__(self, column, length):
        super().__init__(column)
        self.length = length
        self.object = Quad(self.column, length)

        # Add new state variables
        self.being_held = False
        self.hold_started = False
        self.hold_completed = False
        
    def fix_vertices(self, y_bound, dt):
        """
        Control how each vertex of the note moves:
        Top vertices always move.
        Bottom vertices stop if the note is being held.
        """
        for i in range(4):
            v = self.object.vertices_3D[i]
            screen_pos = world_to_screen(v)

            if screen_pos is None:
                continue

            # Always move top vertices
            if i in (0, 1):
                self.object.vertices_3D[i, 2] -= Z_VELOCITY * dt
            # Move bottom vertices only if above judgment line or not being held
            elif not self.being_held or self.object.vertices_3D[i, 2] > JUDGMENT:
                self.object.vertices_3D[i, 2] -= Z_VELOCITY * dt
            # When being held, fix bottom vertices at judgment line
            elif self.being_held and self.object.vertices_3D[i, 2] <= JUDGMENT:
                self.object.vertices_3D[i, 2] = JUDGMENT

    def update(self, dt):
        """Update position and re-project vertices to 2D screen space."""
        # Use judgment line instead of screen height
        self.fix_vertices(JUDGMENT, dt)

        # Re-project to 2D after update
        verts_2D = []
        for v in self.object.vertices_3D:
            screen_pos = world_to_screen(v)
            if screen_pos is None:
                self.object.vertices_2D = None
                return
            verts_2D.append(screen_pos)

        self.object.vertices_2D = np.array(verts_2D)
    
    def is_top_in_judgment_zone(self):
        """Check if the top of the long note is within the judgment zone."""
        top_z = min(self.object.vertices_3D[0][2], self.object.vertices_3D[1][2])
        return JUDGMENT - 1.8 <= top_z <= JUDGMENT + 1.8
    
    def is_bottom_in_judgment_zone(self):
        """Check if the bottom of the long note is within the judgment zone."""
        bottom_z = min(self.object.vertices_3D[2][2], self.object.vertices_3D[3][2])
        return JUDGMENT - 1.8 <= bottom_z <= JUDGMENT + 1.8