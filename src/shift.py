import numpy as np
import pandas as pd
from pulp import LpProblem, LpMinimize, lpDot, lpSum
from ortoolpy import addvars, addbinvars
import random

from log import setup_logger
from utils import current_datetime


def read_csv(file_name, sep='\t', index_col=None):
    df = pd.read_csv(file_name, sep=sep, index_col=index_col)
    return df


def main():
    logger = setup_logger('logs', '{}.log'.format(current_datetime('%Y%m%d_%H%M%S')))

    # データを取得
    df_shift = read_csv('prototype/Shift.tsv', sep='\t', index_col=0)
    df_manage = read_csv('prototype/Manage.tsv', sep='\t', index_col=0)
    df_member = read_csv('prototype/Member.tsv', sep='\t', index_col=0)

    num_date, num_member = df_shift.shape
    date, member = df_shift.index, df_shift.employee

    df_shift['必要人数'] = df_manage.need  # １シフトあたりの必要人数の列を追加

    logger.info('シフト日数: {}, シフト日時: {}'.format(num_date, date))
    logger.info('メンバー数: {}, メンバー: {}'.format(num_member, member))
    logger.info('shift')
    logger.info(df_shift)
    logger.info('member')
    logger.info(df_member)

    # 日ごとに人数が足りないかチェック
    shortage_date = []
    for d, row in df_shift.iterrows():
        # print('{}日\tシフト入れる人数: {}, 必要人数: {}'.format(d, row[member].sum(), row['必要人数']))
        if row[member].sum() < row['必要人数']:
            shortage_date.append(d)

    if shortage_date:
        logger.info('下記日付について人員が足りません')
        logger.info('日,'.join(shortage_date))
        return

    # 最適化のための変数作成
    df_var = pd.DataFrame(np.array(addbinvars(num_date, num_member)), columns=member, index=date)
    df_var['必要人数'] = addvars(num_date)  # 必要人数を満たすためのペナルティ変数
    df_var['新人'] = addvars(num_date)  # 新人だけになった時のペナルティ変数
    df_var_amount = pd.DataFrame(addvars(num_member), index=member).T  # メンバーごとのシフト量を調整するためのペナルティ変数

    # 計算しやすくするため、0と1を逆転させたshiftを用意
    shift_rev = df_shift[member].apply(lambda x: 1 - x, axis=1)

    prob = LpProblem(name='shift', sense=LpMinimize)

    # 制約: 希望していない場所には入らないようにする
    for (_, s), (_, v) in zip(shift_rev.iterrows(), df_var[member].iterrows()):
        # シフト表とシフト変数の内積(要素積)を計算する
        # 入れない場所に1が立っているため、変数が1をとると入れない場所に入れることになってしまうためペナルティがかかるようになっている
        prob += lpDot(s, v) <= 0

    # 制約: シフトに必要な人数に対するペナルティを求める
    for (_, s), (_, v) in zip(df_shift.iterrows(), df_var.iterrows()):
        prob += v['必要人数'] >= (lpSum(v[member]) - s['必要人数'])
        prob += v['必要人数'] >= -(lpSum(v[member]) - s['必要人数'])

    # 制約: メンバーごとのシフト量に対するペナルティを求める
    for (_, m), (_, v), (_, v_a) in zip(df_member.iteritems(), df_var[member].iteritems(), df_var_amount.iteritems()):
        prob += lpSum(v) + v_a >= m['amount']
        prob += lpSum(v) - v_a <= m['amount']
