

class Player(object):
    def __init__(self):
        self.cash = 100000
        self.portfolio = Portfolio(self)
        
        
class Portfolio(object):
    def __init__(self, player):
        self.player = player
        #{"stock name": (num_shares, cost_avg)}
        self.stocks = {}
        
    def add_stock(self, stock, num_shares):
        if self.player.cash >= stock.price * num_shares:
            name = stock.name
            if name in self.stocks:
                stock, num, avg = self.stocks[name]
            else:
                num, avg = (0, 0)
                self.stocks[name] = (stock, num, avg) 
            new_avg = ((num * avg) + (stock.price * num_shares)) / float(num + num_shares)
            self.stocks[name] = (stock, num + num_shares, new_avg)
            self.player.cash -= stock.price * num_shares
            
    def sell_stock(self, stock, num_shares):
        name = stock.name
        if self.stocks[name][1] >= num_shares:
            self.player.cash += stock.price * num_shares
            qty, avg = self.stocks[stock.name][1:]
            self.stocks[stock.name] = (stock, qty - num_shares, avg)
        if self.stocks[name][1] <= 0:
            del self.stocks[name]
        
    def get_portfolio_value(self):
        value = 0
        for c_name in self.stocks:
            stock, num, avg = self.stocks[c_name]
            value += stock.price * num
        return value

    def get_portfolio_cost(self):
        cost = 0
        for stock in self.stocks:
            cost += self.stocks[stock][1] * self.stocks[stock][2]
        return cost
        