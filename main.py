import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Get wallapop results into pandas graphs')
    parser.add_argument('-kw', help='keyword to search on wallapop')
    parser.add_argument('-pmin', type=int, help='minimum price to search on wallapop')
    parser.add_argument('-pmax', type=int, help='maximum price to search on wallapop')

    return parser.parse_args()


def do_stuff(args):
    print(args)


def main():
    args = parse_args()
    do_stuff(args)


if __name__ == '__main__':
    main()
