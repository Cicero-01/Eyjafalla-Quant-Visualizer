# Eyjafalla-Quant-Backtesting-Visualizer

This is not a trading system...

## 如何开始 Quick Start 
1. 传入CSV文件 / Prepare your csv files 
2. 把CSV文件放入对应文件夹 / Put them into the results folder 
3. 运行Main.py / Run: python Main.py 
4. HTML文件会自动打开 / Open example.html in your browser （automatically）
## 如何使用自己的数据 / How to use your own backtesting data

您可以将基于自己的策略和市场数据的回测结果导入我们的可视化工具（*Eyjafalla*）中。**您只需要确保回测结果使用我们的标准格式进行命名**。所有的数据**都应由`.csv`格式储存**。

You can import backtesting results based on your own strategies and market data into our visualization tool (*Eyjafalla*). You just need to **ensure that the results are named and structured using our standard format.**  All data must be saved **in `.csv` format.** 

除了K线数据和指标外，还可以显示**至多3种**策略的净值曲线和买卖记录。

In addition to K-line data and indicators, the tool can simultaneously display NAV curves and trade records for **up to 3 different strategies**.

```
├──Main.py               # run this file / 运行这个
├──feature_store.csv     # necessary / 必须
└── results/             # Strategy results / 策略结果文件夹 
	├── trade_1/ # 策略1 (可选 / Optional) 
		├── nav.csv │
		└── trade.csv 
	├── trade_2/ # 策略2 (可选 / Optional) 
		 ├── nav.csv 
		 └── trade.csv 
	└── trade_3/ # 策略3 (可选 / Optional) 
		├── nav.csv 
		└── trade.csv
```

*Eyjafalla*可以识别的标准列名如下：

*Eyjafalla* recognizes the following standard column names:
### 1. 基础K线与特征库 / Feature Store and Basic K Lines 

*Eyjafalla*会根据上传的特征库（`feature_store.csv`)进行绘图。使用时需要提供各个交易日的价格数据画出基础K线（绿涨红跌）。

*Eyjafalla* generates visualizations based on the uploaded feature store (`feature_store.csv`). The feature store should contain daily price data required for plotting basic candlestick charts (green for upward movements and red for downward movements).
#### K线 / K lines

| Open Time | Open | Close | High | Low |
| --------- | ---- | ----- | ---- | --- |
|           |      |       |      |     |

**解释/ Description：**

| 列名 / Column | 说明 / Description                   | 数据类型 / Type  |
| ----------- | ---------------------------------- | ------------ |
| `Open Time` | 一根K线的开盘时间/ Open time of the candle | `datetime64` |
| `Open`      | 开盘价/ Open price                    | `float`      |
| `Close`     | 收盘价/ Close                         | `float`      |
| `High`      | 最高价/ High price                    | `float`      |
| `Low`       | 最低价/ Low price                     | `float`      |

如您研究的对象为一些公募基金（OF），可能会遇到只有每日净值的情况。您只需在"Open Time"列后直接创建"Close"列，在其中填入对应交易日净值即可，如：

If you are working with publicly offered funds (OFs), you may encounter datasets that only provide daily NAV data. In this case, simply create a "Close" column after the "Open Time" column and enter the corresponding NAV for each trading day, as shown below:

| Open Time | Close | 
| --------- | ---- | 
|           |      | 


#### 技术指标 / Technical Indicators

技术指标放在K线列的后面，如：

Technical indicators should be placed after the basic candlestick columns, for example:

| Open Time | ……  | Low | MA5 | Weekly_MA20 | BOLL_UB | BOLL_LB | BOLL_MB |
| --------- | --- | --- | --- | ----------- | ------- | ------- | ------- |
|           | ……  |     |     |             |         |         |         |

*Eyjafalla*能自动识别feature_store.csv中以”MA“（日均线）、”Weekly_MA“（周均线）开头，以及“BOLL_UP“、”BOLL_LB“、”BOLL_MB“（布林带三轨）命名的指标列（如有）。如果缺少某些指标列，也不会影响基础 K 线的绘制。

*Eyjafalla* can automatically detect indicator columns in `feature_store.csv` with names beginning with `MA` (daily moving averages), `Weekly_MA` (weekly moving averages), and `BOLL_UP`, `BOLL_LB`, and `BOLL_MB` (the three Bollinger Bands). (If have)

These indicator columns are optional. Missing indicator data will not affect the generation of basic candlestick charts.

若需要添加其他指标，可以在`/tools/mod_Eyjafalla.py`中的Layer2函数` _add_technical_indicators(fig, df)`下进行添加。

If you need to add custom indicators, you can modify the `_add_technical_indicators(fig, df)` function in `/tools/mod_Eyjafalla.py`.

