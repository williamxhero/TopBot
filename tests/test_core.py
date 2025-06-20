"""
核心模块测试
"""

import pytest
import numpy as np
import pandas as pd
from peak_valley_detector.core.score_driven_bocpd import ScoreDrivenModel, rigorous_sd_bocpd
from peak_valley_detector.core.changepoint_detector import HybridChangePointDetector, ExtremaClassifier


class TestScoreDrivenModel:
    """测试 Score-Driven 模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = ScoreDrivenModel(nu=5.0, omega=0.01, alpha=0.05, beta=0.9)
        assert model.nu == 5.0
        assert model.omega == 0.01
        assert model.alpha == 0.05
        assert model.beta == 0.9
    
    def test_update_variance(self):
        """测试方差更新"""
        model = ScoreDrivenModel()
        variance_t = 0.1
        score_t = 0.05
        new_variance = model.update_variance(variance_t, score_t)
        assert new_variance > 0
        assert isinstance(new_variance, float)
    
    def test_compute_score(self):
        """测试得分计算"""
        model = ScoreDrivenModel()
        x_t = 10.0
        mu_t = 9.5
        variance_t = 0.1
        score = model.compute_score(x_t, mu_t, variance_t)
        assert isinstance(score, float)


class TestChangePointDetector:
    """测试变点检测器"""
    
    def setup_method(self):
        """设置测试数据"""
        np.random.seed(42)
        self.series = np.random.randn(100)
        self.detector = HybridChangePointDetector()
    
    def test_initialization(self):
        """测试检测器初始化"""
        detector = HybridChangePointDetector()
        assert detector is not None
    
    def test_detect_ruptures_dynp(self):
        """测试 Ruptures Dynp 算法"""
        changepoints = self.detector.detect_ruptures_dynp(self.series, n_bkps=5)
        assert isinstance(changepoints, list)
        assert all(isinstance(cp, int) for cp in changepoints)
    
    def test_detect_volatility_based(self):
        """测试基于波动率的检测"""
        changepoints = self.detector.detect_volatility_based(self.series)
        assert isinstance(changepoints, list)


class TestExtremaClassifier:
    """测试极值点分类器"""
    
    def setup_method(self):
        """设置测试数据"""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        values = np.sin(np.linspace(0, 4*np.pi, 100)) + np.random.randn(100) * 0.1
        self.series = pd.Series(values, index=dates)
    
    def test_classify_extrema(self):
        """测试极值点分类"""
        # 测试峰值
        result = ExtremaClassifier.classify_extrema(
            self.series.values, 25, window=3
        )
        assert result in ['peak', 'trough', None]
    
    def test_classify_changepoints(self):
        """测试变点分类"""
        changepoints = [10, 30, 50, 70]
        peaks, troughs = ExtremaClassifier.classify_changepoints(
            self.series, changepoints, window=2
        )
        assert isinstance(peaks, list)
        assert isinstance(troughs, list)


class TestSDBocdpIntegration:
    """测试 SD-BOCPD 集成功能"""
    
    def test_rigorous_sd_bocpd_basic(self):
        """测试基本 SD-BOCPD 功能"""
        np.random.seed(42)
        series = np.random.randn(50)
        
        changepoints, variances, scores = rigorous_sd_bocpd(
            series, nu=5.0, omega=0.01, alpha=0.05, beta=0.9
        )
        
        assert isinstance(changepoints, list)
        assert isinstance(variances, np.ndarray)
        assert isinstance(scores, np.ndarray)
        assert len(variances) == len(series)
        assert len(scores) == len(series)
    
    def test_rigorous_sd_bocpd_empty_series(self):
        """测试空序列处理"""
        series = np.array([])
        changepoints, variances, scores = rigorous_sd_bocpd(series)
        
        assert changepoints == []
        assert len(variances) == 0
        assert len(scores) == 0


if __name__ == "__main__":
    pytest.main([__file__])
