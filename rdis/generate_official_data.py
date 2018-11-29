import linecache as lc
from datetime import date
from data_utils import (
    DataGenerator as dg,
    simple_obj_creator,
)

YEAR = date.today().year


def load_sample(num) -> None:
    """
    Read sample from txt file then pass line to simple_obj_creator fn
    :param num: 3:main, 4:main_inv, 5:sub, 6:sub_inv
    :return: None
    """
    path = 'info.txt'
    file = lc.getline(path, num).strip()
    with open(file, encoding='utf8') as f:
        for i, line in enumerate(f):
            obj = simple_obj_creator(line, is_person=False)
            exist = dg.is_exist(obj.id)
            if exist:
                household_data(obj)
            else:
                print(obj, exist)
            if i == 10000:
                break


def household_data(samp, exist=True):
    data = []
    if exist:
        household = dg.get_household(samp.id)
        for member in household:
            extract_data(member)
    else:
        extract_data(samp, exist)


def extract_data(member, exist=True):
    person_data = [''] * 11
    if exist:
        person_data[0] = str(YEAR - int(member['birth'][:4]))
        person_data[1] = member['role']
        person_data[2] = member['code']
        person_data[3] = dg.get_farmer_insurance(member['id'])
        person_data[4] = dg.get_elder_allowance(member['id'])
        print(person_data)
    else:
        ...


if __name__ == '__main__':
    dg = dg()
    sample_num = eval(input('sample_num = '))
    load_sample(sample_num)
