import tensorflow as tf
import pandas as pd
import numpy as np
import os
import sys
from api.parameters_modelling import exclude_x, log_transformation_feat, continuous_features, val_split, test_split
from tensorflow.keras import regularizers
from tensorflow.keras.layers import BatchNormalization
import tensorflow as tf
from log_conf import Logger

pd.options.mode.chained_assignment = None  # default='warn'
AUTOTUNE = tf.data.experimental.AUTOTUNE


def time_features_func(df):
    df['Date'] = pd.to_datetime(df['Open Time'], unit = 'ms')
    df['Year'] = pd.DatetimeIndex(df['Date']).year
    df['Month'] = pd.DatetimeIndex(df['Date']).month
    df['Day of Week'] = pd.DatetimeIndex(df['Date']).dayofweek
    df['Day of Month'] = pd.DatetimeIndex(df['Date']).day
    df['Day of Year'] = pd.DatetimeIndex(df['Date']).dayofyear
    df['Week of Month'] = pd.DatetimeIndex(df['Date']).day // 7
    df['Week of Year'] = df['Date'].dt.isocalendar().week.astype('int64')
    df['hour'] =df.Date.dt.hour
    df['minute'] =df.Date.dt.minute
    df['minute_of_day'] = df.hour*60 + df.minute
    Logger.logr.info('Time preprocessing done')
    return df

def create_target_variables(df):
    # df = df.drop('Unnamed: 0', axis=1)
    df['Mid Price'] = (df['Open Price'] + df['Close Price'])/2
    df['y'] = (df['Open Price'].shift(-1) + df['Close Price'].shift(-1))/2  # the target is predicting the next close price
    df['benchmark'] = df['Mid Price']
    Logger.logr.info('Target preprocessing done')
    return df


def create_last_reporting(df, columns=['Open Price', 'Close Price', 'Mid Price']):
    """Twice periods previously w.r.t the y variable"""
    for column in columns:
        df[column+'_prev'] = df[column].shift(1)
    df = df.dropna()
    Logger.logr.info('Last preprocessing done')
    return df

def create_deviations(df):
    df['high_low'] = df['High price'] - df['Low Price']
    df['high_close'] = df['High price'] - df['Close Price']
    df['high_open'] = df['High price'] - df['Open Price']
    df['open_low'] = df['Close Price'] - df['Low Price']
    df['spread'] =df['Close Price'] - df['Open Price']
    df['spread_ind'] = 1*(df['spread'] < 0)
    df['spread'] =np.abs(df.spread)
    Logger.logr.info('Deviations preprocessing done')
    return df

def create_stats(df, features = ['high_low', 'high_close', 'high_open', 'open_low', 'spread', 'Open Price', 'High price', 'Low Price', 'Close Price']):
    for feature in features:
        series_1h, series_1d, series_1w, series_1m =  df[feature].rolling(window = 60), df[feature].rolling(window = 1500), df[feature].rolling(window = 10000), df[feature].rolling(window = 50000)
        df['rolling_avg_{}_1h'.format(feature)] = series_1d.mean() # rolling avg over 1 hour
        df['rolling_avg_{}_1d'.format(feature)] = series_1d.mean() # rolling avg over 1 day
        df['rolling_avg_{}_1w'.format(feature)] = series_1w.mean() # rolling avg over 1 week
        df['rolling_avg_{}_1m'.format(feature)] = series_1m.mean() # rolling avg over 1 month
        df['rolling_max_{}_1h'.format(feature)] = series_1d.max() # rolling max over 1 hour
        df['rolling_max_{}_1d'.format(feature)] = series_1d.max() # rolling max over 1 day
        df['rolling_max_{}_1w'.format(feature)] = series_1w.max() # rolling max over 1 week
        df['rolling_max_{}_1m'.format(feature)] = series_1m.max()  # rolling max over 1 month
        #df['rolling_min_{}_1h'.format(feature)] = series_1d.min() # rolling min over 1 hour
        #df['rolling_min_{}_1d'.format(feature)] = series_1d.min() # rolling min over 1 day
        #df['rolling_min_{}_1w'.format(feature)] = series_1w.min() # rolling min over 1 week
        #df['rolling_min_{}_1m'.format(feature)] = series_1m.min() # rolling min over 1 month
    df = df.dropna()
    Logger.logr.info('Rolling preprocessing done')
    return df

