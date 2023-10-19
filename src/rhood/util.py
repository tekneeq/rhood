import datetime


def valid_date(s):
    """

    return strings
    """
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date().strftime("%Y-%m-%d")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


def get_dt_obj(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def get_dt_str(dt_obj):
    return dt_obj.strftime("%Y-%m-%d")