#### 市场状态 / Market State

*Eyjafalla*能自动识别feature_store.csv中的状态列，并进行分色绘制。

*Eyjafalla* automatically detects market state columns in feature_store.csv and displays different market states using color-coded regions.

如果将市场分为2种状态，请将列名命名为"State_2"(`0/1`)；如您使用经典道氏理论等方法将市场分为3状态，请将列命名为"State_3"(`0/1/2`)，如：

If you classify the market into two states, name the column "State_2" (`0/1`). If you use methods such as the classical Dow Theory to classify the market into three states, name the column "State_3" (`0/1/2`), as shown below:

| Open Time | ……  | Low | MA5 | Weekly_MA20 | BOLL_UB | …… | Market State |
| --------- | --- | --- | --- | ----------- | ------- | ------- | ------- |
|           | ……  |     |     |             |         |  ……       |         |

请遵循 Please follow：

| 列名 / Column | 说明 / Description                   | 数据类型 / Type  |
| ----------- | ---------------------------------- | ------------ |
| `State_2` | 2状态 / 2 State | `0/1` |
| `State_3`  | 3状态 / 3 State | `0/1/2`      |



### 2.账户净值 / Net Asset Value  （nav.csv）

如果您回测时想关注模拟账户金额随着一段走势的变化，可以按如下的格式记录每个交易日结束后的净值变化：

If you want to track how the simulated account value changes throughout the backtesting period, record the daily NAV after each trading day according to the following format:

| Trade Date | NAV |
| ---------- | --- |
|            |     |

`Trade Date` 交易日/ Trading date （datetime 64）

`NAV` 账户净值/ Net Asset Value（float）

#### 为什么使用净值而不是绝对金额？/ Why use NAV instead of absolute amounts?

使用净值可以消除初始资金大小的差异，便于直观地比较不同策略的收益率表现。 

NAV normalizes the performance, making it easier to evaluate and compare different strategies regardless of the initial capital.
#### 如何计算净值？/ How to calculate NAV?

在每个交易日结束后，计算：当前本金/初始本金。

At the end of each trading day, calculate: Total Asset Value / Initial Capital.
### 3.交易明细 Trade Records (trade.csv)

用于记录回测或实盘审计时的买卖信号，可以识别的格式如下：

This file records buy and sell signals generated during backtesting or live trading audits. The supported format is as follows:

| Trade Time | Action    | Price | Position |
| ---------- | --------- | ----- | -------- |
|            | Bull/Sell |       |          |

**解释/ Description：**

| 列名 / Column  | 说明 / Description                                          | 数据类型 / Type  |
| ------------ | --------------------------------------------------------- | ------------ |
| `Trade Time` | 交易发生的时间 / Time of the trade                               | `datetime64` |
| `Action`     | 动作 (只能是 `Buy` 或 `Sell`) / Action                          | `string`     |
| `Price`      | 交易时的成交价 / Execution price                                 | `float`      |
| `Position`   | 交易完成后的账户总计价资产 / Total account asset value after the trade | `float`      |

**示例/Example: 

例如，花100 USD 买入股票，`Action`=`Buy`，`Position`=`100`  ; 卖出时账户变成110 USD，`Action`=`Sell`，`Position`=`110`

For example, if you purchase stocks worth 100 USD, set `Action`=`Buy` and `Position`=`100`. When the position is closed and the account value increases to 110 USD, record `Action`=`Sell` and `Position`=`110`.

⚠️*Eyjafalla*是基于`'Position'`计算一次买卖区间的盈亏的

⚠️*Eyjafalla* calculates the profit/loss of a trade cycle based on the changes in the `'Position'` column
## 提示 / Tips

1.我们建议您上传日线级别数据进行绘图，小时线和分钟线的数据量过大，可能会导致浏览器卡顿并影响绘图效果。

We recommend using Daily timeframe data. Hourly or minute-level data may cause browser lag due to the massive rendering load.

2.**文档更新 (Documentation):** 后续我们将上传一份单独的、更详尽的格式命名与扩展规范文档。

A separate, detailed naming convention and extension guide will be uploaded later.

## **免责声明 / Disclaimer:** 

本工具仅供研究学习使用，**不构成任何投资或财务建议**。开发者及贡献者对因使用本软件或其中代码所造成的任何直接或间接财务损失，不承担任何法律责任。金融市场交易具有极高风险，请在真实交易前进行充分测试，并自行承担所有风险 (DYOR)。

This project and its tools are provided for educational and research purposes only and **do not constitute financial or investment advice**. The developers and contributors assume no legal responsibility or liability for any direct or indirect financial losses incurred from the use of this software. Trading in financial markets involves significant risk. Always do your own research (DYOR) and test thoroughly before real trading.
