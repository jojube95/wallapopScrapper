import argparse
import requests


def parse_args():
    parser = argparse.ArgumentParser(description='Get wallapop results into pandas graphs')
    parser.add_argument('-kw', help='keyword to search on wallapop')
    parser.add_argument('-pmin', type=int, help='minimum price to search on wallapop')
    parser.add_argument('-pmax', type=int, help='maximum price to search on wallapop')

    return parser.parse_args()


def do_stuff(args):
    print(args)
    json_response = get_wallapop_data(args.kw, args.pmin, args.pmax)
    print(json_response)


def get_wallapop_data(keyword, min_price, max_price):
    url = 'https://api.wallapop.com/api/v3/general/search/'
    params = {
        'keywords': keyword,
        'min_sale_price': min_price,
        'max_sale_price': max_price,
        'latitude': 40.41956,
        'longitude': -3.69196,
        'order_by': 'price_low_to_high'
    }
    response = requests.get(url, params=params)
    return response.json()


def main():
    args = parse_args()
    do_stuff(args)


if __name__ == '__main__':
    main()
