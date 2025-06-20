"""
数据获取模块
处理股票历史数据的抓取和预处理
"""

import akshare as ak
import pandas as pd
import numpy as np


class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self, symbol: str, start_date: str):
        """
        初始化数据获取器
        
        Args:
            symbol: 股票代码，如 "000001"
            start_date: 开始日期，格式 "YYYY-MM-DD"
        """
        self.symbol = symbol
        self.start_date = start_date
    
    def get_hist(self, period: str) -> pd.DataFrame:
        """
        通用历史行情抓取（复权收盘 / 最高 / 最低）
        
        Args:
            period: 时间周期，如 "daily", "weekly"
            
        Returns:
            DataFrame: 包含 close, high, low 的历史数据
        """
        df_raw = ak.stock_zh_a_hist(
            symbol=self.symbol,
            period=period,
            start_date=self.start_date,
            adjust="qfq"
        )
        
        df = (df_raw[['日期', '收盘', '最高', '最低']]
               .rename(columns={
                   '日期': 'date',
                   '收盘': 'close',
                   '最高': 'high',
                   '最低': 'low'
               }))
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()
        return df
    
    def get_daily(self) -> pd.DataFrame:
        """获取日线数据"""
        return self.get_hist('daily')
    
    def get_weekly(self) -> pd.Series:
        """获取周线收盘价数据"""
        daily = self.get_daily()
        return daily['close'].resample('W-FRI').last()
    
    def get_60min(self) -> pd.DataFrame:
        """获取60分钟K线数据"""
        h1_raw = ak.stock_zh_a_hist_min_em(
            symbol=self.symbol,
            period="60",
            adjust="qfq"
        )
        
        # 合成完整时间戳，防止索引重复
        h1_raw['datetime'] = pd.to_datetime(h1_raw['时间'])
        h1_raw = h1_raw.set_index('datetime').sort_index()
        return h1_raw
