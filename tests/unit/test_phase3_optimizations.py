"""
Phase 3 优化验证测试
测试缓存键生成、索引安全、性能优化
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys
import tempfile
import shutil
import json
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from factor_neutralizer.core.FactorNeutralizer import FactorNeutralizer


class TestCacheKeyOptimization(unittest.TestCase):
    """测试缓存键生成优化 (Bug-006)"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self._create_test_data()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_data(self):
        """创建测试数据"""
        factor_dir = os.path.join(self.temp_dir, 'factors')
        price_dir = os.path.join(self.temp_dir, 'price')
        os.makedirs(factor_dir, exist_ok=True)
        os.makedirs(price_dir, exist_ok=True)
        
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        symbols = ['600000.SH', '000001.SZ']
        
        price_data = pd.DataFrame(np.random.randn(10, 2), index=dates, columns=symbols)
        price_data.to_pickle(os.path.join(price_dir, 'stock_close.pkl'))
        
        factor_data = pd.DataFrame(np.random.randn(10, 2), index=dates, columns=symbols)
        factor_data.to_pickle(os.path.join(factor_dir, 'momentum.pkl'))
        
        industry_data = pd.DataFrame({'code': symbols, 'industry': ['银行', '银行']})
        industry_data.to_pickle(os.path.join(self.temp_dir, 'industry.pkl'))
        
        index_data = pd.DataFrame({
            'index_code': ['000001.SH'] * 2,
            'trade_date': ['20230101'] * 2,
            'con_code': symbols
        })
        index_data.to_pickle(os.path.join(self.temp_dir, 'index.pkl'))
        
        mv_data = pd.DataFrame(np.random.uniform(1e9, 1e11, (10, 2)), index=dates, columns=symbols)
        mv_data.to_pickle(os.path.join(self.temp_dir, 'mv.pkl'))
    
    def test_cache_key_uniqueness(self):
        """测试缓存键唯一性 - 不同参数不应冲突"""
        neutralizer = FactorNeutralizer(
            factor_dir=os.path.join(self.temp_dir, 'factors'),
            price_dir=os.path.join(self.temp_dir, 'price'),
            industry_file=os.path.join(self.temp_dir, 'industry.pkl'),
            index_file=os.path.join(self.temp_dir, 'index.pkl'),
            market_value_file=os.path.join(self.temp_dir, 'mv.pkl'),
            output_dir=os.path.join(self.temp_dir, 'output'),
            enable_cache=True,
            industry_file_type='pkl',
            index_file_type='pkl',
            market_value_file_type='pkl'
        )
        
        # 测试不同参数组合产生不同缓存键
        key1 = neutralizer._get_cache_key('test', a=1, b=23)
        key2 = neutralizer._get_cache_key('test', a=12, b=3)
        
        # 旧实现中这两个会产生冲突，新实现应该不同
        self.assertNotEqual(key1, key2, 
            "不同参数组合的缓存键应该不同")
        print(f"✓ 缓存键唯一性验证通过: {key1[:8]}... != {key2[:8]}...")
    
    def test_cache_key_format(self):
        """测试缓存键格式 - 应为32位十六进制"""
        neutralizer = FactorNeutralizer(
            factor_dir=os.path.join(self.temp_dir, 'factors'),
            price_dir=os.path.join(self.temp_dir, 'price'),
            industry_file=os.path.join(self.temp_dir, 'industry.pkl'),
            index_file=os.path.join(self.temp_dir, 'index.pkl'),
            market_value_file=os.path.join(self.temp_dir, 'mv.pkl'),
            output_dir=os.path.join(self.temp_dir, 'output'),
            enable_cache=True,
            industry_file_type='pkl',
            index_file_type='pkl',
            market_value_file_type='pkl'
        )
        
        key = neutralizer._get_cache_key('industry_neutralization', method='regression')
        
        # 应为32位十六进制字符串
        self.assertEqual(len(key), 32, "缓存键应为32位")
        self.assertTrue(all(c in '0123456789abcdef' for c in key), "缓存键应为十六进制")
        print(f"✓ 缓存键格式验证通过: {key}")


