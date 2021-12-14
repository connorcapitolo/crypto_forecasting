import json

data = {}

data['validation_score'] = 0.6
data['unique_id'] = 6
data['training_time_stamp'] = 123456
data['hyperparameters'] = {}
data['symbol'] = 'BNBUSDT'

with open('model_metrics_BNBUSDT.json', 'w') as outfile:
    json.dump(data, outfile)