def log_transformation(df, log_transformation_features=log_transformation_feat):
    for feature in log_transformation_features:
        df['log_{}'.format(feature)] = np.log(1+df[feature].astype('float').values)
        df = df.drop(feature, axis=1)
    Logger.logr.info('Logs preprocessing done')
    return df

def _split(df, train_val_date=val_split, val_test_date=test_split, exclude_x=exclude_x):
    # Standardize the dataframe
    df = df.reset_index(drop=True)
    features_list = [col for col in df.columns if col not in exclude_x]
    X = df[features_list].astype('float')  # added by David
    Logger.logr.info('Splits done')
    return X, features_list

def standardize(X, x_mean, x_std):
    X = (X - x_mean) / x_std
    Logger.logr.info('Standardization done')
    return X

def generate_input_sequences(data, feats, seq_len = 32):
    empty_np_array = np.zeros((len(data)-seq_len+1, seq_len, len(feats)))
    dfvs = data[feats].values
    for i in range(len(data)-seq_len+1):
      x = np.expand_dims(dfvs[i:i+seq_len, :], axis = 0)
      empty_np_array[i] = x
    return empty_np_array

def generate_tf_data(X, batch_size):
    X = X[-128:,:,:]
    X = tf.convert_to_tensor(X, dtype=tf.float32)
    input_data = tf.data.Dataset.from_tensor_slices(X)
    input_data = input_data.batch(batch_size)
    input_data = input_data.prefetch(AUTOTUNE)

    return input_data

def preprocess_df(df, batch_size, x_mean, x_std):
    # df = select_last_year(df)
    df = time_features_func(df)
    df = create_target_variables(df)
    df = create_last_reporting(df)
    df = create_deviations(df)
    df = create_stats(df)
    df = log_transformation(df)
    X, features_list = _split(df)
    X = standardize(X, x_mean, x_std)
    X_seq = generate_input_sequences(X, X.columns.values.tolist(), 8)
    input_data = generate_tf_data(X_seq, batch_size)
    return input_data, features_list

def create_model():
    batch_size = 128
    lr = 1e-3
    optimizer = 'Adam'
    n_layers = 3
    n_units = 32
    dropout = 0.2
    weight_decay = 1e-4
    if optimizer == 'Adam':
        opt = tf.keras.optimizers.Adam(learning_rate=lr)
    elif optimizer == 'SGD':
        lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(lr, decay_steps=500, decay_rate=0.9,staircase=True)  
        opt = tf.keras.optimizers.SGD(learning_rate=lr_schedule)

    lstm_model = tf.keras.models.Sequential()

    if n_layers == 1:
        lstm_model.add(tf.keras.layers.LSTM(n_units, return_sequences=False))
    else:
        for n in range(n_layers):
            if n == n_layers - 1:
                lstm_model.add(tf.keras.layers.LSTM(n_units, return_sequences=False))
                lstm_model.add(tf.keras.layers.Dropout(dropout))
            else:
                lstm_model.add(tf.keras.layers.LSTM(n_units, return_sequences=True))
                lstm_model.add(BatchNormalization())
                lstm_model.add(tf.keras.layers.Dropout(dropout))
                
    lstm_model.add(tf.keras.layers.Dense(units=n_units, kernel_regularizer=regularizers.l2(l2=weight_decay)))

    MAX_EPOCHS = 10
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=2, mode='min')
    lstm_model.compile(loss=tf.keras.losses.MeanSquaredError(), optimizer=opt, metrics=[tf.metrics.MeanAbsoluteError(), tf.keras.losses.MeanSquaredError()])
    return lstm_model





