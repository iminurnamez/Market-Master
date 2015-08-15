from operator import attrgetter
from random import shuffle
from itertools import cycle
import pygame as pg
from .. import tools, prepare
from ..components.labels import Label, Button, ButtonGroup
from ..components.graphs import DataLine, LineGraph
from ..components.graph_styles import MARKET_GRAPH
from ..components.line_colors import LINE_COLORS


class MarketGraph(tools._State):
    def __init__(self):
        super(MarketGraph, self).__init__()
        self.screen_rect = pg.display.get_surface().get_rect()
        self.font = prepare.FONTS["weblysleekuisl"]
        self.make_buttons()
        #                                             num_data_points, step   
        self.time_scale = "Week"
    
    
                                          
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
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["exchange_button"],
                   call=self.leave_state, args="EXCHANGE", click_sound=click)
        
        top = 445
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["show_button"],
                   call=self.show_all, click_sound=click)
        top += space
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["hide_button"],
                   call=self.hide_all, click_sound=click)
             
        new_left = 300
        new_top = 350
        new_space = 110        
        small_w, small_h = (100, 30)           
        Button((new_left, new_top, small_w, small_h), self.buttons, text="Week",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="Week", click_sound=click)
        new_left += new_space
        Button((new_left, new_top, small_w, small_h), self.buttons, text="Quarter",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="Quarter", click_sound=click)
        new_left += new_space
        Button((new_left, new_top, small_w, small_h), self.buttons, text="Year",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="Year", click_sound=click)
        new_left += new_space
        Button((new_left, new_top, small_w, small_h), self.buttons, text="5 Year",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="5 Year", click_sound=click)
        new_left += new_space
        Button((new_left, new_top, small_w, small_h), self.buttons, text="10 Year",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="10 Year", click_sound=click)
      
        
    def show_all(self, *args):
        for line in self.graph.data_lines:
            line.active = True
        self.graph.make_graph()
            
    def hide_all(self, *args):
        for line in self.graph.data_lines:
            line.active = False
            
    def make_labels(self):
        self.labels = []
        e = self.persist["economy"]
        info = (("Economic Outlook", "{:}".format(e.condition_names[e.condition])),
                   ("Interest Rate", "{:.2f}%".format(e.interest_rate * 100)),
                   ("Market Activity", "{}".format(e.activity_names[e.activity])))
        top = 400
        left = 700
        left2 = 930
        for text, val_text in info:
            self.labels.append(Label(self.font, 16, text, "gray80", {"topleft": (left, top)}))
            color = "gray80"
            if text == "Economic Outlook":
                color = e.condition_colors[e.condition]
            self.labels.append(Label(self.font, 16, val_text,  color, {"topleft": (left2, top)}))
            top += 24
            
    def leave_state(self, next_state):
        self.next = next_state
        self.done = True
        
    def startup(self, persistent):
        self.persist = persistent
        self.time_scale = "Week"
        self.make_data_lines()
        self.make_graph()
        self.make_labels()
        
        
        
    def make_graph(self):
        lines = self.data_lines[self.time_scale]
        self.graph = LineGraph((0, 0), self.screen_rect.size,
                                          lines, MARKET_GRAPH)
                                          
    def make_data_lines(self):    
        econ = self.persist["economy"]
        companies = sorted(econ.companies, key=attrgetter("symbol"))
        colors_ = LINE_COLORS[:]
        shuffle(colors_)
        lines = {"Week": [], "Quarter": [], "Year": [],
                                   "5 Year": [], "10 Year": []}
        colors = cycle(colors_)
        current_day = econ.day
        for c in companies:
            color = next(colors)
            history = c.stock.price_history
            hist_len = len(history)
            if hist_len < 7:
                week = history[:]
            else:
                week = history[current_day - 6:]            
            if hist_len < 91:
                quarter = history[:]
            else:
                quarter = history[current_day - 90:]
            if hist_len < 364:
                year = history[:]
            else:
                year = history[current_day - 363:]
            if hist_len < 364*5:
                if hist_len < 5:
                    five_year = history[:]
                else:
                    five_year = history[::5]
            else:
                five_year = history[current_day - 1819::5]
            if hist_len < 3640:
                if hist_len < 10:
                    ten_year = history[:]
                else:    
                    ten_year = history[::10]
            else:
                ten_year = history[current_day - 3639::10]            
            
            wkmin = min([x[0] for x in week])
            qmin = min([x[0] for x in quarter])
            yrmin = min([x[0] for x in year])
            fyrmin = min([x[0] for x in five_year])
            tyrmin = min([x[0] for x in ten_year])
            
            wk = [(x[0] - wkmin, x[3]) for x in week]
            q = [(x[0] - qmin, x[3]) for x in quarter]
            yr = [(x[0] - yrmin, x[3]) for x in year]
            fyr = [(x[0] - fyrmin, x[3]) for x in five_year]
            tyr = [(x[0] - tyrmin, x[3]) for x in ten_year]
            
            lines["Week"].append(DataLine(wk, color, c.symbol))
            lines["Quarter"].append(DataLine(q, color, c.symbol))       
            lines["Year"].append(DataLine(yr, color, c.symbol))
            lines["5 Year"].append(DataLine(fyr, color, c.symbol))
            lines["10 Year"].append(DataLine(tyr, color, c.symbol))
        self.data_lines = lines
        
    def change_time_scale(self, time_scale):
        d = self.data_lines
        for line1, line2 in zip(d[self.time_scale], d[time_scale]):
            line2.active = line1.active
        self.time_scale = time_scale
        if not any((line.active for line in d[self.time_scale])):    
            for line in d[self.time_scale]:
                line.active = True
        self.make_graph()     
        
    def quit_game(self):
        self.done = True
        self.quit = True
        self.persist["economy"].save(self.persist["player"])
        
    def get_event(self, event):
        self.graph.get_event(event)
        self.buttons.get_event(event)
        if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
            self.quit_game()
        elif event.type == pg.QUIT:
            self.quit_game()
    
    def update(self, keys, dt):
        self.graph.update()
        mouse_pos = pg.mouse.get_pos()
        self.buttons.update(mouse_pos)
        
    
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.graph.draw(surface)
        for label in self.labels:
            label.draw(surface)
        self.buttons.draw(surface)
        
       