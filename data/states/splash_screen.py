import pygame as pg
from .. import tools, prepare
from ..components.labels import Label
from ..components.animation import Animation, Task

class SplashScreen(tools._State):
    def __init__(self):
        super(SplashScreen, self).__init__()
        self.owl_sound  = prepare.SFX["owl_sound"]
        self.screen_rect = pg.display.get_surface().get_rect()
        sr = self.screen_rect
        self.next = "TITLE"
        self.font  = prepare.FONTS["PerfectDOS"]
        self.animations = pg.sprite.Group()
        self.owl = Owl(self.screen_rect.center)        
        task = Task(self.owl.fade_in, 10, args=(self.owl.fade, self.owl.fade_out))
        task2 = Task(self.leave_state, 11000)
        self.animations.add(task, task2)
        self.owl_sound.play()

    def leave_state(self):
        self.persist = {}
        self.done = True
                
    def update(self, keys, dt):
        self.animations.update(dt)
        self.owl.update(dt)

    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.owl.draw(surface)
        
        
class Owl(object):
    def __init__(self, center):
        space = 86
        font  = prepare.FONTS["weblysleekuisb"]
        ears, face, body, feet = ("^^", "(0,0)", "/###\\", "##")
        midtops = [(center[0], center[1] - 135), (center[0], center[1] - space),
                        (center[0], center[1]), (center[0], center[1] + 65), (center[0], center[1] + 20)]
        
        self.ears = Label(font, 84, ears, "gray80", {"midtop": midtops[0]}, bg="black")
        self.face = Label(font, 84, face, "gray80", {"midtop": midtops[1]}, bg="black")
        self.body = Label(font, 84, body, "gray80", {"midtop": midtops[2]}, bg="black")
        self.feet = Label(font, 84, feet, "gray80", {"midtop": midtops[3]}, bg="black")
        for x in (self.ears, self.face, self.body, self.feet):
            x.image.set_colorkey(pg.Color("black"))#x.image.convert()
            x.alpha = 0
         
        self.title = Label(font, 84, "Topleft Games", "gray80", {"midtop": midtops[4]}, bg="black")
        self.title.image.set_colorkey(pg.Color("black"))
        self.title.alpha = 0
        self.animations = pg.sprite.Group()
        self.fade_time = 5000
        
    def fade_in(self, callback, next_callback):
        ear = Animation(alpha=255, duration=int(self.fade_time * .5), round_values=True)
        ear.start(self.ears)
        face = Animation(alpha=255, duration=self.fade_time * .5, round_values=True)
        face.start(self.face)
        body = Animation(alpha=255, duration=int(self.fade_time * .5), round_values=True)
        body.start(self.body)
        feet = Animation(alpha=255, duration=int(self.fade_time * .5), round_values=True)
        feet.callback = self.fade
        feet.start(self.feet)
        self.animations.add(ear, face, body, feet)
        
    def fade(self):
        ear = Animation(alpha=0, duration=int(self.fade_time * .5), round_values=True)
        ear.start(self.ears)
        body = Animation(alpha=0, duration=int(self.fade_time * .5), round_values=True)
        body.start(self.body)
        feet = Animation(alpha=0, duration=int(self.fade_time * .5), round_values=True)
        feet.start(self.feet)
        title = Animation(alpha=255, duration=self.fade_time, round_values=True)
        title.callback = self.fade_out
        title.start(self.title)
        
        self.animations.add(ear, body, feet, title)
        
    def fade_out(self):
        face = Animation(alpha=0, duration=int(self.fade_time*.6), round_values=True)
        face.start(self.face)
        title = Animation(alpha=0, duration=int(self.fade_time*.6), round_values=True)
        title.start(self.title)
        self.animations.add(face, title)
        
    def update(self, dt):
        self.animations.update(dt)
        for x in (self.ears, self.face, self.body, self.feet, self.title):
            x.image.set_alpha(x.alpha)
    
    def draw(self, surface):
        for x in (self.ears, self.face, self.feet,  self.body, self.title):
            x.draw(surface)