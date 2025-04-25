import argparse


def setup_parser():
    parser = argparse.ArgumentParser(prog='service', description="Let's find out the currency rates!")
    parser.add_argument('--usd', type=float, help='Set amount for USD')
    parser.add_argument('--rub', type=float, help='Set amount for RUB')
    parser.add_argument('--eur', type=float, help='Set amount for EUR')
    parser.add_argument('--period', type=int, required=True, help='Set period (in minutes). Getting data every N minutes')
    parser.add_argument('--debug',  default=False, help='Enable debug mode (0/1/true/false/y/n)')
    args = parser.parse_args()

    if not (args.usd or args.rub or args.eur):
        parser.error('At least one of --usd, --rub, or --eur must be provided.')
    
    debug_value = str(args.debug).lower()
    if debug_value in ['1', 'true', 'y']:
        args.debug = True
    elif debug_value in ['0', 'false', 'n']:
        args.debug = False
    else:
        parser.error('Invalid value for --debug. Use 0, 1, true, false, y, n, True, False, Y, N')

    return args
