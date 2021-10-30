import pygame
import random
from itertools import accumulate as _accumulate, repeat as _repeat
from bisect import bisect as _bisect

SIZE_X = 1800
SIZE_Y = 900

COLOR_NIGHT_SKY = (50, 50, 50)
COLOR_SNOW = (255, 255, 255)

FPS = 60

EVENT_GAME_OVER = 0
EVENT_NONE = -1

MAX_NEW_SNOWFLAKES = 10
PROB_NEW_SNOWFLAKE = 0.01
NUM_INIT_SNOWFLAKES = 50


def choices(population, weights=None, *, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """
    n = len(population)
    if cum_weights is None:
        if weights is None:
            _int = int
            n += 0.0    # convert to float for a small speed improvement
            return [population[_int(random.random() * n)] for i in _repeat(None, k)]
        cum_weights = list(_accumulate(weights))
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != n:
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect
    total = cum_weights[-1] + 0.0   # convert to float
    hi = n - 1
    return [population[bisect(cum_weights, random.random() * total, 0, hi)]
            for i in _repeat(None, k)]


# State Transition Probability Matrix for dx
DX_TRANS_PROB_MATRIX = [
    [0.2, 0.4, 0.5, 0.0, 0.0],
    [0.1, 0.3, 0.5, 0.0, 0.0],
    [0.1, 0.2, 0.6, 0.2, 0.1],
    [0.0, 0.0, 0.5, 0.3, 0.1],
    [0.0, 0.0, 0.5, 0.4, 0.2]]


class Snowflake():
    def __init__(self, screen, x, y, dx, dy, r, da, color, image):
        self.screen = screen
        self.x = x
        self.y = y
        self.color = color
        self.dx = dx
        self.dy = int(dy*r/10)
        self.image = image
        self.image = pygame.transform.scale(self.image, (r, r))
        self.da = da
        self.angle = 0.0

    def draw(self):
        rot_image = pygame.transform.rotate(self.image, self.angle)
        self.screen.blit(rot_image, (self.x, self.y))

    def update(self):
        dx = self.dx
        idx = dx + 2
        prob = DX_TRANS_PROB_MATRIX[idx]
        self.dx = choices([-2, -1, 0, 1, 2], weights=prob)[0]
        self.x += self.dx
        self.y += self.dy
        self.angle += self.da


class GameEngine():
    def __init__(self):
        pygame.init()

        # Set up the drawing window
        self.screen = pygame.display.set_mode([SIZE_X, SIZE_Y])
        self.clock = pygame.time.Clock()

        # Load snowflakes sprite sheet
        sheet = pygame.image.load('snowflakes.png').convert_alpha()
        w = sheet.get_width()
        h = sheet.get_height()
        sf_image = []
        for i in range(3):
            for j in range(3):
                sf_image.append(sheet.subsurface(i*w/3, j*h/3, w/3, h/3))
        self.sf_image = sf_image

        # Initialize snowflakes
        self.snowflakes = []
        for i in range(NUM_INIT_SNOWFLAKES):
            sf = self.new_snowflake(random.randrange(SIZE_X), random.randrange(SIZE_Y))
            self.snowflakes.append(sf)

    def new_snowflake(self, x, y):
        return Snowflake(self.screen, x, y, 0, 1, random.randint(10, 20),
                           random.uniform(-3.0, +3.0),
                           COLOR_SNOW,
                           self.sf_image[random.randrange(9)])

    def process_events(self):
        return_event = EVENT_NONE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_event = EVENT_GAME_OVER

        return return_event

    def draw(self):
        # Fill the background with night sky color
        self.screen.fill(COLOR_NIGHT_SKY)

        #  Draw snowflake
        for sf in self.snowflakes:
            sf.draw()

        # Flip the display
        pygame.display.flip()

    def update(self):
        for sf in self.snowflakes:
            sf.update()

        # Remove snowflakes at the very bottom
        self.snowflakes = [sf for sf in self.snowflakes if sf.y <= SIZE_Y]

        # Add new snowflakes at the top
        for i in range(MAX_NEW_SNOWFLAKES):
            if random.random() <= PROB_NEW_SNOWFLAKE:
                sf = self.new_snowflake(random.randrange(SIZE_X), 0)
                self.snowflakes.append(sf)

    def run(self):
        # Run until the user asks to quit
        event = EVENT_NONE
        while event != EVENT_GAME_OVER:
            # Did the user click the window close button?
            event = self.process_events()

            # Draw scene
            self.draw()

            # Run at speed FPS
            self.clock.tick(FPS)

            # Update snowflakes
            self.update()

        # Done! Time to quit.
        pygame.quit()


def main():
    game = GameEngine()
    game.run()


if __name__ == '__main__':
    main()
