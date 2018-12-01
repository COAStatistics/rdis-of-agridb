import json
import linecache as lc
import xlrd
from collections import OrderedDict
from datetime import date
from data_utils import (
    DataGenerator as dg,
    simple_obj_creator,
)

YEAR = date.today().year
INSURANCE_DICT = {}
OFFICIAL_DATA = {}


def init_data(num) -> None:
    """
    Read sample from txt file then pass line to simple_obj_creator fn
    :param num: 1:main, 0:sub
    :return: None
    """
    path = 'info.txt'
    num = 3 if num else 4
    file = lc.getline(path, num).strip()
    load_insurance(lc.getline(path, 7).strip())
    with open(file, encoding='utf8') as f:
        for i, line in enumerate(f):
            obj = simple_obj_creator(line, is_person=False)
            exist = dg.is_exist(obj.id)
            if exist:
                extract_data(obj)
            else:
                extract_data(obj, False)


def load_insurance(path):
    wb = xlrd.open_workbook(path)

    for sheet_page in range(4):
        sheet = wb.sheet_by_index(sheet_page)

        if sheet.name == '國保給付':
            calculate_national_insurance_payment(sheet)

        elif sheet.name == '勞就保給付':
            calculate_labor_insurance_payment(sheet)

        elif sheet.name == '勞退':
            calculate_labor_pension(sheet)

        else:
            calculate_farmer_insurance_payment(sheet)


def calculate_national_insurance_payment(sheet):
    distinct_dict = {}
    for i in range(0, sheet.nrows):
        row = sheet.row_values(i)
        _id = row[0]
        id_type = _id + '-' + str(int(row[1]))

        if id_type not in distinct_dict:
            value = int(row[3])
            insurance_type = int(row[1])

            if insurance_type in [60, 66]:
                add_insurance(_id, value, 0)
            else:
                mon_start = int(str(int(row[2]))[-2:])
                allance = value * (13 - mon_start)
                distinct_dict[id_type] = allance
                add_insurance(_id, allance, 0)


def calculate_labor_insurance_payment(sheet):
    distinct_dict = {}
    annuity = [45, 48, 35, 36, 37, 38, 55, 56, 57, 59]
    for i in range(0, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        id_type = farm_id + '-' + str(int(row[1]))

        if id_type not in distinct_dict:
            value = int(row[3])
            insurance_type = int(row[1])

            if insurance_type not in annuity:
                add_insurance(farm_id, value, 1)
            else:
                mon_start = int(str(int(row[2]))[-2:])
                allance = value * (13 - mon_start)
                distinct_dict[id_type] = allance
                add_insurance(farm_id, allance, 1)

        else:
            value = int(row[3])
            insurance_type = int(row[1])
            if insurance_type not in annuity:
                add_insurance(farm_id, value, 1)


def calculate_labor_pension(sheet):
    for i in range(0, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        value = int(row[3])
        add_insurance(farm_id, value, 2)


def calculate_farmer_insurance_payment(sheet):
    for i in range(0, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        value = int(row[2])
        add_insurance(farm_id, value, 3)


def add_insurance(farm_id, amount, sheet_num):
    if farm_id in INSURANCE_DICT:
        INSURANCE_DICT.get(farm_id)[sheet_num] += amount
    else:
        amount_list = [0] * 4
        amount_list[sheet_num] = amount
        INSURANCE_DICT[farm_id] = amount_list


def extract_data(samp, exist=True):
    birthday = ''
    members = []
    declaration = set()
    disaster = []
    fallow_trans = []
    livestock = {}
    sb_sbdy = []

    if exist:
        household = dg.get_household(samp.id)
        birthday = int(list(filter(lambda x: x['app_id'] == samp.id, household))[0]['birth'][:4]) - 1911
        for member in household:
            person_data = member_data(member)
            members.append(person_data)

            declaration_data = dg.get_declaration(member['id'])
            if declaration_data:
                declaration = declaration.union(declaration_data)

            trans_crop_data = dg.get_fallow_transfer(member['id'])
            if trans_crop_data:
                fallow_trans.extend(trans_crop_data)

            disaster_data = dg.get_disaster(member['id'])
            if disaster_data:
                disaster.extend(disaster_data)

            livestock_data = dg.get_livestock(member['app_id'])
            if livestock_data:
                livestock.update(livestock_data)

            sb_sbdy_data = dg.get_sb_subsidy(member, samp)
            if any(int(i) > 0 for i in sb_sbdy_data[1:]):
                sb_sbdy.append(sb_sbdy_data)
    else:
        person_data = member_data(samp, exist)
        members.append(person_data)
    declaration = ','.join(list(declaration)) if declaration else ''
    generate_json_data(samp, birthday, members, declaration, fallow_trans, disaster, livestock, sb_sbdy)


def member_data(member, exist=True):
    person_data = [''] * 11
    appid = member['app_id'] if exist else member.id
    if exist:
        person_data[0] = str(int(member['birth'][:4]) - 1911)
        person_data[1] = member['role']
        person_data[2] = member['code']
        person_data[3] = dg.get_farmer_insurance(member['id'])
        person_data[4] = dg.get_elder_allowance(member['id'])
        person_data[10] = dg.get_landlord_or_tenant(member['id'])

    if appid in INSURANCE_DICT:
        for index, i in enumerate(INSURANCE_DICT.get(appid), start=5):
            if i > 0:
                person_data[index] = format(i, '8,d')
    return person_data


def generate_json_data(sample, birthday, household, declaration, fallow_transfer, disaster, livestock, sb_sbdy):
    data = OrderedDict()
    data['name'] = sample.name
    data['address'] = sample.addr
    data['birthday'] = str(birthday)
    data['farmerId'] = sample.id
    data['telephone'] = sample.tel
    data['layer'] = sample.layer
    data['serial'] = sample.farmer_num[-5:]
    data['household'] = household
    data['monEmp'] = []
    data['declaration'] = declaration
    data['cropSbdy'] = fallow_transfer
    data['disaster'] = disaster
    data['livestock'] = livestock
    data['sbSbdy'] = sb_sbdy
    OFFICIAL_DATA[sample.farmer_num] = data


def output_josn_data(data) -> None:
    file_name = '公務資料.json' if dg.main else '公務資料_備選.json'
    path = r'../' + file_name
    with open(path, 'w', encoding='utf8') as f:
        f.write(json.dumps(data,  ensure_ascii=False))


if __name__ == '__main__':
    while True:
        sample_num = eval(input('main(1), or sub(0) = '))
        if sample_num in [0, 1]:
            break
    dg = dg(sample_num)
    init_data(sample_num)
    # output_josn_data(OFFICIAL_DATA)
