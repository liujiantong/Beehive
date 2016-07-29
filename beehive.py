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

    def __init__(self, bee_id, premium, comb, pool_percent=defalut_small_pool_ratio):
        self.id = bee_id
        self.honeycomb = comb
        self.premium = premium
        self.balance = 0
        self.small_pool_percent = pool_percent

        small_pool = int(math.floor(self.premium * self.small_pool_percent))
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
        small_pool = self.premium * self.small_pool_percent
        self.balance += small_pool
        self.honeycomb.hive.renew(self.premium - small_pool)

    def __str__(self):
        return '[Bee:%d | comb_id:%d | balance:%d]' % (self.id, self.honeycomb.id, self.balance)


class Random:

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


def output_config(honeycomb_size, bee_size, days, ratio):
    line_str = "====================================================================="
    config_str = "%s\n蜂巢小组总数:\t\t%s\n每个小组总人数:\t\t%s\n模拟天数:\t\t%s\n小池比例:\t\t%s\n%s\n" \
                 % (line_str, honeycomb_size, bee_size, days, ratio, line_str)
    logging.info(config_str)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Simulating Beehive...\n")

    parser = argparse.ArgumentParser(description='蜂巢投保模拟程序')
    parser.add_argument('--comb_num', '-N', type=int, default=default_honeycomb_size_in_hive, help='模拟的蜂巢小组总数')
    parser.add_argument('--bee_num', '-n', type=int, default=default_bee_size_in_honeycomb, help='模拟的每个小组总人数')
    parser.add_argument('--days', '-d', type=int, default=N_Days, help='模拟的总天数')
    parser.add_argument('--ratio', '-r', type=float, default=defalut_small_pool_ratio, help='小池比例')

    args = parser.parse_args()

    honeycomb_size_in_hive = args.comb_num
    bee_size_in_honeycomb = args.bee_num
    days = args.days
    ratio = args.ratio

    output_config(honeycomb_size_in_hive, bee_size_in_honeycomb, days, ratio)

    the_comb_id = 0
    the_bee_id = 0
    the_hive = Beehive()

    premiums = Random.generate_premium(honeycomb_size_in_hive * bee_size_in_honeycomb)

    for i in xrange(honeycomb_size_in_hive):
        the_comb_id += 1
        comb = Honeycomb(the_comb_id, the_hive)
        # logging.debug("honeycomb:%d", the_comb_id)

        for j in xrange(bee_size_in_honeycomb):
            the_bee_id += 1
            # premium = generate_premium()
            premium = premiums[bee_size_in_honeycomb * i + j]
            bee = Bee(the_bee_id, premium, comb, ratio)
            # logging.debug("bee:%d", the_bee_id)

    # logging.debug("Beehive:%s", the_hive)

    try:
        for evt_num in Random.generate_claim_event(days):
            charges = Random.generate_charge(evt_num)
            for i in xrange(evt_num):
                bee = random.choice(the_hive.bees())
                charge = int(charges[i])
                logging.debug("%s charge %d", bee, charge)
                bee.charge(charge)
    except BankruptException as e:
        logging.warn(e)

    logging.info("Beehive:%s", the_hive)

    # logging.info("Remaining:%d in Beehive", the_hive.balance)

