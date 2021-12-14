import os
import time

from binance import ThreadedWebsocketManager

api_secret = os.environ["BINANCE_SECRETS_KEY"]
api_key = os.environ["BINANCE_API_KEY"]


def main():

    symbol = 'BNBBTC'

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(message):
        print("handle_socket_message():")
        # print(msg)
        # Save the data
        # check if candle or top of the book data
        data = message["data"]
        information_kline = data.get('k')
        is_candle_closed = information_kline.get('x')
        if is_candle_closed == True:
            print('Writing', data)
            price_history_dict = {
                'symbol_id': 1,
                'open_time': information_kline.get('t'),
                'open_price': float(information_kline.get('o')),
                'high_price': float(information_kline.get('h')),
                'low_price': float(information_kline.get('l')),
                'close_price': float(information_kline.get('c')),
                'volume_traded': float(information_kline.get('v')),
                'close_time': information_kline.get('T'),
                'quote_asset_volume': float(information_kline.get('q')),
                'number_of_trades': information_kline.get('n'),
                'taker_buy_base_asset_volume': float(information_kline.get('V')),
                'taker_buy_quote_asset_volume': float(information_kline.get('Q'))
            }
            print(price_history_dict)

    #twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    #twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker',
               'bnbbtc@kline_1m']  # 'bnbbtc@kline'

    streams = ['bnbbtc@kline_1m']
    print("streams:", streams)
    twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    twm.join()


if __name__ == "__main__":
    main()
