"""
可视化模块
处理多层次峰谷检测结果的图表展示
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Optional
import warnings

# 设置matplotlib参数
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 110
warnings.filterwarnings('ignore')


class MultiLayerVisualizer:
    """多层次峰谷检测结果可视化器"""
    
    def __init__(self, figsize: tuple = (12, 6)):
        """
        初始化可视化器
        
        Args:
            figsize: 图表尺寸
        """
        self.figsize = figsize
    
    def plot_multi_layer_results(self, 
                                symbol: str,
                                daily_data: pd.DataFrame,
                                weekly_data: pd.Series,
                                h1_data: pd.DataFrame,
                                macro_peaks: List,
                                macro_troughs: List,
                                mid_peaks: List,
                                mid_troughs: List,
                                micro_peaks: List,
                                micro_troughs: List) -> None:
        """
        绘制多层次峰谷检测结果
        
        Args:
            symbol: 股票代码
            daily_data: 日线数据
            weekly_data: 周线数据
            h1_data: 60分钟数据
            macro_peaks: 宏观峰值日期列表
            macro_troughs: 宏观谷值日期列表
            mid_peaks: 中观峰值日期列表
            mid_troughs: 中观谷值日期列表
            micro_peaks: 微观峰值日期列表
            micro_troughs: 微观谷值日期列表
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 绘制主要价格线（日线）
        ax.plot(daily_data.index, daily_data['close'], 
               label='Close Price', linewidth=1, color='black', alpha=0.8)
        
        # 宏观层 (Score-Driven BOCPD)
        if len(macro_peaks) > 0:
            ax.scatter(macro_peaks, weekly_data.loc[macro_peaks],
                      marker='^', s=90, color='red', 
                      label='Macro Peak (SD-BOCPD)', zorder=5)
        
        if len(macro_troughs) > 0:
            ax.scatter(macro_troughs, weekly_data.loc[macro_troughs],
                      marker='v', s=90, color='green', 
                      label='Macro Trough (SD-BOCPD)', zorder=5)
        
        # 中观层
        if len(mid_peaks) > 0:
            ax.scatter(mid_peaks, daily_data.loc[mid_peaks, 'close'],
                      marker='^', s=50, color='orange', 
                      label='Mid Peak', alpha=0.8, zorder=4)
        
        if len(mid_troughs) > 0:
            ax.scatter(mid_troughs, daily_data.loc[mid_troughs, 'close'],
                      marker='v', s=50, color='lime', 
                      label='Mid Trough', alpha=0.8, zorder=4)
        
        # 微观层（使用右轴）
        if len(micro_peaks) > 0 or len(micro_troughs) > 0:
            ax2 = ax.twinx()
            
            if len(micro_peaks) > 0:
                ax2.scatter(micro_peaks, h1_data.loc[micro_peaks, '收盘'],
                           marker='^', s=25, color='purple', 
                           label='Micro Peak', alpha=0.6, zorder=3)
            
            if len(micro_troughs) > 0:
                ax2.scatter(micro_troughs, h1_data.loc[micro_troughs, '收盘'],
                           marker='v', s=25, color='blue', 
                           label='Micro Trough', alpha=0.6, zorder=3)
            
            # 同步y轴范围
            ax2.set_ylim(ax.get_ylim())
            ax2.set_ylabel('60min Price', fontsize=10, alpha=0.7)
        
        # 设置图表属性
        ax.set_title(f"{symbol} – Multi-Layer Peaks & Troughs (SD-BOCPD)", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price', fontsize=12)
        ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # 自动调整日期显示
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.show()
    
    def plot_changepoint_analysis(self, 
                                 series: pd.Series,
                                 changepoints: List[int],
                                 title: str = "Change Point Detection Results") -> None:
        """
        绘制变点检测分析图
        
        Args:
            series: 时间序列数据
            changepoints: 变点索引列表
            title: 图表标题
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # 上图：原始序列和变点
        ax1.plot(series.index, series.values, 'b-', linewidth=1, alpha=0.8)
        
        if changepoints:
            cp_dates = [series.index[cp] for cp in changepoints if cp < len(series)]
            cp_values = [series.iloc[cp] for cp in changepoints if cp < len(series)]
            ax1.scatter(cp_dates, cp_values, color='red', s=50, 
                       marker='o', zorder=5, label=f'{len(changepoints)} Change Points')
        
        ax1.set_title(title, fontsize=14)
        ax1.set_ylabel('Price', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 下图：收益率序列
        returns = series.pct_change().dropna()
        ax2.plot(returns.index, returns.values, 'g-', linewidth=0.8, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('Returns', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Return', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_score_driven_diagnostics(self, 
                                     series: pd.Series,
                                     scores: np.ndarray,
                                     variances: np.ndarray,
                                     changepoints: List[int]) -> None:
        """
        绘制Score-Driven模型诊断图
        
        Args:
            series: 原始时间序列
            scores: 得分序列
            variances: 方差序列
            changepoints: 变点列表
        """
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        
        # 价格序列
        axes[0].plot(series.index, series.values, 'b-', linewidth=1)
        if changepoints:
            cp_dates = [series.index[cp] for cp in changepoints if cp < len(series)]
            cp_values = [series.iloc[cp] for cp in changepoints if cp < len(series)]
            axes[0].scatter(cp_dates, cp_values, color='red', s=40, zorder=5)
        axes[0].set_title('Price Series with Change Points', fontsize=12)
        axes[0].set_ylabel('Price')
        axes[0].grid(True, alpha=0.3)
        
        # 得分序列
        if len(scores) > 0:
            score_dates = series.index[1:len(scores)+1]
            axes[1].plot(score_dates, scores[1:], 'orange', linewidth=1)
            axes[1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
            axes[1].set_title('GAS Model Scores', fontsize=12)
            axes[1].set_ylabel('Score')
            axes[1].grid(True, alpha=0.3)
        
        # 动态方差序列
        if len(variances) > 0:
            var_dates = series.index[1:len(variances)+1]
            axes[2].plot(var_dates, variances[1:], 'green', linewidth=1)
            axes[2].set_title('Dynamic Variance', fontsize=12)
            axes[2].set_xlabel('Date')
            axes[2].set_ylabel('Variance')
            axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()


def create_summary_report(symbol: str,
                         macro_peaks_count: int,
                         macro_troughs_count: int,
                         mid_peaks_count: int,
                         mid_troughs_count: int,
                         micro_peaks_count: int,
                         micro_troughs_count: int,
                         total_changepoints: int) -> None:
    """
    创建检测结果摘要报告
    
    Args:
        symbol: 股票代码
        各层次的峰谷数量
        total_changepoints: 总变点数
    """
    print("\n" + "="*60)
    print(f"多层次峰谷检测结果摘要 - {symbol}")
    print("="*60)
    print(f"宏观层 (周线 + SD-BOCPD):")
    print(f"  • 峰值 (Peaks):  {macro_peaks_count}")
    print(f"  • 谷值 (Troughs): {macro_troughs_count}")
    print(f"  • 总变点数: {total_changepoints}")
    print(f"\n中观层 (日线):")
    print(f"  • 峰值 (Peaks):  {mid_peaks_count}")
    print(f"  • 谷值 (Troughs): {mid_troughs_count}")
    print(f"\n微观层 (60分钟):")
    print(f"  • 峰值 (Peaks):  {micro_peaks_count}")
    print(f"  • 谷值 (Troughs): {micro_troughs_count}")
    print("="*60)
    print("检测方法: 严谨 Score-Driven BOCPD + Ruptures 专业库")
    print("="*60)
