import pygame as pg
from .. import tools, prepare
from ..components.labels import Label, Button, ButtonGroup


        
class PortfolioScreen(tools._State):
    def __init__(self):
        super(PortfolioScreen, self).__init__()
        self.screen_rect = pg.display.get_surface().get_rect()
        self.font = prepare.FONTS["weblysleekuisl"]
        self.bold_font = prepare.FONTS["weblysleekuisb"]
        self.lefts = (100, 300, 400, 500, 600, 700)
        titles = ("Company", "Shares", "P/E Ratio",
                    "Cost Avg.", "Curr. Price", "Return")
        self.titles = [Label(self.bold_font, 16, title, "antiquewhite", {"topleft": (left, 10)})
                           for title, left in zip(titles, self.lefts)]
        self.bg_colors = {0: pg.Color("gray5"), 1: pg.Color("gray10")}
        
    def startup(self, persistent):
        self.persist = persistent
        self.player = self.persist["player"]
        self.make_labels_buttons(self.persist["economy"])
        
    def make_labels_buttons(self, economy):
        click = prepare.SFX["click_2"]
        self.buttons = ButtonGroup()
        self.buy_buttons = pg.sprite.Group()
        self.labels = []
        self.bg_rects = []
        folio = self.player.portfolio
        top = 50
        bw, bh = 70, 25
        buy_left = 830
        sell_left = 915
        space =25
        num = 0
        for name in folio.stocks:
            stock, shares, avg = folio.stocks[name]
            price = stock.price
            today = stock.company.daily_history[-1]
            pe_ratio = today[6] / float(stock.num_shares)
            return_ = (price * shares) - (shares * avg)
            texts = (name, "{:,}".format(int(shares)), "{:.2f}".format(pe_ratio),
                        "{:.2f}".format(avg), "{:.2f}".format(price), "{:.2f}".format(return_))
            for text, left in zip(texts, self.lefts):
                label = Label(self.font, 16, text, "gray80", {"topleft": (left, top)})
                self.labels.append(label)
                midy = label.rect.centery
            Button((buy_left, (midy - (bh//2)), bw, bh), self.buttons, text="Buy",
                       font=self.font, font_size=16, text_color=pg.Color("gray80"), 
                       fill_color=pg.Color("gray20"), call=self.buy_shares, args=stock, click_sound=click)
            Button((sell_left, (midy - (bh//2)), bw, bh), self.buttons, text="Sell",
                       font=self.font, font_size=16, text_color=pg.Color("gray80"), 
                       fill_color=pg.Color("gray20"), call=self.sell_shares, args=stock, click_sound=click)
            self.bg_rects.append((pg.Rect(self.lefts[0], top, 1000-self.lefts[0], space),
                                             self.bg_colors[num%2]))
            top += space
            num += 1
        
        #nav buttons
        w, h = (64, 52)
        left = 15
        top = 150
        space = 64
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["exchange_button"],
                   call=self.leave_state, args="EXCHANGE", click_sound=click)
        top += space
        Button((left, top, w, h), self.buttons, idle_image=prepare.GFX["market_button"],
                   call=self.leave_state, args="MARKETGRAPH", click_sound=click)
                       
                       
                       
        pleft, ptop = 17, 476
        pleft2 = 117
        portval = folio.get_portfolio_value()
        casht = "${:,.2f}".format(self.player.cash)
        port = "${:,.2f}".format(portval)
        net = "${:,.2f}".format(portval + self.player.cash)
        pairs = (("Cash", casht), ("Portfolio", port), ("Net Worth", net))
        text_color = pg.Color("gray80")
        for cat, val in pairs:
            self.labels.append(Label(self.bold_font, 16, cat, text_color,
                                       {"topleft": (pleft, ptop)}))
            self.labels.append(Label(self.bold_font, 16, val, text_color,
                                       {"topleft": (pleft2, ptop)}))
            ptop += 20
    
    
    def buy_shares(self, stock):
        self.persist["stock"] = stock
        self.leave_state("BUYSTOCK")
        
    def sell_shares(self, stock):
        self.persist["stock"] = stock
        self.leave_state("SELLSTOCK")
        
    def leave_state(self, next_state):
        self.next = next_state
        self.done = True
        
    def quit_game(self):
        self.done = True
        self.quit = True
        self.persist["economy"].save(self.persist["player"])
        
    def get_event(self, event):
        self.buttons.get_event(event)
        if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
            self.quit_game()
        elif event.type == pg.QUIT:
            self.quit_game()
        
    def update(self, keys, dt):
        mouse_pos = pg.mouse.get_pos()
        self.buttons.update(mouse_pos)
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        for rect, color in self.bg_rects:
            pg.draw.rect(surface, color, rect) 
        for title in self.titles:
            title.draw(surface)
        for label in self.labels:
            label.draw(surface)
        self.buttons.draw(surface)    
        