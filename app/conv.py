import re
import bisect

from . import utils

def extract_cust_qry(v1, v2):
    '''
    提取客户活期归属市县账户
        v1: 活期所有账户(含跨市县网点)
        v2: 归属市县所有网点
    '''

    return [x for x in v1 if x['acct_open_org'] in [y['brch_code'] for y in v2]]

def extract_cust_fix(v1, v2):
    '''
    提取客户定期归属市县账户
        v1: 定期所有账户(含跨市县网点)
        v2: 归属市县所有网点
    '''

    return [x for x in v1 if x['op_inst'] in [y['brch_code'] for y in v2]]

def is_many_agmt_name(v):
    '''判定一个身份证号多个账户名称'''

    return len(set([x['agmt_name'] for x in v])) > 1

def total_cust_asset(v1, v2):
    ''' 
    汇总客户名下所有资产
        v1: 客户市县所有网点资产
        v2: 归属市县所有网点
    '''

    qry = sum([x['qry_bal'] for x in v1 if x['org_id'] in [y['brch_code'] for y in v2]])
    fix = sum([x['fix_bal'] for x in v1 if x['org_id'] in [y['brch_code'] for y in v2]])
    gf = sum([x['gf_quot'] for x in v1 if x['org_id'] in [y['brch_code'] for y in v2]])
    ins = sum([x['ins_bal'] for x in v1 if x['org_id'] in [y['brch_code'] for y in v2]])
    fund = sum([x['fund_bal'] for x in v1 if x['org_id'] in [y['brch_code'] for y in v2]])

    results = []
    if not is_many_agmt_name(v1):
        d = dict()
        x = v1[0]
        d['agmt_name'] = x['agmt_name'][0] + '*'
        d['birth'] = x['birth']
        d['age'] = x['age']
        d['sex'] = x['sex']
        d['mobile_num'] = x['mobile_num']
        d['mobile_flag'] = x['mobile_flag']
        d['id_hy'] = x['id_hy']
        d['servicestt'] = x['servicestt']
        d['cust_other'] = x['cust_other']
        d['bal_date'] = x['bal_date']
        d['qry_bal'] = qry
        d['fix_bal'] = fix
        d['gf_quot'] = gf
        d['ins_bal'] = ins
        d['fund_bal'] = fund

        results.append(d)
    else:
        for k in set([x['agmt_name'] for x in v1]):
            for x in v1:
                if x['agmt_name'] == k:
                    d = dict()
                    d['agmt_name'] = x['agmt_name']
                    d['birth'] = x['birth']
                    d['age'] = x['age']
                    d['sex'] = x['sex']
                    d['mobile_num'] = x['mobile_num']
                    d['mobile_flag'] = x['mobile_flag']
                    d['id_hy'] = x['id_hy']
                    d['servicestt'] = x['servicestt']
                    d['cust_other'] = x['cust_other']
                    d['bal_date'] = x['bal_date']
                    d['qry_bal'] = qry
                    d['fix_bal'] = fix
                    d['gf_quot'] = gf
                    d['ins_bal'] = ins
                    d['fund_bal'] = fund

                    results.append(d)

    return results

def total_latest_days_bal(v):
    '''
    汇总每日所有网点余额
    '''

    all_summ_date = [x['summ_date'] for x in v]

    rec = []
    for x in all_summ_date:
        bal = 0
        acct_num = 0
        for y in v:
            if x == y['summ_date']:
                bal = bal + y['bal']
                acct_num = acct_num + y['acct_num']
            
        d = dict()
        d['summ_date'] = x
        d['bal'] = bal
        d['acct_num'] = acct_num
        d['details'] = [x for x in v if x['summ_date'] == d['summ_date']]

        rec.append(d)

    return rec

def extract_brch_30days_bal(v):
    '''抽取网点近30天的余额细数'''

    datelist = [y['summ_date'] for x in v for y in x['details']]
    for x in v:
        rec = []
        for y in x['details'][-30:]:
            rec.append(y['bal'])
        x['all_bal'] = ','.join([str(z) for z in rec])
        x['diff30'] = round(((rec[-1] - rec[0])*1.0/rec[0]) * 100, 2)

    return {'datelist': datelist[-30:], 'data': v}

def merge_brch_acc(all_brch, acc):
    '''归并网点账户数据'''

    results = []
    for x in all_brch:
        d = dict()
        rec = []
        for y in acc:
            if y['org_id'] == x['brch_code']:
                rec.append(y)

        d['details'] = rec
        d['cnt'] = len(rec)
        d['amt'] = sum([z['amt'] for z in rec])
        d['brch'] = x
        results.append(d)

    return [x for x in results if x['cnt'] != 0]

def merge_brch_acc_bal(all_brch, acc):
    '''归并网点账户数据'''

    results = []
    for x in all_brch:
        d = dict()
        rec = []
        for y in acc:
            if y['org_id'] == x['brch_code']:
                rec.append(y)

        d['details'] = rec
        d['cnt'] = len(rec)
        d['bal'] = sum([z['bal'] for z in rec])
        d['brch'] = x
        results.append(d)
    return [x for x in results if x['cnt'] != 0]

