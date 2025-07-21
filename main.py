"""
多层次峰谷检测主程序 - 严谨 Score-Driven BOCPD 版本
使用模块化架构，集成专业变点检测算法
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, argrelextrema
import ta
import warnings

# 导入自定义模块
from peak_valley_detector.data.fetcher import StockDataFetcher
from peak_valley_detector.core.changepoint_detector import HybridChangePointDetector, ExtremaClassifier
from peak_valley_detector.visualization.visualizer import MultiLayerVisualizer, create_summary_report

warnings.filterwarnings('ignore')


def main():
    """主程序入口"""
    
    # ========== 1. 参数配置 ==========
    SYMBOL = "000001"  # 平安银行
    START_DATE = "2024-06-01"
    
    print(f"开始分析股票 {SYMBOL}，起始日期: {START_DATE}")
    print("使用严谨的 Score-Driven BOCPD 方法进行多层次峰谷检测\n")
    
    # ========== 2. 数据获取 ==========
    print("正在获取数据...")
    data_fetcher = StockDataFetcher(
        source="akshare",
    )

    # 获取各时间周期数据
    df_daily = data_fetcher.get_daily(SYMBOL, start_date=START_DATE)
    wk_series = data_fetcher.get_weekly(SYMBOL, start_date=START_DATE)
    h1_data = data_fetcher.get_60min(SYMBOL, start_date=START_DATE)
    
    print(f"日线数据: {len(df_daily)} 条")
    print(f"周线数据: {len(wk_series)} 条")
    print(f"60分钟数据: {len(h1_data)} 条\n")
    
    # ========== 3. 宏观层检测 (周线 + SD-BOCPD) ==========
    print("=" * 50)
    print("宏观层分析 (周线 + Score-Driven BOCPD)")
    print("=" * 50)
    
    # 使用混合变点检测器
    detector = HybridChangePointDetector()
    cp_indices = detector.detect_comprehensive(wk_series.values)
    
    print(f"检测到 {len(cp_indices)} 个变点: {cp_indices}\n")
    
    # 峰谷分类
    classifier = ExtremaClassifier()
    macro_peaks_dt, macro_troughs_dt = classifier.classify_changepoints(
        wk_series, cp_indices, window=2
    )
    
    # ========== 4. 中观层检测 (日线) ==========
    print("\n" + "=" * 50)
    print("中观层分析 (日线)")
    print("=" * 50)
    
    # 使用传统方法检测日线极值点
    mid_peaks_idx = argrelextrema(df_daily['close'].values, np.greater, order=12)[0]
    mid_troughs_idx = argrelextrema(df_daily['close'].values, np.less, order=12)[0]
    
    mid_peaks_dt = df_daily.iloc[mid_peaks_idx].index
    mid_troughs_dt = df_daily.iloc[mid_troughs_idx].index
    
    print(f"中观层检测结果:")
    print(f"  • 日线峰值: {len(mid_peaks_dt)} 个")
    print(f"  • 日线谷值: {len(mid_troughs_dt)} 个")
    
    # ========== 5. 微观层检测 (60分钟) ==========
    print("\n" + "=" * 50)
    print("微观层分析 (60分钟)")
    print("=" * 50)
    
    # ATR过滤 + 峰谷检测
    close_60 = h1_data['收盘']
    atr = ta.volatility.average_true_range(
        h1_data['最高'], h1_data['最低'], h1_data['收盘'], window=14
    )
    
    # 过滤低波动区域
    valid = atr > atr.mean() * 1.2
    valid_close = close_60[valid]
    
    # 检测微观极值点
    micro_peaks_idx = find_peaks(valid_close.values, distance=6)[0]
    micro_troughs_idx = find_peaks(-valid_close.values, distance=6)[0]
    
    micro_peaks_dt = valid_close.index[micro_peaks_idx]
    micro_troughs_dt = valid_close.index[micro_troughs_idx]
    
    print(f"微观层检测结果:")
    print(f"  • 60分钟峰值: {len(micro_peaks_dt)} 个")
    print(f"  • 60分钟谷值: {len(micro_troughs_dt)} 个")
    
    # ========== 6. 结果可视化 ==========
    print("\n" + "=" * 50)
    print("生成可视化图表")
    print("=" * 50)
    
    visualizer = MultiLayerVisualizer(figsize=(14, 8))
    
    # 绘制综合结果图
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
    
    # 绘制变点分析图
    visualizer.plot_changepoint_analysis(
        series=wk_series,
        changepoints=cp_indices,
        title=f"{SYMBOL} - Score-Driven BOCPD 变点检测分析"
    )
    
    # ========== 7. 生成摘要报告 ==========
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


if __name__ == "__main__":
    main()
