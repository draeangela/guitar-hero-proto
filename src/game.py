# -------------------------------------------------------------
# game_manager.py
#
# Core game logic for the Guitar Hero-style rhythm game "Note Rush".
# Handles initialization, input, rendering, scoring, and game loop.
# -------------------------------------------------------------
import pygame
import sys
from src.constants import *
from src.matrices import world_to_screen
from src.notes import ShortNote, LongNote
from src.shapes import draw_lines, draw_judgment, draw_column_labels, draw_title_screen
from src.key_handler import ColumnHighlighter

class GameManager:
    def __init__(self):
        """Initialize the game, load assets, and set up game state."""
        pygame.init()
        pygame.mixer.init()

        # Screen Settings
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Note Rush")

        # Time
        self.clock = pygame.time.Clock()
        self.running = True
        self.elapsed_time = 0

        # Note States
        self.notes = []
        self.hittable_notes = []

        # Highlighter
        self.highlighter = ColumnHighlighter() 

        # Game Text
        self.font = pygame.font.SysFont(None, 36)
        self.score = 0
        self.judgment_messages = []

        # Add title screen state
        self.show_title_screen = True

        # Load sounds
        self.hit_sound = pygame.mixer.Sound("sounds/column_sound.wav")
        self.hit_success_sound = pygame.mixer.Sound("sounds/hit_success.wav")
        self.song_sound = pygame.mixer.Sound("sounds/happy_birthday.wav")

        # Load note schedule
        self.scheduled_notes = self.load_song_notes()

    @staticmethod
    def find_note_length(t_start, t_end):
        """Calculate the visual length of a long note based on time."""
        return Z_VELOCITY * (t_end - t_start)

    def calculate_score(self, z):
        """Return judgment string and points based on note's Z-position accuracy."""
        diff = abs(z - JUDGMENT)
        if diff == 0:
            return "PERFECT!", 100
        elif diff <= 0.5:
            return "GREAT!", 80
        elif diff <= 1.2:
            return "GOOD", 50
        elif diff <= 1.8:
            return "OK", 20
        else:
            return "MISS", 0

    def load_song_notes(self):
        """Load and return scheduled notes (short and long) for the song."""
        time_j = TIME_AT_JUDGMENT

        # Tuple array of timestamps and column
        short_notes_data = [
            (4.435, 5), (4.678, 5), (7.423, 5), (7.645, 5),
            (10.445, 5), (10.662, 5), (12.001, 4), (12.222, 4),
            (13.453, 2), (13.732, 2),
        ]

        # Tuple array of timestamps (start time, end time) and column
        long_notes_data = [
            (4.903, 5.420, 4), (5.420, 5.845, 3), (5.845, 6.406, 2),
            (6.406, 7.162, 3), (7.914, 8.446, 4), (8.446, 8.995, 3),
            (8.995, 9.454, 2), (9.454, 10.230, 1), (11.007, 11.457, 2),
            (11.457, 11.937, 3), (12.432, 12.989, 2), (12.989, 13.331, 3),
            (13.956, 14.405, 1), (14.405, 14.935, 2), (14.935, 15.433, 3),
            (14.935, 15.433, 5), (15.433, 19, 2), (15.433, 19, 4),
        ]

        # Tuple array of spawn time and type of note
        scheduled = []
        for t, col in short_notes_data:
            spawn_time = t - time_j
            scheduled.append((spawn_time, ShortNote(col)))
        for t1, t2, col in long_notes_data:
            length = self.find_note_length(t1, t2)
            spawn_time = t1 - time_j + (t2 - t1)
            scheduled.append((spawn_time, LongNote(col, length)))

        return scheduled

    def check_hit(self, key):
        """Handle key press events and determine if a note was successfully hit."""
        if key not in COLUMN_KEYS:
            return
        col = COLUMN_KEYS[key]
        for note in self.hittable_notes:
            if isinstance(note, LongNote) and note.column == col: # Handle LongNote functionality
                if note.is_bottom_in_judgment_zone() and not note.being_held:
                    note.being_held = True
                    note.hold_started = True
                    return
            elif not note.hit and note.column == col: # Handle ShortNote functionality
                z = note.object.get_testing_z()
                if JUDGMENT - 1.8 <= z <= JUDGMENT + 1.8: # Judgment zone
                    note.hit = True
                    judgment, pts = self.calculate_score(z)
                    self.score += pts
                    self.judgment_messages.append((judgment, self.elapsed_time))
                    return

    def handle_key_release(self, key):
        """Handle key release events for ending long note holds and scoring."""
        if key not in COLUMN_KEYS:
            return
        col = COLUMN_KEYS[key]
        for note in self.notes:
            if isinstance(note, LongNote) and note.column == col and note.being_held:
                if note.is_top_in_judgment_zone():
                    note.hold_completed = True
                    note.hit = True
                    z = note.object.vertices_3D[0][2]
                    judgment, pts = self.calculate_score(z)
                    self.score += pts
                    self.judgment_messages.append((judgment, self.elapsed_time))
                else:
                    note.hit = True
                note.being_held = False
                return
                

    def run(self):
        """Main game loop: process events, update state, render visuals."""
        judgment_y = world_to_screen((0, 0, JUDGMENT))[1] # Y-Coord of judgment line

        while self.running:
            dt = self.clock.tick(60) / 1000
            
            # Processes all input events: quitting the game, key presses/releases, and starting the game from the title screen.
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN:
                    if self.show_title_screen: # Implement initial game states
                        self.show_title_screen = False # Any key pressed on title screen starts the game
                        self.song_sound.play()  
                        self.elapsed_time = 0 
                    else: # Hit functionality
                        self.highlighter.press_key(e.key) 
                        self.check_hit(e.key)
                        self.hit_sound.play()
                elif e.type == pygame.KEYUP and not self.show_title_screen: # Release functionality
                    self.highlighter.release_key(e.key)
                    self.handle_key_release(e.key)
            
            if self.show_title_screen: 
                draw_title_screen(self.screen)
            else:
                self.elapsed_time += dt
                
                self.notes.extend([n for t, n in self.scheduled_notes if t <= self.elapsed_time]) # Spawn notes
                self.scheduled_notes = [(t, n) for (t, n) in self.scheduled_notes if t > self.elapsed_time] # Keep only the notes that are waiting to appear

                # Other states
                self.screen.fill((0, 0, 0))
                draw_lines(self.screen)

                # Prepares lists to track hittable notes and those that need to be removed after being missed or hit
                self.hittable_notes.clear()
                notes_to_remove = []

                # Iterates through all notes, updates their position, checks for misses, and renders them
                for note in self.notes:
                    if note.hit and not isinstance(note, LongNote):
                        notes_to_remove.append(note)
                        continue
                    if isinstance(note, LongNote) and note.hit:
                        notes_to_remove.append(note)
                        continue

                    note.update(dt)

                    # Special handling for long notes
                    if isinstance(note, LongNote):
                        bottom_z = note.object.vertices_3D[2][2]
                        top_z = note.object.vertices_3D[0][2]

                        if bottom_z < JUDGMENT - 2 and not note.hold_started:
                            self.judgment_messages.append(("MISS", self.elapsed_time))
                            note.hit = True
                            notes_to_remove.append(note)
                            continue
                        elif top_z < JUDGMENT - 2:
                            if not note.hold_completed:
                                note.hit = True
                            notes_to_remove.append(note)
                            continue
                    else: # Remove if gone past the judgment zone
                        z = note.object.get_testing_z()
                        if z < JUDGMENT - 2:
                            notes_to_remove.append(note)
                            continue

                    note.draw(self.screen) # Draw note onto the screen

                    # Update hittable_notes
                    if isinstance(note, LongNote):
                        if note.is_bottom_in_judgment_zone() or note.is_top_in_judgment_zone():
                            self.hittable_notes.append(note)
                    else:
                        z = note.object.get_testing_z()
                        if JUDGMENT - 1.8 <= z <= JUDGMENT + 1.8:
                            self.hittable_notes.append(note)

                # Remove notes
                for n in notes_to_remove:
                    if n in self.notes:
                        self.notes.remove(n)

                # Column settings
                draw_judgment(self.screen)
                self.highlighter.draw(self.screen)
                draw_column_labels(self.screen, self.font)

                # Render score
                self.screen.blit(
                    self.font.render(f"SCORE: {self.score}", True, (255, 255, 255)), (20, 20)
                )

                # Judgment messages
                self.judgment_messages = [
                    (msg, t) for (msg, t) in self.judgment_messages if self.elapsed_time - t < 1.0
                ]

                if self.judgment_messages: # Render most recent judgment message
                    msg, t = self.judgment_messages[-1]
                    color = (255, 255, 255)
                    surface = self.font.render(msg, True, color)
                    rect = surface.get_rect(center=(SCREEN_WIDTH // 2, judgment_y - 100))
                    self.screen.blit(surface, rect)

            pygame.display.flip()

        # Game exit
        self.song_sound.stop()
        pygame.quit()
        sys.exit()