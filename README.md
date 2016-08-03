# 蜂巢互助模型模拟程序

蜂巢互助模型模拟程序通过模拟蜂巢模型的运行机制, 评估商业模型的风险水平.


## 安装依赖

1. [下载Anaconda for python2.7.x](https://www.continuum.io/downloads)
2. 安装Anaconda


## 快速使用

1. git clone http://githup.com/liujiantong/Beehive
2. cd Beehive
3. python ./beehive.py


## 命令行参数

使用命令: beehive.py -h 可以打印模拟程序的帮助说明. beehive.py 支持以下的命令行参数:

* --comb_size,  -N    模拟的蜂巢小组总数
* --bee_size,   -n    模拟的每个小组总人数
* --months,     -m    模拟总天数
* --output_fig, -o    分析图表文件名; 如果在命令行指定 -o 参数, 程序将为每个scenario 生成一个模拟结果统计直方图.

例如, beehive.py -N 2000 -o sim.png 将蜂巢小组总数指定为: 2000, 输出分析图表文件为: sim.png.

#### 注意: 运行程序时如果输入以上的命令行参数, 将覆盖配置文件中相应的参数.


## 配置文件解析

### conf.py

用于设置以下全局参数:

* 分析图表文件名
* 每月明细模拟结果CSV
* **投保金额分布参数**
* **赔付金额Gamma分布参数**
* **赔付频率Poison分布参数**

### scenarios.py

用于设置以下每个scenario 的模拟参数:

* 模拟总月份数
* 准备金总额
* 模拟的蜂巢小组总数
* 模拟的每个小组总人数
* 最高赔付金额 or
* 最高赔付比例

每个scenario 配置成python的一个字典对象, 多个scenario则写成python的数组形式. 
如下例子定义了两个scenario 的模拟参数.
```
scenario_config = [
    {
        # 模拟总月份数
        'N_Months': 12,
        # 准备金总额
        'global_reserve_fund': 3000000,
        # 模拟的蜂巢小组总数
        'honeycomb_size_in_hive': 100,
        # 模拟的每个小组总人数
        'bee_size_in_honeycomb': 5,
        # 最高赔付金额
        'max_premium_constant': 100,
        'max_premium_ratio': 0.05,
    },
    {
        'N_Months': 12,
        'global_reserve_fund': 3000000,
        'honeycomb_size_in_hive': 500,
        'bee_size_in_honeycomb': 5,
        'max_premium_constant': 100,
        'max_premium_ratio': 0.05,
    },
]

```


## 生成模拟结果

beehive.py 运行结束后, 将生成模拟结果, 存放在 ./data 目录下. 
在data目录下, 每个scenario 将会生成一个子目录, 例如上面的例子将生成 scenario00 和 scenario01 两个子目录, 存放模拟结果的CSV文件.

模拟结果的CSV文件, 分为以下两类:

1. 每月汇总结果输出

    - 文件名字格式为: **m%02d_hive_stats.csv**, 例如第2个月份的模拟结果文件为: m02_hive_stats.csv
    
2. 每月明细结果

    - 文件名字格式为: **m%02d_bees_detail.csv**, 例如第3个月份的模拟结果文件为: m03_bees_detail.csv
    

### 每月汇总结果输出
* 会员编号
* 小组编号
* 保费
* 小池余额
* 大池余额
* 出险次数
* 出险金额n

### 每月明细结果
* 小组个数
* 每小组人数
* 小池比例
* 大池单次扣款限额
* 准备金余额
* 小池余额
* 大池余额
* 总出险次数
* 总出险金额

### 统计直方图

如果在命令行指定 -o 参数, 程序将为每个scenario, 在相应的子目录下, 生成一个模拟结果统计直方图.

