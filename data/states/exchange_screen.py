from operator import attrgetter
import pygame as pg
from .. import tools, prepare
from ..components.labels import Label, Button, ButtonGroup


class StockLabel(object):
    def __init__(self, stock, topleft, num, player):
        self.stock = stock
        self.topleft = topleft
        self.font = prepare.FONTS["PerfectDOS"]
        self.make_labels(num, player)
        
    def make_labels(self, num, player):    
        s = self.stock
        self.template = "{:<8}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}{:<+7.2f}"
        if not num % 2:
            bg = "gray5"
        else:
            bg = "gray10"
        reg_color = "gray60"
        high_color = "gray90"
        if s.name in player.portfolio.stocks:
            avg = player.portfolio.stocks[s.name][2]
            if s.price >= avg:
                reg_color = "darkgreen"
                high_color = "green"
            else:
                reg_color = "darkred"
                high_color = "red"
            
        
        text = self.template.format(s.symbol, s.year_low, s.year_high, s.open_price, s.price, s.price - s.open_price)
        self.regular_label = Label(self.font, 14, text, reg_color, {"topleft": self.topleft}, bg)
        self.highlight = Label(self.font, 14, text, high_color, {"topleft": self.topleft}, bg)
        self.label = self.regular_label
     
    def set_text(self, player):
        s = self.stock
        if s.name in player.portfolio.stocks:
            avg = player.portfolio.stocks[s.name][2]
            if s.price >= avg:
                reg_color = "darkgreen"
                high_color = "green"
            else:
                reg_color = "darkred"
                high_color = "red"
            self.regular_label.color = pg.Color(reg_color)
            self.highlight.color = pg.Color(high_color)
        
        text = self.template.format(s.symbol, s.year_low, s.year_high, s.open_price, s.price, s.price - s.open_price)
        self.regular_label.set_text(text)
        self.highlight.set_text(text)
        
    def update(self, mouse_pos):
        self.label = self.regular_label
        if self.regular_label.rect.collidepoint(mouse_pos):
            self.label = self.highlight
                
    def draw(self, surface):
        self.label.draw(surface)

        
class ExchangeScreen(tools._State):
    def __init__(self):
        super(ExchangeScreen, self).__init__()
        self.screen_rect = pg.display.get_surface().get_rect()
        self.bold_font = prepare.FONTS["weblysleekuisb"]
        self.font = prepare.FONTS["PerfectDOS"]
        headers = ("Company", "52WkLo",
                         "52WkHi", "Open", "Price", "Change")
        template = "{:8}{:8}{:8}{:11}{:10}{:7}"
        text = template.format(*headers)
        self.header = Label(self.bold_font, 14, text, "antiquewhite", {"topleft": (140, 5)})
        self.header2 = Label(self.bold_font, 14, text, "antiquewhite", {"topleft": (580, 5)})
        self.make_buttons()
        
    def make_buttons(self):
        click = prepare.SFX["click_2"]
        self.buttons = ButtonGroup()
        w, h = (64, 52)
        left = 15
        top = 150
        space = 64
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["portfolio_button"],
                   call=self.leave_state, args="PORTFOLIO", click_sound=click)
        top += space
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["market_button"],
                   call=self.leave_state, args="MARKETGRAPH", click_sound=click)
        
    def leave_state(self, next_state):
        self.next = next_state
        self.done = True
        
    def startup(self, persistent):
        self.persist = persistent
        self.economy = self.persist["economy"]
        self.make_labels()
        self.game_clock = self.economy.game_clock
    
    def make_labels(self):
        player = self.persist["player"]
        companies = self.economy.companies
        stocks = sorted([c.stock for c in companies], key=attrgetter("symbol"))
        top = 30
        left = 140
        space = 18
        self.stock_labels = []
        num = 0
        for stock in stocks:
            self.stock_labels.append(StockLabel(stock, (left, top), num, player))
            top += space
            num += 1
            if top > self.economy.ticker_tape.rect.top - space:
                top = 30
                left = 580
                
    def quit_game(self):
        self.done = True
        self.quit = True
        self.persist["economy"].save(self.persist["player"])
        
    def get_event(self, event):
        self.buttons.get_event(event)
        self.economy.game_clock.get_event(event)
        if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
            self.quit_game()
        elif event.type == pg.QUIT:
            self.quit_game()
        elif event.type == pg.MOUSEBUTTONUP:
            for label in self.stock_labels:
                if label.highlight.rect.collidepoint(event.pos):
                    self.done = True
                    self.next = "STOCKSCREEN"
                    self.persist["stock"] = label.stock
        
    def update(self, keys, dt):
        mouse_pos = pg.mouse.get_pos()
        self.economy.update(dt, self.persist["player"])
        self.economy.ticker_tape.update(dt)
        self.buttons.update(mouse_pos)
        for label in self.stock_labels:
            label.set_text(self.persist["player"])
            label.update(mouse_pos)
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.header.draw(surface)
        self.header2.draw(surface)
        for label in self.stock_labels:
            label.draw(surface)
        self.buttons.draw(surface)
        self.game_clock.draw(surface)
        self.economy.ticker_tape.draw(surface)        