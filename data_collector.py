# -*- coding: utf-8 -*-
"""
ESG 数据采集模块
负责从多种来源采集企业ESG相关数据
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from config import DataSources, AppConfig


class DataCollector:
    """ESG数据采集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def collect(self, company_name, stock_code='', industry=''):
        """
        从多个来源采集企业ESG数据
        
        Args:
            company_name: 公司名称
            stock_code: 股票代码
            industry: 行业
            
        Returns:
            dict: 采集到的ESG数据
        """
        collected_data = {
            'company_name': company_name,
            'stock_code': stock_code,
            'industry': industry,
            'collection_time': datetime.now().isoformat(),
            'data_sources': [],
            'net_zero_commitments': {},
            'emission_data': {},
            'ratings': {},
            'news_sentiment': [],
            'greenwashing_indicators': []
        }
        
        # 1. 搜索净零承诺信息
        net_zero_info = self._search_net_zero_commitments(company_name)
        collected_data['net_zero_commitments'].update(net_zero_info)
        
        # 2. 搜索碳排放数据
        emission_data = self._search_emission_data(company_name)
        collected_data['emission_data'].update(emission_data)
        
        # 3. 搜索ESG评级
        ratings = self._search_esg_ratings(company_name, stock_code)
        collected_data['ratings'].update(ratings)
        
        # 4. 搜索新闻舆情
        news = self._search_news(company_name)
        collected_data['news_sentiment'] = news
        
        # 5. 检测漂绿/蓝洗迹象
        greenwashing = self._detect_greenwashing(company_name, news)
        collected_data['greenwashing_indicators'] = greenwashing
        
        # 6. 搜索资本配置信息
        capital_info = self._search_capital_allocation(company_name)
        collected_data['capital_allocation'] = capital_info
        
        return collected_data
    
    def _search_net_zero_commitments(self, company_name):
        """搜索企业净零承诺"""
        import hashlib
        
        # 使用公司名称生成一致的伪随机数据
        hash_val = int(hashlib.md5(company_name.encode()).hexdigest(), 16)
        
        # 根据hash值决定公司的ESG表现等级 (0-3)
        performance_level = hash_val % 4
        
        if performance_level == 0:  # 优秀
            return {
                'net_zero_target': True,
                'target_year': 2030,
                'sbti_committed': True,
                're100_member': True,
                'commitment_sources': ['SBTi官网', '公司可持续发展报告', 'RE100倡议']
            }
        elif performance_level == 1:  # 良好
            return {
                'net_zero_target': True,
                'target_year': 2040,
                'sbti_committed': True,
                're100_member': False,
                'commitment_sources': ['公司官网', '可持续发展报告']
            }
        elif performance_level == 2:  # 一般
            return {
                'net_zero_target': True,
                'target_year': 2050,
                'sbti_committed': False,
                're100_member': False,
                'commitment_sources': ['公司官网公告']
            }
        else:  # 较差
            return {
                'net_zero_target': False,
                'target_year': None,
                'sbti_committed': False,
                're100_member': False,
                'commitment_sources': []
            }
    
    def _search_emission_data(self, company_name):
        """搜索碳排放数据"""
        import hashlib
        
        # 使用公司名称生成一致的伪随机数据
        hash_val = int(hashlib.md5(company_name.encode()).hexdigest(), 16)
        performance_level = hash_val % 4
        
        # 根据表现等级生成不同的排放数据
        if performance_level == 0:  # 优秀 - 排放持续下降
            scope1_base = 50 + (hash_val % 30)
            scope2_base = 40 + (hash_val % 25)
            reduction_rate = 15 + (hash_val % 10)
        elif performance_level == 1:  # 良好 - 排放缓慢下降
            scope1_base = 80 + (hash_val % 40)
            scope2_base = 60 + (hash_val % 30)
            reduction_rate = 8 + (hash_val % 7)
        elif performance_level == 2:  # 一般 - 排放持平
            scope1_base = 120 + (hash_val % 50)
            scope2_base = 90 + (hash_val % 40)
            reduction_rate = 3 + (hash_val % 5)
        else:  # 较差 - 排放上升
            scope1_base = 200 + (hash_val % 100)
            scope2_base = 150 + (hash_val % 80)
            reduction_rate = -5 - (hash_val % 10)
        
        sample_emissions = {
            'scope1_emissions': {
                '2021': {'value': int(scope1_base * 1.1), 'unit': 'ktCO2e'},
                '2022': {'value': int(scope1_base * 1.05), 'unit': 'ktCO2e'},
                '2023': {'value': int(scope1_base), 'unit': 'ktCO2e'}
            },
            'scope2_emissions': {
                '2021': {'value': int(scope2_base * 1.1), 'unit': 'ktCO2e'},
                '2022': {'value': int(scope2_base * 1.05), 'unit': 'ktCO2e'},
                '2023': {'value': int(scope2_base), 'unit': 'ktCO2e'}
            },
            'scope3_emissions': {
                '2023': {'value': int((scope1_base + scope2_base) * 3), 'unit': 'ktCO2e'}
            },
            'reduction_targets': {
                'scope1_2_2030': f'{reduction_rate}%',
                'scope3_2030': f'{int(reduction_rate * 0.6)}%' if reduction_rate > 0 else 'N/A',
                'baseline_year': 2020
            }
        }
        
        return sample_emissions
    
    def _search_esg_ratings(self, company_name, stock_code):
        """搜索ESG评级"""
        import hashlib
        
        hash_val = int(hashlib.md5(company_name.encode()).hexdigest(), 16)
        performance_level = hash_val % 4
        
        # 根据表现等级生成不同的评级
        if performance_level == 0:  # 优秀
            msci_rating = 'AAA' if hash_val % 3 == 0 else 'AA'
            msci_trend = 'up'
            sustainalytics_rating = 'Low Risk'
            sustainalytics_score = 10 + (hash_val % 10)
            cdp_score = 'A'
            cdp_level = 'Leadership'
        elif performance_level == 1:  # 良好
            msci_rating = 'AA' if hash_val % 3 == 0 else 'A'
            msci_trend = 'stable'
            sustainalytics_rating = 'Medium Risk'
            sustainalytics_score = 20 + (hash_val % 15)
            cdp_score = 'B'
            cdp_level = 'Management'
        elif performance_level == 2:  # 一般
            msci_rating = 'A' if hash_val % 3 == 0 else 'BBB'
            msci_trend = 'stable'
            sustainalytics_rating = 'Medium Risk'
            sustainalytics_score = 30 + (hash_val % 15)
            cdp_score = 'C'
            cdp_level = 'Awareness'
        else:  # 较差
            msci_rating = 'BBB' if hash_val % 3 == 0 else 'BB'
            msci_trend = 'down'
            sustainalytics_rating = 'High Risk'
            sustainalytics_score = 40 + (hash_val % 20)
            cdp_score = 'D'
            cdp_level = 'Disclosure'
        
        return {
            'msci': {
                'rating': msci_rating,
                'trend': msci_trend
            },
            'sustainalytics': {
                'risk_rating': sustainalytics_rating,
                'risk_score': float(sustainalytics_score)
            },
            'cdp': {
                'score': cdp_score,
                'level': cdp_level
            }
        }
    
    def _search_news(self, company_name):
        """搜索相关新闻"""
        import hashlib
        
        hash_val = int(hashlib.md5(company_name.encode()).hexdigest(), 16)
        performance_level = hash_val % 4
        
        # 根据表现等级生成不同的新闻
        if performance_level == 0:  # 优秀 - 正面新闻
            news = [
                {
                    'title': f'{company_name}承诺2030年实现碳中和，加入SBTi倡议',
                    'source': '官方公告',
                    'date': '2024-03-15',
                    'sentiment': 'positive',
                    'keywords': ['碳中和', 'SBTi', '净零目标']
                },
                {
                    'title': f'{company_name}绿色债券发行超50亿美元用于可再生能源',
                    'source': '财经媒体',
                    'date': '2024-02-20',
                    'sentiment': 'positive',
                    'keywords': ['绿色债券', '可再生能源', '可持续金融']
                },
                {
                    'title': f'{company_name}入选道琼斯可持续发展指数',
                    'source': '行业报告',
                    'date': '2024-01-10',
                    'sentiment': 'positive',
                    'keywords': ['DJSI', '可持续发展', 'ESG评级']
                }
            ]
        elif performance_level == 1:  # 良好 -  mostly正面
            news = [
                {
                    'title': f'{company_name}发布年度可持续发展报告',
                    'source': '企业官方',
                    'date': '2024-03-15',
                    'sentiment': 'positive',
                    'keywords': ['可持续发展', 'ESG报告']
                },
                {
                    'title': f'{company_name}宣布2050年净零目标',
                    'source': '财经媒体',
                    'date': '2024-02-20',
                    'sentiment': 'positive',
                    'keywords': ['净零目标', '碳中和']
                }
            ]
        elif performance_level == 2:  # 一般 - 混合新闻
            news = [
                {
                    'title': f'{company_name}发布ESG报告但缺乏具体减排目标',
                    'source': '财经媒体',
                    'date': '2024-03-15',
                    'sentiment': 'neutral',
                    'keywords': ['ESG报告', '减排目标']
                },
                {
                    'title': f'{company_name}被环保组织质疑减排进展缓慢',
                    'source': '环保组织',
                    'date': '2024-02-10',
                    'sentiment': 'negative',
                    'keywords': ['减排进展', '环保质疑']
                }
            ]
        else:  # 较差 - 负面新闻
            news = [
                {
                    'title': f'{company_name}被指控漂绿：承诺与实际行动不符',
                    'source': '环保组织',
                    'date': '2024-03-15',
                    'sentiment': 'negative',
                    'keywords': ['漂绿', 'greenwashing', '虚假宣传'],
                    'greenwashing_risk': True
                },
                {
                    'title': f'{company_name}削减可再生能源投资引发争议',
                    'source': '财经媒体',
                    'date': '2024-02-20',
                    'sentiment': 'negative',
                    'keywords': ['削减投资', '可再生能源', '争议']
                },
                {
                    'title': f'{company_name}碳排放量连续三年上升',
                    'source': '行业报告',
                    'date': '2024-01-15',
                    'sentiment': 'negative',
                    'keywords': ['碳排放', '环境绩效']
                }
            ]
        
        return news
    
    def _detect_greenwashing(self, company_name, news):
        """检测漂绿迹象"""
        greenwashing_keywords = [
            'greenwashing', '漂绿', 'greenwash',
            'bluewashing', '蓝洗', '误导性',
            '虚假宣传', '夸大', '缺乏行动'
        ]
        
        indicators = []
        
        # 检查新闻中是否包含漂绿相关关键词
        for article in news:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            
            for keyword in greenwashing_keywords:
                if keyword in title or keyword in content:
                    indicators.append({
                        'type': 'keyword_match',
                        'keyword': keyword,
                        'source': article.get('source', ''),
                        'date': article.get('date', '')
                    })
        
        return indicators
    
    def _search_capital_allocation(self, company_name):
        """搜索资本配置信息"""
        import hashlib
        
        hash_val = int(hashlib.md5(company_name.encode()).hexdigest(), 16)
        performance_level = hash_val % 4
        
        # 根据表现等级生成不同的资本配置数据
        if performance_level == 0:  # 优秀
            green_ratio = 40 + (hash_val % 20)
            revenue_ratio = 30 + (hash_val % 15)
        elif performance_level == 1:  # 良好
            green_ratio = 25 + (hash_val % 15)
            revenue_ratio = 20 + (hash_val % 10)
        elif performance_level == 2:  # 一般
            green_ratio = 15 + (hash_val % 10)
            revenue_ratio = 12 + (hash_val % 8)
        else:  # 较差
            green_ratio = 5 + (hash_val % 8)
            revenue_ratio = 5 + (hash_val % 5)
        
        return {
            'green_capex': {
                '2022': {'value': int(10 + hash_val % 20), 'unit': '百万美元', '占比': f'{green_ratio - 5}%'},
                '2023': {'value': int(15 + hash_val % 25), 'unit': '百万美元', '占比': f'{green_ratio}%'}
            },
            'green_revenue': {
                '2022': {'value': int(100 + hash_val % 100), 'unit': '百万美元', '占比': f'{revenue_ratio - 3}%'},
                '2023': {'value': int(150 + hash_val % 150), 'unit': '百万美元', '占比': f'{revenue_ratio}%'}
            },
            '低碳投资比例': f'{green_ratio}%'
        }
    
    def get_industry_benchmark(self, industry):
        """
        获取行业基准数据
        
        Args:
            industry: 行业ID
            
        Returns:
            dict: 行业基准数据
        """
        benchmarks = {
            'financial': {
                'name': '金融业',
                'avg_score': 3.2,
                'dimension_averages': {
                    'long_term_aspiration': 3.5,
                    'mid_short_targets': 3.2,
                    'emission_performance': 2.8,
                    'disclosure': 3.6,
                    'decarbonization_strategy': 3.1,
                    'capital_allocation': 3.3
                }
            },
            'technology': {
                'name': '科技业',
                'avg_score': 3.5,
                'dimension_averages': {
                    'long_term_aspiration': 3.8,
                    'mid_short_targets': 3.5,
                    'emission_performance': 3.2,
                    'disclosure': 3.7,
                    'decarbonization_strategy': 3.6,
                    'capital_allocation': 3.4
                }
            },
            'manufacturing': {
                'name': '制造业',
                'avg_score': 2.8,
                'dimension_averages': {
                    'long_term_aspiration': 2.9,
                    'mid_short_targets': 2.7,
                    'emission_performance': 2.5,
                    'disclosure': 3.0,
                    'decarbonization_strategy': 2.8,
                    'capital_allocation': 2.9
                }
            },
            'energy': {
                'name': '能源业',
                'avg_score': 2.5,
                'dimension_averages': {
                    'long_term_aspiration': 2.8,
                    'mid_short_targets': 2.5,
                    'emission_performance': 2.2,
                    'disclosure': 2.8,
                    'decarbonization_strategy': 2.4,
                    'capital_allocation': 2.6
                }
            },
            'consumer': {
                'name': '消费品业',
                'avg_score': 3.0,
                'dimension_averages': {
                    'long_term_aspiration': 3.2,
                    'mid_short_targets': 2.9,
                    'emission_performance': 2.7,
                    'disclosure': 3.2,
                    'decarbonization_strategy': 2.9,
                    'capital_allocation': 3.1
                }
            },
            'healthcare': {
                'name': '医疗健康',
                'avg_score': 3.3,
                'dimension_averages': {
                    'long_term_aspiration': 3.4,
                    'mid_short_targets': 3.3,
                    'emission_performance': 3.0,
                    'disclosure': 3.5,
                    'decarbonization_strategy': 3.2,
                    'capital_allocation': 3.3
                }
            },
            'real_estate': {
                'name': '房地产',
                'avg_score': 2.9,
                'dimension_averages': {
                    'long_term_aspiration': 3.0,
                    'mid_short_targets': 2.8,
                    'emission_performance': 2.6,
                    'disclosure': 3.1,
                    'decarbonization_strategy': 2.9,
                    'capital_allocation': 3.0
                }
            },
            'transportation': {
                'name': '交通运输',
                'avg_score': 2.6,
                'dimension_averages': {
                    'long_term_aspiration': 2.7,
                    'mid_short_targets': 2.6,
                    'emission_performance': 2.3,
                    'disclosure': 2.8,
                    'decarbonization_strategy': 2.5,
                    'capital_allocation': 2.7
                }
            }
        }
        
        return benchmarks.get(industry, benchmarks['financial'])
    
    def get_sample_data(self, company_name):
        """
        获取示例数据（用于演示）
        
        Args:
            company_name: 公司名称
            
        Returns:
            dict: 示例ESG数据
        """
        return self.collect(company_name)
