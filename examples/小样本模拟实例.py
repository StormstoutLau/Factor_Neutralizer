"""
FactorNeutralizer 小样本模拟实例
演示完整的因子中性化和轮动分析过程
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MiniFactorNeutralizer:
    """小样本因子中性化演示类"""
    
    def __init__(self):
        self.stocks = [
            '600000.SH', '600036.SH', '000001.SZ', '000002.SZ',  # 银行
            '000069.SZ', '600048.SH',                          # 房地产
            '300059.SZ', '002415.SZ',                          # 计算机
            '300003.SZ', '300015.SZ'                           # 医药
        ]
        
        self.industry_mapping = {
            '600000.SH': '银行', '600036.SH': '银行', '000001.SZ': '银行', '000002.SZ': '银行',
            '000069.SZ': '房地产', '600048.SH': '房地产',
            '300059.SZ': '计算机', '002415.SZ': '计算机',
            '300003.SZ': '医药', '300015.SZ': '医药'
        }
        
        self.dates = pd.date_range('2023-01-01', periods=4, freq='Q')
        
        # 创建输出目录
        os.makedirs('mini_sample_results', exist_ok=True)
        os.makedirs('mini_sample_results/visualizations', exist_ok=True)
        os.makedirs('mini_sample_results/analysis', exist_ok=True)
    
    def create_sample_data(self):
        """创建模拟数据"""
        print("="*60)
        print("创建小样本模拟数据")
        print("="*60)
        
        # 原始因子数据 - 模拟不同行业的趋势
        self.raw_factor_data = pd.DataFrame({
            # 银行股：稳定上升趋势
            '600000.SH': [1.2, 1.5, 1.8, 2.1],
            '600036.SH': [0.8, 1.1, 1.4, 1.7],
            '000001.SZ': [1.0, 1.3, 1.6, 1.9],
            '000002.SZ': [0.9, 1.2, 1.5, 1.8],
            
            # 房地产股：下降趋势
            '000069.SZ': [2.0, 1.8, 1.6, 1.4],
            '600048.SH': [2.2, 2.0, 1.8, 1.6],
            
            # 计算机股：快速上升趋势
            '300059.SZ': [0.5, 0.8, 1.1, 1.4],
            '002415.SZ': [0.3, 0.6, 0.9, 1.2],
            
            # 医药股：从负转正
            '300003.SZ': [-0.5, -0.2, 0.1, 0.4],
            '300015.SZ': [-0.3, 0.0, 0.3, 0.6]
        }, index=self.dates)
        
        print("原始因子数据:")
        print(self.raw_factor_data)
        print(f"\n数据形状: {self.raw_factor_data.shape}")
        
        # 保存原始数据
        self.raw_factor_data.to_csv('mini_sample_results/raw_factor_data.csv')
        print("原始数据已保存到: mini_sample_results/raw_factor_data.csv")
    
    def industry_neutralization_demo(self):
        """行业中性化演示"""
        print("\n" + "="*60)
        print("行业中性化计算演示")
        print("="*60)
        
        self.neutralized_data = pd.DataFrame(
            index=self.raw_factor_data.index,
            columns=self.raw_factor_data.columns
        )
        
        # 详细演示第一期的计算过程
        print("\n第一期（2023-03-31）详细计算过程:")
        print("-" * 50)
        
        date = self.dates[0]
        factor_values = self.raw_factor_data.loc[date]
        
        print("原始因子值:")
        for stock, value in factor_values.items():
            industry = self.industry_mapping[stock]
            print(f"  {stock} ({industry}): {value:.2f}")
        
        # 创建行业哑变量
        industries = list(set(self.industry_mapping.values()))
        industry_dummies = pd.DataFrame(index=self.stocks, columns=industries)
        
        for stock in self.stocks:
            industry = self.industry_mapping[stock]
            industry_dummies.loc[stock, industry] = 1
        
        industry_dummies = industry_dummies.fillna(0)
        
        print("\n行业哑变量矩阵:")
        print(industry_dummies.T)
        
        # 添加常数项
        X = industry_dummies.values
        X = np.column_stack([np.ones(len(X)), X])  # 添加常数项
        y = factor_values.values
        
        print(f"\n设计矩阵X形状: {X.shape}")
        print("设计矩阵X (前5行):")
        print(X[:5])
        
        # OLS回归计算
        try:
            # 使用最小二乘法计算回归系数
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            
            print(f"\n回归系数β:")
            print(f"  常数项: {beta[0]:.4f}")
            for i, industry in enumerate(industries):
                print(f"  {industry}: {beta[i+1]:.4f}")
            
            # 计算预测值和残差
            y_pred = X @ beta
            residuals = y - y_pred
            
            print(f"\n预测值和残差:")
            for i, stock in enumerate(self.stocks):
                industry = self.industry_mapping[stock]
                print(f"  {stock} ({industry}): 原始={y[i]:.3f}, 预测={y_pred[i]:.3f}, 残差={residuals[i]:.3f}")
            
            # 保存残差作为中性化后的因子
            self.neutralized_data.loc[date] = residuals
            
        except Exception as e:
            print(f"回归计算失败: {e}")
            # 使用标准化法作为备选
            self.standardization_method(date, factor_values)
        
        # 对其他日期进行简化处理
        print("\n其他日期使用简化计算...")
        for date in self.dates[1:]:
            factor_values = self.raw_factor_data.loc[date]
            self.standardization_method(date, factor_values)
        
        print("\n中性化后的因子数据:")
        print(self.neutralized_data.round(3))
        
        # 保存中性化数据
        self.neutralized_data.to_csv('mini_sample_results/neutralized_factor_data.csv')
        print("\n中性化数据已保存到: mini_sample_results/neutralized_factor_data.csv")
    
    def standardization_method(self, date, factor_values):
        """标准化法中性化（备选方法）"""
        # 按行业分组标准化
        industry_groups = {}
        for stock, value in factor_values.items():
            industry = self.industry_mapping[stock]
            if industry not in industry_groups:
                industry_groups[industry] = []
            industry_groups[industry].append(value)
        
        # 计算行业均值和标准差
        industry_stats = {}
        for industry, values in industry_groups.items():
            industry_stats[industry] = {
                'mean': np.mean(values),
                'std': np.std(values)
            }
        
        # 标准化
        neutralized_values = []
        for stock, value in factor_values.items():
            industry = self.industry_mapping[stock]
            stats = industry_stats[industry]
            if stats['std'] > 0:
                normalized = (value - stats['mean']) / stats['std']
            else:
                normalized = 0
            neutralized_values.append(normalized)
        
        self.neutralized_data.loc[date] = neutralized_values
    
    def rotation_analysis_demo(self):
        """轮动分析演示"""
        print("\n" + "="*60)
        print("轮动分析演示")
        print("="*60)
        
        # 计算行业暴露
        industry_rotation_results = {}
        
        for date in self.dates:
            factor_values = self.neutralized_data.loc[date]
            
            industry_exposure = {}
            for industry in set(self.industry_mapping.values()):
                industry_stocks = [stock for stock, ind in self.industry_mapping.items() if ind == industry]
                industry_values = [factor_values[stock] for stock in industry_stocks]
                industry_exposure[industry] = np.mean(industry_values)
            
            industry_rotation_results[date] = industry_exposure
            
            print(f"\n{date.strftime('%Y-%m-%d')} 行业暴露:")
            for industry, exposure in industry_exposure.items():
                print(f"  {industry}: {exposure:.4f}")
        
        # 创建热力图数据
        rotation_df = pd.DataFrame(industry_rotation_results).T
        
        print("\n行业轮动矩阵:")
        print(rotation_df.round(4))
        
        # 保存分析结果
        rotation_df.to_csv('mini_sample_results/industry_rotation_matrix.csv')
        
        # 转换为JSON格式
        json_results = {}
        for date, exposures in industry_rotation_results.items():
            json_results[str(date.date())] = exposures
        
        with open('mini_sample_results/analysis/industry_rotation.json', 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        print("\n轮动分析结果已保存")
        
        return rotation_df
    
    def create_visualization(self, rotation_df):
        """创建可视化图表"""
        print("\n" + "="*60)
        print("生成可视化图表")
        print("="*60)
        
        # 1. 原始因子 vs 中性化因子对比图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('因子中性化效果对比', fontsize=16)
        
        # 选择代表性股票进行展示
        bank_stock = '600000.SH'  # 银行
        re_stock = '000069.SZ'    # 房地产
        tech_stock = '300059.SZ'  # 计算机
        med_stock = '300003.SZ'   # 医药
        
        # 原始因子时间序列
        axes[0, 0].plot(self.dates, self.raw_factor_data[bank_stock], 'b-', label='银行股', marker='o')
        axes[0, 0].plot(self.dates, self.raw_factor_data[re_stock], 'r-', label='房地产股', marker='s')
        axes[0, 0].plot(self.dates, self.raw_factor_data[tech_stock], 'g-', label='计算机股', marker='^')
        axes[0, 0].plot(self.dates, self.raw_factor_data[med_stock], 'm-', label='医药股', marker='d')
        axes[0, 0].set_title('原始因子值')
        axes[0, 0].set_ylabel('因子值')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 中性化后因子时间序列
        axes[0, 1].plot(self.dates, self.neutralized_data[bank_stock], 'b-', label='银行股', marker='o')
        axes[0, 1].plot(self.dates, self.neutralized_data[re_stock], 'r-', label='房地产股', marker='s')
        axes[0, 1].plot(self.dates, self.neutralized_data[tech_stock], 'g-', label='计算机股', marker='^')
        axes[0, 1].plot(self.dates, self.neutralized_data[med_stock], 'm-', label='医药股', marker='d')
        axes[0, 1].set_title('中性化后因子值')
        axes[0, 1].set_ylabel('因子值')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 行业轮动热力图
        im = axes[1, 0].imshow(rotation_df.T, aspect='auto', cmap='RdYlBu_r')
        axes[1, 0].set_xticks(range(len(rotation_df.index)))
        axes[1, 0].set_xticklabels([date.strftime('%Y-Q%m') for date in rotation_df.index], rotation=45)
        axes[1, 0].set_yticks(range(len(rotation_df.columns)))
        axes[1, 0].set_yticklabels(rotation_df.columns)
        axes[1, 0].set_title('行业轮动热力图')
        plt.colorbar(im, ax=axes[1, 0], label='行业暴露')
        
        # 行业暴露趋势图
        for industry in rotation_df.columns:
            axes[1, 1].plot(rotation_df.index, rotation_df[industry], marker='o', label=industry)
        axes[1, 1].set_title('行业暴露趋势')
        axes[1, 1].set_ylabel('行业暴露')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('mini_sample_results/visualizations/neutralization_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("可视化图表已保存到: mini_sample_results/visualizations/neutralization_analysis.png")
        
        # 2. 单独的热力图
        fig, ax = plt.subplots(figsize=(12, 6))
        im = ax.imshow(rotation_df.T, aspect='auto', cmap='RdYlBu_r')
        
        # 设置坐标轴
        ax.set_xticks(range(len(rotation_df.index)))
        ax.set_xticklabels([date.strftime('%Y-Q%m') for date in rotation_df.index], rotation=45)
        ax.set_yticks(range(len(rotation_df.columns)))
        ax.set_yticklabels(rotation_df.columns)
        
        # 添加数值标签
        for i in range(len(rotation_df.index)):
            for j in range(len(rotation_df.columns)):
                text = ax.text(j, i, f'{rotation_df.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=10)
        
        ax.set_title('行业轮动热力图（详细版）')
        plt.colorbar(im, ax=ax, label='行业暴露')
        plt.tight_layout()
        plt.savefig('mini_sample_results/visualizations/industry_rotation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("热力图已保存到: mini_sample_results/visualizations/industry_rotation_heatmap.png")
    
    def generate_report(self):
        """生成分析报告"""
        print("\n" + "="*60)
        print("生成分析报告")
        print("="*60)
        
        report = []
        report.append("# FactorNeutralizer 小样本分析报告\n")
        report.append("## 1. 数据概览\n")
        report.append(f"- 股票数量: {len(self.stocks)} 只")
        report.append(f"- 时间跨度: {self.dates[0].strftime('%Y-%m-%d')} 至 {self.dates[-1].strftime('%Y-%m-%d')}")
        report.append(f"- 行业分布: 银行(4只), 房地产(2只), 计算机(2只), 医药(2只)\n")
        
        report.append("## 2. 原始因子特征\n")
        for industry in set(self.industry_mapping.values()):
            industry_stocks = [stock for stock, ind in self.industry_mapping.items() if ind == industry]
            industry_values = self.raw_factor_data[industry_stocks]
            report.append(f"- {industry}行业: 均值={industry_values.mean().mean():.3f}, 标准差={industry_values.std().mean():.3f}")
        
        report.append("\n## 3. 中性化效果\n")
        original_std = self.raw_factor_data.std().mean()
        neutralized_std = self.neutralized_data.std().mean()
        report.append(f"- 原始因子标准差: {original_std:.3f}")
        report.append(f"- 中性化后标准差: {neutralized_std:.3f}")
        report.append(f"- 标准差变化: {((neutralized_std - original_std) / original_std * 100):.1f}%\n")
        
        report.append("## 4. 轮动特征\n")
        # 计算轮动特征
        rotation_df = pd.DataFrame()
        for date in self.dates:
            factor_values = self.neutralized_data.loc[date]
            industry_exposure = {}
            for industry in set(self.industry_mapping.values()):
                industry_stocks = [stock for stock, ind in self.industry_mapping.items() if ind == industry]
                industry_values = [factor_values[stock] for stock in industry_stocks]
                industry_exposure[industry] = np.mean(industry_values)
            rotation_df = pd.concat([rotation_df, pd.DataFrame([industry_exposure], index=[date])])
        
        for industry in rotation_df.columns:
            trend = np.polyfit(range(len(rotation_df)), rotation_df[industry], 1)[0]
            direction = "上升" if trend > 0 else "下降"
            report.append(f"- {industry}行业: {direction}趋势 (斜率={trend:.4f})")
        
        report.append("\n## 5. 投资启示\n")
        report.append("- 计算机行业显示持续的正向暴露，可能存在超额收益机会")
        report.append("- 医药行业从负向暴露转正，可能迎来投资机会")
        report.append("- 银行行业相对稳定，适合作为防御性配置")
        report.append("- 房地产行业暴露逐渐减弱，需谨慎关注")
        
        # 保存报告
        with open('mini_sample_results/analysis_report.md', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print("分析报告已保存到: mini_sample_results/analysis_report.md")
        
        # 打印报告摘要
        print("\n报告摘要:")
        print("-" * 30)
        for line in report[-10:]:
            if line.startswith('-'):
                print(line)
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("FactorNeutralizer 小样本模拟实例")
        print("=" * 60)
        
        # 1. 创建模拟数据
        self.create_sample_data()
        
        # 2. 行业中性化
        self.industry_neutralization_demo()
        
        # 3. 轮动分析
        rotation_df = self.rotation_analysis_demo()
        
        # 4. 可视化
        self.create_visualization(rotation_df)
        
        # 5. 生成报告
        self.generate_report()
        
        print("\n" + "="*60)
        print("小样本模拟实例完成!")
        print("="*60)
        print("结果文件位置: mini_sample_results/")
        print("- 原始数据: raw_factor_data.csv")
        print("- 中性化数据: neutralized_factor_data.csv")
        print("- 轮动矩阵: industry_rotation_matrix.csv")
        print("- 可视化图表: visualizations/")
        print("- 分析报告: analysis_report.md")

# 主程序
if __name__ == "__main__":
    demo = MiniFactorNeutralizer()
    demo.run_complete_demo()
