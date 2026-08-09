import webbrowser
from tools.mod_Eyjafalla import draw_kline

print("正在运行可视化模块...")
print("Visualization Module is running ...")

# 1. 填写K线特征库路径
# Step1. select the path of your featurestore.csv
kline_path = "Example_featurestore.csv"

# 2. (可选)配置你要对比的策略结果文件夹,最多传入三组，每组只需保证文件夹里有 trade.csv
# Step2. (optional) Configure strategy folders, up to 3 strategies
# just ensure a file named 'trade.csv' exists in each folder
my_strategies = [
    {'name': 'CTA_Baseline', 'folder': 'results/trade_1'},
    {'name': 'CTA_HMM_Enhanced', 'folder': 'results/trade_2'},
    {'name': 'CTA_2', 'folder': 'results/trade_3'}
]

# name: 网页中策略显示的名字

# 3. 极简调用，传入参数，填写将要生成的HTML文件的名称，获取返回的HTML路径
# Step3. input the parameters such as paths, the path of HTML generated would return
html_path = draw_kline(
    kline_csv_path=kline_path,
    strategies_config=my_strategies,
    output_html="Example.html",  # 生成文件名 / the name of the HTML generated
    title="BTC_USDT backtesing"        # 页面标题 / the title in the HTML page
)

# 4. (可选) 自动在系统默认浏览器中弹开画好的图表
# Step4. (optional) open the html file in the browser automatically
print(f"🎉 准备在浏览器中打开: {html_path}")
webbrowser.open(f"file://{html_path}")