from tensorflow.keras.models import load_model
import numpy as np

def make_prediction() -> float:

    lstm_model = load_model('model_ex6.h5')
    x_train = np.load('x_train.npy')
    assert x_train.shape == (1, 32, 8)

    lstm_prediction = lstm_model.predict(np.expand_dims(x_train[0], axis=0))
    float_prediction = float(lstm_prediction[0][0])

    close_price_mean=15592.779883026773
    close_price_std=15397.688146787825

    prediction = float_prediction * close_price_std + close_price_mean

    return prediction
