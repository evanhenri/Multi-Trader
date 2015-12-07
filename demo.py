import api_util

import btce
import poloniex

def main():
    api_util.init_config()

    btce_trade = btce.TradeAPI()
    info = btce_trade.getInfo()
    trans_hist = btce_trade.TransHistory()
    print(info, trans_hist)

    btce_public = btce.PublicAPI()
    ticker = btce_public.ticker('btc_usd')
    depth = btce_public.depth('ltc_btc')
    print(ticker, depth)

    poloniex_trade = poloniex.TradeAPI()
    balances = poloniex_trade.returnBalances()
    btc_deposit_addr = poloniex_trade.generateNewAddress('btc')
    print(balances, btc_deposit_addr)

    poloniex_public = poloniex.PublicAPI()
    vol24 = poloniex_public.return24Volume()
    ticker = poloniex_public.returnTicker()
    print(vol24, ticker)

if __name__ == '__main__':
    main()