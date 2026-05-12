"""
可视化模块重构 - 提升代码可读性
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from factor_neutralizer.utils.logger_config import get_logger

@dataclass
class VisualizationConfig:
    """可视化配置"""
    max_industries: int = 15
    figure_size: Tuple[int, int] = (12, 6)
    dpi: int = 150
    fontsize: int = 8
    title_fontsize: int = 10
    colormap: str = 'RdBu_r'
    vmin: float = -2
    vmax: float = 2

class BaseVisualizer(ABC):
    """可视化基类"""
    
    def __init__(self, output_dir: str, config: Optional[VisualizationConfig] = None):
        """
        初始化可视化器
        
        Args:
            output_dir: 输出目录
            config: 可视化配置
        """
        self.output_dir = output_dir
        self.config = config or VisualizationConfig()
        self.logger = get_logger()
    
    @abstractmethod
    def visualize(self, data: Dict, factor_name: str) -> bool:
        """可视化数据"""
        pass
    
    def _create_output_path(self, factor_name: str, suffix: str) -> str:
        """创建输出路径"""
        import os
        return os.path.join(self.output_dir, 'visualizations', f'{factor_name}_{suffix}.png')
    
    def _setup_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """设置图形"""
        fig, ax = plt.subplots(figsize=self.config.figure_size)
        return fig, ax
    
    def _save_figure_async(self, fig: plt.Figure, output_path: str) -> bool:
        """异步保存图形"""
        try:
            from concurrent.futures import ThreadPoolExecutor
            
            def save_task():
                try:
                    fig.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
                    plt.close(fig)
                    return True
                except Exception as e:
                    plt.close(fig)
                    self.logger.error(f"保存图形失败: {e}")
                    return False
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(save_task)
                success = future.result()
                
                if success:
                    self.logger.info(f"图形保存成功: {output_path}")
                else:
                    self.logger.error(f"图形保存失败: {output_path}")
                
                return success
                
        except Exception as e:
            self.logger.error(f"异步保存失败: {e}")
            plt.close(fig)
            return False

class IndustryRotationVisualizer(BaseVisualizer):
    """行业轮动可视化器"""
    
    def visualize(self, industry_rotation_results: Dict, factor_name: str) -> bool:
        """
        可视化行业轮动
        
        Args:
            industry_rotation_results: 行业轮动结果
            factor_name: 因子名称
            
        Returns:
            bool: 是否成功
        """
        try:
            # 数据预处理
            processed_data = self._preprocess_data(industry_rotation_results)
            if not processed_data:
                return False
            
            # 创建图形
            fig, ax = self._setup_figure()
            
            # 绘制热力图
            success = self._draw_heatmap(ax, processed_data, factor_name)
            if not success:
                plt.close(fig)
                return False
            
            # 保存图形
            output_path = self._create_output_path(factor_name, 'industry_rotation')
            return self._save_figure_async(fig, output_path)
            
        except Exception as e:
            self.logger.error(f"行业轮动可视化失败: {e}")
            return False
    
    def _preprocess_data(self, quarterly_data: Dict) -> Optional[pd.DataFrame]:
        """预处理数据"""
        if not quarterly_data:
            self.logger.warning("季度数据为空")
            return None
        
        # 提取所有行业
        all_industries = set()
        for exposure_dict in quarterly_data.values():
            all_industries.update(exposure_dict.keys())
        
        all_industries = sorted(list(all_industries))
        
        # 选择显示的行业
        top_industries = self._select_top_industries(quarterly_data, all_industries)
        
        # 创建数据框
        rotation_df = self._create_rotation_df(quarterly_data, top_industries)
        
        return rotation_df
    
    def _select_top_industries(self, quarterly_data: Dict, all_industries: List[str]) -> List[str]:
        """选择显示的行业"""
        if len(all_industries) <= self.config.max_industries:
            return all_industries
        
        # 按最新期的暴露绝对值排序
        latest_date = max(quarterly_data.keys())
        industry_ranking = sorted(
            quarterly_data[latest_date].items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )
        
        return [item[0] for item in industry_ranking[:self.config.max_industries]]
    
    def _create_rotation_df(self, quarterly_data: Dict, top_industries: List[str]) -> pd.DataFrame:
        """创建轮动数据框"""
        rotation_df = pd.DataFrame(
            index=sorted(quarterly_data.keys()), 
            columns=top_industries, 
            dtype=np.float32
        )
        
        for date, exposure_dict in quarterly_data.items():
            for industry in top_industries:
                if industry in exposure_dict:
                    rotation_df.loc[date, industry] = float(exposure_dict[industry])
        
        return rotation_df.fillna(0)
    
    def _draw_heatmap(self, ax: plt.Axes, rotation_df: pd.DataFrame, factor_name: str) -> bool:
        """绘制热力图"""
        try:
            # 绘制图像
            im = ax.imshow(rotation_df.T, aspect='auto', 
                          cmap=self.config.colormap, 
                          vmin=self.config.vmin, 
                          vmax=self.config.vmax)
            
            # 设置坐标轴
            self._setup_axes(ax, rotation_df, factor_name)
            
            # 添加颜色条
            self._add_colorbar(ax, im)
            
            return True
            
        except Exception as e:
            self.logger.error(f"绘制热力图失败: {e}")
            return False
    
    def _setup_axes(self, ax: plt.Axes, rotation_df: pd.DataFrame, factor_name: str):
        """设置坐标轴"""
        # X轴
        ax.set_xticks(range(len(rotation_df.index)))
        ax.set_xticklabels(
            [date.strftime('%Y-%m') for date in rotation_df.index], 
            rotation=45, ha='right', fontsize=self.config.fontsize
        )
        
        # Y轴
        ax.set_yticks(range(len(rotation_df.columns)))
        
        # 标签设置
        try:
            ax.set_yticklabels(rotation_df.columns, fontsize=self.config.fontsize)
            ax.set_title(f'因子 {factor_name} 行业轮动 (Top {len(rotation_df.columns)})', 
                        fontsize=self.config.title_fontsize)
        except Exception:
            # 回退到英文标签
            english_labels = [f'Ind_{i+1}' for i in range(len(rotation_df.columns))]
            ax.set_yticklabels(english_labels, fontsize=self.config.fontsize)
            ax.set_title(f'Factor {factor_name} Industry Rotation (Top {len(rotation_df.columns)})', 
                        fontsize=self.config.title_fontsize)
    
    def _add_colorbar(self, ax: plt.Axes, im):
        """添加颜色条"""
        try:
            plt.colorbar(im, ax=ax, label='行业暴露')
        except Exception:
            plt.colorbar(im, ax=ax, label='Industry Exposure')

class MarketValueRotationVisualizer(BaseVisualizer):
    """市值轮动可视化器"""
    
    def visualize(self, market_value_rotation_results: Dict, factor_name: str) -> bool:
        """
        可视化市值轮动
        
        Args:
            market_value_rotation_results: 市值轮动结果
            factor_name: 因子名称
            
        Returns:
            bool: 是否成功
        """
        try:
            if not market_value_rotation_results:
                self.logger.warning("市值轮动数据为空")
                return False
            
            # 创建图形
            fig, ax = self._setup_figure()
            
            # 绘制折线图
            success = self._draw_line_plot(ax, market_value_rotation_results, factor_name)
            if not success:
                plt.close(fig)
                return False
            
            # 保存图形
            output_path = self._create_output_path(factor_name, 'market_value_rotation')
            return self._save_figure_async(fig, output_path)
            
        except Exception as e:
            self.logger.error(f"市值轮动可视化失败: {e}")
            return False
    
    def _draw_line_plot(self, ax: plt.Axes, rotation_data: Dict, factor_name: str) -> bool:
        """绘制折线图"""
        try:
            dates = sorted(rotation_data.keys())
            exposures = [rotation_data[date] for date in dates]
            
            ax.plot(dates, exposures, marker='o', linewidth=2, markersize=4)
            ax.set_title(f'因子 {factor_name} 市值暴露轮动', fontsize=self.config.title_fontsize)
            ax.set_xlabel('季度', fontsize=self.config.fontsize)
            ax.set_ylabel('市值暴露', fontsize=self.config.fontsize)
            ax.grid(True, alpha=0.3)
            
            # 添加数值标签
            for date, exposure in zip(dates, exposures):
                ax.text(date, exposure, f'{exposure:.3f}', 
                       ha='center', va='bottom', fontsize=self.config.fontsize)
            
            return True
            
        except Exception as e:
            self.logger.error(f"绘制折线图失败: {e}")
            return False

class VisualizationManager:
    """可视化管理器"""
    
    def __init__(self, output_dir: str, config: Optional[VisualizationConfig] = None):
        """
        初始化可视化管理器
        
        Args:
            output_dir: 输出目录
            config: 可视化配置
        """
        self.output_dir = output_dir
        self.config = config or VisualizationConfig()
        self.logger = get_logger()
        
        # 初始化可视化器
        self.visualizers = {
            'industry_rotation': IndustryRotationVisualizer(output_dir, config),
            'market_value_rotation': MarketValueRotationVisualizer(output_dir, config)
        }
    
    def visualize_industry_rotation(self, industry_rotation_results: Dict, factor_name: str) -> bool:
        """可视化行业轮动"""
        visualizer = self.visualizers['industry_rotation']
        return visualizer.visualize(industry_rotation_results, factor_name)
    
    def visualize_market_value_rotation(self, market_value_rotation_results: Dict, factor_name: str) -> bool:
        """可视化市值轮动"""
        visualizer = self.visualizers['market_value_rotation']
        return visualizer.visualize(market_value_rotation_results, factor_name)
    
    def batch_visualize(self, results_dict: Dict[str, Dict], viz_type: str) -> Dict[str, bool]:
        """批量可视化"""
        if viz_type not in self.visualizers:
            self.logger.error(f"不支持的可视化类型: {viz_type}")
            return {}
        
        visualizer = self.visualizers[viz_type]
        results = {}
        
        for factor_name, data in results_dict.items():
            success = visualizer.visualize(data, factor_name)
            results[factor_name] = success
            
            if success:
                self.logger.info(f"{factor_name} {viz_type} 可视化成功")
            else:
                self.logger.error(f"{factor_name} {viz_type} 可视化失败")
        
        return results
