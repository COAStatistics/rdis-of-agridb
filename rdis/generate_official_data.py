import linecache as lc
import xlrd
from datetime import date
from data_utils import (
    DataGenerator as dg,
    simple_obj_creator,
)

YEAR = date.today().year
INSURANCE_DICT = {}


def init_data(num) -> None:
    """
    Read sample from txt file then pass line to simple_obj_creator fn
    :param num: 3:main, 4:main_inv, 5:sub, 6:sub_inv
    :return: None
    """
    path = 'info.txt'
    file = lc.getline(path, num).strip()
    load_insruance(lc.getline(path, 7).strip())
    with open(file, encoding='utf8') as f:
        for i, line in enumerate(f):
            obj = simple_obj_creator(line, is_person=False)
            exist = dg.is_exist(obj.id)
            if exist:
                extract_data(obj)
            else:
                extract_data(obj, False)
            if i == 0:
                break


def load_insruance(path):
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
    members = []
    declaration = set()
    disaster = []
    fallow_trans = []
    livestock = {}
    sb_sbdy = []

    if exist:
        household = dg.get_household(samp.id)
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

            sb_sbdy_data = dg.get_sb_subsidy(member)
            if any(i > 0 for i in sb_sbdy_data[1:]):
                sb_sbdy.append(sb_sbdy_data)
    else:
        person_data = member_data(samp, exist)
        members.append(person_data)


def member_data(member, exist=True):
    person_data = [''] * 11
    appid = member['app_id'] if exist else member.id
    if exist:
        person_data[0] = str(YEAR - int(member['birth'][:4]))
        person_data[1] = member['role']
        person_data[2] = member['code']
        person_data[3] = dg.get_farmer_insurance(member['id'])
        person_data[4] = dg.get_elder_allowance(member['id'])
        person_data[10] = dg.get_landlord_or_tenant(member['id'])

    if appid in INSURANCE_DICT:
        for index, i in enumerate(INSURANCE_DICT.get(appid), start=5):
            if i > 0:
                person_data[index] = i
    return person_data


if __name__ == '__main__':
    dg = dg()
    sample_num = eval(input('sample_num = '))
    init_data(sample_num)
