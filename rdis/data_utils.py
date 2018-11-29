import shelve
from collections import namedtuple

SAMPLE_ATTR = ['layer', 'name', 'tel', 'addr', 'county', 'town',
               'link_num', 'id', 'farmer_num', 'main_tpye', 'area', 'sample_num']

PERSON_ATTR = ['addr_code', 'id', 'birthday', 'hh_num', 'addr',
               'role', 'annotation', 'h_type', 'h_code']

Sample = namedtuple('Sample', SAMPLE_ATTR)
Person = namedtuple('Person', PERSON_ATTR)


def simple_obj_creator(text, is_person=True):
    l = text.strip().split('\t')
    if is_person:
        return Person._make(l)
    else:
        return Sample._make(l)


class DataGenerator:
    with shelve.open('../agridb') as f:
        __AMPL = f['appid_member_pk_link']
        __M = f['member']
        __HNMPL = f['household_num_members_pk_link']
        __ROLE = f['role']
        __CODE = {0: '', 1: '死亡', 2: '除戶'}
        __MPFIPL = f['member_pk_farmer_insurance_pk_link']
        __MPEPL = f['member_pk_elder_pk_link']

    @classmethod
    def is_exist(cls, appid) -> bool:
        exist = cls.__AMPL.get(appid)
        return True if exist else False

    @classmethod
    def __get_member(cls, pk):
        return cls.__M.get(pk)

    @classmethod
    def get_household(cls, samp_id) -> list:
        sample = cls.__get_member(cls.__AMPL[samp_id])
        household = []
        for i in cls.__HNMPL[sample['household']]:
            member = cls.__get_member(i)
            member['code'] = cls.__CODE[member['code']]
            member['role'] = cls.__ROLE[member['role']]
            household.append(member)
        return household

    @classmethod
    def get_farmer_insurance(cls, appid):
        if cls.__MPFIPL.get(appid):
            return 'Y'
        else:
            return ''

    @classmethod
    def get_elder_allowance(cls, appid):
        if cls.__MPEPL.get(appid):
            return 'Y'
        else:
            return ''

