"""
集成测试 - 全链路验证
测试完整的数据加载 -> 中性化 -> 保存 -> 轮动分析流程
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys
import tempfile
import shutil
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from factor_neutralizer.core.FactorNeutralizer import FactorNeutralizer


class TestIntegration(unittest.TestCase):
    """集成测试 - 全链路验证"""
    
    def setUp(self):
        """创建测试数据"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试目录
        self.factor_dir = os.path.join(self.temp_dir, 'factors')
        self.price_dir = os.path.join(self.temp_dir, 'price')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.factor_dir, exist_ok=True)
        os.makedirs(self.price_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 创建日期和股票代码（包含沪市、深市、创业板、科创板）
        self.dates = pd.date_range('2023-01-01', periods=50, freq='D')
        self.symbols = [
            '600000.SH', '600036.SH', '601398.SH',  # 沪市主板
            '688001.SH', '688981.SH',                # 科创板
            '000001.SZ', '000858.SZ',                # 深市主板
            '300059.SZ', '300750.SZ',                # 创业板
        ]
        
        # 创建价格数据
        price_data = pd.DataFrame(
            np.random.randn(50, 9) * 0.02 + 1,
            index=self.dates,
            columns=self.symbols
        )
        price_data.to_pickle(os.path.join(self.price_dir, 'stock_close.pkl'))
        
        # 创建多个因子数据
        for i, factor_name in enumerate(['momentum', 'value', 'growth']):
            factor_data = pd.DataFrame(
                np.random.randn(50, 9) + i * 0.5,
                index=self.dates,
                columns=self.symbols
            )
            factor_data.to_pickle(os.path.join(self.factor_dir, f'{factor_name}.pkl'))
        
        # 创建行业数据
        industry_data = pd.DataFrame({
            'code': self.symbols,
            'industry': ['银行', '银行', '银行', '电子', '电子', 
                        '食品饮料', '食品饮料', '计算机', '计算机']
        })
        industry_data.to_pickle(os.path.join(self.temp_dir, 'industry_mapping.pkl'))
        
        # 创建指数数据
        index_data = pd.DataFrame({
            'index_code': ['000001.SH'] * len(self.symbols),
            'trade_date': ['20230101'] * len(self.symbols),
            'con_code': self.symbols
        })
        index_data.to_pickle(os.path.join(self.temp_dir, 'index_constituents.pkl'))
        
        # 创建市值数据（使用纯数字列名测试代码转换）
        mv_columns = ['600000', '600036', '601398', '688001', '688981',
                     '000001', '000858', '300059', '300750']
        mv_data = pd.DataFrame(
            np.random.uniform(1e9, 1e11, (50, 9)),
            index=self.dates,
            columns=mv_columns
        )
        mv_data.to_pickle(os.path.join(self.temp_dir, 'stock_market_value.pkl'))
    
    def tearDown(self):
        """清理测试数据"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_pipeline(self):
        """测试完整流程: 加载 -> 中性化 -> 保存 -> 分析"""
        print("\n" + "="*60)
        print("集成测试: 全链路验证")
        print("="*60)
        
        # Step 1: 创建中性化处理器
        print("\n[Step 1] 创建中性化处理器...")
        neutralizer = FactorNeutralizer(
            factor_dir=self.factor_dir,
            price_dir=self.price_dir,
            industry_file=os.path.join(self.temp_dir, 'industry_mapping.pkl'),
            index_file=os.path.join(self.temp_dir, 'index_constituents.pkl'),
            market_value_file=os.path.join(self.temp_dir, 'stock_market_value.pkl'),
            output_dir=self.output_dir,
            enable_cache=False,
            industry_file_type='pkl',
            index_file_type='pkl',
            market_value_file_type='pkl'
        )
        
        # 验证数据加载
        self.assertIsNotNone(neutralizer.price_data)
        self.assertEqual(len(neutralizer.factors), 3)
        self.assertIsNotNone(neutralizer.industry_data)
        self.assertIsNotNone(neutralizer.market_value_data)
        print("✓ 数据加载成功")
        
        # Step 2: 验证股票代码转换
        print("\n[Step 2] 验证股票代码转换...")
        for col in neutralizer.market_value_data.columns:
            self.assertIn('.', col, f"市值列名 {col} 缺少交易所后缀")
        print("✓ 股票代码转换正确")
        
        # Step 3: 行业中性化（回归法）
        print("\n[Step 3] 行业中性化（回归法）...")
        factor_name = 'momentum'
        factor_data = neutralizer.factors[factor_name]
        
        result_regression = neutralizer.industry_neutralization(
            factor_data, method='regression'
        )
        
        self.assertIsNotNone(result_regression)
        self.assertEqual(result_regression.shape, factor_data.shape)
        self.assertFalse(result_regression.isna().all().all())
        print("✓ 回归中性化成功")
        
        # Step 4: 行业中性化（标准化法）
        print("\n[Step 4] 行业中性化（标准化法）...")
        result_std = neutralizer.industry_neutralization(
            factor_data, method='standardization'
        )
        
        self.assertIsNotNone(result_std)
        self.assertEqual(result_std.shape, factor_data.shape)
        print("✓ 标准化中性化成功")
        
        # Step 5: 批量处理所有因子
        print("\n[Step 5] 批量处理所有因子...")
        neutralizer.process_all_factors(
            neutralization_type='industry',
            industry_method='regression',
            force_reprocess=True
        )
        
        # 验证结果已保存
        self.assertEqual(len(neutralizer.neutralized_factors), 3)
        for fname in ['momentum', 'value', 'growth']:
            output_path = os.path.join(self.output_dir, 'factors', f'{fname}_neutralized.pkl')
            self.assertTrue(os.path.exists(output_path), f"因子 {fname} 未保存")
        print("✓ 批量处理成功")
        
        # Step 6: 轮动分析
        print("\n[Step 6] 轮动分析...")
        neutralizer.rotation_analysis()
        
        # 验证分析结果已保存
        industry_rotation_path = os.path.join(self.output_dir, 'analysis', 'industry_rotation.json')
        market_value_rotation_path = os.path.join(self.output_dir, 'analysis', 'market_value_rotation.json')
        
        self.assertTrue(os.path.exists(industry_rotation_path), "行业轮动结果未保存")
        self.assertTrue(os.path.exists(market_value_rotation_path), "市值轮动结果未保存")
        
        # 验证JSON内容
        with open(industry_rotation_path, 'r', encoding='utf-8') as f:
            industry_data = json.load(f)
        self.assertIn('momentum', industry_data)
        
        with open(market_value_rotation_path, 'r', encoding='utf-8') as f:
            mv_data = json.load(f)
        self.assertIn('momentum', mv_data)
        print("✓ 轮动分析成功")
        
        # Step 7: 验证可视化输出
        print("\n[Step 7] 验证可视化输出...")
        viz_dir = os.path.join(self.output_dir, 'visualizations')
        if os.path.exists(viz_dir):
            viz_files = [f for f in os.listdir(viz_dir) if f.endswith('.png')]
            self.assertGreater(len(viz_files), 0, "未生成可视化图表")
            print(f"✓ 生成 {len(viz_files)} 个可视化图表")
        
        # Step 8: 验证日志输出
        print("\n[Step 8] 验证日志输出...")
        log_dir = os.path.join(self.output_dir, 'logs')
        self.assertTrue(os.path.exists(log_dir), "日志目录未创建")
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        self.assertGreater(len(log_files), 0, "未生成日志文件")
        print(f"✓ 生成日志文件: {log_files[0]}")
        
        print("\n" + "="*60)
        print("✅ 集成测试全部通过！")
        print("="*60)
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n[错误处理测试] 验证异常情况...")
        
        # 测试1: 行业数据文件不存在
        with self.assertRaises(FileNotFoundError):
            FactorNeutralizer(
                factor_dir=self.factor_dir,
                price_dir=self.price_dir,
                industry_file=os.path.join(self.temp_dir, 'nonexistent.pkl'),
                index_file=os.path.join(self.temp_dir, 'index_constituents.pkl'),
                market_value_file=os.path.join(self.temp_dir, 'stock_market_value.pkl'),
                output_dir=self.output_dir,
                enable_cache=False,
                industry_file_type='pkl',
                index_file_type='pkl',
                market_value_file_type='pkl'
            )
        print("✓ 行业数据缺失时正确抛出异常")
        
        # 测试2: 因子目录不存在
        with self.assertRaises(FileNotFoundError):
            FactorNeutralizer(
                factor_dir=os.path.join(self.temp_dir, 'nonexistent'),
                price_dir=self.price_dir,
                industry_file=os.path.join(self.temp_dir, 'industry_mapping.pkl'),
                index_file=os.path.join(self.temp_dir, 'index_constituents.pkl'),
                market_value_file=os.path.join(self.temp_dir, 'stock_market_value.pkl'),
                output_dir=self.output_dir,
                enable_cache=False,
                industry_file_type='pkl',
                index_file_type='pkl',
                market_value_file_type='pkl'
            )
        print("✓ 因子目录缺失时正确抛出异常")
    
    def test_idempotency(self):
        """测试幂等性 - 多次运行结果一致"""
        print("\n[幂等性测试] 验证多次运行结果一致...")
        
        # 第一次运行
        neutralizer1 = FactorNeutralizer(
            factor_dir=self.factor_dir,
            price_dir=self.price_dir,
            industry_file=os.path.join(self.temp_dir, 'industry_mapping.pkl'),
            index_file=os.path.join(self.temp_dir, 'index_constituents.pkl'),
            market_value_file=os.path.join(self.temp_dir, 'stock_market_value.pkl'),
            output_dir=self.output_dir,
            enable_cache=False,
            industry_file_type='pkl',
            index_file_type='pkl',
            market_value_file_type='pkl'
        )
        
        result1 = neutralizer1.industry_neutralization(
            neutralizer1.factors['momentum'], method='regression'
        )
        
        # 第二次运行
        neutralizer2 = FactorNeutralizer(
            factor_dir=self.factor_dir,
            price_dir=self.price_dir,
            industry_file=os.path.join(self.temp_dir, 'industry_mapping.pkl'),
            index_file=os.path.join(self.temp_dir, 'index_constituents.pkl'),
            market_value_file=os.path.join(self.temp_dir, 'stock_market_value.pkl'),
            output_dir=self.output_dir + '_2',
            enable_cache=False,
            industry_file_type='pkl',
            index_file_type='pkl',
            market_value_file_type='pkl'
        )
        
        result2 = neutralizer2.industry_neutralization(
            neutralizer2.factors['momentum'], method='regression'
        )
        
        # 比较结果（允许浮点误差）
        pd.testing.assert_frame_equal(result1, result2)
        print("✓ 多次运行结果一致")


if __name__ == '__main__':
    # 运行测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出总结
    print("\n" + "="*60)
    print("集成测试总结")
    print("="*60)
    print(f"测试总数: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ 所有集成测试通过！")
    else:
        print("\n❌ 存在未通过的测试")
    
    sys.exit(0 if result.wasSuccessful() else 1)
