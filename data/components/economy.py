import os
try:
    import CPickle as pickle
except ImportError:
    import pickle
from math import pi, cos, sin
import random
import pygame as pg
from .. import prepare
from .industry import Industry
from .industry_info import INDUSTRIES
from .labels import Label, Button, ButtonGroup
from .animation import Animation, Task
from .player import Player


TWOPI = pi * 2


class Economy(object):
    def __init__(self):
        self.interest_rate = .05
        conditions = ["Dismal", "Grizzly", "Bearish", "Flat",
                            "Bullish", "Taurific", "Phenomenal"]
        self.condition_names = {x: name for x, name in enumerate(conditions, start=-3)}
        colors = ("red", "orangered", "orange", "gray90", "yellowgreen", "greenyellow", "green")
        self.condition_colors = {x: color for x, color in enumerate(colors, start=-3)}
        self.next_conditions = {
                    -3: (-3, -2, -2, -1),
                    -2: (-3, -2, -2, -1, -1, -1, 0),
                    -1: (-3, -2, -2, -1, -1, -1, -1, 0, 0, 0, 0, 1, 1),
                    0: (-2, -1, -1, 2, 1, 1, 1, 0, 0, 0, 0),
                    1: (3, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, -1, -1),
                    2: (3, 2, 2, 1, 1, 1, 0),
                    3: (3, 2, 2, 1)
                }
        self.condition = 0
        
        hourly_change_ranges = [(.70, 1.01125), (.85,1.025), (.90, 1.05), (.95, 1.05),
                                              (.95, 1.10), (.975, 1.15), (.9875,1.3)]
        self.hourly_changes = {x: change for x, change in enumerate(hourly_change_ranges, start=-3)}                                     
        self.daily_interest_changes = {
                    -3: (1.0, 1.01),
                    -2: (1.0, 1.005),
                    -1: (1.0, 1.0025),
                    0: (1.0, 1.0),
                    1: (.975, 1.0),
                    2: (.95, 1.0),
                    3: (.9, 1.0)
                    }
        activity = ("Dead", "Tepid", "Tame", "Busy", "Hectic", "Manic")
        activity_chances = (25, 50, 100, 200, 400, 700) #chance in 1000 that price will move
        self.activity_chances = {x: chance for x, chance in enumerate(activity_chances)}
        self.activity_names = {x: name for x, name in enumerate(activity)}
        self.activity = 2
        
        self.make_industries(INDUSTRIES)
        
        
        self.companies = []   
        for industry in self.industries:
            self.companies.extend(industry.companies)
        
       
        self.hours = 0
        self.day = 0
        self.sim_speeds = {0: "Paused",
                                     1: "Very Slow",
                                     2: "Slow",
                                     3: "Normal",
                                     4: "Fast",
                                     5: "Very Fast"}
        self.hour_lengths = {0: 0,
                                     1: 10000,
                                     2: 5000,
                                     3: 2500,
                                     4: 625,
                                     5: 100}
        self.sim_speed = 5
        self.current_quarter = 1
        self.timer = 0
        self.game_clock = GameClock((16, 20), self)
        self.ticker_tape = TickerTape()
        
        #Seed Economy
        for _ in range(1000):
            self.update(100, Player())
        
    def save(self, player):
        #can't pickle surfaces, oops
        self.game_clock = None
        self.ticker_tape = None
        for c in self.companies:
            c.investments.empty()
        e_path = os.path.join("resources", "saves", "econsave.pickle")
        p_path = os.path.join("resources", "saves", "playersave.pickle")
        with open(e_path, "wb") as e_save:
            econ = pickle.dump(self, e_save)
        with open(p_path, "wb") as p_save:
            player_ = pickle.dump(player, p_save)
            
    def update(self, dt, player):
        self.game_clock.update(dt, self.hour_lengths[self.sim_speed])
        if self.hour_lengths[self.sim_speed]:
            self.timer += dt
            if self.timer >= self.hour_lengths[self.sim_speed]:
                self.timer -= self.hour_lengths[self.sim_speed]
                self.hours += 1
                self.hourly_update()
                
            if self.hours == 8:
                self.day += 1
                self.hours = 0
                self.daily_update()
                self.game_clock.reset()
                
                if not self.day % 7:
                    self.weekly_update()
       
                if not self.day % 91:
                    self.ticker_tape.news_items = []
                    self.quarterly_update(player)
            
    def get_industry_averages(self):     
        averages = {}
        for industry in self.industries:
            num = 0.
            cash = 0
            assets = 0
            debt = 0
            bv = 0
            rev = 0
            earn = 0
            pe_ratio = 0
            dividends = 0
            for c in industry.companies:
                num += 1
                cash += c.cash
                assets += c.assets
                debt += c.debt
                bv += c.daily_history[-1][1] / float(c.stock.num_shares)
                rev +=  c.daily_history[-1][3] / float(c.stock.num_shares)
                earn += c.daily_history[-1][6] / float(c.stock.num_shares)
                pe_ratio += float(c.stock.price) / (earn / float(c.stock.num_shares))
                dividends += float(c.stock.dividend)
            if num:
                averages[industry.name] = cash/num, assets/num, debt/num, bv/num, rev/num, earn/num, pe_ratio/num, dividends/num
            else:
                averages[industry.name] = 0, 0, 0, 0, 0, 0, 0, 0
        return averages
        
    def update_condition(self):
        chance = abs(self.condition)
        if random.randint(0, 10) <= chance:
            self.condition = random.choice(self.next_conditions[self.condition])
            self.interest_rate = self.interest_rate * random.uniform(*self.daily_interest_changes[self.condition])
            self.interest_rate = max(0, min(.15, self.interest_rate))
    
    def hourly_update(self):        
        #change prices for stocks
        for c in self.companies:
            c.hourly_update(self)
        
    def daily_update(self):
        self.update_condition()
        for c in self.companies:
            c.daily_update(self)
        
    def weekly_update(self):
        #update_condition - more variance than daily
        for c in self.companies:
            c.weekly_update(self)
        
    def monthly_update(self):
        for c in self.companies:
            c.monthly_update(self)
        
    def quarterly_update(self, player):
        for c in self.companies:
            c.quarterly_update(self, player)        
        
    def make_industries(self, industries):
            self.industries = []
            for ind in industries:
                self.industries.append(Industry(ind, self))
    
    
