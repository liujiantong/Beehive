#!/usr/bin/env python

import unittest
from beehive import *


class HiveTestCases(unittest.TestCase):

    def setUp(self):
        self.beehive = Beehive()
        self.honeycomb = Honeycomb(1, self.beehive)

    def test_bee(self):
        bee = Bee(10, 2000, self.honeycomb)
        self.assertEqual(10, bee.id)
        self.assertEqual(bee.balance, 2000 * small_pool_percent)
        self.assertEqual(2000 * small_pool_percent, self.honeycomb.balance())
        self.assertEqual(2000 * (1 - small_pool_percent), self.beehive.balance)

    def test_charge(self):
        bee = Bee(10, 2000, self.honeycomb)
        bal = 2000 * small_pool_percent
        bee.charge(100)
        self.assertEqual(bal-100, bee.balance)
        self.assertEqual(2000-bal, self.beehive.balance)

        bee.charge(210)
        self.assertEqual(bal-100-210, bee.balance)

        bee.charge(300)
        self.assertEqual(0, bee.balance)
        self.assertEqual(2000-610, self.beehive.balance)

        self.assertRaises(BankruptException, bee.charge, 1500)

    def test_honeycomb(self):
        bee1 = Bee(10, 2000, self.honeycomb)
        bee2 = Bee(10, 3000, self.honeycomb)

        self.assertEqual(5000 * small_pool_percent, self.honeycomb.balance())

        bal1 = 2000 * small_pool_percent
        bal2 = 3000 * small_pool_percent
        self.assertEqual(bal1, bee1.balance)
        self.assertEqual(bal2, bee2.balance)

        bee1.charge(100)
        self.assertEqual(bal1 - 100, bee1.balance)
        self.assertEqual(5000 * (1-small_pool_percent), self.beehive.balance)
        self.assertEqual(bal2, bee2.balance)

        bee1.charge(500)
        self.assertEqual(0, bee1.balance)
        self.assertEqual(bal2 - 100, bee2.balance)

        bee2.charge(200)
        self.assertEqual(bal2 - 100 - 200, bee2.balance)
        self.assertEqual(bee2.balance, self.honeycomb.balance())

        bee1.charge(100)
        self.assertEqual(bal2 - 100 - 200 - 100, bee2.balance)
        print "hive balance:", self.beehive.balance
        self.assertEqual(self.beehive.balance, 5000 * (1-small_pool_percent))

        bee2.charge(1000)
        self.assertEqual(0, bee1.balance)
        self.assertEqual(0, bee2.balance)
        print "hive balance:", self.beehive.balance

    def test_beehive(self):
        pass


if __name__ == '__main__':
    unittest.main()
