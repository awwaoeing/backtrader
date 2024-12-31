import backtrader as bt
import datetime

class MyStrategy(bt.Strategy):

    def log(self, csv, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), csv))

    def __init__(self):
        self.sma = bt.indicators.SMA(self.datas[0], period=3)
        self.crossup = bt.indicators.CrossUp(self.datas[0], self.sma)
        self.crossdown = bt.indicators.CrossDown(self.datas[0], self.sma)

    def next(self):
        if self.crossup > 0:
            self.log('BUY, %.2f' % self.datas[0].close[0])
            self.buy()
        elif self.crossdown > 0:
            self.log('SELL, %.2f' % self.datas[0].close[0])
            self.close()

if __name__ == '__main__':

    cerebro = bt.Cerebro()

      # 1. 添加数据
    data = bt.feeds.GenericCSVData(
            dataname='data.csv',  # 替换为你的数据文件名
            dtformat=('%Y-%m-%d'),
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=-1  # 未使用，设置为 -1
            )
    cerebro.adddata(data)

    # 2. 添加策略
    cerebro.addstrategy(MyStrategy)

    # 3. 设置初始资金
    cerebro.broker.setcash(100000.0)

    # 4. 设置交易佣金
    cerebro.broker.setcommission(commission=0.001)

    # 5. 运行回测
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    cerebro.run()
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')

    # 6. 可选：绘制回测结果
    cerebro.plot()
