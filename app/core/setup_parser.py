import argparse
from decimal import Decimal

from app.core.logger import logger
from app.core.settings import settings


def setup_parser():
    parser = argparse.ArgumentParser(
        prog='currency-service',
        description="Let's find out the currency rates!"
    )
    parser.add_argument(
        '--period',
        type=int,
        required=True,
        help='Set period (in minutes). Getting data every N minutes'
    )
    parser.add_argument(
        '--debug',
        default=False,
        help='Enable debug mode (0/1/true/false/y/n)'
    )
    args, remaining = parser.parse_known_args()

    balance = {}
    try:
        if len(remaining) % 2 != 0:
            parser.error(f"Missing value for {remaining[-1]}")

        for cur, value in zip(remaining[::2], remaining[1::2]):
            if not cur.startswith('--') and len(cur[2:]) != 3:
                parser.error(f"Expected currency flag, for exapmple usd, eur. Got {cur}")
            if not value.replace('.', '', 1).isdigit():
                parser.error(f"Invalid amount for {cur}: {value}.")
            balance[cur[2:].lower()] = Decimal(value)
    except ValueError as e:
        parser.error(f"Invalid format: {e}")

    if not balance:
        raise ValueError('At least one of --usd, --rub, or --eur must be provided.')
        # balance = {'rub': Decimal(0), 'usd': Decimal(0), 'eur': Decimal(0)}

    args.balance = balance

    logger.info(f"Balance has been set: {args.balance}")

    debug_value = str(args.debug).lower()
    if debug_value in settings.TRUE_VALUE:
        args.debug = True
    elif debug_value in settings.FALSE_VALUE:
        args.debug = False
    else:
        parser.error('Invalid value for --debug. Use 0, 1, true, false, y, n, True, False, Y, N')
    return args