def merge_brch_purchase(all_brch, purchase_accrue):
    '''归并网点归属购买数据'''

    results = []
    for x in all_brch:
        d = dict()
        rec = []
        for y in purchase_accrue:
            if y['accrue_organ'] == x['brch_code']:
                rec.append(y)
        
        d['details'] = rec
        d['cnt'] = len(rec)
        d['quot'] = utils.abbr(sum([c['succ_affirm_quot'] for c in rec]))
        d['brch'] = x
        results.append(d)

    return [x for x in results if x['cnt'] != 0] 

def merge_brch_redeem(all_brch, redeem_accrue):
    '''归并网点归属赎回数据'''

    results = []
    for x in all_brch:
        d = dict()
        rec = []
        for y in redeem_accrue:
            if y['organ_code'] == x['brch_code']:
                rec.append(y)
        
        d['details'] = rec
        d['cnt'] = len(rec)
        d['quot'] = utils.abbr(sum([c['succ_affirm_quot'] for c in rec]))
        d['brch'] = x
        results.append(d)

    return [x for x in results if x['cnt'] != 0]

def merge_brch_due(all_brch, due_detail):
    '''归并网点到期数据'''

    results = []
    for x in all_brch:
        d = dict()
        rec = []
        for y in due_detail:
            if y['accrue_organ'] == x['brch_code']:
                rec.append(y)
        
        d['details'] = rec
        d['cnt'] = len(rec)
        d['quot'] = utils.abbr(sum([c['total_quot'] for c in rec]))
        d['brch'] = x
        results.append(d)

    return [x for x in results if x['cnt'] != 0]

def merge_brch_cim_quot(all_quot, type_quot, everyday_quot):
    '''合并网点理财份数'''

    results = []
    
    for x in all_quot:
        d = dict()
        rec = [0,0,0]
        for y in type_quot:
            if y['org_name'] == x['brch_name']:
                if y['prod_type'] == '0001':
                    rec[0] = y['total_quot']
                elif  y['prod_type'] == '0002':
                    rec[1] = y['total_quot']
                else: 
                    rec[2] = y['total_quot']

        res = []
    
        for z in everyday_quot[-30:]:
            for i in z['details']:
                if i['brch_name'] == x['brch_name']:
                    res.append(i['total_quot'])
                    
        datelist = [x['summ_date'].strftime('%m-%d') for x in everyday_quot[-30:]]
               
        d['org_name'] = x['brch_name']
        d['total_quot'] = x['total_quot']
        d['acct_num'] = x['acct_num']
        d['type01'] = rec[0]
        d['type02'] = rec[1]
        d['type03'] = rec[2]

        d['all_quot'] = ','.join([str(z) for z in res])
        d['diff30'] = round(((res[-1] - res[0])*1.0/res[0]) * 100, 2)
        results.append(d)

        results.sort(key=lambda x: x['total_quot'], reverse=True)

    return {'datelist': datelist, 'data': results}

def filter_lost_data(v, d):
    '''
    过滤缺失日期的数据
        v: 数据
        d: 缺失日期
    '''

    return [x for x in v if x['summ_date'].strftime('%Y.%m.%d') not in d]

def add_etl_table_cnname(results, etl_table_name):
    '''补齐etl数据表中文名称'''

    for x in results:
        if x['name'] in etl_table_name:
            x['cnname'] = etl_table_name[x['name']]   

def merge_brch_ins(all_brch, ins_detail):
    '''归并网点保险数据'''

    results = []
    for x in all_brch:
        d = dict()
        rec = []
        for y in ins_detail:
            if y['unit_code'] == x['brch_code']:
                rec.append(y)
        
        d['details'] = rec
        d['cnt'] = len(rec)
        d['accum_pay'] = utils.abbr(sum([c['accum_pay'] for c in rec]))
        d['brch'] = x
        results.append(d)

    return [x for x in results if x['cnt'] != 0]    

def search_rmk(all_elem, elem):    
    '''搜索活期交易明细备注'''

    #关键字key: tran_date + sys_seqno
    all_elem_keys = [x['sort_key'] for x in all_elem]
    i = bisect.bisect(all_elem_keys, elem)
    if all_elem_keys and (all_elem_keys[i-1] == elem):
        return all_elem[i-1]
    else:
        return None

def merge_qry_cdm_dtl_rmk(dtl, rmk):
    '''合并指定内部账户的活期交易明细和备注'''

    for x in dtl:
        y = search_rmk(rmk, x['sort_key'])
        if y is not None:
            if y['remark'] != '':
                if '|' in y['remark']:
                    s = y['remark'].split('|')
                    if (len(s[2]) > 8) and re.search('\d+', s[2]):
                        s[2] = s[2][:4] + '*'*4 + s[2][-4:]
                    k = '|'.join(s)
                    x['remark'] = k
                else:
                    x['remark'] = y['remark']
            else:
                x['remark'] = y['remark']

            x['term_name'] = y['term_name']
        else:
            x['remark'] = None
            x['term_name'] = None 