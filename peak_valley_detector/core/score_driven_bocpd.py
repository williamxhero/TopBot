"""
Score-Driven BOCPD 算法模块
实现严谨的 GAS 模型和贝叶斯在线变点检测
"""

import numpy as np
from scipy import stats
from typing import List, Tuple


class ScoreDrivenModel:
    """GAS (Generalized Autoregressive Score) 模型实现
    基于学生 t 分布的 Score-Driven 动态参数更新
    """
    
    def __init__(self, nu: float = 5.0, omega: float = 0.01, 
                 alpha: float = 0.05, beta: float = 0.9):
        """
        初始化 GAS 模型
        
        Args:
            nu: 学生 t 分布自由度参数
            omega: GAS 常数项
            alpha: score 系数 (短期冲击)
            beta: 自回归系数 (长期持续)
        """
        self.nu = nu
        self.omega = omega
        self.alpha = alpha
        self.beta = beta
        
    def update_variance(self, variance_t: float, score_t: float) -> float:
        """GAS 方差更新方程"""
        return self.omega + self.alpha * score_t**2 + self.beta * variance_t
    
    def compute_score(self, x_t: float, mu_t: float, variance_t: float) -> float:
        """计算基于学生 t 分布的得分函数"""
        standardized = (x_t - mu_t) / np.sqrt(variance_t)
        score = (self.nu + 1) * standardized / (self.nu + standardized**2)
        return score * np.sqrt(variance_t)


class BayesianOnlineChangePointDetection:
    """贝叶斯在线变点检测 (BOCPD) 算法实现"""
    
    def __init__(self, hazard_rate: float = 1/100, threshold: float = 0.7):
        """
        初始化 BOCPD 算法
        
        Args:
            hazard_rate: 变点先验概率 (1/期望运行长度)
            threshold: 变点检测阈值
        """
        self.hazard_rate = hazard_rate
        self.threshold = threshold
        self.run_length_probs = np.array([1.0])  # P(r_t)
        self.changepoints = []
        
    def update(self, predictive_prob: float) -> bool:
        """
        更新运行长度分布并检测变点
        
        Args:
            predictive_prob: 当前观测的预测概率
            
        Returns:
            bool: 是否检测到变点
        """
        # 预测分布: P(r_t | x_1:t-1)
        growth_probs = self.run_length_probs * (1 - self.hazard_rate)
        changepoint_prob = np.sum(self.run_length_probs) * self.hazard_rate
        
        # 新的运行长度分布
        new_run_length_probs = np.zeros(len(growth_probs) + 1)
        new_run_length_probs[0] = changepoint_prob
        new_run_length_probs[1:] = growth_probs
        
        # 创建与新运行长度分布匹配的似然向量
        likelihood = np.full(len(new_run_length_probs), predictive_prob)
        
        # 似然加权
        self.run_length_probs = new_run_length_probs * likelihood
        
        # 归一化（避免除零）
        total_prob = np.sum(self.run_length_probs)
        if total_prob > 0:
            self.run_length_probs /= total_prob
        else:
            self.run_length_probs = np.ones(len(self.run_length_probs)) / len(self.run_length_probs)
        
        # 检测变点
        return self.run_length_probs[0] > self.threshold


def rigorous_sd_bocpd(series: np.ndarray, 
                     nu: float = 5.0, omega: float = 0.01, 
                     alpha: float = 0.05, beta: float = 0.9,
                     hazard_rate: float = 1/50, threshold: float = 0.5) -> Tuple[List[int], np.ndarray, np.ndarray]:
    """
    严谨的 Score-Driven BOCPD 实现
    
    Args:
        series: 时间序列数据
        nu: 学生 t 分布自由度
        omega, alpha, beta: GAS 模型参数
        hazard_rate: BOCPD 变点先验概率
        threshold: 变点检测阈值
        
    Returns:
        Tuple containing:
        - changepoints: 变点索引列表
        - variances: 动态方差序列
        - scores: 得分序列
    """
    n = len(series)
    if n < 2:
        return [], np.array([]), np.array([])
    
    # 初始化模型
    gas_model = ScoreDrivenModel(nu, omega, alpha, beta)
    bocpd = BayesianOnlineChangePointDetection(hazard_rate, threshold)
    
    # 存储结果
    changepoints = []
    variances = np.zeros(n)
    scores = np.zeros(n)
    
    # 初始化
    mu_t = series[0]
    variance_t = np.var(series[:min(10, n)])  # 使用前几个观测初始化方差
    
    for t in range(1, n):
        x_t = series[t]
        
        # 计算得分
        score_t = gas_model.compute_score(x_t, mu_t, variance_t)
        scores[t] = score_t
        
        # 更新方差 (GAS)
        variance_t = gas_model.update_variance(variance_t, score_t)
        variances[t] = variance_t
        
        # 计算预测概率 (基于学生 t 分布)
        standardized = (x_t - mu_t) / np.sqrt(variance_t)
        predictive_prob = stats.t.pdf(standardized, df=nu)
        
        # BOCPD 更新
        is_changepoint = bocpd.update(predictive_prob)
        
        if is_changepoint:
            changepoints.append(t)
            # 重置参数
            mu_t = x_t
            variance_t = omega / (1 - beta)  # 长期方差
            bocpd = BayesianOnlineChangePointDetection(hazard_rate, threshold)
        else:
            # 更新均值 (简单移动平均或 EWMA)
            mu_t = 0.95 * mu_t + 0.05 * x_t
    
    return changepoints, variances, scores
