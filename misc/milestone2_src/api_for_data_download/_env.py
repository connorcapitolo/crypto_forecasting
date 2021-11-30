import os
'''This is just some boilerplate for where things should be stored and how they can be accessed
A reminder that if this is being imported into another module, all of these must be defined since PYthon goes through this whole .py file. I do not have host, port, user, or mdp environment variables defined, so I place these in functions so API.py will run
'''

def get_major_coins():
    major_coins = ['BTC', 'ETH', 'BNB', 'USDT', 'BUSD', 'USD']
    return major_coins


def get_api_info():
    # SEE THAT I HAVE UPDATED THE ENVIRONMENT VARIABLE NAME
    # how to appropriately do this so that it persists on a Mac
    # 1. In terminal: vim ~/.bash_profile
    # 2. export BINANCE_SECRET_KEY=(insert_your_specific_key)
    # 3. export BINANCE_API_KEY=(insert_your_specific_key)
    # 4. save your work and close out
    # 5. In terminal: source ~/.bash_profile
    api_key = os.environ['BINANCE_API_KEY']
    api_secret = os.environ['BINANCE_SECRET_KEY']
    return api_key, api_secret

def get_host_port_user_mdp():
    host = os.environ['host']  # the endpoint of the database in aws
    port = 3306
    user = os.environ['user']
    mdp = os.environ['password']
    return host, port, user, mdp
