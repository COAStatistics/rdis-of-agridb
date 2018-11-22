import linecache
import requests
import shelve
from itertools import chain
from json import loads
from sys import exc_info

PATH = 'info.txt'
API = linecache.getline(PATH, 1).strip()
API_TOKEN = linecache.getline(PATH, 2).strip()
HEADER = {
    'Authorization': API_TOKEN
}


def get_all_data(db) -> chain:
    next_page = "{}{}/".format(API, db)
    data_list = []

    while next_page:
        try:
            res = requests.get("{}".format(next_page), headers=HEADER)
        except Exception:
            t, v, b = exc_info()
            print(t, v)
            break
        else:
            try:
                json_data = loads(res.text)
            except Exception:
                t, v, b = exc_info()
                print(t, v)
                break
            else:
                next_page = json_data['next']
                data_list.append(json_data['results'])
    return chain(*data_list)


def dump_data(name, data):
    with shelve.open('../agridb') as f:
        f[name] = data


def load_data(name) -> dict:
    with shelve.open('../agridb') as f:
        data = f.get(name)
    return data


def print_data(name, count=10) -> None:
    with shelve.open('../agridb') as f:
        data = f.get(name)
        for i, j in enumerate(data.items(), start=1):
            print(j)
            if i == count:
                break


if __name__ == '__main__':
    print_data('crop')
    # data = load_data('crop')
    # for i in data:
    #     print(i)
    # # data = get_all_data('household')
    # data = load_data('crop')
    # d = {}
    # for i in data:
    #     d[i['id']] = i
    # dump_data('crop', d)