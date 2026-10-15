import pygame
from .player import Player
from .platform import Platform
from .hazard import Hazard

# Game Engine

WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

MAX_FALL_SPEED = 15
GAME_OVER_INPUT_DELAY = 30  # frames to ignore keys so held keys don't dismiss the screen

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gravity = 0.6

        self.start_x, self.start_y = 40, height - 120
        self.player = Player(self.start_x, self.start_y)

        # A simple hand-built level: platforms with gaps between them
        # (falling into a gap means falling off the bottom of the
        # screen), one hazard, and a goal near the right edge.
        ground_y = height - 40
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 140),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ]
        self.hazards = [Hazard(240, ground_y - 14, 100)]
        self.goal_x = 740

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False
        self.game_over_frames = 0

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN and self.game_over_frames >= GAME_OVER_INPUT_DELAY:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def update(self):
        if self.game_over:
            self.game_over_frames += 1
            return

        self.player.vy += self.gravity
        self.player.x = max(0, self.player.x + self.player.vx)

        # Cap the fall speed so a single frame can't move the player far.
        self.player.vy = min(self.player.vy, MAX_FALL_SPEED)

        prev_bottom = self.player.y + self.player.height
        self.player.y += self.player.vy
        new_bottom = self.player.y + self.player.height
        self.player.on_ground = False
        for platform in self.platforms:
            # Swept check: land if the player's bottom edge went from
            # at/above the platform top to at/below it this frame, even
            # if the two rects never overlap at the end of the frame.
            overlaps_x = (self.player.x < platform.x + platform.width
                          and self.player.x + self.player.width > platform.x)
            crossed_top = prev_bottom <= platform.y <= new_bottom
            if overlaps_x and crossed_top and self.player.vy >= 0:
                self.player.y = platform.y - self.player.height
                self.player.vy = 0
                self.player.on_ground = True
                new_bottom = platform.y

        for hazard in self.hazards:
            if self.player.rect().colliderect(hazard.rect()):
                self.game_over = True
                return

        if self.player.y > self.height:
            self.game_over = True
            return

        if self.player.x >= self.goal_x:
            self.score += 1
            self.player.x, self.player.y = self.start_x, self.start_y
            self.player.vy = 0

    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())
        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)
        pygame.draw.rect(screen, GREEN, goal_rect)

        pygame.draw.rect(screen, WHITE, self.player.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*BLACK, 160))
            screen.blit(overlay, (0, 0))

            title = self.font.render("Game Over", True, WHITE)
            final = self.font.render(f"Final Score: {self.score}", True, WHITE)
            prompt = self.font.render("Press any key to exit", True, WHITE)
            cx, cy = self.width // 2, self.height // 2
            screen.blit(title, title.get_rect(center=(cx, cy - 50)))
            screen.blit(final, final.get_rect(center=(cx, cy)))
            screen.blit(prompt, prompt.get_rect(center=(cx, cy + 50)))
