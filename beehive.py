#!/usr/bin/env python
# encoding: utf8

import random
import math
import logging
import argparse

from functools import reduce
import numpy as np
from scipy import stats

import conf
import pool_remain


class BankruptException(Exception):
    pass


class Beehive:

    def __init__(self, hive_id, reserve_fund, calc_max_premium):
        self.id = hive_id
        self.all_honeycombs = []
        self.reserve_fund = reserve_fund
        self.calc_max_premium = calc_max_premium

    def charge(self, bee0, fee):
        """
        此时客户小池和大池的金额已耗尽, 需要动用大池里的金额, 按余额比例分配且不超过最高限额
        :param fee: 需要赔付的金额
        :return:
        """
        sum = self.pool_balance()
        sum1 = 0
        for bee in self.bees_iter():
            fee_bee = fee * (bee.pool_balance / sum)
            max_fee = self.calc_max_premium(bee.pool_balance)
            fee_sub = min(fee_bee, max_fee)
            bee.pool_balance -= fee_sub
            sum1 += fee_sub

        if sum1 < fee:
            sub_fee = fee - sum1
            self.__charge_reserve_fund(sub_fee)

    def bees_iter(self):
        for comb in self.all_honeycombs:
            for bee in comb.bees:
                yield bee

    def bees(self):
        return [bee for comb in self.all_honeycombs for bee in comb.bees]

    def pool_balance(self):
        return reduce((lambda x, y: x + y), [b.pool_balance for b in self.bees_iter()])

    def __charge_reserve_fund(self, fee):
        remaining = self.reserve_fund - fee
        if remaining <= 0:
            raise BankruptException
        self.reserve_fund -= remaining

    def __str__(self):
        str_val = "Beehive simulation | balance:%d\n\n" % self.pool_balance()
        for comb in self.all_honeycombs:
            str_val += '%s\n' % comb
        return str_val


class Honeycomb:

    def __init__(self, comb_id, hive):
        self.id = comb_id
        self.hive = hive
        self.bees = []
        self.hive.all_honeycombs.append(self)

    def join_bee__(self, bee):
        # logging.debug("bee:%s", bee)
        self.bees.append(bee)

    def balance(self):
        return reduce((lambda x, y: x + y), [b.balance for b in self.bees])

    def __str__(self):
        return "[Honeycomb:%d | balance:%d]" % (self.id, self.balance())

    def detail(self):
        return "[Honeycomb:%d\n%s]" % (self.id, str([str(bee) for bee in self.bees]))


class Bee:

    def __init__(self, bee_id, premium, comb, pool_ratio):
        self.id = bee_id
        self.honeycomb = comb
        self.premium = premium
        self.balance = 0
        self.small_pool_ratio = pool_ratio

        small_pool = int(math.floor(self.premium * self.small_pool_ratio))
        self.balance += small_pool
        self.pool_balance = premium - small_pool
        self.honeycomb.join_bee__(self)

    def charge(self, fee):
        remaining = self.balance - fee
        if remaining >= 0:
            self.balance = remaining
            return 0
        else:
            self.balance = 0
            remain_tmp = -1 * remaining

            if self.pool_balance >= remain_tmp:
                self.pool_balance -= remain_tmp
                return 0

            self.pool_balance = 0
            remain_fee = remain_tmp - self.pool_balance

            self.honeycomb.hive.charge(self, remain_fee)
            return remain_fee

    def renew(self):
        small_pool = self.premium * self.small_pool_ratio
        self.balance += small_pool
        self.pool_balance = self.premium - small_pool

    def __str__(self):
        return '[Bee:%d | comb_id:%d | balance:%d | pool_balance:%d]' % \
               (self.id, self.honeycomb.id, self.balance, self.pool_balance)


