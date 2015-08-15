import random
import pygame as pg
from ..components.animation import Animation

         
class Management(object):
    
    def __init__(self, company):
        self.aggression_names = {
            1: "Timid",
            2: "Conservative",
            3: "Balanced",
            4: "Bold",
            5: "Audacious"
            }
        self.all_priorities = ["Productivity", "Capacity", "Efficiency", "Stock Price", "Debt"]
        self.aversion_ranges = {1: .5,
                                      2: 1.0,
                                      3: 2.0,
                                      4: 3.0,
                                      5: 4.0}
        self.company = company
        self.priorities = random.sample(self.all_priorities, random.randint(1, 3))
        self.aggression = random.choice((1, 2, 2, 2, 3, 3, 3, 4, 4, 5))
        self.debt_aversion = random.choice((1, 2, 2, 2, 3, 3, 3, 4, 4, 5))
        
    def get_priority(self):
        return random.choice(self.priorities)
        
    def invest(self, economy):
        if self.company.cash <= 0:
            return
        
        priority = self.get_priority()
        c = self.company
        capital = c.cash * self.aggression * .15
        revenue = float(c.revenue_per_employee * c.num_employees)
        debt_of_revenue = c.debt / float(revenue)
        if debt_of_revenue >= self.aversion_ranges[self.debt_aversion]:
            priority = "Debt"
        if priority == "Debt":
            c.cash -= capital
            c.debt -= capital * .99
            economy.ticker_tape.add_news("{} ({}) paid down ${:,} of debt".format(c.name, c.symbol, int(capital * .99)))
        
        elif priority == "Productivity":
            capital_per = float(capital / c.num_employees)
            adj_per = capital_per / float(c.revenue_per_employee)
            increase = adj_per * random.uniform(.19, .21)
            amount = c.revenue_per_employee * increase
            final = c.revenue_per_employee + amount        
            invest = Animation(revenue_per_employee=final, duration=80)
            invest.start(c)
            c.investments.add(invest)
            economy.ticker_tape.add_news("{}  ({}) invested ${:,} in productivity upgrades".format(c.name, c.symbol, int(capital)))
        
        elif priority == "Efficiency":
            percent = capital / float(c.assets)
            amount = percent
            invest = Animation(expense_percentage=c.expense_percentage - amount,
                                        duration=80, transition="out_cubic")
            c.assets += capital * (1 - c.expense_percentage)
            invest.start(c)
            c.investments.add(invest)
            economy.ticker_tape.add_news("{}  ({}) invested ${:,} in efficiency upgrades".format(c.name, c.symbol, int(capital)))
        elif priority == "Capacity":
            if capital < c.revenue_per_employee:
                pass
            else:
                num = capital // c.revenue_per_employee
                c.cash -= num * c.revenue_per_employee
                total = c.num_employees + num
                ani = Animation(num_employees=total, duration=80, round_values=True)
                ani.start(c)
                c.investments.add(ani)
                economy.ticker_tape.add_news("{}  ({}) invested ${:,} in expanding capacity".format(c.name, c.symbol, int(num * c.revenue_per_employee)))
        elif priority == "Stock Price":
            revenue = c.revenue_per_employee * c.num_employees
            if c.stock.dividend < (revenue * self.aggression * .005) / float(c.stock.num_shares):
                amt = capital / c.stock.num_shares
                c.stock.dividend += amt
                economy.ticker_tape.add_news("{}  ({}) raised their dividend ${:.2f} to ${:.2f}".format(c.name, c.symbol, amt, c.stock.dividend))
                                
            else:
                
                shares = int((capital * .9) / c.stock.price)
                c.stock.num_shares -= shares
                c.cash -= capital            
                economy.ticker_tape.add_news("{}  ({}) bought back {:,} shares for {:,}".format(c.name, c.symbol, shares, int(capital)))


class Labor(object):
    def __init__(self, company):
        self.comapny = company
        self.morale = 1 #0-1, .9 means 90% production

