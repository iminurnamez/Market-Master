import pygame as pg
from ..import tools, prepare
from ..components.labels import Label, Button, ButtonGroup


class StockSaleScreen(tools._State):
    def __init__(self):
        super(StockSaleScreen, self).__init__()
        screen = pg.display.get_surface().get_rect()
        self.window = pg.Rect(0, 0, 400, 450)
        self.window.center = screen.center
        self.bg_color = pg.Color("gray5")
        self.frame_color = pg.Color("gray20")
        self.font = prepare.FONTS["weblysleekuisl"]
        self.title = Label(prepare.FONTS["weblysleekuisb"], 24, "Sell Shares",
                                "gray80", {"midtop": (self.window.centerx, self.window.top + 5)})
        self.negative = prepare.SFX["negative_2"]
        self.noise = prepare.SFX["stock_noise"]
        
    def startup(self, persistent):
        self.persist = persistent
        self.stock = self.persist["stock"]
        self.player = self.persist["player"]
        self.num_shares = 0
        self.make_labels()
        self.make_buttons()
        self.noise.play()
        
    def make_labels(self):
        stock = self.stock
        name_ = self.stock.company.name
        symbol_ = self.stock.company.symbol
        name = Label(self.font, 16, "{}".format(name_), "gray80",
                {"midtop": (self.window.centerx, self.title.rect.bottom)})
        symbol = Label(self.font, 18, "{}".format(symbol_), "gray80", 
                {"midtop": (self.window.centerx, name.rect.bottom)})
        shares_title = Label(self.font, 16, "Shares", "gray80",
                {"topleft": (self.window.left + 65, self.window.top + 150)})
        price_title = Label(self.font, 16, "Price", "gray80",
                {"topleft": (self.window.left + 185, self.window.top + 150)})
        self.shares_label = Label(self.font, 16, "{}".format(self.num_shares),
                "gray80", {"topleft": (self.window.left + 60, self.window.top + 200)})
        x = Label(self.font, 16, "X", "gray80",
                {"topleft": (self.window.left + 140, self.window.top + 200)})
        price = Label(self.font, 16, "{:.2f}".format(stock.price), "gray80",
                {"topleft": (self.window.left + 190, self.window.top + 200)})
        equals = Label(self.font, 16, "=", "gray80",
                {"topleft": (self.window.left + 245, self.window.top + 200)})
        self.total_label = Label(self.font, 16, "{:.2f}".format(stock.price * self.num_shares),
                "gray80", {"topleft": (self.window.left + 275, self.window.top + 200)})
        
        self.labels = [name, symbol, shares_title, price_title, self.shares_label,
                           x, price, equals, self.total_label]
        
    def make_buttons(self):
        click = prepare.SFX["click_2"]
        self.buttons = ButtonGroup()
        w, h  = 60, 20
        left = self.window.left + 65
        top = self.window.top + 250
        top2 = self.window.top + 280
        for num in (1, 10, 100, 1000):
            Button((left, top, w, h), self.buttons, text="+{}".format(num), text_color=pg.Color("gray80"), 
                       fill_color=pg.Color("gray20"), font=self.font, font_size=14, call=self.add_shares, args=num, click_sound=click)
            Button((left, top2, w, h), self.buttons, text="-{}".format(num), text_color=pg.Color("gray80"), 
                       fill_color=pg.Color("gray20"), font=self.font, font_size=14, call=self.subtract_shares, args=num, click_sound=click)                       
            left += 70
        
        bw, bh = 120, 50
        b_left = self.window.centerx - (bw//2)
        b_top = self.window.top + 330         
        Button((b_left, b_top, bw, bh), self.buttons, text="Sell Shares", text_color=pg.Color("gray80"), 
                       fill_color=pg.Color("gray20"), font=self.font, font_size=14, call=self.sell_stock, click_sound=click)
        Button((b_left, b_top + 60, bw, bh), self.buttons, text="Cancel", text_color=pg.Color("gray80"), 
                       fill_color=pg.Color("gray20"), font=self.font, font_size=14, call=self.leave_state, args="STOCKSCREEN", click_sound=click)
        
    def sell_stock(self, *args):
        total = self.num_shares * self.stock.price
        self.player.portfolio.sell_stock(self.stock, self.num_shares)
        self.leave_state("PORTFOLIO")
            
    def leave_state(self, next_state):
        self.next = next_state
        self.noise.stop()
        self.done = True
            
    def quit_game(self):
        self.done = True
        self.quit = True
        self.persist["economy"].save(self.persist["player"])
        
    def add_shares(self, num):
        folio = self.player.portfolio
        if self.num_shares + num <= folio.stocks[self.stock.name][1]:
            self.num_shares += num
        else:
            self.negative.play()
    
    def subtract_shares(self, num):
        self.num_shares = max(0, self.num_shares - num)
        
    def get_event(self, event):
        self.buttons.get_event(event)
        if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
            self.quit_game()
        elif event.type == pg.QUIT:
            self.quit_game()
        
    def update(self, keys, dt):
        mouse_pos = pg.mouse.get_pos()
        self.buttons.update(mouse_pos)
        self.shares_label.set_text("{}".format(self.num_shares))
        self.total_label.set_text("{:.2f}".format(self.stock.price * self.num_shares))
        
    def draw(self, surface):
        pg.draw.rect(surface, self.bg_color, self.window)
        pg.draw.rect(surface, self.frame_color, self.window, 2)
        self.title.draw(surface)
        for label in self.labels:
            label.draw(surface)
        self.buttons.draw(surface)    
    
        