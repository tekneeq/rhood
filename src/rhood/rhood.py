import robin_stocks as rs
from secrets import config

"""
Trading algo:
    - 1 hourly: whenever we hit 200 EMA whil 50 EMA is higher, buy the bounce

    
    Need SPY prices ending every N min
        60 min for 1h
        1440 min for daily
"""


rs.robinhood.authentication.login(
    username=config.USERNAME,
    password=config.PASSWORD,
    expiresIn=172800,
    by_sms=True,
)
