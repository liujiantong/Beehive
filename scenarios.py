# encoding: utf8

import collections


Scenario = collections.namedtuple('Scenario', [
    'N_Months', 'global_reserve_fund',
    'honeycomb_size_in_hive', 'bee_size_in_honeycomb',
    'max_premium_constant', 'max_premium_ratio'
])

# Scenario 配置
scenario_config = [
    {
        # 模拟总月份数
        'N_Months': 12,

        # 准备金总额
        'global_reserve_fund': 3000000,

        # 模拟的蜂巢小组总数
        'honeycomb_size_in_hive': 1000,
        # 模拟的每个小组总人数
        'bee_size_in_honeycomb': 5,

        # 最高赔付金额
        'max_premium_constant': 100,
        'max_premium_ratio': 0.05,
    },
]

