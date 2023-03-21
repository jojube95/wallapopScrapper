import argparse
import requests
import pandas as pd
import re


def do_stuff(args):
    print(args)

    result_dataframe = iterate_items(args.component, args.pmin, args.pmax)

    result_dataframe = add_product_identifier_to_dataframe(args.component, result_dataframe)[['id', 'title', 'description', 'product', 'price']]

    print(result_dataframe)


def add_product_identifier_to_dataframe(component, dataframe):
    products = generate_products(component, dataframe)

    dataframe['product'] = products

    return dataframe


def generate_products(component, dataframe):
    products = []

    for index, row in dataframe.iterrows():
        product = get_product_name(component, row['title'], row['description'])
        product = normalize_product(product)
        products.append(product)

    return products


def normalize_product(product):
    # TODO
    return ''


def get_product_name(component, title, description):
    title = title.lower()
    description = description.lower()

    if component == 'cpu':
        return get_product_name_cpu(title, description)
    else:
        return get_product_name_gpu(title, description)


def get_product_name_cpu(title, description):
    pattern_model_intel = r"i(3|5|7|9)( |-| - | -|- )[0-9]{3,4}(k|t|)"
    pattern_model_amd = r"(ryzen|fx)( |-| - | -|- )(\w|)(3|5|7|9|)\s*[0-9]{3,4}"

    match = re.search(pattern_model_intel, title)

    if match is None:
        match = re.search(pattern_model_intel, description)
        if match is None:
            match = re.search(pattern_model_amd, title)
            if match is None:
                match = re.search(pattern_model_amd, description)
                if match is None:
                    return ''
            else:
                return match.group().strip()
        else:
            return match.group().strip()
    else:
        return match.group().strip()


def get_product_name_gpu(title, description):
    model = 'GTX'

    pattern = "\\s*[0-9]{3,4}\\s*(ti|super|)"

    match = re.search(pattern, title)

    if match is None:
        match = re.search(pattern, description)
        if match is None:
            return ''
        else:
            serie = match.group().strip()
    else:
        serie = match.group().strip()

    return model + ' ' + serie


def iterate_items(component, min_price, max_price):
    dataframes = []
    start_item = 0
    while True:
        print(start_item)
        dataframe = normalize_json(get_wallapop_data(component, min_price, max_price, start_item))
        start_item += 40
        if dataframe.empty:
            break
        else:
            dataframes.append(dataframe)

    return pd.concat(dataframes).reset_index(drop=True)


def get_wallapop_data(component, min_price, max_price, start_item):
    if component == 'cpu':
        keyword = 'procesador y placa base'
    else:
        keyword = 'gtx'

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
    parser.add_argument('-component', help='component to search on wallapop, [gpu | cpu]')
    parser.add_argument('-pmin', type=int, help='minimum price to search on wallapop')
    parser.add_argument('-pmax', type=int, help='maximum price to search on wallapop')

    return parser.parse_args()


def main():
    args = parse_args()
    do_stuff(args)


if __name__ == '__main__':
    main()
