"""
Peak Valley Detector 基本使用示例
演示如何使用多层次峰谷检测系统
"""

import sys
import os

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from peak_valley_detector import (
    StockDataFetcher,
    HybridChangePointDetector,
    ExtremaClassifier,
    MultiLayerVisualizer,
    create_summary_report
)
import numpy as np
from scipy.signal import argrelextrema
import ta


def basic_example():
    """基本使用示例"""
    print("=" * 60)
    print("Peak Valley Detector - 基本使用示例")
    print("=" * 60)
    
    # 配置参数
    SYMBOL = "000001"  # 平安银行
    START_DATE = "2024-06-01"
    
    print(f"分析股票: {SYMBOL}")
    print(f"起始日期: {START_DATE}\n")
    
    try:
        # 1. 数据获取
        print("1. 获取股票数据...")
        data_fetcher = StockDataFetcher(SYMBOL, START_DATE, source="akshare")
        
        df_daily = data_fetcher.get_daily()
        wk_series = data_fetcher.get_weekly()
        h1_data = data_fetcher.get_60min()
        
        print(f"   日线数据: {len(df_daily)} 条")
        print(f"   周线数据: {len(wk_series)} 条")
        print(f"   60分钟数据: {len(h1_data)} 条\n")
        
        # 2. 宏观层检测 (周线 + SD-BOCPD)
        print("2. 宏观层变点检测...")
        detector = HybridChangePointDetector()
        cp_indices = detector.detect_comprehensive(wk_series.values)
        
        # 峰谷分类
        classifier = ExtremaClassifier()
        macro_peaks_dt, macro_troughs_dt = classifier.classify_changepoints(
            wk_series,
            cp_indices,
            window=1,  # 缩小窗口提高响应速度
            check_right=False,
        )
        
        # 3. 中观层检测 (日线)
        print("\n3. 中观层峰谷检测...")
        mid_peaks_idx = argrelextrema(df_daily['close'].values, np.greater, order=12)[0]
        mid_troughs_idx = argrelextrema(df_daily['close'].values, np.less, order=12)[0]
        
        mid_peaks_dt = df_daily.iloc[mid_peaks_idx].index
        mid_troughs_dt = df_daily.iloc[mid_troughs_idx].index
        
        print(f"   日线峰值: {len(mid_peaks_dt)} 个")
        print(f"   日线谷值: {len(mid_troughs_dt)} 个")
        
        # 4. 微观层检测 (60分钟)
        print("\n4. 微观层峰谷检测...")
        close_60 = h1_data['收盘']
        atr = ta.volatility.average_true_range(
            h1_data['最高'], h1_data['最低'], h1_data['收盘'], window=14
        )
        
        # 过滤低波动区域
        valid = atr > atr.mean() * 1.2
        valid_close = close_60[valid]
        
        from scipy.signal import find_peaks
        micro_peaks_idx = find_peaks(valid_close.values, distance=6)[0]
        micro_troughs_idx = find_peaks(-valid_close.values, distance=6)[0]
        
        micro_peaks_dt = valid_close.index[micro_peaks_idx]
        micro_troughs_dt = valid_close.index[micro_troughs_idx]
        
        print(f"   60分钟峰值: {len(micro_peaks_dt)} 个")
        print(f"   60分钟谷值: {len(micro_troughs_dt)} 个")
        
        # 5. 结果可视化
        print("\n5. 生成可视化图表...")
        visualizer = MultiLayerVisualizer(figsize=(14, 8))
        
        # 绘制综合结果
        visualizer.plot_multi_layer_results(
            symbol=SYMBOL,
            daily_data=df_daily,
            weekly_data=wk_series,
            h1_data=h1_data,
            macro_peaks=macro_peaks_dt,
            macro_troughs=macro_troughs_dt,
            mid_peaks=mid_peaks_dt,
            mid_troughs=mid_troughs_dt,
            micro_peaks=micro_peaks_dt,
            micro_troughs=micro_troughs_dt
        )
        
        # 6. 生成摘要报告
        create_summary_report(
            symbol=SYMBOL,
            macro_peaks_count=len(macro_peaks_dt),
            macro_troughs_count=len(macro_troughs_dt),
            mid_peaks_count=len(mid_peaks_dt),
            mid_troughs_count=len(mid_troughs_dt),
            micro_peaks_count=len(micro_peaks_dt),
            micro_troughs_count=len(micro_troughs_dt),
            total_changepoints=len(cp_indices)
        )
        
        print("\n示例运行完成！")
        
    except Exception as e:
        print(f"运行出错: {e}")
        print("请确保已安装所需依赖包：pip install -r requirements.txt")


def advanced_example():
    """高级使用示例 - 自定义参数"""
    print("\n" + "=" * 60)
    print("Peak Valley Detector - 高级使用示例")
    print("=" * 60)
    
    # 创建合成数据进行演示
    import pandas as pd
    
    # 生成模拟股价数据
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    trend = np.linspace(10, 15, 100)
    noise = np.random.randn(100) * 0.5
    prices = trend + np.sin(np.linspace(0, 4*np.pi, 100)) * 2 + noise
    
    series = pd.Series(prices, index=dates)
    
    print("使用合成数据演示高级功能...")
    
    # 使用自定义参数的变点检测
    detector = HybridChangePointDetector()
    
    # 尝试不同的检测方法
    print("\n测试不同检测算法:")
    
    # 方法1: Ruptures Dynp
    cp_dynp = detector.detect_ruptures_dynp(series.values, n_bkps=8)
    print(f"Dynp 方法检测到 {len(cp_dynp)} 个变点")
    
    # 方法2: SD-BOCPD (自定义参数)
    cp_sdbocpd = detector.detect_sd_bocpd(
        series.values, 
        nu=4.0, omega=0.001, alpha=0.08, beta=0.85,
        hazard_rate=1/20, threshold=0.4
    )
    print(f"SD-BOCPD 方法检测到 {len(cp_sdbocpd)} 个变点")
    
    # 方法3: 基于波动率
    cp_vol = detector.detect_volatility_based(series.values, window=5, percentile=80)
    print(f"波动率方法检测到 {len(cp_vol)} 个变点")
    
    # 可视化比较
    visualizer = MultiLayerVisualizer()
    visualizer.plot_changepoint_analysis(
        series=series,
        changepoints=cp_dynp,
        title="合成数据变点检测示例"
    )
    
    print("\n高级示例运行完成！")


if __name__ == "__main__":
    # 运行基本示例
    basic_example()
    
    # 运行高级示例
    advanced_example()
