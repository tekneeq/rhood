import argparse
import datetime
import sys
import time
from pytz import timezone
import robin_stocks as rs
from secrets import config
from ssh_pymongo import MongoSession
import pprint
from util import valid_date
import pathlib
import json
from pytz import timezone
import requests


"""
Trading algo:
    - 1 hourly: whenever we hit 200 EMA whil 50 EMA is higher, buy the bounce

    
    Need SPY prices ending every N min
        60 min for 1h
        1440 min for daily
"""

ITER_DELAY = 5
TICKER = "SPY"
TZ = timezone("EST")

T_FORMAT = "%Y-%m-%d"
PP = pprint.PrettyPrinter(width=41, compact=True)
PTRACK_URL = "http://ptrackit.com/mongo_opts"

WRITE_FILE = 0
WRITE_MONGO = 1


def get_exp_date(args):
    expirationDate = args.expdate
    if expirationDate is None:
        if args.dfn > 0:
            expirationDate = (datetime.datetime.now() + datetime.timedelta(days=args.dfn)).strftime(T_FORMAT)
        else:
            expirationDate = datetime.datetime.today().strftime(T_FORMAT)
    return expirationDate


def main():
    parser = argparse.ArgumentParser()
    # expiration date
    parser.add_argument("-d", help="format YYYY-MM-DD", dest="expdate", default=None, type=valid_date)
    # date from now
    parser.add_argument("--dfn", dest="dfn", default=0, type=int)
    parser.add_argument("-r", dest="range", default=10, type=int)

    args = parser.parse_args()

    # rs login
    rs.robinhood.authentication.login(
        username=config.USERNAME,
        password=config.PASSWORD,
        expiresIn=604800,
        by_sms=True,
    )

    # get exp date
    expirationDate = get_exp_date(args)

    opt_list = rs.robinhood.options.find_options_by_expiration(TICKER, expirationDate)
    if not opt_list:
        print("No option data for %s. Exiting.." % expirationDate)
        sys.exit(0)

    # Print option data based on strike price
    opt_list_sorted = sorted(opt_list, key=lambda d: d["strike_price"])
    PP.pprint(opt_list_sorted)

    # write to file
    if WRITE_FILE:
        d_today = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M")
        json_fname = "%s_%s_%s.json" % (TICKER, expirationDate, d_today)
        data_dir = pathlib.Path().absolute() / "data" / TICKER
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(data_dir / json_fname, "w") as fp:
            json.dump(opt_list_sorted, fp, indent=4)

    # current ticket price
    ticker_price = round(
        float(rs.robinhood.stocks.get_latest_price(TICKER, priceType=None, includeExtendedHours=True)[0]),
        2,
    )

    # post to Mongo
    tz = timezone("EST")
    for d in opt_list_sorted:
        delta = abs(float(d["strike_price"]) - float(ticker_price))

        if delta <= args.range:
            # print(f"Inserting {d['strike_price']} delta {delta} < range {args.range}")
            #                 "rh_id": d["id"],

            # symbol + strike price + exp date + type  == unique
            opt_data = {
                "symbol": d["symbol"],
                "strike_price": d["strike_price"],
                "expiration_date": d["expiration_date"],
                "type": d["type"],
                "mark_price": d["mark_price"],
                "underlying_price": ticker_price,
                "open_interest": d["open_interest"],
                "volume": d["volume"],
                "delta": d["delta"],
                "gamma": d["gamma"],
                "rho": d["rho"],
                "theta": d["theta"],
                "vega": d["vega"],
                "implied_volatility": d["implied_volatility"],
                "data_date": datetime.datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S"),
                "version": 2,
            }

            print(f"Inserting {opt_data}")
            if WRITE_MONGO:
                headers = {"Content-type": "application/json", "Accept": "text/plain"}
                r = requests.post(PTRACK_URL, data=json.dumps(opt_data), headers=headers)


if __name__ == "__main__":
    main()
