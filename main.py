import argparse
import requests
import pandas as pd
import re
import json

with open('data/cpu_benchmarks.json') as f:
    cpu_benchmarks = json.load(f)

with open('data/gpu_benchmarks.json') as f:
    gpu_benchmarks = json.load(f)


def do_stuff(args):
    print(args)

    result_dataframe = iterate_items(args.component, args.pmin, args.pmax)

    result_dataframe = add_product_identifier_to_dataframe(args.component, result_dataframe)[['title', 'description', 'web_slug', 'flags.reserved', 'product', 'price']]

    result_dataframe = remove_reserverd_products(result_dataframe)[['title', 'description', 'web_slug', 'product', 'price']]

    result_dataframe = normalize_dataframe(result_dataframe)

    result_dataframe = add_benchmark_column(result_dataframe, args.component)

    result_dataframe = result_dataframe.dropna(subset=['benchmark'])

    result_dataframe = add_price_benchmark_ratio(result_dataframe)

    generate_wallapop_url(result_dataframe)

    print(result_dataframe)


def generate_wallapop_url(dataframe):
    dataframe['web_slug'] = dataframe['web_slug'].astype(str).apply(lambda x: 'https://es.wallapop.com/item/' + x)


def remove_reserverd_products(dataframe):
    return dataframe[dataframe['flags.reserved'] != True]


def add_price_benchmark_ratio(dataframe):
    ratios = []

    for index, row in dataframe.iterrows():
        ratios.append(row['benchmark'] / row['price'])

    dataframe['ratio'] = ratios

    return dataframe


def add_benchmark_column(dataframe, component):
    benchmarks = []

    for index, row in dataframe.iterrows():
        benchmarks.append(get_benchmark_mark(row['product'], component))

    dataframe['benchmark'] = benchmarks

    return dataframe


def get_benchmark_mark(product, component):
    if component == 'cpu':
        return cpu_benchmarks.get(product)
    else:
        return gpu_benchmarks.get(product)


def normalize_dataframe(dataframe):
    return dataframe.dropna(subset=['product'])


def add_product_identifier_to_dataframe(component, dataframe):
    products = generate_products(component, dataframe)

    dataframe['product'] = products

    return dataframe


def generate_products(component, dataframe):
    products = []

    for index, row in dataframe.iterrows():
        product = get_product_name(component, row['title'], row['description'])
        products.append(product)

    return products


def normalize_cpu_product_name(product):
    if product:
        return product.upper()
    else:
        ''


def normalize_gpu_product_name(product):
    if product:
        return product.upper()
    else:
        ''


def get_product_name(component, title, description):
    title = title.lower()
    description = description.lower()

    if component == 'cpu':
        return normalize_cpu_product_name(get_product_name_cpu(title, description))
    else:
        return normalize_gpu_product_name(get_product_name_gpu(title, description))


def get_product_name_cpu(title, description):
    pattern_model_intel = r"(i3|i5|i7|i9)( |-| - | -|- )([0-9]{3,4})(k|t|r|p|h|hr|s|)"
    pattern_model_amd = r"(ryzen|fx)( |-| - | -|- )(3|5|7|9|)\s*([0-9]{3,4})"

    result = re.search(pattern_model_intel, title)

    if result is None:
        result = re.search(pattern_model_intel, description)
        if result is None:
            result = re.search(pattern_model_amd, title)
            if result is None:
                result = re.search(pattern_model_amd, description)
                if result is None:
                    product = ''
                else:
                    product = f"{result.group(1)} {result.group(3)} {result.group(4)}"
            else:
                product = f"{result.group(1)} {result.group(3)} {result.group(4)}"
        else:
            product = f"{result.group(1)}-{result.group(3)}{result.group(4)}"
    else:
        product = f"{result.group(1)}-{result.group(3)}{result.group(4)}"

    return product


def get_product_name_gpu(title, description):
    pattern1 = r"(GTX|Gtx|gtx)(\s*|)([0-9]{3,4})(\s*|)(ti|super|)"

    result = re.search(pattern1, title)

    if result is None:
        result = re.search(pattern1, description)
        if result is None:
            product = ''
        else:
            product = f"{result.group(1)} {result.group(3)} {result.group(5)}"
    else:
        product = f"{result.group(1)} {result.group(3)} {result.group(5)}"

    if product == '':
        pattern2 = r"([0-9]{3,4})(\s*|)(ti|super|)(\s*|)(GTX|Gtx|gtx)"
        result = re.search(pattern2, title)
        if result is None:
            result = re.search(pattern2, description)
            if result is None:
                product = ''
            else:
                product = f"{result.group(5)} {result.group(1)} {result.group(3)}"
        else:
            product = f"{result.group(5)} {result.group(1)} {result.group(3)}"

    return product


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
