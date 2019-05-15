
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window

from functools import partial
from random import random as rnd
import math as m


class Particle:
    def __init__(self, x, y, speed, size, id, w, h):
        self.color = [x / w, y / w, 1]
        self.pos = [x, y]
        self.vel = [2 * (rnd() - 0.5) * speed, 2 * (rnd() - 0.5) * speed]
        self.mass = size * (rnd() + 1)
        self.size = (self.mass, self.mass)
        self.id = id
        self.hover = False


class EvoCanvasApp(App):
    def check_collision(self, p1, p2):
        x1, y1 = p1.pos
        w1, h1 = p1.size
        x2, y2 = p2.pos
        w2, h2 = p2.size

        # if ((x1 + w1 >= x2 and x1 <= x2) or (x1 + w1 <= x2 + w2 and x1 >= x2 + w2)) and ((y1 + h1 >= y2 and y1 <= y2) or (y1 + h1 <= y2 + h2 and y1 >= y2 + h2)):
        #     return True
        r = (w1 + w2) / 2
        if m.sqrt((x1 - x2 + (w1 - w2) / 2)**2 + (y1 - y2 + (h1 - h2) / 2)**2) <= r:
            return True
        return False

    def draw(self):
        self.wid.canvas.clear()
        self.label1.text = str(len(self.particles))
        with self.wid.canvas:
            for i in self.particles:
                if i.hover or i.id == self.selected:
                    Color(1, 1, 1)
                    Ellipse(pos=(i.pos[0] + self.wid.x - 2, i.pos[1] + self.wid.y - 2), size=(i.size[0] + 4, i.size[1] + 4))
                Color(*i.color)
                Ellipse(pos=(i.pos[0] + self.wid.x, i.pos[1] + self.wid.y), size=i.size)

    def collision(self, i, p1, p2):
        if self.check_collision(p1, p2):
            m1 = p2.mass / p1.mass
            m2 = p1.mass / p2.mass
            vel_1_tmp = [m1 * p2.vel[0], m1 * p2.vel[1]]
            vel_2_tmp = [m2 * p1.vel[0], m2 * p1.vel[1]]

            p1.vel, p2.vel = vel_1_tmp, vel_2_tmp

            dx = 0
            dy = 0
            x1, y1 = p1.pos
            w1, h1 = p1.size
            x2, y2 = p2.pos
            w2, h2 = p2.size

            if x1 != x2:
                g = m.atan(abs(y1-y2)/abs(x1-x2))
            else:
                g = m.pi * (-1, 1)[y1 > y2] / 2

            d = ((w1 + w2) / 2 - m.sqrt((x1 + w1 / 2 - x2 - w2 / 2)**2 + (y1 + h1 / 2 - y2 - h2 / 2)**2)) / 2
            dx = m.cos(g) * d * (1, -1)[x2 > x1]
            dy = m.sin(g) * d * (1, -1)[y2 > y1]
            p1.pos = [p1.pos[0] + dx, p1.pos[1] + dy]
            p2.pos = [p2.pos[0] - dx, p2.pos[1] - dy]

    def set_mouse_pos(self, p, dt=0):
        self.pos_schedule.cancel()
        self.prev_mouse = self.mouse[:]
        self.mouse = p
        self.pos_schedule = Clock.schedule_once(self.update_mouse, 0.1)

    def update_mouse(self, dt):
        self.set_mouse_pos(self.mouse)

    def tick(self, dt):
        self.update_window_size()

        def d(val):
            return m.sqrt((val.pos[0])**2 + (val.pos[1])**2)

        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i:]:
                self.collision(i, p1, p2)

            mx = self.mouse[0] - self.wid.x
            my = self.mouse[1] - self.wid.y
            if m.sqrt((mx - p1.pos[0] - p1.size[0] / 2)**2 + (my - p1.pos[1] - p1.size[1] / 2)**2) < p1.size[0]:
                p1.hover = True
                if self.clicked and self.selected == -1:
                    self.selected = p1.id
                    self.clicked = False
            else:
                p1.hover = False

            if self.selected == p1.id or self.ctrl:
                p1.vel = [self.mouse[0] - self.prev_mouse[0], self.mouse[1] - self.prev_mouse[1]]

            p1.pos = [p1.pos[0] + p1.vel[0], p1.pos[1] + p1.vel[1]]

            if p1.pos[0] + p1.size[0] > self.w:
                p1.vel[0] *= -1
                p1.pos[0] -= p1.pos[0] + p1.size[0] - self.w
            elif p1.pos[0] < 0:
                p1.vel[0] *= -1
                p1.pos[0] -= p1.pos[0]
            if p1.pos[1] + p1.size[1] > self.h:
                p1.vel[1] *= -1
                p1.pos[1] -= p1.pos[1] + p1.size[1] - self.h
            elif p1.pos[1] < 0:
                p1.vel[1] *= -1
                p1.pos[1] -= p1.pos[1]

        self.draw()

        if dt:
            self.label2.text = str(int(1/dt)) + ' FPS'

        self.dt = dt
        Clock.schedule_once(self.tick)

    def add(self, n, *largs):
        self.particles += [Particle(rnd() * self.w, rnd() * self.h, self.speed, self.size, len(self.particles) + i, self.w, self.h) for i in range(n)]

    def update_window_size(self):
        self.w, self.h = Window.size
        self.h -= 50

    def sub(self, n, *largs):
        if not n:
            n = len(self.particles)
        if len(self.particles) >= n:
            self.particles = self.particles[:-n]
        else:
            self.particles = []

    def on_mouse_down(self, *args):
        self.clicked = True

    def on_mouse_up(self, *args):
        for i in self.particles:
            if i.id == self.selected:
                i.vel[0] = self.mouse[0] - self.prev_mouse[0]
                i.vel[1] = self.mouse[1] - self.prev_mouse[1]
        self.clicked = False
        self.selected = -1

    def on_key_down(self, *args):
        if args[1] == 305:
            self.ctrl = True

    def on_key_up(self, *args):
        if args[1] == 305:
            self.ctrl = False

    def build(self):
        self.clicked = False
        self.selected = -1
        self.speed = 3
        self.size = 20
        self.mouse = (0, 0)
        self.ctrl = False
        Window.bind(mouse_pos=lambda w, p: self.set_mouse_pos(p))
        Window.bind(on_touch_down=self.on_mouse_down)
        Window.bind(on_touch_up=self.on_mouse_up)
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)
        self.pos_schedule = Clock.schedule_once(self.update_mouse, 0.1)
        self.update_window_size()

        self.particles = []
        self.add(100)

        self.wid = Widget(size=(self.w, self.h))

        self.label1 = Label(text='0')
        self.label2 = Label(text='0 FPS')

        btn_add = Button(text='+ 10', on_press=partial(self.add, 10))
        btn_add1 = Button(text='+ 1', on_press=partial(self.add, 1))
        btn_sub = Button(text='- 10', on_press=partial(self.sub, 10))
        btn_clear = Button(text='Clear', on_press=partial(self.sub, 0))

        layout = BoxLayout(size_hint=(1, None), height=50)
        layout.add_widget(btn_add)
        layout.add_widget(btn_add1)
        layout.add_widget(btn_sub)
        layout.add_widget(btn_clear)
        layout.add_widget(self.label1)
        layout.add_widget(self.label2)

        root = BoxLayout(orientation='vertical')
        root.add_widget(self.wid)
        root.add_widget(layout)

        self.tick(0)

        return root


if __name__ == '__main__':
    EvoCanvasApp().run()
