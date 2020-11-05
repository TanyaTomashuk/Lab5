import pygame as pg
import numpy as np
from random import randint

SCREEN_SIZE = (800, 600)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

pg.init()


def random_col():
    '''
    :return: random color
    '''
    return randint(0, 254), randint(0, 254), randint(0, 254)


class Ball:
    '''
    Creates a cannon ball according to the power and direction of the Gun.
    Controls it's movement(and reflection from walls).
    '''
    def __init__(self, coord, vel, rad=15, color=None):
        '''
        Initializes ball's parameters (color, radius) and initial coordinates and velocity.
        '''
        if color is None:
            color = random_col()
        self.color = color
        self.coord = coord
        self.vel = vel
        self.rad = rad
        self.is_alive = True

    def draw(self, screen):
        '''
        Draws the ball on the screen.
        '''
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def move(self, t_step=1., g=2.):
        '''
        Moves the ball according to it's velocity and time step.
        Changes the ball's velocity due to gravitational force.
        '''
        self.vel[1] += int(g * t_step)
        for i in range(2):
            self.coord[i] += int(self.vel[i] * t_step)
        self.check_walls()
        if self.vel[0]**2 + self.vel[1]**2 < 2**2 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
            self.is_alive = False

    def check_walls(self, refl_ort=0.8, refl_par=0.9):
        '''
        Inelastically reflects ball's velocity when ball collides with the walls.
        '''
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)


class Table:
    '''
    Writes on the screen the score and the quantity of the used balls.
    '''
    def __init__(self, destroyed=0, used=0):
        '''
        Initializes the needed parameters and the font of the text on the screen.
        '''
        self.destroyed = destroyed
        self.used = used
        self.font = pg.font.SysFont("Helvetic", 35)

    def score(self):
        '''
        :return: Final score for the moment of calculation.
        '''
        return self.destroyed - self.used

    def draw(self, screen):
        '''
        Draws the score on the screen.
        '''
        score_surf = self.font.render("Score: {}".format(self.score()), True, BLACK)
        screen.blit(score_surf, [10, 20])
        balls_surf = self.font.render("Balls used: {}".format(self.used), True, BLACK)
        screen.blit(balls_surf, [300, 20])


class Gun:
    '''
    Creates a gun. Controls gun's power, motion and striking.
    '''
    def __init__(self, coord=[30, SCREEN_SIZE[1]//2], min_pow=20, max_pow=50):
        '''
        Initializes gun's parameters (direction, min/max power, color) and initial coordinates and velocity.
        '''
        self.coord = coord
        self.angle = 0
        self.min_pow = min_pow
        self.max_pow = max_pow
        self.pow = min_pow
        self.active = False

    def activate(self):
        '''
        Activates the gun.
        '''
        self.active = True

    def draw(self, screen):
        '''
        Draws the gun on the screen.
        '''
        end_pos = [self.coord[0] + self.pow*np.cos(self.angle),
                   self.coord[1] + self.pow*np.sin(self.angle)]
        pg.draw.line(screen, RED, self.coord, end_pos, 5)

    def strike(self):
        '''
        Creates a cannon ball, according to gun's current direction and power.
        '''
        vel = [int(self.pow * np.cos(self.angle)), int(self.pow * np.sin(self.angle))]
        self.active = False
        self.pow = self.min_pow
        return Ball(list(self.coord), vel)

    def power(self):
        '''
        Increases current gun power.
        '''
        if self.active and self.pow < self.max_pow:
            self.pow += 1

    def move(self, inc):
        '''
        Moves the gun along Oy.
        '''
        if (self.coord[1] > 30 or inc > 0) and (self.coord[1] < SCREEN_SIZE[1] - 30 or inc < 0):
            self.coord[1] += inc

    def set_angle(self, mouse_pos):
        '''
        Sets gun's direction.
        '''
        self.angle = np.arctan2(mouse_pos[1] - self.coord[1],
                                mouse_pos[0] - self.coord[0])


class Target:
    '''
    Creates a static target, controls it's movement(none) and collision with a cannon ball.
    '''
    def __init__(self, coord=None, color=None, rad=30):
        '''
        Sets coordinates, color and radius of the target.
        '''
        self.rad = rad
        if coord is None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad), randint(rad, SCREEN_SIZE[1] - rad)]
        self.coord = coord
        if color is None:
            color = random_col()
        self.color = color
        self.is_alive = True

    def check_collision(self, ball):
        '''
        Checks if the ball has collided into the target.
        '''
        dist = sum([(self.coord[i] - ball.coord[i]) ** 2 for i in range(2)]) ** 0.5
        min_dist = self.rad + ball.rad
        return dist <= min_dist

    def draw(self, screen):
        '''
        Draws a target.
        '''
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def move(self):
        '''
        Target is static.
        '''
        pass


