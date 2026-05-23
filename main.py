import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math
import numpy as np

pygame.init()
WIDTH, HEIGHT = 1400, 900

SUN_COLOR = (255, 240, 150)
MERCURY_COLOR = (169, 139, 119)
VENUS_COLOR = (255, 205, 100)
EARTH_COLOR = (70, 130, 180)
EARTH_LAND_COLOR = (50, 160, 75)
MARS_COLOR = (210, 90, 50)
JUPITER_COLORS = [
    (245, 210, 170),
    (225, 190, 140),
    (205, 160, 110),
    (180, 130, 90),
    (150, 100, 60)
]
SATURN_COLOR = (240, 220, 180)
URANUS_COLOR = (175, 220, 230)
NEPTUNE_COLOR = (60, 100, 200)
MOON_COLOR = (180, 180, 180)

class Camera:
    def __init__(self):
        self.pos = [0, 30, 60]
        self.target = [0, 0, 0]
        self.up = [0, 1, 0]
        self.yaw = 0
        self.pitch = -20
        self.distance = 60
        
    def update(self):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        self.pos[0] = self.target[0] + self.distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        self.pos[1] = self.target[1] + self.distance * math.sin(pitch_rad)
        self.pos[2] = self.target[2] + self.distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        
    def apply(self):
        gluLookAt(*self.pos, *self.target, *self.up)

class Planet:
    def __init__(self, name, radius, distance, color, orbital_period, rotation_period, has_ring=False):
        self.name = name
        self.radius = radius
        self.distance = distance
        self.color = color
        self.orbital_period = orbital_period
        self.rotation_period = rotation_period
        self.has_ring = has_ring
        self.rotation_angle = np.random.uniform(0, 360)
        self.orbit_angle = np.random.uniform(0, 360)
        self.moons = []
        
    def update(self, dt):
        if self.rotation_period > 0:
            self.rotation_angle += 360 * dt / self.rotation_period
        if self.orbital_period > 0:
            self.orbit_angle += 360 * dt / self.orbital_period
        for moon in self.moons:
            moon.update(dt)
    
    def draw_sphere(self, radius, color, detail=48):
        glColor3f(color[0]/255.0, color[1]/255.0, color[2]/255.0)
        quadric = gluNewQuadric()
        gluSphere(quadric, radius, detail, detail)
    
    def draw_ring(self, inner_radius, outer_radius, color):
        glColor4f(color[0]/255.0, color[1]/255.0, color[2]/255.0, 0.5)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glBegin(GL_QUAD_STRIP)
        for i in range(361):
            angle = math.radians(i)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            glVertex3f(inner_radius * cos_a, 0, inner_radius * sin_a)
            glVertex3f(outer_radius * cos_a, 0, outer_radius * sin_a)
        glEnd()
        glPopMatrix()
    
    def draw_orbit(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.4, 0.4, 0.6, 0.2)
        glBegin(GL_LINE_LOOP)
        for i in range(360):
            angle = math.radians(i)
            x = self.distance * math.cos(angle)
            z = self.distance * math.sin(angle)
            glVertex3f(x, 0, z)
        glEnd()
        glEnable(GL_LIGHTING)
    
    def render(self, show_orbits=True):
        glPushMatrix()
        if self.orbital_period > 0:
            glRotatef(self.orbit_angle, 0, 1, 0)
            glTranslatef(self.distance, 0, 0)
            if show_orbits:
                self.draw_orbit()
        glPushMatrix()
        glRotatef(self.rotation_angle, 0, 1, 0)
        if self.name == "Sun":
            emission = [1.0, 0.9, 0.6, 1.0]
            glMaterialfv(GL_FRONT, GL_EMISSION, emission)
            self.draw_sphere(self.radius, self.color)
            glMaterialfv(GL_FRONT, GL_EMISSION, [0, 0, 0, 1])
        else:
            self.draw_sphere(self.radius, self.color)
        if self.name == "Saturn" and self.has_ring:
            self.draw_ring(self.radius * 1.5, self.radius * 2.3, SATURN_COLOR)
        glPopMatrix()
        for moon in self.moons:
            moon.render(show_orbits)
        glPopMatrix()

