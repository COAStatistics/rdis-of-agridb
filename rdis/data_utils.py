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
        __OTPTL = f['owner_pk_tenant_pk_link']
        __MPTPL = f['member_pk_tenant_pk_link']
        __MPDPL = f['member_pk_declare_pk_link']
        __DPTPL = f['declare_pk_transfercrop_pk_link']
        __TRANSFER_CROP = f['transfercrop']
        __CROP = f['crop']
        __FALLOW_TRANSFPER = f['fallowtransfer']
        __MPFTPK = f['member_pk_fallowtransfer_pk_link']
        __MDPL = f['member_disaster_pk_link']
        __DISASTER = f['disaster']
        __EVENT = f['disasterevent']
        __LIVESTOCK = f['livestock_result']
        __ALPL = f['appid_livestock_pk_link']
        __TENANTTRANS = f['tenanttransfer']
        __MPTTPL = f['member_pk_tenanttransfer_pk_link']
        __LANDLORD_RENT = f['landlordrent']
        __MPLLRPL = f['member_pk_landlordrent_pk_link']
        __LANDLORD_RETIRE = f['landlordretire']
        __MPLLRTPL = f['member_pk_landlordretire_pk_link']

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
            member['code'] = cls.__CODE.get(member['code'])
            member['role'] = cls.__ROLE.get(member['role'])
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

    @classmethod
    def get_landlord_or_tenant(cls, appid):
        sb = ''
        if cls.__OTPTL.get(appid):
            sb += '小'
        if cls.__MPTPL.get(appid):
            sb += '大'
        return sb

    @classmethod
    def get_declaration(cls, appid):
        dcl = set()
        trans_pk = cls.__DPTPL.get(cls.__MPDPL.get(appid))
        if trans_pk:
            for i in trans_pk:
                tc = cls.__TRANSFER_CROP[i]
                crop = cls.__CROP[tc['crop']]['name']
                dcl.add(crop)
        return dcl

    @classmethod
    def get_fallow_transfer(cls, appid) -> list:
        fallow_trans = []
        trans_pk = cls.__MPFTPK.get(appid)
        if trans_pk:
            for i in trans_pk:
                trans = cls.__FALLOW_TRANSFPER.get(i)
                crop = cls.__CROP[trans['crop']]['name']
                fallow_trans.append([crop, trans['subsidy'], trans['period']])
        return fallow_trans

    @classmethod
    def get_disaster(cls, appid) -> list:
        disaster = {}
        disaster_pk = cls.__MDPL.get(appid)
        if disaster_pk:
            for i in disaster_pk:
                dis = cls.__DISASTER[i]
                event = cls.__EVENT[dis['event']]['name']
                crop = cls.__CROP[dis['crop']]['name']
                area = round(dis['area'], 4)
                subsidy = dis['subsidy']
                if area > 0:
                    l = disaster.get((event, crop))
                    if l:
                        l[2] = round(l[2]+area, 4)
                        l[3] += subsidy
                    else:
                        disaster[(event, crop)] = [event, crop, area, subsidy]
        return list(disaster.values())

    @classmethod
    def get_livestock(cls, appid):
        result = {}
        livestock_pk = cls.__ALPL.get(appid)
        if livestock_pk:
            for i in livestock_pk:
                livestock = [None] * 7
                info = cls.__LIVESTOCK.get(i)

    @classmethod
    def get_sb_subsidy(cls, member) -> list:
        tenant_trans = cls.__get_tenant_transfer(member['id'])
        landlord_rent = cls.__get_landlord_rent(member['id'])
        landlord_retire = cls.__get_landlord_retire(member['id'])
        name = member['name'] if member['name'] else ''
        return [name, tenant_trans, landlord_rent, landlord_retire]

    @classmethod
    def __get_tenant_transfer(cls, appid) -> int:
        subsidy = 0
        tenant_trans_pk = cls.__MPTTPL.get(appid)
        if tenant_trans_pk:
            for i in tenant_trans_pk:
                tenant_trans = cls.__TENANTTRANS.get(i)
                subsidy += tenant_trans['subsidy']
        return subsidy

    @classmethod
    def __get_landlord_rent(cls, appid) -> int:
        subsidy = 0
        llr_pk = cls.__MPLLRPL.get(appid)
        if llr_pk:
            for i in llr_pk:
                llr = cls.__LANDLORD_RENT.get(i)
                subsidy += llr['subsidy']
        return subsidy

    @classmethod
    def __get_landlord_retire(cls, appid) -> int:
        subsidy = 0
        llr_pk = cls.__MPLLRTPL.get(appid)
        if llr_pk:
            for i in llr_pk:
                llr = cls.__LANDLORD_RETIRE.get(i)
                subsidy += llr['subsidy']
        return subsidy




