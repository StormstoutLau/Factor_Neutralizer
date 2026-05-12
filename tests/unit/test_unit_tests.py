"""
单元测试 - 核心功能测试
"""

import unittest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import pickle

# 导入要测试的模块
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from factor_neutralizer.core.FactorNeutralizer import FactorNeutralizer
from factor_neutralizer.utils.config_manager import ConfigManager, FactorNeutralizerConfig, DataConfig
from factor_neutralizer.utils.logger_config import FactorNeutralizerLogger

class TestFactorNeutralizer(unittest.TestCase):
    """FactorNeutralizer单元测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试数据
        self.create_test_data()
        
        # 创建测试配置
        self.test_config = self.create_test_config()
        
        # 初始化日志
        self.logger = FactorNeutralizerLogger(os.path.join(self.temp_dir, 'logs'))
    
    def tearDown(self):
        """测试后清理"""
        # 关闭日志处理器，释放文件句柄
        if hasattr(self, 'logger') and self.logger:
            self.logger.close()
        # 删除临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建测试因子数据
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        symbols = [f'{i:06d}.SH' for i in range(600000, 600120)]
        
        # 价格数据
        price_data = pd.DataFrame(
            np.random.randn(50, 120) * 0.02 + 1,
            index=dates,
            columns=symbols
        )
        with open(os.path.join(self.temp_dir, 'price_data.pkl'), 'wb') as f:
            pickle.dump(price_data, f)
        
        # 因子数据
        for factor_name in ['momentum', 'value']:
            factor_data = pd.DataFrame(
                np.random.randn(50, 120),
                index=dates,
                columns=symbols
            )
            with open(os.path.join(self.temp_dir, f'{factor_name}.pkl'), 'wb') as f:
                pickle.dump(factor_data, f)
        
        # 行业数据
        industry_data = pd.DataFrame({
            'code': symbols,
            'industry': np.random.choice(['银行', '房地产', '计算机'], 120)
        })
        with open(os.path.join(self.temp_dir, 'industry_mapping.pkl'), 'wb') as f:
            pickle.dump(industry_data, f)
        
        # 指数数据
        index_data = pd.DataFrame({
            'index_code': ['000001.SH'] * 120,
            'trade_date': ['20230101'] * 120,
            'con_code': symbols
        })
        with open(os.path.join(self.temp_dir, 'index_constituents.pkl'), 'wb') as f:
            pickle.dump(index_data, f)
        
        # 市值数据
        market_value_data = pd.DataFrame(
            np.random.uniform(1e9, 1e11, (50, 120)),
            index=dates,
            columns=symbols
        )
        with open(os.path.join(self.temp_dir, 'stock_market_value.pkl'), 'wb') as f:
            pickle.dump(market_value_data, f)
    
    def create_test_config(self):
        """创建测试配置"""
        return FactorNeutralizerConfig(
            output_dir=os.path.join(self.temp_dir, 'output'),
            index_code='000001.SH',
            data=DataConfig(
                factor_dir=self.temp_dir,
                price_dir=os.path.join(self.temp_dir, 'price_data.pkl'),
                industry_file=os.path.join(self.temp_dir, 'industry_mapping.pkl'),
                index_file=os.path.join(self.temp_dir, 'index_constituents.pkl'),
                market_value_file=os.path.join(self.temp_dir, 'stock_market_value.pkl'),
                industry_file_type='pkl',
                index_file_type='pkl',
                market_value_file_type='pkl'
            )
        )
    
    def test_initialization(self):
        """测试初始化"""
        # 测试正常初始化
        neutralizer = FactorNeutralizer(
            factor_dir=self.test_config.data.factor_dir,
            price_dir=self.test_config.data.price_dir,
            industry_file=self.test_config.data.industry_file,
            index_file=self.test_config.data.index_file,
            market_value_file=self.test_config.data.market_value_file,
            output_dir=self.test_config.output_dir,
            index_code=self.test_config.index_code,
            enable_cache=True
        )
        
        # 检查基本属性
        self.assertEqual(neutralizer.factor_dir, self.test_config.data.factor_dir)
        self.assertEqual(neutralizer.price_dir, self.test_config.data.price_dir)
        self.assertEqual(neutralizer.output_dir, self.test_config.output_dir)
        self.assertTrue(neutralizer.enable_cache)
        
        # 检查数据是否加载
        self.assertIsNotNone(neutralizer.price_data)
        self.assertIsNotNone(neutralizer.factors)
        self.assertIsNotNone(neutralizer.industry_data)
    
    def test_memory_optimization(self):
        """测试内存优化"""
        neutralizer = FactorNeutralizer(
            factor_dir=self.test_config.data.factor_dir,
            price_dir=self.test_config.data.price_dir,
            industry_file=self.test_config.data.industry_file,
            index_file=self.test_config.data.index_file,
            market_value_file=self.test_config.data.market_value_file,
            output_dir=self.test_config.output_dir,
            index_code=self.test_config.index_code
        )
        
        # 创建测试DataFrame
        test_df = pd.DataFrame({
            'float_col': np.random.randn(100),
            'int_col': np.random.randint(0, 100, 100),
            'str_col': ['A'] * 50 + ['B'] * 50
        })
        
        # 应用内存优化
        optimized_df = neutralizer._optimize_memory_usage(test_df)
        
        # 检查数据类型优化
        self.assertEqual(optimized_df['float_col'].dtype, np.float32)
        self.assertTrue(optimized_df['int_col'].dtype in [np.int32, np.int8, np.int16])
        self.assertEqual(optimized_df['str_col'].dtype.name, 'category')
    
    def test_industry_neutralization(self):
        """测试行业中性化"""
        neutralizer = FactorNeutralizer(
            factor_dir=self.test_config.data.factor_dir,
            price_dir=self.test_config.data.price_dir,
            industry_file=self.test_config.data.industry_file,
            index_file=self.test_config.data.index_file,
            market_value_file=self.test_config.data.market_value_file,
            output_dir=self.test_config.output_dir,
            index_code=self.test_config.index_code
        )
        
        # 获取第一个因子
        factor_name = list(neutralizer.factors.keys())[0]
        factor_data = neutralizer.factors[factor_name]
        
        # 执行行业中性化
        result = neutralizer.industry_neutralization(factor_data, method='regression')
        
        # 检查结果
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, factor_data.shape)
        self.assertFalse(result.isnull().all().all())  # 确保不是全NaN
    
    def test_cache_operations(self):
        """测试缓存操作"""
        neutralizer = FactorNeutralizer(
            factor_dir=self.test_config.data.factor_dir,
            price_dir=self.test_config.data.price_dir,
            industry_file=self.test_config.data.industry_file,
            index_file=self.test_config.data.index_file,
            market_value_file=self.test_config.data.market_value_file,
            output_dir=self.test_config.output_dir,
            index_code=self.test_config.index_code,
            enable_cache=True
        )
        
        # 测试缓存保存
        test_data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        cache_key = neutralizer._get_cache_key('test', param1='value1')
        
        neutralizer._save_to_cache(cache_key, test_data)
        
        # 测试缓存加载
        loaded_data = neutralizer._load_from_cache(cache_key)
        self.assertIsNotNone(loaded_data)
        pd.testing.assert_frame_equal(test_data, loaded_data)
        
        # 测试缓存清理
        neutralizer._clear_cache()
        loaded_data_after_clear = neutralizer._load_from_cache(cache_key)
        self.assertIsNone(loaded_data_after_clear)
    
    def test_file_type_detection(self):
        """测试文件类型检测"""
        neutralizer = FactorNeutralizer(
            factor_dir=self.test_config.data.factor_dir,
            price_dir=self.test_config.data.price_dir,
            industry_file=self.test_config.data.industry_file,
            index_file=self.test_config.data.index_file,
            market_value_file=self.test_config.data.market_value_file,
            output_dir=self.test_config.output_dir,
            index_code=self.test_config.index_code
        )
        
        # 测试PKL文件检测
        pkl_file = os.path.join(self.temp_dir, 'test.pkl')
        with open(pkl_file, 'wb') as f:
            pickle.dump({'test': 'data'}, f)
        
        file_type = neutralizer._detect_file_type(pkl_file)
        self.assertEqual(file_type, 'pkl')
        
        # 测试CSV文件检测
        csv_file = os.path.join(self.temp_dir, 'test.csv')
        with open(csv_file, 'w') as f:
            f.write('a,b\n1,2\n')
        
        file_type = neutralizer._detect_file_type(csv_file)
        self.assertEqual(file_type, 'csv')
    
    def test_batch_operations(self):
        """测试批量操作"""
        neutralizer = FactorNeutralizer(
            factor_dir=self.test_config.data.factor_dir,
            price_dir=self.test_config.data.price_dir,
            industry_file=self.test_config.data.industry_file,
            index_file=self.test_config.data.index_file,
            market_value_file=self.test_config.data.market_value_file,
            output_dir=self.test_config.output_dir,
            index_code=self.test_config.index_code
        )
        
        # 测试批量保存
        test_factors = {
            'factor1': pd.DataFrame({'a': [1, 2, 3]}),
            'factor2': pd.DataFrame({'b': [4, 5, 6]})
        }
        
        batch_dir = os.path.join(self.temp_dir, 'batch_test')
        os.makedirs(batch_dir, exist_ok=True)
        
        saved_count = neutralizer._batch_save_factors(test_factors, batch_dir)
        self.assertEqual(saved_count, 2)
        
        # 测试批量加载
        loaded_factors = neutralizer._batch_load_factors(batch_dir)
        self.assertEqual(len(loaded_factors), 2)
        
        # 检查数据一致性
        for factor_name in test_factors:
            self.assertIn(factor_name, loaded_factors)

class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
    
    def tearDown(self):
        """测试后清理"""
        # 关闭日志处理器，释放文件句柄
        if hasattr(self, 'logger') and self.logger:
            self.logger.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_creation(self):
        """测试配置创建"""
        config_manager = ConfigManager(self.config_file)
        
        # 检查默认配置
        self.assertIsNotNone(config_manager.config)
        self.assertIsNotNone(config_manager.config.data)
        self.assertIsNotNone(config_manager.config.processing)
        self.assertIsNotNone(config_manager.config.optimization)
        self.assertIsNotNone(config_manager.config.logging)
    
    def test_config_save_load(self):
        """测试配置保存和加载"""
        config_manager = ConfigManager(self.config_file)
        
        # 修改配置
        config_manager.config.index_code = '000300.SH'
        config_manager.config.processing.force_reprocess = True
        
        # 保存配置
        config_manager.save_config(config_manager.config)
        
        # 重新加载配置
        new_config_manager = ConfigManager(self.config_file)
        
        # 检查配置是否正确加载
        self.assertEqual(new_config_manager.config.index_code, '000300.SH')
        self.assertTrue(new_config_manager.config.processing.force_reprocess)
    
    def test_config_validation(self):
        """测试配置验证"""
        config_manager = ConfigManager(self.config_file)
        
        # 创建有效配置
        valid_config = config_manager.config
        self.assertTrue(config_manager.validate_config())
        
        # 创建无效配置（不存在的路径）
        invalid_config = config_manager.config
        invalid_config.data.factor_dir = '/nonexistent/path'
        config_manager.config = invalid_config
        
        # 验证应该失败但不会抛出异常
        result = config_manager.validate_config()
        # 注意：由于路径不存在，验证会返回False，但不会抛出异常

class TestLogger(unittest.TestCase):
    """日志系统测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = FactorNeutralizerLogger(os.path.join(self.temp_dir, 'logs'))
    
    def tearDown(self):
        """测试后清理"""
        # 关闭日志处理器，释放文件句柄
        if hasattr(self, 'logger') and self.logger:
            self.logger.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_creation(self):
        """测试日志器创建"""
        self.assertIsNotNone(self.logger.logger)
        self.assertTrue(len(self.logger.logger.handlers) > 0)
    
    def test_log_methods(self):
        """测试日志方法"""
        # 测试各种日志级别
        self.logger.info("测试信息日志")
        self.logger.warning("测试警告日志")
        self.logger.error("测试错误日志")
        self.logger.debug("测试调试日志")
        
        # 检查日志文件是否创建
        log_files = os.listdir(os.path.join(self.temp_dir, 'logs'))
        self.assertTrue(len(log_files) > 0)
    
    def test_specialized_logging(self):
        """测试专用日志方法"""
        self.logger.log_memory_usage(100.5, "测试阶段")
        self.logger.log_performance("测试操作", 2.5, "详情")
        self.logger.log_data_info("测试数据", (100, 50), "test.csv")
        self.logger.log_cache_operation("保存", "test_key", True)
        self.logger.log_neutralization_result("test_factor", "regression", 200, True)

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestFactorNeutralizer,
        TestConfigManager,
        TestLogger
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == '__main__':
    print("开始运行单元测试...")
    success = run_tests()
    
    if success:
        print("\n所有测试通过！")
    else:
        print("\n部分测试失败，请检查代码。")