class TestIndexSafety(unittest.TestCase):
    """测试索引安全修复 (Bug-008)"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self._create_test_data()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_data(self):
        """创建测试数据 - 故意制造索引不匹配"""
        factor_dir = os.path.join(self.temp_dir, 'factors')
        price_dir = os.path.join(self.temp_dir, 'price')
        os.makedirs(factor_dir, exist_ok=True)
        os.makedirs(price_dir, exist_ok=True)
        
        dates = pd.date_range('2023-01-01', periods=20, freq='D')
        
        # 价格数据有10只股票
        price_symbols = [f'600{i:03d}.SH' for i in range(10)]
        price_data = pd.DataFrame(np.random.randn(20, 10), index=dates, columns=price_symbols)
        price_data.to_pickle(os.path.join(price_dir, 'stock_close.pkl'))
        
        # 因子数据也有10只股票
        factor_data = pd.DataFrame(np.random.randn(20, 10), index=dates, columns=price_symbols)
        factor_data.to_pickle(os.path.join(factor_dir, 'momentum.pkl'))
        
        # 行业数据只有8只股票（故意缺失2只）
        industry_symbols = price_symbols[:8]
        industry_data = pd.DataFrame({
            'code': industry_symbols,
            'industry': ['银行', '电子', '计算机', '食品饮料', '银行', '电子', '计算机', '食品饮料']
        })
        industry_data.to_pickle(os.path.join(self.temp_dir, 'industry.pkl'))
        
        index_data = pd.DataFrame({
            'index_code': ['000001.SH'] * 10,
            'trade_date': ['20230101'] * 10,
            'con_code': price_symbols
        })
        index_data.to_pickle(os.path.join(self.temp_dir, 'index.pkl'))
        
        mv_data = pd.DataFrame(np.random.uniform(1e9, 1e11, (20, 10)), index=dates, columns=price_symbols)
        mv_data.to_pickle(os.path.join(self.temp_dir, 'mv.pkl'))
    
    def test_index_mismatch_handling(self):
        """测试行业哑变量索引不匹配时不会崩溃"""
        print("\n[Bug-008] 测试索引安全...")
        
        neutralizer = FactorNeutralizer(
            factor_dir=os.path.join(self.temp_dir, 'factors'),
            price_dir=os.path.join(self.temp_dir, 'price'),
            industry_file=os.path.join(self.temp_dir, 'industry.pkl'),
            index_file=os.path.join(self.temp_dir, 'index.pkl'),
            market_value_file=os.path.join(self.temp_dir, 'mv.pkl'),
            output_dir=os.path.join(self.temp_dir, 'output'),
            enable_cache=False,
            industry_file_type='pkl',
            index_file_type='pkl',
            market_value_file_type='pkl'
        )
        
        # 获取因子数据
        factor_data = neutralizer.factors['momentum']
        
        # 行业数据只有8只股票，因子数据有10只
        # 旧代码会抛出 KeyError，新代码应该安全处理
        try:
            result = neutralizer.industry_neutralization(factor_data, method='regression')
            
            # 验证结果
            self.assertIsNotNone(result)
            self.assertEqual(result.shape, factor_data.shape)
            print("✓ 索引不匹配时安全处理，未抛出异常")
            
        except KeyError as e:
            self.fail(f"索引不匹配时应安全处理，不应抛出 KeyError: {e}")


class TestPerformanceOptimization(unittest.TestCase):
    """测试性能优化"""
    
    def test_fast_regression_method(self):
        """测试快速回归方法存在"""
        # 创建最小实例以访问方法
        temp_dir = tempfile.mkdtemp()
        
        try:
            factor_dir = os.path.join(temp_dir, 'factors')
            price_dir = os.path.join(temp_dir, 'price')
            os.makedirs(factor_dir, exist_ok=True)
            os.makedirs(price_dir, exist_ok=True)
            
            dates = pd.date_range('2023-01-01', periods=5, freq='D')
            symbols = ['600000.SH', '000001.SZ']
            
            price_data = pd.DataFrame(np.random.randn(5, 2), index=dates, columns=symbols)
            price_data.to_pickle(os.path.join(price_dir, 'stock_close.pkl'))
            
            factor_data = pd.DataFrame(np.random.randn(5, 2), index=dates, columns=symbols)
            factor_data.to_pickle(os.path.join(factor_dir, 'momentum.pkl'))
            
            industry_data = pd.DataFrame({'code': symbols, 'industry': ['银行', '银行']})
            industry_data.to_pickle(os.path.join(temp_dir, 'industry.pkl'))
            
            index_data = pd.DataFrame({
                'index_code': ['000001.SH'] * 2,
                'trade_date': ['20230101'] * 2,
                'con_code': symbols
            })
            index_data.to_pickle(os.path.join(temp_dir, 'index.pkl'))
            
            mv_data = pd.DataFrame(np.random.uniform(1e9, 1e11, (5, 2)), index=dates, columns=symbols)
            mv_data.to_pickle(os.path.join(temp_dir, 'mv.pkl'))
            
            neutralizer = FactorNeutralizer(
                factor_dir=factor_dir,
                price_dir=price_dir,
                industry_file=os.path.join(temp_dir, 'industry.pkl'),
                index_file=os.path.join(temp_dir, 'index.pkl'),
                market_value_file=os.path.join(temp_dir, 'mv.pkl'),
                output_dir=os.path.join(temp_dir, 'output'),
                enable_cache=False,
                industry_file_type='pkl',
                index_file_type='pkl',
                market_value_file_type='pkl'
            )
            
            # 测试 _fast_regression 方法存在且可调用
            X = np.random.randn(10, 3).astype(np.float32)
            y = np.random.randn(10).astype(np.float32)
            
            result = neutralizer._fast_regression(X, y)
            
            self.assertEqual(len(result), 10)
            self.assertIsInstance(result, np.ndarray)
            print("✓ 快速回归方法可用")
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    print("="*60)
    print("Phase 3 优化验证测试")
    print("="*60)
    
    # 运行测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCacheKeyOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestIndexSafety))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceOptimization))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("Phase 3 优化测试总结")
    print("="*60)
    print(f"测试总数: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ 所有 Phase 3 优化验证通过！")
    else:
        print("\n❌ 存在未通过的测试")