class Company(object):
    def __init__(self, name, symbol, size, industry, economy):
        self.name = name
        self.symbol = symbol
        self.num_employees = size
        self.industry = industry
        self.industry_name = industry.name
        avgs = industry.averages
        self.salary = avgs["Payroll per Employee"] * random.uniform(.9, 1.1)
        self.revenue_per_employee = avgs["Revenue per Employee"] * random.uniform(.95, 1.05)
        self.expense_percentage = (avgs["Expense Percentage"] * random.uniform(.95, 1.05))                       
        self.assets = self.revenue_per_employee * self.num_employees * 5 #should have a minimum?
        self.cash = self.assets / 1000.
        self.debt = self.assets * random.uniform(0.00, .7)
        self.daily_history = []
        self.stock = Stock(self, economy)
        self.management = Management(self)
        self.labor = Labor(self)
        self.investments = pg.sprite.Group()
    
    @property        
    def book_value(self):
        value = (self.assets + self.cash) - self.debt
        return value
            
    def daily_report(self, day, interest_rate):
        revenue = self.num_employees * self.revenue_per_employee
        expenses = revenue * self.expense_percentage
        salaries = self.num_employees * self.salary
        profits = revenue - (expenses + salaries)
        pe_ratio = profits/float(self.stock.num_shares)
        dividend = self.stock.dividend
        self.cash += (self.cash * (interest_rate/364.)) / 364.
        self.cash += profits / 364.
        self.cash -= (self.debt * (interest_rate/364.)) / 364.
        info = [day, self.book_value, self.debt, revenue, expenses, salaries, profits, pe_ratio, dividend]
        self.daily_history.append(info)
        
    def hourly_update(self, economy):
        self.stock.hourly_update(economy)
        
    def daily_update(self, economy):
        self.daily_report(economy.day, economy.interest_rate)
        self.stock.daily_update(economy)
        self.investments.update(1)
        
    def weekly_update(self, economy):
        pass
        
    def quarterly_update(self, economy, player):
        dividend = self.stock.dividend * self.stock.num_shares * .25
        if self.cash < dividend:
            self.stock.dividend = 0
            economy.ticker_tape.add_news("{} has cancelled their dividend".format(self.name))
        else:
            self.cash -= dividend
            if self.name in player.portfolio.stocks:
                num = player.portfolio.stocks[self.name][1]
                player.cash += num * self.stock.dividend
        self.management.invest(economy)
        self.stock.quarterly_update(economy, player)
    
    def quarterly_report(self):
        pass    

    
class Stock(object):
    def __init__(self, company, economy):
        self.company = company
        self.symbol = self.company.symbol
        self.name = self.company.name
        num_shares = 1
        if self.company.book_value <= 0:
            num_shares = (self.company.revenue_per_employee * self.company.num_employees)
        else:
            split_point = random.randint(20, 100)
            while self.company.book_value / float(num_shares) > split_point:
                num_shares += 20000
        self.num_shares = num_shares
        self.dividend = 0
        self.price = self.get_price(economy)
        self.year_low = self.price
        self.year_high = self.price
        self.open_price = self.price
        self.daily_high = self.price
        self.daily_low = self.price
        #(day, num_shares, open_price, close_price, daily_low, daily_high)
        self.price_history = []
               
    def offer_shares(self, capital_goal):
        pass
        
    def get_market_price(self, economy):
        c = self.company
        if self.num_shares:
            book_value_ps = c.book_value / float(self.num_shares)
            earnings_ps = (c.revenue_per_employee * c.num_employees) / float(self.num_shares)
        else:
            book_value_ps = 0
            earnings_ps = 0
        if len(c.daily_history) > 1:
            back = min(364, len(c.daily_history))
            growth = (c.daily_history[-1][6] - c.daily_history[-back][6]) / float(c.daily_history[-back][6])
            discounted_return = (earnings_ps * growth) / (1. + economy.interest_rate)
        else:
            discounted_return = earnings_ps / (1. + economy.interest_rate)
        base = book_value_ps + discounted_return + self.dividend
        if base < 1:
            base = 1
        return base
        
    def get_price(self, economy):
        base = self.get_market_price(economy)
        price = base * random.uniform(*economy.hourly_changes[economy.condition])
        return price
        
    def hourly_update(self, economy):
        if random.randint(0, 1000) < economy.activity_chances[economy.activity]:
            self.price = self.get_price(economy)
            if self.daily_high is not None:
                if self.price > self.daily_high:
                    self.daily_high = self.price
            else:
                self.daily_high = self.price
            if self.daily_low is not None:
                if self.price < self.daily_low:
                    self.daily_low = self.price
            else:
                self.daily_low = self.price
        if not self.price_history:
            pass
        elif len(self.price_history) <= 364:
            year_high = max((x[5] for x in self.price_history))
            year_low = min((x[4] for x in self.price_history))
            self.year_low = min(self.price, year_low)
            self.year_high = max(self.price, year_high)
        else:
            year_high = max((x[5] for x in self.price_history[-364:]))            
            year_low = min((x[4] for x in self.price_history[-364:]))
            self.year_low = min(self.price, year_low)
            self.year_high = max(self.price, year_high)            
             
    def daily_update(self, economy):
        self.price_history.append([economy.day, self.num_shares, self.open_price, self.price, self.daily_low, self.daily_high])
        self.open_price = self.price
        self.daily_low = self.price
        self.daily_high = self.price
        
    def weekly_update(self, economy):
        pass
        
    def monthly_update(self, economy):
        pass
        
    def quarterly_update(self, economy, player):
        num = 0
        while self.price > 100:
            self.num_shares *= 2 #split
            num += 2
            if self.name in player.portfolio.stocks:
                num, avg = player.portfolio.stocks[self.name]
                total = num * avg
                qty = num * 2
                new_avg = total / float(qty)
                player.portfolio.stocks[self.name] = (qty, new_avg)                
            self.price = self.get_price(economy)
        if num:
            economy.ticker_tape.add_news("{}'s stock split {} to 1".format(self.name, num))
    
        
        