class MovingTarget(Target):
    '''
    Creates a moving target, using the creation of a static target.
    Controls it's motion and collision with a cannon ball.
    '''
    def __init__(self, coord=None,  color=None, rad=30):
        '''
        Sets coordinates, velocity, color and radius of the target.
        '''
        super().__init__(coord, color, rad)
        self.vx = randint(-25, +25)
        self.vy = randint(-25, +25)
        self.vel = [self.vx, self.vy]

    def move(self, t_step=1., g=2.):
        '''
        Moves the target according to it's velocity and time step.
        Changes the target's velocity due to gravitational force.
        '''
        self.vel[1] += int(g * t_step)
        for i in range(2):
            self.coord[i] += int(self.vel[i] * t_step)
        self.check_walls()
        if self.vel[0]**2 + self.vel[1]**2 < 2**2 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
            self.is_alive = False

    def check_walls(self, refl_ort=0.8, refl_par=0.9):
        '''
        Inelastically reflects target's velocity when target collides with the walls.
        '''
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)


class Manager:
    '''
    Manages events' handling, ball's and target's creation, motion and collisions, etc.
    '''
    def __init__(self, n_targets=3):
        '''
        Sets the number of moving and static targets.
        :param n_targets: 3
        '''
        self.gun = Gun()
        self.table = Table()
        self.balls = []
        self.targets = []
        self.n_targets = n_targets
        self.new_level()

    def new_level(self):
        '''
        Creates a new level, when the previous is completed.
        '''
        for i in range(self.n_targets):
            self.targets.append(Target(rad=randint(max(3, 30 - 2 * max(0, self.table.score())),
                                                   30 - max(0, self.table.score()))))
        for i in range(self.n_targets):
            self.targets.append(MovingTarget(rad=randint(max(3, 30 - 2 * max(0, self.table.score())),
                                                         30 - max(0, self.table.score()))))

    def process(self, events, screen):
        '''
        Runs all necessary methods. Creates new level.
        '''
        done = self.handle_events(events)

        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)

        self.move()
        self.collide()
        self.draw(screen)

        if len(self.targets) == 0 and len(self.balls) == 0:
            self.new_level()

        return done

    def draw(self, screen):
        '''
        Draws balls, gun, targets and score.
        '''
        for ball in self.balls:
            ball.draw(screen)
        for target in self.targets:
            target.draw(screen)
        self.gun.draw(screen)
        self.table.draw(screen)

    def move(self):
        '''
        Moves balls, targets and gun, removes dead balls.
        '''
        dead_balls = []
        for i, ball in enumerate(self.balls):
            ball.move(g=2)
            if not ball.is_alive:
                dead_balls.append(i)
        for i in reversed(dead_balls):
            self.balls.pop(i)
        for i, target in enumerate(self.targets):
            target.move()
        self.gun.power()

    def collide(self):
        '''
        Checks if the ball collides into the target.
        '''
        collisions = []
        targets_c = []
        for i, ball in enumerate(self.balls):
            for j, target in enumerate(self.targets):
                if target.check_collision(ball):
                    collisions.append([i, j])
                    targets_c.append(j)
        targets_c.sort()
        for j in reversed(targets_c):
            self.table.destroyed += 1
            self.targets.pop(j)

    def handle_events(self, events):
        '''
        Handles events from keyboard.
        '''
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.gun.move(-5)
                elif event.key == pg.K_DOWN:
                    self.gun.move(5)
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.gun.activate()
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.gun.strike())
                    self.table.used += 1
        return done


screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("The gun of Tomashuk")
clock = pg.time.Clock()
screen.fill(WHITE)

mgr = Manager(n_targets=3)

done = False

while not done:
    clock.tick(30)

    done = mgr.process(pg.event.get(), screen)

    pg.display.flip()

    screen.fill(WHITE)


pg.quit()
