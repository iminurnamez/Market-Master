from . import prepare,tools
from .states import splash_screen, title_screen, exchange_screen
from .states import stock_screen, market_graph, portfolio_screen
from .states import stock_purchase, stock_sale

def main():
    controller = tools.Control(prepare.CAPTION)
    states = {
            "SPLASH": splash_screen.SplashScreen(),
            "TITLE": title_screen.TitleScreen(),
            "EXCHANGE": exchange_screen.ExchangeScreen(),
            "STOCKSCREEN": stock_screen.StockScreen(),
            "MARKETGRAPH": market_graph.MarketGraph(),
            "PORTFOLIO": portfolio_screen.PortfolioScreen(),
            "BUYSTOCK": stock_purchase.StockPurchaseScreen(),
            "SELLSTOCK": stock_sale.StockSaleScreen()
            }
    controller.setup_states(states, "SPLASH")
    controller.main()
