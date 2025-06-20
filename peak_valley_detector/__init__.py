"""
多层次峰谷检测系统 - 严谨 Score-Driven BOCPD 版本

本包实现了基于严谨 Score-Driven BOCPD (Bayesian Online Change Point Detection) 
方法的多层次股票峰谷检测系统。

主要模块:
- core: 核心算法模块 (Score-Driven BOCPD, 变点检测)
- data: 数据获取和处理模块
- visualization: 可视化模块
- utils: 工具函数模块

基本使用:
    from peak_valley_detector.data.fetcher import StockDataFetcher
    from peak_valley_detector.core.changepoint_detector import HybridChangePointDetector
    from peak_valley_detector.visualization.visualizer import MultiLayerVisualizer
"""

__version__ = "2.0.0"
__author__ = "AI Assistant"
__email__ = "assistant@ai.com"

# 导入主要类和函数
from .core.changepoint_detector import HybridChangePointDetector, ExtremaClassifier
from .data.fetcher import StockDataFetcher
from .visualization.visualizer import MultiLayerVisualizer, create_summary_report

__all__ = [
    'HybridChangePointDetector',
    'ExtremaClassifier', 
    'StockDataFetcher',
    'MultiLayerVisualizer',
    'create_summary_report'
]
