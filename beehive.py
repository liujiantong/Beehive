#!/usr/bin/env python

import argparse
import random
import math
import logging

from functools import reduce
from itertools import chain

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


small_pool_percent = 0.25

premium_mu = 1500
premium_sigma = 300

charge_mu = 300
charge_sigma = 50

N_Days = 365

claim_freq_lambda = 50

honeycomb_size_in_hive = 1000
bee_size_in_honeycomb = 5


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
        str_val = "Beehive simulation | balance:%d\n" % self.balance
        for comb in self.all_honeycombs:
            str_val += '\n%s\n' % comb
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
                fee = bee.balance / sum
                bee.balance -= fee
        else:
            delta = premium - sum
            for bee in self.bees:
                bee.balance = 0

            remaining = self.hive.balance - delta
            if remaining < 0:
                raise BankruptException('OMG, I bankrupted!')
            else:
                self.hive.balance = remaining

    def __str__(self):
        return "[Honeycomb:%d\n%s\n]" % (self.id, str([str(bee) for bee in self.bees]))


class Bee:

    def __init__(self, bee_id, premium, comb):
        self.id = bee_id
        self.honeycomb = comb
        self.premium = premium
        self.balance = 0

        small_pool = int(math.floor(self.premium * small_pool_percent))
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
        small_pool = self.premium * small_pool_percent
        self.balance += small_pool
        self.honeycomb.hive.renew(self.premium - small_pool)

    def __str__(self):
        return '[Bee:%d | comb_id:%d | balance:%d]' % (self.id, self.honeycomb.id, self.balance)


def generate_premium():
    return int(random.gauss(premium_mu, premium_sigma))


def generate_charge(size):
    return np.random.normal(charge_mu, charge_sigma, size)


def generate_claim_event(days):
    return np.random.poisson(claim_freq_lambda, days)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Simulating Beehive...\n")

    the_comb_id = 0
    the_bee_id = 0
    the_hive = Beehive()

    for i in xrange(honeycomb_size_in_hive):
        the_comb_id += 1
        comb = Honeycomb(the_comb_id, the_hive)
        # logging.debug("honeycomb:%d", the_comb_id)

        for j in xrange(bee_size_in_honeycomb):
            the_bee_id += 1
            premium = generate_premium()
            bee = Bee(the_bee_id, premium, comb)
            # logging.debug("bee:%d", the_bee_id)

    # logging.debug("Beehive:%s", the_hive)

    for evt_num in generate_claim_event(N_Days):
        charges = generate_charge(evt_num)
        for i in xrange(evt_num):
            bee = random.choice(the_hive.bees())
            charge = int(charges[i])
            logging.debug("%s charge %d", bee, charge)
            bee.charge(charge)

    logging.debug("Beehive:%s", the_hive)

    logging.info("Remaining:%d in Beehive", the_hive.balance)

