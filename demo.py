import btce
import poloniex

def main():
    api_key = '123456789'
    api_secret = 'abcdefggijkl'
    nonce_file_path = '/path/to/nonce.json'

    # brce trade api
    btce_trade = btce.TradeAPI(api_key, api_secret, nonce_file_path)
    info = btce_trade.user_info()
    trans_hist = btce_trade.tx_history()
    print(info, trans_hist)

    # btce public api
    ticker = btce.ticker('btc_usd')
    depth = btce.depth('ltc_btc')
    print(ticker, depth)

    # poloniex trade api
    poloniex_trade = poloniex.TradeAPI(api_key, api_secret, nonce_file_path)
    balances = poloniex_trade.balances()
    btc_deposit_addr = poloniex_trade.generate_deposit_address('btc')
    print(balances, btc_deposit_addr)

    # poloniex public api
    vol24 = poloniex.vol_24hr()
    ticker = poloniex.ticker()
    print(vol24, ticker)

if __name__ == '__main__':
    main()