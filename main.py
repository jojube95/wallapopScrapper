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

    result_dataframe = add_product_identifier_to_dataframe(args.component, result_dataframe)[['id', 'title', 'description', 'product', 'price']]

    result_dataframe = normalize_dataframe(result_dataframe)

    result_dataframe = add_benchmark_column(result_dataframe, args.component)

    result_dataframe = normalize_dataframe(result_dataframe)

    result_dataframe = result_dataframe.dropna(subset=['benchmark'])

    result_dataframe = add_price_benchmark_ratio(result_dataframe)

    print(result_dataframe)


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
        return re.sub(r"(i\d*)( | -| -| - |-)(\d*)", r"\1-\3", product, count=1).upper()
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
    pattern_model_intel = r"i(3|5|7|9)( |-| - | -|- )(\d*)(k|t|)"
    pattern_model_amd = r"(ryzen|fx)( |-| - | -|- )(\w|)(3|5|7|9|)\s*(\d*)"

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
