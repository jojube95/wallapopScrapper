import argparse
import requests
import pandas as pd


def do_stuff(args):
    print(args)

    result_dataframe = iterate_items(args.kw, args.pmin, args.pmax)

    print(result_dataframe)


def iterate_items(keyword, min_price, max_price):
    dataframes = []
    start_item = 0
    while True:
        print(start_item)
        dataframe = normalize_json(get_wallapop_data(keyword, min_price, max_price, start_item))
        start_item += 40
        if dataframe.empty:
            break
        else:
            dataframes.append(dataframe)

    return pd.concat(dataframes).reset_index(drop=True)


def get_wallapop_data(keyword, min_price, max_price, start_item):
    url = 'https://api.wallapop.com/api/v3/general/search/'
    params = {
        'keywords': keyword,
        'min_sale_price': min_price,
        'max_sale_price': max_price,
        'latitude': 40.41956,
        'longitude': -3.69196,
        'order_by': 'price_low_to_high',
        'country_code': 'ES',
        'category_ids': 15000,
        'distance': 600000,
        'start': start_item
    }
    response = requests.get(url, params=params)
    return response.json()


def normalize_json(json_list):
    df = pd.json_normalize(json_list, record_path=['search_objects'], max_level=1)
    return df


def parse_args():
    parser = argparse.ArgumentParser(description='Get wallapop results into pandas graphs')
    parser.add_argument('-kw', help='keyword to search on wallapop')
    parser.add_argument('-pmin', type=int, help='minimum price to search on wallapop')
    parser.add_argument('-pmax', type=int, help='maximum price to search on wallapop')

    return parser.parse_args()


def main():
    args = parse_args()
    do_stuff(args)


if __name__ == '__main__':
    main()
