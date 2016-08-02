#!/usr/bin/env python

import unittest
from beehive import *
import conf


small_pool_percent = 0.25


class HiveTestCases(unittest.TestCase):

    def setUp(self):
        self.beehive = Beehive(0, 30000000, calc_max_premium_ratio, conf)
        self.honeycomb = Honeycomb(1, self.beehive)

    def test_bee(self):
        bee = Bee(10, 2000, self.honeycomb, small_pool_percent)
        self.assertEqual(10, bee.id)
        self.assertEqual(bee.balance, 2000 * small_pool_percent)
        self.assertEqual(2000 * small_pool_percent, self.honeycomb.balance())
        self.assertEqual(500, self.beehive.balance())

    def test_charge(self):
        bee = Bee(10, 2000, self.honeycomb, small_pool_percent)
        bal = 2000 * small_pool_percent
        bee.charge(100)
        self.assertEqual(bal-100, bee.balance)
        self.assertEqual(400, self.beehive.balance())

        bee.charge(210)
        self.assertEqual(bal-100-210, bee.balance)

        bee.charge(300)
        self.assertEqual(0, bee.balance)
        self.assertEqual(0, self.beehive.balance())

        # self.assertRaises(BankruptException, bee.charge, 1500)

    def test_honeycomb(self):
        bee1 = Bee(10, 2000, self.honeycomb, small_pool_percent)
        bee2 = Bee(10, 3000, self.honeycomb, small_pool_percent)

        self.assertEqual(5000 * small_pool_percent, self.honeycomb.balance())

        bal1 = 2000 * small_pool_percent
        bal2 = 3000 * small_pool_percent
        self.assertEqual(bal1, bee1.balance)
        self.assertEqual(bal2, bee2.balance)

        bee1.charge(100)
        self.assertEqual(bal1 - 100, bee1.balance)
        self.assertEqual(1150, self.beehive.balance())
        self.assertEqual(bal2, bee2.balance)

        bee1.charge(500)
        self.assertEqual(0, bee1.balance)
        self.assertEqual(750, bee2.balance)

        bee2.charge(200)
        self.assertEqual(550, bee2.balance)
        self.assertEqual(bee2.balance, self.honeycomb.balance())

        bee1.charge(100)
        self.assertEqual(550, bee2.balance)
        # print "hive balance:", self.beehive.balance()
        self.assertEqual(550, self.beehive.balance())

        bee2.charge(1000)
        self.assertEqual(0, bee1.balance)
        self.assertEqual(0, bee2.balance)
        # print "hive balance:", self.beehive.balance()

    def test_beehive(self):
        pass

    def testScenario(self):
        from scenarios import Scenario, scenario_config
        s = []
        for sc in scenario_config:
            s.append(Scenario(**sc))

        self.assertEqual(12, s[0].N_Months)
        self.assertEqual(1000, s[0].honeycomb_size_in_hive)


if __name__ == '__main__':
    unittest.main()

