"""
核心算法模块

包含Score-Driven BOCPD算法和变点检测器的实现
"""

from .score_driven_bocpd import ScoreDrivenModel, BayesianOnlineChangePointDetection, rigorous_sd_bocpd
from .changepoint_detector import HybridChangePointDetector, ExtremaClassifier

__all__ = [
    'ScoreDrivenModel',
    'BayesianOnlineChangePointDetection', 
    'rigorous_sd_bocpd',
    'HybridChangePointDetector',
    'ExtremaClassifier'
]