class GameClock(object):
    def __init__(self, topleft, economy):
        self.economy = economy
        self.image = prepare.GFX["clockicon"]
        self.rect = self.image.get_rect(topleft=topleft)
        self.hour_angle = pi
        self.minute_angle = pi / 2.
        self.buttons = ButtonGroup()
        font = prepare.FONTS["weblysleekuisb"]
        self.speed_name = self.economy.sim_speeds[self.economy.sim_speed]
        
        yrs, days = divmod(self.economy.day, 364)
        self.date = Label(font, 14, "Yr: {} Day{}".format(yrs + 1, days), "gray80",
                                 {"midbottom": self.rect.midtop})
        self.label = Label(font, 14, self.speed_name, "gray80",
                                 {"midtop": self.rect.midbottom})
        Button((self.rect.left, self.label.rect.bottom - 5, 20, 20), self.buttons, text="-",
                  font=font, font_size=16, call=self.decrease_speed)        
        Button((self.rect.right - 20, self.label.rect.bottom - 5, 20, 20), self.buttons, text="+",
                  font=font, font_size=16, call=self.increase_speed)
                  
    def decrease_speed(self, *args):
        self.economy.sim_speed = max(0, self.economy.sim_speed - 1)
        self.speed_name = self.economy.sim_speeds[self.economy.sim_speed]
        self.label.set_text(self.speed_name)
        
    def increase_speed(self, *args):
        self.economy.sim_speed = min(5, self.economy.sim_speed + 1)
        self.speed_name = self.economy.sim_speeds[self.economy.sim_speed]
        self.label.set_text(self.speed_name)
        
    def update(self, dt, hour_length):
        if hour_length != 0:
            self.hour_angle -= ((TWOPI / 12.) / float(hour_length)) * dt
            self.hour_angle = self.hour_angle % TWOPI        
            self.hour_endpoint = (self.rect.centerx + cos(self.hour_angle) * 26,
                                           self.rect.centery - sin(self.hour_angle) * 26)
        mouse_pos = pg.mouse.get_pos()
        self.buttons.update(mouse_pos)
        yrs, days = divmod(self.economy.day, 364)
        self.date.set_text("Yr {} Day {}".format(yrs + 1, days))
        
    def get_event(self, event):
        self.buttons.get_event(event)
        
    def reset(self):
        #set clock to 9am
        self.hour_angle = pi
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        pg.draw.line(surface, pg.Color("gray20"), self.rect.center, self.hour_endpoint)
        self.buttons.draw(surface)
        self.label.draw(surface)
        self.date.draw(surface)
                
     
class TickerLabel(object):
    
    def __init__(self, news_item, midleft):
        self.font = prepare.FONTS["weblysleekuisb"]
        self.label = Label(self.font, 16, news_item, "gray80", {"midleft": midleft})
        self.done = False
        
    def draw(self, surface):
        self.label.draw(surface)

        
class TickerTape(object):
    def __init__(self):
        top = 520
        self.rect = pg.Rect(0, top, prepare.SCREEN_SIZE[0], prepare.SCREEN_SIZE[1] - top) 
        self.duration = 9000 
        self.news_items = []
        self.labels = []
        self.start_pos = self.rect.right + 10, self.rect.centery
        self.animations  = pg.sprite.Group()
        
    def set_done(self, ticker):
        ticker.done = True
        
    def add_news(self, news_item):
        self.news_items.append(news_item)
        
    def update(self, dt):
        self.animations.update(dt)
        self.labels = [x for x in self.labels if not x.done]
        
        if self.news_items:
            if not self.labels or (self.labels[-1].label.rect.right < prepare.SCREEN_SIZE[0] - 60):
                item = self.news_items[0]
                ticker = TickerLabel(item, self.start_pos)
                self.labels.append(ticker)
                ani = Animation(x=-500, duration=self.duration, round_values=True)
                ani.start(ticker.label.rect)
                task = Task(self.set_done, self.duration, args=(ticker,))
                self.animations.add(task, ani)
                if len(self.news_items) > 1:
                    self.news_items = self.news_items[1:]
                else:
                    self.news_items = []

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(43,68,87), self.rect)
        pg.draw.line(surface, pg.Color("gray40"), self.rect.topleft, self.rect.topright, 2)        
        for label in self.labels:
            label.draw(surface)
            