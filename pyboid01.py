import pygame
from random import randint
from math import sqrt
import operator
from functools import reduce

BLACK = (0,0,0)
GREY = (51, 51, 51)
BLUE = (51, 102, 255)
WHITE = (255,255,255)
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 710
DELTA_TIME = 1.0/15


class BoidManager(object):
    def __init__(self, neighbor_distance=25, initial_boids=300):
        self.neighbor_distance = neighbor_distance
        self.boids = []

        for b in range(0, initial_boids):
            self.create_boid()

    def create_boid(self):
        boid = Boid()
        self.add_boid(boid)

    def add_boid(self, boid):
        self.boids.append(boid)

    def remove_boid(self, boid):
        self.boids.remove(boid)

    def get_boid_index(self, boid):
        return self.boids.index(boid)

    def find_neighbors_of_boid(self, pos, distance):
        d2 = distance**2
        neighbors = list(filter(lambda x: d2 > (pos[0] - x.pos[0])**2 + (pos[1] - x.pos[1])**2, self.boids))
        return neighbors

    def update_boids(self):
        for boid in self.boids:
            neighbors = self.find_neighbors_of_boid(boid.pos, self.neighbor_distance)
            boid.update(neighbors)


class Boid(object):
    def __init__(self):
        rand_pos = (float(randint(1, SCREEN_WIDTH-10)), float(randint(1, SCREEN_HEIGHT-10)))
        self.pos = rand_pos
        self.vel = (float(randint(-10, 10)), float(randint(-10, 10)))
        self.maximum_vel = 25
        self.neighbors = None

        self.weights = {
            'cohesion': 0.5,
            'alignment': 1,
            'separation': 50,
            'avoid_walls': 800
        }

    def weight_cohesion(self, cohesion):
        return (cohesion[0]*self.weights['cohesion'], cohesion[1]*self.weights['cohesion'])

    def cohesion(self, neighbors):
        # get neighbors and neighbor count
        plist = [x.pos for x in neighbors]
        ntotal = len(neighbors)

        # maths
        sum_pos = reduce(lambda x, y: (x[0]+y[0], x[1]+y[1]), plist)
        avg_pos = (sum_pos[0]/ntotal, sum_pos[1]/ntotal)

        # return where we are going
        return self.weight_cohesion(((avg_pos[0]-self.pos[0]), avg_pos[1]-self.pos[1]))

    def weight_alignment(self, alignment):
        return (alignment[0] * self.weights['alignment'], alignment[1] * self.weights['alignment'])

    def alignment(self, neighbors):
        # get neighbors and neighbor velocities
        vlist = [x.vel for x in neighbors]
        ntotal = len(neighbors)

        # maths
        sum_vel = reduce(lambda x, y: (x[0]+y[0], x[1]+y[1]), vlist)
        avg_vel = (sum_vel[0]/ntotal, sum_vel[1]/ntotal)

        # return average velocity
        return self.weight_alignment(avg_vel)

    def weight_separation(self, separation):
        return (separation[0] * self.weights['separation'], separation[1] * self.weights['separation'])

    def separation(self, neighbors):
        # get neighbors and list of vector differences
        dlist = [(self.pos[0]-x.pos[0], self.pos[1]-x.pos[1]) for x in neighbors]
        total_vec = (0, 0)
        for diff in dlist:
            diff_mag = (diff[0]**2 + diff[1]**2)
            total_vec = (total_vec[0] + (diff[0] / diff_mag), total_vec[1] + (diff[1] / diff_mag))

        return self.weight_separation(total_vec)

    def weight_avoid_walls(self, avoidance):
        return (avoidance[0] * self.weights['avoid_walls'], avoidance[1] * self.weights['avoid_walls'])

    def avoid_walls(self):
        left_wall_distance = self.pos[0] - 0
        top_wall_distance = self.pos[1] - 0
        right_wall_distance = self.pos[0] - SCREEN_WIDTH
        bottom_wall_distance = self.pos[1] - SCREEN_HEIGHT

        avoidance_vec = (1/left_wall_distance + 1/right_wall_distance, 1/top_wall_distance + 1/bottom_wall_distance)
        return self.weight_avoid_walls(avoidance_vec)


    def update(self, neighbors):
        neighbors.remove(self)
        self.neighbors = len(neighbors)

        if len(neighbors):
            cohesion_vel = self.cohesion(neighbors)
            avg_vel = self.alignment(neighbors)
            sep_vel = self.separation(neighbors)
            avoid_walls_vel = self.avoid_walls()

            acceleration = tuple(map(sum, zip(cohesion_vel, avg_vel, sep_vel, avoid_walls_vel)))
            self.vel = (self.vel[0] + acceleration[0] * DELTA_TIME, self.vel[1] + acceleration[1] * DELTA_TIME)
            self.vel_mag = sqrt(self.vel[0]**2 + self.vel[1]**2)
            if self.vel_mag > self.maximum_vel:
                self.vel = (self.vel[0]*self.maximum_vel/self.vel_mag, self.vel[1]*self.maximum_vel/self.vel_mag)

        self.pos = (self.pos[0] + self.vel[0] * DELTA_TIME, self.pos[1] + self.vel[1] * DELTA_TIME)
        if self.pos[0] >= SCREEN_WIDTH:
            self.pos = (SCREEN_WIDTH-1, self.pos[1])
            self.vel = (-self.vel[0], self.vel[1])
        if self.pos[1] >= SCREEN_HEIGHT:
            self.pos = (self.pos[0], SCREEN_HEIGHT-1)
            self.vel = (self.vel[0], -self.vel[1])
        if self.pos[0] <= 0:
            self.pos = (1, self.pos[1])
            self.vel = (-self.vel[0], self.vel[1])
        if self.pos[1] <= 0:
            self.pos = (self.pos[0], 1)
            self.vel = (self.vel[0], -self.vel[1])


pygame.init()

size = (SCREEN_WIDTH,SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Boids")

playing = True

clock = pygame.time.Clock()

boid_manager = BoidManager()

while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False

    screen.fill(BLACK)

    boid_manager.update_boids()

    for boid in boid_manager.boids:
        if boid.neighbors is None:
            pygame.draw.ellipse(screen, GREY, [boid.pos[0], boid.pos[1], 10, 10], 0)
        elif boid.neighbors > 0:
            pygame.draw.ellipse(screen, WHITE, [boid.pos[0], boid.pos[1], 10, 10], 0)
        else:
            pygame.draw.ellipse(screen, BLUE, [boid.pos[0], boid.pos[1], 10, 10], 0)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()