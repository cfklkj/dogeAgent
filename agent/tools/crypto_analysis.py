"""
Crypto Analysis Tools for dogeAgent
提供技术指标计算与自然语言解读
"""
from typing import List, Dict, Any, Optional
import numpy as np

class CryptoAnalysisTool:
    """加密货币分析工具类"""
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """
        计算 RSI (相对强弱指数)
        :param prices: 收盘价列表
        :param period: 周期 (默认 14)
        :return: RSI 值 (0-100)
        """
        if len(prices) < period + 1:
            return None
        
        # 计算价格变化
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        # 确保有足够的值计算
        if len(gain) < period:
            return None
            
        # 计算平均涨跌幅 (使用简单移动平均)
        avg_gain = np.mean(gain[-period:]) if len(gain) >= period else np.mean(gain)
        avg_loss = np.mean(loss[-period:]) if len(loss) >= period else np.mean(loss)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_ma(self, prices: List[float], period: int = 7) -> Optional[float]:
        """
        计算移动平均线 (MA)
        :param prices: 价格列表
        :param period: 周期
        :return: MA 值
        """
        if len(prices) < period:
            return None
        return round(np.mean(prices[-period:]), 2)
    
    def interpret_rsi(self, rsi: float) -> str:
        """解读 RSI 值"""
        if rsi > 70:
            return "超买 (可能回调)"
        elif rsi < 30:
            return "超卖 (可能反弹)"
        elif rsi > 55:
            return "偏强"
        elif rsi < 45:
            return "偏弱"
        else:
            return "中性"
    
    def analyze_trend(self, klines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        综合趋势分析
        :param klines: K 线数据列表
        :return: 分析结果
        """
        if len(klines) < 30:
            return {'success': False, 'error': '数据不足，需要至少 30 条 K 线'}
        
        closes = [k['close'] for k in klines]
        
        # 计算指标
        rsi_14 = self.calculate_rsi(closes, 14)
        ma_7 = self.calculate_ma(closes, 7)
        ma_30 = self.calculate_ma(closes, 30)
        
        # 判断趋势
        current_price = closes[-1]
        trend = "震荡"
        if ma_7 and ma_30:
            if ma_7 > ma_30 and current_price > ma_7:
                trend = "多头 (MA7>MA30)"
            elif ma_7 < ma_30 and current_price < ma_7:
                trend = "空头 (MA7<MA30)"
        
        # 生成自然语言总结
        rsi_text = f"RSI: {rsi_14} ({self.interpret_rsi(rsi_14)})" if rsi_14 else "RSI: 数据不足"
        ma_text = f"MA7: {ma_7} | MA30: {ma_30}" if ma_7 and ma_30 else "MA: 数据不足"
        
        summary = f"当前趋势：{trend}。{rsi_text}。{ma_text}。"
        
        return {
            'success': True,
            'current_price': current_price,
            'rsi': rsi_14,
            'ma_7': ma_7,
            'ma_30': ma_30,
            'trend': trend,
            'summary': summary
        }

# 实例化工具
analysis_tool = CryptoAnalysisTool()

# 测试代码
if __name__ == "__main__":
    # 模拟 K 线数据测试
    test_klines = [{'close': 100 + i * 0.5} for i in range(50)]
    result = analysis_tool.analyze_trend(test_klines)
    if result['success']:
        print(result['summary'])
    else:
        print(result['error'])
