import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Use English labels to avoid Chinese font issues
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

print("Loading backtest results...")

# Load data
portfolio1 = pd.read_csv("真实数据_策略1年均线.csv")
portfolio2 = pd.read_csv("真实数据_策略2RSI.csv")
portfolio1['日期'] = pd.to_datetime(portfolio1['日期'])
portfolio2['日期'] = pd.to_datetime(portfolio2['日期'])

# Load index data
df = pd.read_csv("931446_真实完整历史数据.csv")
df['日期'] = pd.to_datetime(df['日期'])
df = df[df['日期'] <= '2023-12-31']

# Calculate MA250 and RSI
df['MA250'] = df['收盘'].rolling(window=250).mean()
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
df['RSI'] = calculate_rsi(df['收盘'])

# Buy & Hold baseline
start_idx = 250
bh_values = 100000 * (df['收盘'].iloc[start_idx:] / df['收盘'].iloc[start_idx])

# Create figure with 4 subplots
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(4, 1, hspace=0.35, height_ratios=[2, 1, 1, 1])

# 1. Portfolio Value Comparison
ax1 = fig.add_subplot(gs[0])
ax1.plot(portfolio1['日期'], portfolio1['市值'], label='Strategy 1: MA250', linewidth=2, color='blue')
ax1.plot(portfolio2['日期'], portfolio2['市值'], label='Strategy 2: RSI', linewidth=2, color='orange')
ax1.plot(df['日期'].iloc[start_idx:], bh_values, label='Buy & Hold', linewidth=2, color='green', alpha=0.7)
ax1.axhline(y=100000, color='gray', linestyle='--', label='Initial Capital', alpha=0.5)
ax1.set_title('Portfolio Value Comparison (2009-2023)', fontsize=16, pad=20)
ax1.set_ylabel('Value (Yuan)', fontsize=12)
ax1.legend(loc='best', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1.xaxis.set_major_locator(mdates.YearLocator(2))

# 2. Index Price with MA250
ax2 = fig.add_subplot(gs[1])
ax2.plot(df['日期'], df['收盘'], label='Index Price', linewidth=1.5, color='blue')
ax2.plot(df['日期'], df['MA250'], label='MA250', linewidth=1.5, color='red', alpha=0.7)
ax2.set_title('Index 931446 Price & MA250', fontsize=14, pad=15)
ax2.set_ylabel('Price', fontsize=12)
ax2.legend(loc='best', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax2.xaxis.set_major_locator(mdates.YearLocator(2))

# 3. RSI Indicator
ax3 = fig.add_subplot(gs[2])
ax3.plot(df['日期'], df['RSI'], label='RSI(14)', linewidth=1.5, color='purple')
ax3.axhline(y=75, color='red', linestyle='--', label='Overbought 75', alpha=0.5)
ax3.axhline(y=70, color='red', linestyle=':', label='Overbought 70', alpha=0.5)
ax3.axhline(y=30, color='green', linestyle='--', label='Oversold 30', alpha=0.5)
ax3.set_title('RSI Indicator', fontsize=14, pad=15)
ax3.set_ylabel('RSI', fontsize=12)
ax3.set_ylim(0, 100)
ax3.legend(loc='best', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax3.xaxis.set_major_locator(mdates.YearLocator(2))

# 4. Drawdown Comparison
ax4 = fig.add_subplot(gs[3])
cummax1 = portfolio1['市值'].cummax()
drawdown1 = (portfolio1['市值'] - cummax1) / cummax1 * 100
cummax2 = portfolio2['市值'].cummax()
drawdown2 = (portfolio2['市值'] - cummax2) / cummax2 * 100

ax4.plot(portfolio1['日期'], drawdown1, label='Strategy 1 Drawdown', linewidth=1.5, color='blue')
ax4.plot(portfolio2['日期'], drawdown2, label='Strategy 2 Drawdown', linewidth=1.5, color='orange')
ax4.fill_between(portfolio1['日期'], drawdown1, 0, color='blue', alpha=0.2)
ax4.fill_between(portfolio2['日期'], drawdown2, 0, color='orange', alpha=0.2)
ax4.set_title('Drawdown Comparison', fontsize=14, pad=15)
ax4.set_ylabel('Drawdown (%)', fontsize=12)
ax4.legend(loc='best', fontsize=10)
ax4.grid(True, alpha=0.3)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax4.xaxis.set_major_locator(mdates.YearLocator(2))

plt.tight_layout()
plt.savefig('Backtest_Comparison_Chart.png', dpi=150, bbox_inches='tight')
print("Chart saved as: Backtest_Comparison_Chart.png")

# Create a summary table image
fig2, ax = plt.subplots(figsize=(10, 4))
ax.axis('off')

# Create summary data
summary_data = [
    ['Metric', 'MA250 Strategy', 'RSI Strategy', 'Buy & Hold'],
    ['Final Value (Yuan)', '175,587', '163,065', '264,143'],
    ['Return (%)', '75.59%', '63.07%', '164.14%'],
    ['Max Drawdown (%)', '-32.07%', '-29.12%', 'N/A'],
    ['Trade Count', '95', '81', 'N/A']
]

table = ax.table(cellText=summary_data, cellLoc='center', loc='center',
                 colWidths=[0.25, 0.25, 0.25, 0.25])
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 2)

# Style the header row
for i in range(4):
    table[(0, i)].set_facecolor('#4472C4')
    table[(0, i)].set_text_props(weight='bold', color='white')

plt.title('Backtest Results Summary (2009-2023)', fontsize=16, pad=20)
plt.savefig('Backtest_Summary_Table.png', dpi=150, bbox_inches='tight')
print("Summary table saved as: Backtest_Summary_Table.png")

print("\nDone! Charts created successfully.")