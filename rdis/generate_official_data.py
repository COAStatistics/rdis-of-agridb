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
                extract_data(obj)
            else:
                ...
            if i == 10000:
                break


def extract_data(samp, exist=True):
    members = []
    declaration = set()
    disaster = []
    livestock = {}

    if exist:
        household = dg.get_household(samp.id)
        for member in household:
            person_data = member_data(member)
            members.append(person_data)

            declaration_data = dg.get_declaration(member['id'])
            if declaration_data:
                declaration = declaration.union(declaration_data)

            disaster_data = dg.get_disaster(member['id'])
            if disaster_data:
                disaster += disaster_data

            livestock_data = dg.get_livestock(member['app_id'])

    else:
        member_data(samp, exist)


def member_data(member, exist=True):
    person_data = [''] * 11
    if exist:
        person_data[0] = str(YEAR - int(member['birth'][:4]))
        person_data[1] = member['role']
        person_data[2] = member['code']
        person_data[3] = dg.get_farmer_insurance(member['id'])
        person_data[4] = dg.get_elder_allowance(member['id'])
        person_data[10] = dg.get_landlord_or_tenant(member['id'])
        return person_data
    else:
        return person_data


if __name__ == '__main__':
    dg = dg()
    sample_num = eval(input('sample_num = '))
    load_sample(sample_num)
