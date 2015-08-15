import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
from string import ascii_uppercase as UPPERS
import random
import pygame as pg
from .. import tools, prepare
from ..components.labels import Label, Button, ButtonGroup
from ..components.animation import Animation, Task
from ..components.player import Player
from ..components.economy import Economy, TickerTape, GameClock


class TitleScreen(tools._State):
    def __init__(self):
        super(TitleScreen, self).__init__()
        self.screen_rect = pg.display.get_surface().get_rect()
        sr = self.screen_rect
        self.surf = pg.Surface(sr.size).convert()
        self.bold_font = prepare.FONTS["weblysleekuisb"]
        self.label = Label(self.bold_font, 128, "Market Master", (0, 109, 60), {"midbottom": (sr.centerx, sr.top - 10)})
        self.animations = pg.sprite.Group()
        ani = Animation(centery=sr.centery - 110, duration=2000, round_values=True, transition="out_bounce")
        ani.start(self.label.rect)
        ani.callback = self.make_buttons
        self.animations.add(ani)
        self.numbers = Numbers()
        shuffler = Task(self.numbers.swap_rects, 100, -1)
        self.animations.add(shuffler)
        self.fade_out_time = 2000
        self.negative = prepare.SFX["negative_2"]
        self.buttons = ButtonGroup()
    
    def make_buttons(self):
        screen_rect = pg.display.get_surface().get_rect()
        click = prepare.SFX["click_2"]
        
        w, h  = 320, 90
        left = screen_rect.centerx - (w//2)
        top1 = screen_rect.centery
        top2 = screen_rect.centery + h + 40
        Button((left, top1, w, h), self.buttons, text="New Game", font=self.bold_font, font_size=36,
                    fill_color=pg.Color("gray10"), text_color=pg.Color("gray60"), call=self.new_game,
                    click_sound=click, hover_text_color=pg.Color("gray80"), hover_text="New Game",
                    hover_fill_color=pg.Color("gray10"))        
        Button((left, top2, w, h), self.buttons, text="Load Game", font=self.bold_font, font_size=36,
                    fill_color=pg.Color("gray10"), text_color=pg.Color("gray60"), call=self.load_game,
                    click_sound=click, hover_text_color=pg.Color("gray80"), hover_text="Load Game",
                    hover_fill_color=pg.Color("gray10"))
        
    def new_game(self, *args):
        self.done = True
        self.next = "EXCHANGE"
        self.persist["economy"] = Economy()
        self.persist["player"] = Player()
        
    def load_game(self, *args):
        try:
            e_path = os.path.join("resources", "saves", "econsave.pickle")
            p_path = os.path.join("resources", "saves", "playersave.pickle")
            with open(e_path, "rb") as e_save:
                econ = pickle.load(e_save)
            with open(p_path, "rb") as p_save:    
                player = pickle.load(p_save)
            econ.ticker_tape = TickerTape()
            econ.game_clock = GameClock((6, 20), econ)
            self.persist["economy"] = econ
            self.persist["player"] = player
            self.done = True
            self.next = "EXCHANGE"
        #ain't got time to be more specific
        except:
            self.negative.play()
        
    def quit_game(self):
        self.done = True
        self.quit = True
        
    def startup(self, persistent):
        self.persist = persistent
        pg.mixer.music.load(prepare.MUSIC["DST-TowerDefenseTheme_1"])
        pg.mixer.music.play(-1)
        
    def get_event(self, event):
        self.buttons.get_event(event)
        if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
            self.quit_game()
        elif event.type == pg.QUIT:
            self.quit_game()
       
                
    def update(self, keys, dt):
        self.animations.update(dt)
        mouse_pos = pg.mouse.get_pos()
        self.buttons.update(mouse_pos)

    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.numbers.draw(surface)
        self.label.draw(surface)
        self.buttons.draw(surface)
        
        
        
class Numbers(object):
    def __init__(self):
        left = [RandomLabel((0, y)) for y in range(0, 600, 20)]
        middle = [RandomLabel((345, y)) for y in range(0, 580, 18)]
        right = [RandomLabel((695, y)) for y in range(0, 580, 18)]
        self.labels = left
        self.labels.extend(middle)
        self.labels.extend(right)
    
    def swap_rects(self):
        rects = [x.label.rect for x in self.labels]
        random.shuffle(rects)
        for label, rect in zip(self.labels, rects):
            label.label.rect = rect         
        
    def draw(self, surface):
        for label in self.labels:
            label.draw(surface)
            
        
class RandomLabel(object):
    font  = prepare.FONTS["PerfectDOS"]
    
    def __init__(self, topleft):
        symbol = "".join((random.choice(UPPERS) for _ in range(3)))
        num1 = random.uniform(3.00, 150.00)
        num2 = random.uniform(3.00, 150.00)
        num3 = random.uniform(3.00, 150.00)
        num4 = num3 * random.uniform(.97, 1.03)
        num5 = num4 - num3
        
       
        text = "{}{:8.2f}{:8.2f}{:8.2f}{:8.2f} {:+.2f}".format(symbol, num1, num2, num3, num4, num5)
        self.label = Label(self.font, 14, text, "gray70", {"topleft": topleft}, "black")
        
    def draw(self, surface):
        self.label.draw(surface)