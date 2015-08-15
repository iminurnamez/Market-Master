import random
import pygame as pg
from .. import tools, prepare
from ..components.labels import Label, Button, ButtonGroup
from ..components.graphs import LineGraph, DataLine
from ..components.graph_styles import STOCK_GRAPH


class StockScreen(tools._State):
    def __init__(self):
        super(StockScreen, self).__init__()
        self.screen_rect = pg.display.get_surface().get_rect()
        self.font = prepare.FONTS["weblysleekuisl"]
        self.bold_font = prepare.FONTS["weblysleekuisb"]
        self.make_buttons()
        
    def startup(self, persistent):
        self.persist = persistent
        self.stock = self.persist["stock"]
        self.economy = self.persist["economy"]
        self.title = Label(self.font, 20, self.stock.name, "white", {"topleft": (350, 385)})
        self.time_scale = "Week"
        self.make_data_lines()
        self.make_graph()
        self.make_labels()
        self.game_clock = self.persist["economy"].game_clock
        
        
    def buy_stock(self):
        self.done = True
        self.next = "BUYSTOCK"
        self.persist["stock"] = self.stock
        
    def leave_state(self, next_state):
        self.next = next_state
        self.done = True
        
    def make_buttons(self):
        self.buttons = ButtonGroup()
        w, h = (64, 52)
        left = 5
        top = 100
        space = 64
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["exchange_button"],
                   call=self.leave_state, args="EXCHANGE")
        top += space
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["portfolio_button"],
                   call=self.leave_state, args="PORTFOLIO")
        top += space
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["market_button"],
                   call=self.leave_state, args="MARKETGRAPH")
        
        top = 445
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["show_button"],
                   call=self.show_all)
        top += space
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["hide_button"],
                   call=self.hide_all)
                   
        new_left = 300
        new_top = 355
        new_space = 110        
        small_w, small_h = (100, 30)           
        Button((new_left, new_top, small_w, small_h), self.buttons, text="Week",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="Week")
        new_left += new_space
        Button((new_left, new_top, small_w, small_h), self.buttons, text="Quarter",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="Quarter")
        new_left += new_space
        Button((new_left, new_top, small_w, small_h), self.buttons, text="Year",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="Year")
        new_left += new_space
        Button((new_left, new_top, small_w, small_h), self.buttons, text="5 Year",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="5 Year")
        new_left += new_space
        Button((new_left, new_top, small_w, small_h), self.buttons, text="10 Year",
                    text_color=pg.Color("gray80"), fill_color=pg.Color("gray20"), font=self.font, font_size=14,
                    call=self.change_time_scale, args="10 Year")
        
        buy_left = 800
        buy_top = 500
        buy_w, buy_h = 120, 50
        Button((buy_left, buy_top, buy_w, buy_h), self.buttons, text="Buy Shares",
                   font=self.font, font_size=20, fill_color=pg.Color("gray20"), call=self.buy_shares)
                   
    def buy_shares(self, *args):
        self.done  = True
        self.next = "BUYSTOCK"
        self.persist["stock"] = self.stock        
        
    def show_all(self, *args):
        for line in self.graph.data_lines:
            line.active = True
        self.graph.make_graph()
            
    def hide_all(self, *args):
        for line in self.graph.data_lines:
            line.active = False
    
    def make_labels(self):
        industry_avgs = self.economy.get_industry_averages()
        avgs = industry_avgs[self.stock.company.industry_name]
        self.labels = []
        today = self.stock.company.daily_history[-1]
        book_value_ps = today[1] / float(self.stock.num_shares)
        earnings_ps = today[6] / float(self.stock.num_shares)
        revenue_ps = today[3] / float(self.stock.num_shares)
        peratio = today[7]
        dividend = today[8]
        info = (("Cash", "${:,}".format(int(self.stock.company.cash))),
                   ("Assets", "${:,}".format(int(self.stock.company.assets))),
                   ("Debt", "${:,}".format(int(self.stock.company.debt))),
                   ("Share Price", "{:.2f}".format(self.stock.price)),
                   ("Book Value per Share", "${:.2f}".format(int(book_value_ps))),
                   ("Revenue per Share", "${:.2f}".format(revenue_ps)),
                   ("Earnings per Share", "${:.2f}".format(earnings_ps)),
                   ("P/E Ratio", "${:.2f}".format(earnings_ps)),
                   ("Dividend", "${:.2f}".format(earnings_ps)),
                   )
        cash, assets, debt = ("{:,}".format(int(num)) for num in avgs[:3])
        bv, rev, earn, pe, divs = ("{:.2f}".format(avg) for avg in avgs[3:])
        industry_info = (cash, assets, debt, bv, rev, earn, pe, divs)
        stock_info = (
                            ("P/E Ratio", "{:.2f}".format(self.stock.price / float(earnings_ps))),
                            ("Dividend", "{:.2f}".format(self.stock.dividend)),
                            )
                            
        
        
        top = 420
        left = 300
        left2 = 450
        left3 = 575
        left4 = 800
        
        self.labels.append(Label(self.bold_font, 14, "Industry Average", "gray80", {"topleft": (left3, 400)}))
        for text, industry_text in zip(info, industry_info):
            self.labels.append(Label(self.font, 14, text[0], "gray80", {"topleft": (left, top)}))
            self.labels.append(Label(self.font, 14, text[1], "gray80", {"topleft": (left2, top)}))
            if industry_text:
                self.labels.append(Label(self.font, 14, industry_text, "gray80", {"topleft": (left3, top)}))
            top += 16
        
        
        left10 = 720
        left11 = 820
        top10 = 400
        space10 = 20
        m = self.stock.company.management
        
        management_info = (
                ("Priorities", "{}".format(", ".join(m.priorities))), 
                ("Agression", m.aggression_names[m.aggression]),
                ("Debt Tolerance", m.aggression_names[m.debt_aversion]))
        self.labels.append(Label(self.bold_font, 14, "Management", "gray80", {"topleft": (left10, top10)}))
        top10 += space10
        for title, value in management_info:
            self.labels.append(Label(self.font, 14, title, "gray80", {"topleft": (left10, top10)}))            
            self.labels.append(Label(self.font, 14, value, "gray80", {"topleft": (left11, top10)}))            
            top10 += space10
            
    def make_graph(self):
        lines = self.data_lines[self.time_scale]
        self.graph = LineGraph((0, 0), self.screen_rect.size,
                                          lines, STOCK_GRAPH)
                                          
    def make_data_lines(self):    
        econ = self.persist["economy"]
        history = self.stock.company.daily_history
        stock_history = self.stock.price_history
        hist_len = len(history)
        current_day = econ.day
        names = ("Week", "Quarter", "Year", "5 Year", "10 Year")
        lines = {name: [] for name in names}
        if hist_len < 7:
            week = history[:]
            stock_week = stock_history[:]
        else:
            week = history[current_day - 6:]            
            stock_week = stock_history[current_day - 6:]            
        if hist_len < 91:
            quarter = history[:]
            stock_quarter = stock_history[:]
        else:
            quarter = history[current_day - 90:]
            stock_quarter = stock_history[current_day - 90:]
        if hist_len < 364:
            year = history[:]
            stock_year = stock_history[:]
        else:
            year = history[current_day - 363:]
            stock_year = stock_history[current_day - 363:]
        if hist_len < 364*5:
            if hist_len < 5:
                five_year = history[:]
                stock_five_year = stock_history[:]
            else:
                five_year = history[::5]
                stock_five_year = stock_history[::5]
        else:
            five_year = history[current_day - 1819::5]
            stock_five_year = stock_history[current_day - 1819::5]
        if hist_len < 3640:
            if hist_len < 10:
                ten_year = history[:]
                stock_ten_year = stock_history[:]
            else:    
                ten_year = history[::10]
                stock_ten_year = stock_history[::10]
        else:
            ten_year = history[current_day - 3639::10]            
            stock_ten_year = stock_history[current_day - 3639::10]            
            
        wkmin = min([x[0] for x in week])
        qmin = min([x[0] for x in quarter])
        yrmin = min([x[0] for x in year])
        fyrmin = min([x[0] for x in five_year])
        tyrmin = min([x[0] for x in ten_year])

        slices = week, quarter, year, five_year, ten_year       
        mins = wkmin, qmin, yrmin, fyrmin, tyrmin
        for name, slice_, slicemin in zip(names, slices, mins):
            book = [(x[0] - slicemin, x[1]/1000000.) for x in slice_]
            debt = [(x[0] - slicemin, x[2]/1000000.) for x in slice_]
            revenue = [(x[0] - slicemin, x[3]/1000000.) for x in slice_]
            expenses = [(x[0] - slicemin, x[4]/1000000.) for x in slice_]
            salaries = [(x[0] - slicemin, x[5]/1000000.) for x in slice_]
            earnings = [(x[0] - slicemin, x[6]/1000000.) for x in slice_]
            pe_ratios = [(x[0] - slicemin, x[7]) for x in slice_]
            divs = [(x[0] - slicemin, x[8]) for x in slice_]
            
            lines[name].append(DataLine(book, (102, 203, 157), "Book Value (Millions)"))
            lines[name].append(DataLine(book, (87,43,62), "Debt (Millions)"))
            lines[name].append(DataLine(revenue, (56,87,43), "Annual Revenue(Millions)"))
            lines[name].append(DataLine(expenses, (219, 109, 109), "Annual Expenses (Millions)"))
            lines[name].append(DataLine(salaries, (152, 76, 109), "Annual Payroll (Millions)"))
            lines[name].append(DataLine(earnings, (141,219,109), "Annual Earnings (Millions)"))
            lines[name].append(DataLine(earnings, (141,219,109), "P/E Ratio"))
            lines[name].append(DataLine(earnings, (141,219,109), "Dividend"))
        
        slices2 = stock_week, stock_quarter, stock_year, stock_five_year, stock_ten_year 
        for name, slice2, min2 in zip(names, slices2, mins):
            price_points = [(x[0] - min2, x[3]) for x in slice2]
            share_points = [(x[0]- min2, x[1]/10000.) for x in slice2]
            pe_points = [(x[0]- min2, x[1]/10000.) for x in slice2]
            lines[name].append(DataLine(price_points, (0,109,60), "Stock Price"))
            lines[name].append(DataLine(share_points, (136, 108, 217), "Shares (10,000s)"))
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
        mouse_pos = pg.mouse.get_pos()
        self.graph.update()
        self.buttons.update(mouse_pos)
        
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.graph.draw(surface)
        for label in self.labels:
            label.draw(surface)
        self.buttons.draw(surface)
        self.game_clock.draw(surface)
        self.title.draw(surface)        