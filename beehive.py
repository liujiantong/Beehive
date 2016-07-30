#!/usr/bin/env python
# encoding: utf8

import argparse
import random
import math
import logging

from functools import reduce
from itertools import chain

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


defalut_small_pool_ratio = 0.25

N_Days = 365

claim_freq_lambda = 50

default_honeycomb_size_in_hive = 10000
default_bee_size_in_honeycomb = 5

# 投保分布参数
premium_mu = 1500
premium_sigma = 400

# 索赔金额分布参数
charge_mu = 300
charge_sigma = 100


class BankruptException(Exception):
    pass


class Beehive:

    def __init__(self, hive_id=0):
        self.id = hive_id
        self.balance = 0
        self.all_honeycombs = []

    def renew(self, premium):
        self.balance += premium

    def charge(self, fee):
        remaining = self.balance - fee
        self.balance = remaining
        return remaining

    def bees_iter(self):
        return chain.from_iterable(self.all_honeycombs)

    def bees(self):
        return [bee for comb in self.all_honeycombs for bee in comb.bees]

    def __str__(self):
        str_val = "Beehive simulation | balance:%d\n\n" % self.balance
        for comb in self.all_honeycombs:
            str_val += '%s\n' % comb
        return str_val


class Honeycomb:

    def __init__(self, comb_id, hive):
        self.id = comb_id
        self.hive = hive
        self.bees = []
        self.hive.all_honeycombs.append(self)

    def join_bee__(self, bee, fee):
        # logging.debug("bee:%s", bee)
        self.bees.append(bee)
        self.hive.renew(fee)

    def charge(self, premium):
        sum = reduce((lambda x, y: x + y), [b.balance for b in self.bees])
        if sum > premium:
            # charge everyone in same comb
            for bee in self.bees:
                ratio = bee.balance / sum
                bee.balance -= premium * ratio
        else:
            delta = premium - sum
            for bee in self.bees:
                bee.balance = 0

            remaining = self.hive.balance - delta
            self.hive.balance = remaining
            if remaining < 0:
                raise BankruptException('OMG, I bankrupted!')

    def balance(self):
        return reduce((lambda x, y: x + y), [b.balance for b in self.bees])

    def __str__(self):
        return "[Honeycomb:%d | balance:%d]" % (self.id, self.balance())

    def detail(self):
        return "[Honeycomb:%d\n%s]" % (self.id, str([str(bee) for bee in self.bees]))


class Bee:

    def __init__(self, bee_id, premium, comb, pool_ratio=defalut_small_pool_ratio):
        self.id = bee_id
        self.honeycomb = comb
        self.premium = premium
        self.balance = 0
        self.small_pool_ratio = pool_ratio

        small_pool = int(math.floor(self.premium * self.small_pool_ratio))
        self.balance += small_pool
        self.honeycomb.join_bee__(self, premium - small_pool)

    def charge(self, fee):
        remaining = self.balance - fee
        if remaining >= 0:
            self.balance = remaining
            return 0
        else:
            self.balance = 0
            self.honeycomb.charge(-1 * remaining)
            return remaining

    def renew(self):
        small_pool = self.premium * self.small_pool_ratio
        self.balance += small_pool
        self.honeycomb.hive.renew(self.premium - small_pool)

    def __str__(self):
        return '[Bee:%d | comb_id:%d | balance:%d]' % (self.id, self.honeycomb.id, self.balance)


class Stats:

    def __init__(self):
        pass

    @classmethod
    def generate_premium(cls, size):
        return np.random.normal(premium_mu, premium_sigma, size)

    @classmethod
    def generate_charge(cls, size):
        return np.random.normal(charge_mu, charge_sigma, size)

    @classmethod
    def generate_claim_event(cls, days):
        return np.random.poisson(claim_freq_lambda, days)


def output_config(honeycomb_size, bee_size, sim_count, days, ratio, output_fig):
    line_str = "====================================================================="
    config_str = "%s\n" \
                 "  蜂巢小组总数:\t\t%d\n" \
                 "  每个小组总人数:\t%d\n" \
                 "  模拟次数:\t\t%d\n" \
                 "  模拟天数:\t\t%d\n" \
                 "  小池比例:\t\t%s\n" \
                 "  输出图像文件:\t\t%s\n" \
                 "%s\n" \
                 "  赔付频率泊松过程:\tlambda:%d\n" \
                 "  投保金额高斯分布:\tmu:%d, sigma:%d\n" \
                 "  赔付金额高斯分布:\tmu:%d, sigma:%d\n" \
                 "%s\n" \
                 % (line_str,
                    honeycomb_size, bee_size, sim_count, days, ratio, output_fig,
                    line_str,
                    claim_freq_lambda,
                    premium_mu, premium_sigma,
                    charge_mu, charge_sigma,
                    line_str)
    logging.info(config_str)


def simulate(honeycomb_size, bee_size, days, ratio, output_fig):
    the_comb_id = 0
    the_bee_id = 0
    the_hive = Beehive()
    premiums = Stats.generate_premium(honeycomb_size * bee_size)
    for i in xrange(honeycomb_size):
        the_comb_id += 1
        comb = Honeycomb(the_comb_id, the_hive)
        # logging.debug("honeycomb:%d", the_comb_id)

        for j in xrange(bee_size):
            the_bee_id += 1
            # premium = generate_premium()
            premium = premiums[bee_size * i + j]
            bee = Bee(the_bee_id, premium, comb, ratio)
            # logging.debug("bee:%d", the_bee_id)

    # logging.debug("Beehive:%s", the_hive)

    day_cntr = 0
    evt_sum = 0
    for evt_num in Stats.generate_claim_event(days):
        day_cntr += 1
        try:
            charges = Stats.generate_charge(evt_num)
            for i in xrange(evt_num):
                evt_sum += 1
                bee = random.choice(the_hive.bees())
                charge = int(charges[i])
                logging.debug("%s charge %d", bee, charge)
                bee.charge(charge)
        except BankruptException as e:
            logging.info("第%d天, 共赔付第%d次, 破产啦 !!!", day_cntr, evt_sum)
            logging.warn(e)
            break

    logging.info("Beehive:%s", the_hive)
    # logging.info("Remaining:%d in Beehive", the_hive.balance)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Simulating Beehive...\n")

    parser = argparse.ArgumentParser(description='蜂巢投保模拟程序')
    parser.add_argument('--sim_count', '-C', type=int, default=1, help='模拟次数')
    parser.add_argument('--comb_num', '-N', type=int, default=default_honeycomb_size_in_hive, help='模拟的蜂巢小组总数')
    parser.add_argument('--bee_num', '-n', type=int, default=default_bee_size_in_honeycomb, help='模拟的每个小组总人数')
    parser.add_argument('--days', '-d', type=int, default=N_Days, help='模拟的总天数')
    parser.add_argument('--pool_ratio', '-r', type=float, default=defalut_small_pool_ratio, help='小池比例')
    parser.add_argument('--output_fig', '-o', type=str, default='beehive-simulation.png', help='可视化分析图表文件名')

    args = parser.parse_args()

    sim_count = args.sim_count
    honeycomb_size = args.comb_num
    bee_size = args.bee_num
    days = args.days
    pool_ratio = args.pool_ratio
    output_fig = args.output_fig

    output_config(honeycomb_size, bee_size, sim_count, days, pool_ratio, output_fig)

    for sim_time in xrange(sim_count):
        simulate(honeycomb_size, bee_size, days, pool_ratio, output_fig)

