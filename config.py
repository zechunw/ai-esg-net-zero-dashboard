# -*- coding: utf-8 -*-
"""
ESG 评估系统配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== API配置 ====================
class APIConfig:
    """第三方API配置"""
    # DeepSeek API (主要使用的AI)
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    # OpenAI API (备选)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Anthropic API (备选)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
# ==================== ESG评分维度 ====================
class ESGDimensions:
    """ESG六大核心评估维度"""
    DIMENSIONS = {
        'long_term_aspiration': {
            'name': '长期抱负',
            'name_en': 'Long-term Aspiration',
            'description': '是否有符合《巴黎协定》的长期净零目标',
            'weight': 1.2,
            'indicators': [
                '净零承诺年份',
                '与1.5°C路径一致性',
                'SBTi认证状态'
            ]
        },
        'mid_short_targets': {
            'name': '中短期目标',
            'name_en': 'Mid-short Term Targets',
            'description': '短期减排目标是否清晰并涵盖范畴1、2、3排放',
            'weight': 1.1,
            'indicators': [
                '2030年减排目标',
                '范畴1+2覆盖',
                '范畴3覆盖范围'
            ]
        },
        'emission_performance': {
            'name': '排放绩效',
            'name_en': 'Emission Performance',
            'description': '过去几年的实际碳排量轨迹是否符合预期',
            'weight': 1.3,
            'indicators': [
                '年度减排率',
                '范畴1排放趋势',
                '范畴2排放趋势',
                '范畴3排放趋势'
            ]
        },
        'disclosure': {
            'name': '信息披露',
            'name_en': 'Disclosure',
            'description': '数据透明度，是否遵循TCFD、GRI或IFRS S1/S2标准',
            'weight': 1.0,
            'indicators': [
                'TCFD合规',
                'GRI标准',
                'IFRS S1/S2',
                '数据更新频率'
            ]
        },
        'decarbonization_strategy': {
            'name': '脱碳策略',
            'name_en': 'Decarbonization Strategy',
            'description': '企业的转型计划是否切实可行',
            'weight': 1.2,
            'indicators': [
                '技术路线图',
                '可再生能源比例',
                '供应链减排措施'
            ]
        },
        'capital_allocation': {
            'name': '资本配置',
            'name_en': 'Capital Allocation',
            'description': '"绿色资本支出"与"绿色收入"的实际投入比例',
            'weight': 1.1,
            'indicators': [
                '绿色资本支出占比',
                '绿色收入占比',
                '低碳投资趋势'
            ]
        }
    }
    
    # 契合度等级定义
    FIT_LEVELS = {
        'not_aligned': {
            'name': '不契合',
            'name_en': 'Not Aligned',
            'score_range': (0, 1.5),
            'color': '#d32f2f',
            'icon': 'X'
        },
        'committed': {
            'name': '承诺契合',
            'name_en': 'Committed',
            'score_range': (1.5, 2.5),
            'color': '#f57c00',
            'icon': '!'
        },
        'partially_aligned': {
            'name': '部分契合',
            'name_en': 'Partially Aligned',
            'score_range': (2.5, 3.5),
            'color': '#fbc02d',
            'icon': '~'
        },
        'aligned': {
            'name': '契合净零路径',
            'name_en': 'Aligned',
            'score_range': (3.5, 4.5),
            'color': '#388e3c',
            'icon': 'O'
        },
        'achieving': {
            'name': '正在达成净零',
            'name_en': 'Achieving',
            'score_range': (4.5, 5.0),
            'color': '#1976d2',
            'icon': '*'
        }
    }

# ==================== 数据源配置 ====================
class DataSources:
    """ESG数据源配置"""
    SOURCES = {
        'msci': {
            'name': 'MSCI ESG Ratings',
            'type': 'api',
            'requires_auth': True
        },
        'sustainalytics': {
            'name': 'Sustainalytics',
            'type': 'web',
            'requires_auth': False
        },
        'cdp': {
            'name': 'CDP Climate Change',
            'type': 'api',
            'requires_auth': True
        },
        'news': {
            'name': '新闻舆情',
            'type': 'scraper',
            'keywords': ['greenwashing', '漂绿', 'bluewashing', '蓝洗']
        }
    }

# ==================== AI提示词模板 ====================
class PromptTemplates:
    """AI评估提示词模板"""
    
    EVALUATION_PROMPT = """你是一个专业的ESG分析师，负责评估企业的净零契合度。

请根据以下信息，对企业进行六大维度的评估（1-5分）：

企业信息：
- 名称：{company_name}
- 股票代码：{stock_code}
- 行业：{industry}

收集到的数据：
{data}

请输出JSON格式的评估结果：
{{
    "scores": {{
        "long_term_aspiration": {{
            "score": <分数>,
            "reasoning": "<评分理由>",
            "evidence": ["<证据1>", "<证据2>"]
        }},
        "mid_short_targets": {{...}},
        "emission_performance": {{...}},
        "disclosure": {{...}},
        "decarbonization_strategy": {{...}},
        "capital_allocation": {{...
        }}
    }},
    "overall_score": <加权平均分>,
    "alignment_status": "<契合度状态>",
    "strengths": ["<优势1>", "<优势2>"],
    "weaknesses": ["<劣势1>", "<劣势2>"],
    "improvement_suggestions": ["<建议1>", "<建议2>"],
    "greenwashing_risk": <true/false>,
    "greenwashing_indicators": ["<漂绿迹象1>", "<漂绿迹象2>"]
}}

注意：
1. 如果发现企业"言行不一"（如承诺净零但减少绿色投资），应在相应维度扣分
2. 请严格基于提供的数据进行评估，不要编造信息
3. 评分标准：1=极差，2=较差，3=一般，4=良好，5=优秀
"""

# ==================== 应用配置 ====================
class AppConfig:
    """应用配置"""
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000', '*']
    
    # 数据缓存时间（秒）
    CACHE_DURATION = 3600  # 1小时
    
    # 请求超时（秒）
    REQUEST_TIMEOUT = 30
