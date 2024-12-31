import backtrader as bt
import pandas as pd
import datetime


class MovingAverageStrategy(bt.Strategy):
    """
    简单的移动平均线策略。

    当收盘价上穿移动平均线时买入，当收盘价下穿移动平均线时卖出。

    Args:
        ma_period (int): 移动平均线的周期，默认为20。
        printlog (bool): 是否打印日志，默认为False。
    """
    params = (
        ("ma_period", 20), # 移动平均线的周期，默认为20
        ("printlog", False) # 是否打印日志，默认为False
    )

    def log(self, txt, dt=None):
        """
        记录日志到控制台。

        Args:
            txt (str): 要打印的日志信息。
            dt (datetime.date, 可选): 日志的时间戳，默认为当前数据点的时间。
        """
        dt = dt or self.datas[0].datetime.date(0)
        if self.params.printlog:
             print(f"{dt.isoformat()} {txt}")

    def __init__(self):
      """
        初始化策略。

        获取收盘价数据，创建移动平均线指标，并初始化订单状态。
      """
      self.dataclose = self.datas[0].close
      self.order = None
      self.ma = bt.indicators.SimpleMovingAverage(self.datas[0],period=self.params.ma_period)

    def notify_order(self, order):
        """
          订单状态通知。

          当订单状态发生变化时，会调用此方法，例如提交、接受、完成、取消等。

          Args:
              order (bt.order.Order): 订单对象。
        """
        if order.status in [order.Submitted, order.Accepted]:
           return

        if order.status in [order.Completed]:
           if order.isbuy():
                self.log(f"BUY EXECUTED, Price:{order.executed.price:.2f},Cost:{order.executed.price * order.executed.size:.2f},Size:{order.executed.size: .2f}")
           elif order.issell():
              self.log(f"SELL EXECUTED, Price:{order.executed.price:.2f},Cost:{order.executed.price * order.executed.size:.2f},Size:{order.executed.size: .2f}")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
           self.log(f"Order Canceled/Margin/Rejected")


    def notify_trade(self, trade):
      if not trade.isclosed:
        return
      self.log(f"OPERATION PROFIT, GROSS:{trade.pnl:.2f}, NET:{trade.pnlcomm:.2f}")

    def next(self):
      if self.order:
        return
      if not self.position:
        if self.dataclose[0] > self.ma[0]:
          self.log(f"BUY CREATE, Price:{self.dataclose[0]:.2f}")
          self.order = self.buy()
      elif self.position:
         if self.dataclose[0] < self.ma[0]:
           self.log(f"SELL CREATE, Price:{self.dataclose[0]:.2f}")
           self.order = self.close()


def run_backtest(data_path="data2.csv"):
    cerebro = bt.Cerebro()

    # 加载数据
    data = pd.read_csv(data_path, parse_dates=['datetime'],index_col='datetime')
    data = bt.feeds.PandasData(dataname=data,fromdate = datetime.datetime(2023, 1, 1),todate = datetime.datetime(2023,1,31))
    cerebro.adddata(data)

    # 添加策略
    cerebro.addstrategy(MovingAverageStrategy, printlog=True)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)

    # 设置交易手续费
    cerebro.broker.setcommission(commission=0.0003)

    # 设置仓位管理
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name = "drawdown")

     # 添加观察者
    cerebro.addobserver(bt.observers.Broker)

    # 运行回测
    results = cerebro.run()

    # 输出结果
    sharpe_ratio = results[0].analyzers.sharpe.get_analysis()['sharperatio']
    drawdown = results[0].analyzers.drawdown.get_analysis()['max']

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
    print(f"Sharpe Ratio: {sharpe_ratio}")
    print(f"Max DrawDown: {drawdown}")

    cerebro.plot()
    return cerebro

if __name__ == "__main__":
    cerebro = run_backtest(data_path="data2.csv")
