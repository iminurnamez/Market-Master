import random
from ..components.industry_info import INDUSTRIES
#from ..components.company import Company
from .company import Company

class Industry(object):
    def __init__(self, name, economy):
        self.name = ""
        I = INDUSTRIES[name]
        sizes = I["Sizes"]
        self.size_ranges = []
        for size in sizes:
            self.size_ranges.extend([size for _ in range(sizes[size])])
        avg_keys = ("Revenue per Employee",
                           "Payroll per Employee",
                           "Expense Percentage")
        self.averages = {k: I[k] for k in avg_keys}
        self.make_companies(I["Names"], economy)        
                
    def make_companies(self, names, economy):
        self.companies = []
        for name, symbol in names:
            size = random.randint(*random.choice(self.size_ranges))
            c = Company(name, symbol, size, self, economy)
            self.companies.append(c)
                
    