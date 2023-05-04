import datetime
import time
from pytz import timezone
import robin_stocks as rs
from secrets import config

"""
Trading algo:
    - 1 hourly: whenever we hit 200 EMA whil 50 EMA is higher, buy the bounce

    
    Need SPY prices ending every N min
        60 min for 1h
        1440 min for daily
"""

ITER_DELAY = 5
TICKER = "SPY"


def main():
    rs.robinhood.authentication.login(
        username=config.USERNAME,
        password=config.PASSWORD,
        expiresIn=172800,
        by_sms=True,
    )
    tz = timezone("EST")

    while True:
        ctime = datetime.datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S")
        ticker_price = round(
            float(
                rs.robinhood.stocks.get_latest_price(
                    TICKER, priceType=None, includeExtendedHours=True
                )[0]
            ),
            2,
        )
        print(f"{ctime}: {TICKER} {ticker_price}")

        time.sleep(ITER_DELAY)


if __name__ == "__main__":
    main()
