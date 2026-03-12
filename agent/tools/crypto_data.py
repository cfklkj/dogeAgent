"""
Crypto Data Tools for dogeAgent
提供币圈行情数据获取功能 (Binance & CoinGecko)
"""
import requests
import time
from typing import Optional, Dict, Any

class CryptoDataTool:
    """加密货币数据工具类"""
    
    def __init__(self):
        self.binance_base = "https://api.binance.com/api/v3"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'dogeAgent/1.0'
        })
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """
        获取实时价格
        :param symbol: 币种符号 (如 'BTCUSDT', 'ETHUSDT')
        :return: 包含价格、涨跌幅等信息的字典
        """
        try:
            # 币安 API 获取 24h 行情
            url = f"{self.binance_base}/ticker/24hr"
            params = {'symbol': symbol.upper()}
            resp = self.session.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            
            return {
                'success': True,
                'symbol': symbol.upper(),
                'price': float(data['lastPrice']),
                'change_24h': float(data['priceChangePercent']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'timestamp': time.time()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_klines(self, symbol: str, interval: str = '1d', limit: int = 100) -> Dict[str, Any]:
        """
        获取 K 线数据
        :param symbol: 币种符号
        :param interval: 时间间隔 (1m, 5m, 15m, 1h, 4h, 1d, 1w)
        :param limit: 获取数量
        :return: K 线数据列表
        """
        try:
            url = f"{self.binance_base}/klines"
            params = {'symbol': symbol.upper(), 'interval': interval, 'limit': limit}
            resp = self.session.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            
            # 解析 K 线数据 [开盘时间, 开盘价, 最高价, 最低价, 收盘价, 成交量, ...]
            klines = []
            for k in data:
                klines.append({
                    'open_time': k[0],
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5]),
                    'close_time': k[6]
                })
            
            return {'success': True, 'symbol': symbol.upper(), 'klines': klines}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_coin_info(self, coin_id: str) -> Dict[str, Any]:
        """
        从 CoinGecko 获取币种基本信息
        :param coin_id: CoinGecko ID (如 'bitcoin', 'ethereum')
        :return: 币种基本信息
        """
        try:
            url = f"{self.coingecko_base}/coins/{coin_id}"
            resp = self.session.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            
            return {
                'success': True,
                'name': data.get('name', ''),
                'symbol': data.get('symbol', '').upper(),
                'market_cap_rank': data.get('market_cap_rank'),
                'current_price': data.get('market_data', {}).get('current_price', {}).get('usd'),
                'market_cap': data.get('market_data', {}).get('market_cap', {}).get('usd'),
                'description': data.get('description', {}).get('en', '')[:200] + '...' if data.get('description') else ''
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# 实例化工具
crypto_tool = CryptoDataTool()

# 测试代码
if __name__ == "__main__":
    print("测试 BTC 价格...")
    btc = crypto_tool.get_price('BTCUSDT')
    if btc['success']:
        print(f"BTC: ${btc['price']} ({btc['change_24h']}%)")
    else:
        print(f"失败：{btc['error']}")
    
    print("\n测试 ETH K 线...")
    eth_k = crypto_tool.get_klines('ETHUSDT', '1d', 5)
    if eth_k['success']:
        for k in eth_k['klines']:
            print(f"Close: ${k['close']}")
    else:
        print(f"失败：{eth_k['error']}")
