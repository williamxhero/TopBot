"""
变点检测器模块
集成多种变点检测算法，提供统一接口
"""

import numpy as np
import pandas as pd
import ruptures as rpt
from typing import List, Optional
from .score_driven_bocpd import rigorous_sd_bocpd


class HybridChangePointDetector:
    """混合变点检测器，集成多种算法"""
    
    def __init__(self):
        """初始化检测器"""
        pass
    
    def detect_ruptures_dynp(self, series: np.ndarray, n_bkps: int = 15, 
                           min_size: int = 8) -> List[int]:
        """
        使用 Ruptures 的 Dynp (Dynamic Programming) 算法
        
        Args:
            series: 时间序列数据
            n_bkps: 预期变点数量
            min_size: 最小段长度
            
        Returns:
            变点索引列表
        """
        try:
            algo_dynp = rpt.Dynp(model="l2", min_size=min_size, jump=1)
            cp_dynp = algo_dynp.fit_predict(series.reshape(-1, 1), n_bkps=n_bkps)
            return [cp - 1 for cp in cp_dynp[:-1]]  # 调整索引
        except Exception as e:
            print(f"Dynp 算法失败: {e}")
            return []
    
    def detect_ruptures_bottom_up(self, series: np.ndarray, 
                                 pen: float = 0.5, min_size: int = 6) -> List[int]:
        """
        使用 Ruptures 的 BottomUp 算法
        
        Args:
            series: 时间序列数据
            pen: 惩罚参数
            min_size: 最小段长度
            
        Returns:
            变点索引列表
        """
        try:
            algo_bottom_up = rpt.BottomUp(model="l2", min_size=min_size)
            cp_returns = algo_bottom_up.fit_predict(series.reshape(-1, 1), pen=pen)
            return [cp for cp in cp_returns[:-1]]
        except Exception as e:
            print(f"BottomUp 算法失败: {e}")
            return []
    
    def detect_sd_bocpd(self, series: np.ndarray, 
                       nu: float = 4.0, omega: float = 0.001,
                       alpha: float = 0.06, beta: float = 0.90,
                       hazard_rate: float = 1/25, threshold: float = 0.3) -> List[int]:
        """
        使用 Score-Driven BOCPD 算法
        
        Args:
            series: 时间序列数据
            nu: 学生t分布自由度
            omega: 基础方差
            alpha: 短期冲击系数
            beta: 方差持续性
            hazard_rate: 变点先验概率
            threshold: 检测阈值
            
        Returns:
            变点索引列表
        """
        changepoints, _, _ = rigorous_sd_bocpd(
            series, nu=nu, omega=omega, alpha=alpha, beta=beta,
            hazard_rate=hazard_rate, threshold=threshold
        )
        return changepoints
    
    def detect_volatility_based(self, series: np.ndarray, 
                               window: int = 8, percentile: int = 85) -> List[int]:
        """
        基于波动率的简单变点检测
        
        Args:
            series: 时间序列数据
            window: 滚动窗口大小
            percentile: 阈值百分位数
            
        Returns:
            变点索引列表
        """
        returns = np.diff(np.log(series))
        volatility = pd.Series(returns).rolling(window).std()
        vol_changes = np.abs(np.diff(volatility.fillna(0)))
        vol_threshold = np.percentile(vol_changes, percentile)
        return list(np.where(vol_changes > vol_threshold)[0] + 1)
    
    def detect_comprehensive(self, series: np.ndarray) -> List[int]:
        """
        综合变点检测方法，使用多种算法并优选结果
        
        Args:
            series: 时间序列数据
            
        Returns:
            最终的变点索引列表
        """
        print("正在进行严谨的 Score-Driven BOCPD 变点检测...")
        
        # 方法1: Ruptures Dynp 算法
        print("使用 Ruptures Dynp 算法...")
        cp_dynp = self.detect_ruptures_dynp(series)
        print(f"Dynp 检测到 {len(cp_dynp)} 个变点")
        
        # 方法2: 保守的 SD-BOCPD
        print("使用保守的 SD-BOCPD...")
        cp_sdbocpd = self.detect_sd_bocpd(series)
        print(f"SD-BOCPD 检测到 {len(cp_sdbocpd)} 个变点")
        
        # 方法3: 基于收益率的统计变点检测
        print("使用收益率统计方法...")
        returns = np.diff(np.log(series))
        cp_returns = self.detect_ruptures_bottom_up(returns)
        print(f"收益率方法检测到 {len(cp_returns)} 个变点")
        
        # 综合多种方法的结果，优先考虑专业库的结果
        if len(cp_dynp) > 0:
            cp_indices = cp_dynp
            print(f"采用 Dynp 结果: {len(cp_indices)} 个变点")
        elif len(cp_returns) > 0:
            cp_indices = cp_returns
            print(f"采用收益率方法结果: {len(cp_indices)} 个变点")
        elif len(cp_sdbocpd) > 0:
            cp_indices = cp_sdbocpd
            print(f"采用 SD-BOCPD 结果: {len(cp_indices)} 个变点")
        else:
            # 最后的回退方案：简单的波动率方法
            print("所有方法失效，使用简单波动率检测...")
            cp_indices = self.detect_volatility_based(series)
            print(f"波动率方法检测到 {len(cp_indices)} 个变点")
        
        return cp_indices


class ExtremaClassifier:
    """极值点分类器，将变点分类为峰值或谷值"""
    
    @staticmethod
    def classify_extrema(series: np.ndarray, changepoint_idx: int, 
                        window: int = 3) -> Optional[str]:
        """
        严谨的极值点分类方法
        
        Args:
            series: 时间序列数据
            changepoint_idx: 变点索引
            window: 检查窗口大小
            
        Returns:
            'peak', 'trough' 或 None
        """
        if changepoint_idx < window or changepoint_idx >= len(series) - window:
            return None
        
        # 扩大窗口检查
        left_window = series[changepoint_idx-window:changepoint_idx]
        right_window = series[changepoint_idx+1:changepoint_idx+window+1]
        current_value = series[changepoint_idx]
        
        # Peak: 当前值明显高于左右窗口的最大值
        if (len(left_window) > 0 and len(right_window) > 0 and
            current_value > np.max(left_window) and 
            current_value > np.max(right_window)):
            return 'peak'
        
        # Trough: 当前值明显低于左右窗口的最小值  
        elif (len(left_window) > 0 and len(right_window) > 0 and
              current_value < np.min(left_window) and 
              current_value < np.min(right_window)):
            return 'trough'
        
        return None
    
    @staticmethod
    def classify_changepoints(series: pd.Series, changepoints: List[int], 
                            window: int = 2) -> tuple:
        """
        对变点列表进行峰谷分类
        
        Args:
            series: 带索引的时间序列
            changepoints: 变点索引列表
            window: 分类窗口大小
            
        Returns:
            (peaks_dates, troughs_dates): 峰值和谷值的日期列表
        """
        peaks_dt, troughs_dt = [], []
        
        for idx in changepoints:
            extrema_type = ExtremaClassifier.classify_extrema(
                series.values, idx, window=window
            )
            
            if extrema_type == 'peak':
                peaks_dt.append(series.index[idx])
                print(f"检测到 Peak: {series.index[idx]} (价格: {series.iloc[idx]:.2f})")
            elif extrema_type == 'trough':
                troughs_dt.append(series.index[idx])
                print(f"检测到 Trough: {series.index[idx]} (价格: {series.iloc[idx]:.2f})")
        
        print(f"最终识别: {len(peaks_dt)} 个 Peaks, {len(troughs_dt)} 个 Troughs")
        return peaks_dt, troughs_dt
