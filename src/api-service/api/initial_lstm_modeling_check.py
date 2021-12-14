from api.predictions_get_rid_of import generate_predict_sequences
from api.predictions_get_rid_of import generate_prediction

trial_lst_dict = [
    {
        "id": 1228,
        "name": "BTCUSDT",
        "open_time": 1502974920000,
        "open_price": 4411,
        "high_price": 4411,
        "low_price": 4411,
        "close_price": 4411,
        "volume_traded": 0,
        "close_time": 1502974979999,
        "quote_asset_volume": 0,
        "number_of_trades": 0,
        "taker_buy_base_asset_volume": 0,
        "taker_buy_quote_asset_volume": 0
    },
    {
        "id": 163,
        "name": "BTCUSDT",
        "open_time": 1502942940000,
        "open_price": 4261.48,
        "high_price": 4261.48,
        "low_price": 4261.48,
        "close_price": 4261.48,
        "volume_traded": 0,
        "close_time": 1502942999999,
        "quote_asset_volume": 0,
        "number_of_trades": 0,
        "taker_buy_base_asset_volume": 0,
        "taker_buy_quote_asset_volume": 0
    }
    ]

trial_lst_dict = trial_lst_dict*500

output = generate_prediction('initial_lstm.h5', trial_lst_dict, input_sequence_length = 64)
print(output)