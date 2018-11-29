import linecache
import requests
import shelve
from pprint import pprint
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


def dump_data(name, key):
    data = get_all_data(name)
    d = {}
    for i in data:
        d[i[key]] = i
    with shelve.open('../agridb') as f:
        f[name] = d


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


def create_relation(name, relation_name, key, val, group=True):
    data = load_data(name)
    d = {}
    with shelve.open('../agridb') as f:
        if group:
            for i in data.values():
                if i.get(key):
                    d[i[key]] = d.get(i[key], []) + [i[val]]
            f[relation_name] = d
        else:
            for i in data.values():
                if i.get(key):
                    d[i[key]] = i[val]
            f[relation_name] = d


def inspection_distinct(table_name):
    with shelve.open('../agridb') as f:
        data = {}
        for k, v in f[table_name].items():
            data[v['member']] = data.get(v['member'], 0) + 1
        for i, j in data.items():
            if j > 1:
                print(i, j)


if __name__ == '__main__':
    print_data('appid_member_pk_link', 10)
    # pprint(load_data('owner_pk_tenant_pk_link'))