class Simulation:

    def __init__(self, comb_size, bee_size, days, ratio, calc_max_premium, output_fig='beehive-simulation.png'):
        self.honeycomb_size = comb_size
        self.bee_size = bee_size
        self.days = days
        self.pool_ratio = ratio
        self.output_fig = output_fig

        self.the_comb_id = 0
        self.the_bee_id = 0
        self.the_hive = Beehive(0, conf.global_reserve_fund, calc_max_premium)
        self.calc_max_premium = calc_max_premium

    @staticmethod
    def generate_premium(size):
        return np.random.normal(conf.premium_mu, conf.premium_sigma, size)

    @staticmethod
    def generate_charge(size):
        return np.random.normal(conf.charge_mu, conf.charge_sigma, size)

    @staticmethod
    def generate_claim_event(days):
        return np.random.poisson(conf.claim_freq_lambda, days)

    def simulate(self):
        premiums = Simulation.generate_premium(self.honeycomb_size * self.bee_size)
        for i in xrange(self.honeycomb_size):
            self.the_comb_id += 1
            comb = Honeycomb(self.the_comb_id, self.the_hive)
            # logging.debug("honeycomb:%d", the_comb_id)

            for j in xrange(self.bee_size):
                self.the_bee_id += 1
                premium = premiums[self.bee_size * i + j]
                bee = Bee(self.the_bee_id, premium, comb, self.pool_ratio)
                # logging.debug("bee:%d", bee)

        # logging.debug("Beehive:%s", the_hive)

        day_cntr = 0
        evt_sum = 0
        for evt_num in Simulation.generate_claim_event(self.days):
            day_cntr += 1
            try:
                charges = Simulation.generate_charge(evt_num)
                for i in xrange(evt_num):
                    evt_sum += 1
                    bee = random.choice(self.the_hive.bees())
                    charge = int(charges[i])
                    logging.debug("%s charge %d", bee, charge)
                    bee.charge(charge)
            except BankruptException as e:
                logging.info("第%d天, 共赔付第%d次, 破产啦 !!!", day_cntr, evt_sum)
                logging.warn(e)
                break

        logging.info("Beehive:%s", self.the_hive)
        # logging.info("Remaining:%d in Beehive", the_hive.balance)


def calc_max_premium_constant(pool_balance):
    return conf.max_premium_constant


def calc_max_premium_ratio(pool_balance):
    return pool_balance * conf.max_premium_ratio


def output_config(honeycomb_size, bee_size, days, ratio):
    line_str = "====================================================================="
    config_str = "%s\n" \
                 "  蜂巢小组总数:\t\t%d\n" \
                 "  每个小组总人数:\t%d\n" \
                 "  模拟总天数:\t\t%d\n" \
                 "  小池留存比例:\t\t%s\n" \
                 "%s\n" \
                 "  赔付频率泊松过程:\tlambda:%d\n" \
                 "  投保金额高斯分布:\tmu:%d, sigma:%d\n" \
                 "  赔付金额高斯分布:\tmu:%d, sigma:%d\n" \
                 "%s\n" \
                 % (line_str,
                    honeycomb_size, bee_size, days, ratio,
                    line_str,
                    conf.claim_freq_lambda,
                    conf.premium_mu, conf.premium_sigma,
                    conf.charge_mu, conf.charge_sigma,
                    line_str)
    logging.info(config_str)


@staticmethod
def output_figure(beehive, fig=conf.default_fig_name):
    import matplotlib.pyplot as plt
    from pylab import mpl

    mpl.rcParams['font.sans-serif'] = ['AppleGothic']
    mpl.rcParams['axes.unicode_minus'] = False

    x = [comb.balance() for comb in beehive.all_honeycombs]
    ax = plt.gca()
    ax.hist(x, bins=30, alpha=0.2, color='g')

    ax.set_xlabel(u'小组余额')
    ax.set_ylabel(u'小组数量')
    ax.set_title(u'各小组余额分布')
    plt.savefig(fig)
    plt.show()


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("蜂巢投保模拟程序: Simulating Beehive...\n")

    parser = argparse.ArgumentParser(description='蜂巢投保模拟程序')
    parser.add_argument('--comb_size', '-N', default=conf.honeycomb_size_in_hive, type=int, help='模拟的蜂巢小组总数')
    parser.add_argument('--bee_size', '-n', default=conf.bee_size_in_honeycomb, type=int, help='模拟的每个小组总人数')
    parser.add_argument('--days', '-d', default=conf.N_Days, type=int, help='模拟总天数')
    args = parser.parse_args()

    comb_size = args.comb_size
    bee_size = args.bee_size
    days = args.days

    output_config(comb_size, bee_size, days,
                  pool_remain.small_pool_ratio(conf.bee_size_in_honeycomb))

    simulation = Simulation(comb_size, bee_size, days,
                            pool_remain.small_pool_ratio(conf.bee_size_in_honeycomb),
                            calc_max_premium_ratio)

    # for sim_time in xrange(conf.simulation_count):
    simulation.simulate()