class SolarSystem:
    def __init__(self):
        self.planets = []
        self.stars = []
        self.create_planets()
        self.create_stars()
    
    def create_planets(self):
        sun = Planet("Sun", 2.0, 0, SUN_COLOR, 0, 25.0)
        mercury = Planet("Mercury", 0.4, 8.0, MERCURY_COLOR, 0.24, 58.6)
        venus = Planet("Venus", 0.9, 12.0, VENUS_COLOR, 0.62, 243.0)
        earth = Planet("Earth", 1.0, 16.0, EARTH_COLOR, 1.0, 1.0)
        moon = Planet("Moon", 0.25, 2.5, MOON_COLOR, 0.074, 0.074)
        earth.moons.append(moon)
        mars = Planet("Mars", 0.5, 20.0, MARS_COLOR, 1.88, 1.03)
        jupiter = Planet("Jupiter", 2.2, 28.0, JUPITER_COLORS[0], 11.86, 0.41)
        saturn = Planet("Saturn", 1.8, 36.0, SATURN_COLOR, 29.46, 0.44, has_ring=True)
        uranus = Planet("Uranus", 1.5, 42.0, URANUS_COLOR, 84.01, 0.72)
        neptune = Planet("Neptune", 1.5, 48.0, NEPTUNE_COLOR, 164.8, 0.67)
        self.planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]
    
    def create_stars(self):
        for _ in range(1000):
            theta = np.random.uniform(0, 2 * math.pi)
            phi = np.random.uniform(0, math.pi)
            r = np.random.uniform(100, 300)
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            b = np.random.uniform(0.7, 1.0)
            self.stars.append((x, y, z, (b, b, b)))
    
    def update(self, dt):
        for p in self.planets:
            p.update(dt)
    
    def render(self, show_orbits=True):
        glDisable(GL_LIGHTING)
        glBegin(GL_POINTS)
        for x, y, z, c in self.stars:
            glColor3f(*c)
            glVertex3f(x, y, z)
        glEnd()
        glEnable(GL_LIGHTING)
        for p in self.planets:
            p.render(show_orbits)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Solar System - Realistic Edition")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, WIDTH / HEIGHT, 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)
    glClearColor(0.0, 0.0, 0.02, 1.0)
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 0, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.95, 0.8, 1])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 0.9, 1])
    camera = Camera()
    solar = SolarSystem()
    clock = pygame.time.Clock()
    paused = False
    time_scale = 1.0
    show_orbits = True
    mouse_drag = False
    last_mouse = (0, 0)
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_SPACE:
                    paused = not paused
                elif e.key == K_o:
                    show_orbits = not show_orbits
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    mouse_drag = True
                    last_mouse = e.pos
            elif e.type == MOUSEBUTTONUP:
                mouse_drag = False
            elif e.type == MOUSEMOTION and mouse_drag:
                dx, dy = e.pos[0] - last_mouse[0], e.pos[1] - last_mouse[1]
                camera.yaw += dx * 0.5
                camera.pitch = max(-89, min(89, camera.pitch - dy * 0.5))
                camera.update()
                last_mouse = e.pos

        keys = pygame.key.get_pressed()
        move_speed = 0.8
        if keys[K_UP] or keys[K_w]:
            camera.distance = max(10, camera.distance - move_speed)
        if keys[K_DOWN] or keys[K_s]:
            camera.distance = min(200, camera.distance + move_speed)
        if keys[K_LEFT] or keys[K_a]:
            camera.target[0] -= move_speed
        if keys[K_RIGHT] or keys[K_d]:
            camera.target[0] += move_speed
        camera.update()

        if not paused:
            solar.update(dt * time_scale)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        camera.apply()
        solar.render(show_orbits)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()                                                                      
solar system.py
Displaying solar system.py.
