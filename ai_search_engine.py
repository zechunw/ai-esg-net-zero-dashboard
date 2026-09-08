# -*- coding: utf-8 -*-
"""
AI 搜索引擎模块
使用 DeepSeek API 进行公司信息搜索和ESG评估
"""

import os
import json
import requests
import logging
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from config import APIConfig, ESGDimensions

logger = logging.getLogger(__name__)


class AISearchEngine:
    """AI搜索引擎 - 使用DeepSeek API"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.api_base = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"  # 或 deepseek-coder
        
    def search_company(self, query: str) -> Dict:
        """
        搜索公司信息，支持模糊匹配
        
        Args:
            query: 用户输入的公司名称（可能不准确）
            
        Returns:
            {
                'status': 'success' | 'not_found' | 'multiple_matches',
                'company': {...} | None,
                'candidates': [...] | None,
                'message': str
            }
        """
        logger.debug(f"AISearchEngine.search_company 被调用: {query}")
        
        # 检查API Key是否配置
        if not self.api_key:
            logger.error("DeepSeek API Key 未配置")
            return {
                'status': 'error',
                'company': None,
                'candidates': None,
                'message': 'DeepSeek API Key 未配置，请在 .env 文件中设置 DEEPSEEK_API_KEY'
            }
        
        prompt = f"""你是一个企业信息搜索助手。用户想搜索一家公司："{query}"

请执行以下任务：
1. 判断这是否是一个真实存在的公司（包括上市公司、大型私营企业等）
2. 如果是真实公司，返回准确的公司名称、股票代码（如有）、所属行业
3. 如果用户输入不准确但有相近的公司，返回最匹配的公司信息
4. 如果完全不存在或无法确定，返回not_found
5. 如果有多个可能的公司（如"Apple"可能是苹果公司或苹果农场），返回multiple_matches

请严格按以下JSON格式返回（不要有任何其他文字）：
{{
    "status": "success" | "not_found" | "multiple_matches",
    "company": {{
        "name": "准确的公司全称",
        "short_name": "简称",
        "stock_code": "股票代码（如有）",
        "exchange": "交易所（如有）",
        "industry": "所属行业",
        "country": "所在国家/地区"
    }},
    "candidates": [
        {{"name": "候选公司1", "description": "简要说明"}},
        {{"name": "候选公司2", "description": "简要说明"}}
    ],
    "message": "给用户的提示信息"
}}"""

        try:
            response = self._call_api(prompt)
            result = self._parse_json_response(response)
            return result
        except Exception as e:
            return {
                'status': 'error',
                'company': None,
                'candidates': None,
                'message': f'搜索出错: {str(e)}'
            }
    
    def search_esg_info(self, company_name: str) -> Dict:
        """
        搜索公司的ESG相关信息
        
        Args:
            company_name: 准确的公司名称
            
        Returns:
            {
                'search_process': [...],  # 搜索过程记录
                'data_sources': [...],     # 数据来源
                'esg_data': {...}          # ESG数据
            }
        """
        search_process = []
        
        # Step 1: 搜索净零承诺
        search_process.append({
            'step': 1,
            'action': '搜索净零承诺和气候目标',
            'status': 'searching'
        })
        
        net_zero_prompt = f"""搜索公司"{company_name}"的净零承诺和气候相关信息。

请搜索以下信息并返回JSON格式：
{{
    "net_zero_commitments": {{
        "net_zero_target": true/false,
        "target_year": 年份或null,
        "sbti_committed": true/false,
        "re100_member": true/false,
        "science_based_target": true/false,
        "commitment_sources": ["信息来源1", "信息来源2"]
    }},
    "climate_goals": {{
        "carbon_neutral_target": "碳中和目标描述",
        "renewable_energy_target": "可再生能源目标",
        "emission_reduction_targets": {{
            "scope1_2": "范畴1+2减排目标",
            "scope3": "范畴3减排目标"
        }}
    }},
    "data_sources": [
        {{"name": "来源名称", "url": "链接", "type": "官网/报告/新闻"}}
    ]
}}"""
        
        try:
            net_zero_response = self._call_api(net_zero_prompt)
            net_zero_data = self._parse_json_response(net_zero_response)
            search_process[0]['status'] = 'completed'
            search_process[0]['result'] = f"找到{len(net_zero_data.get('data_sources', []))}个信息源"
        except Exception as e:
            search_process[0]['status'] = 'failed'
            search_process[0]['error'] = str(e)
            net_zero_data = {}
        
        # Step 2: 搜索排放数据
        search_process.append({
            'step': 2,
            'action': '搜索碳排放数据',
            'status': 'searching'
        })
        
        emission_prompt = f"""搜索公司"{company_name}"的碳排放数据和环境绩效。

请搜索以下信息并返回JSON格式：
{{
    "emission_data": {{
        "scope1_emissions": {{"year": 数值, "unit": "吨CO2e", "trend": "上升/下降/持平"}},
        "scope2_emissions": {{"year": 数值, "unit": "吨CO2e", "trend": "上升/下降/持平"}},
        "scope3_emissions": {{"year": 数值, "unit": "吨CO2e", "trend": "上升/下降/持平"}},
        "emission_intensity": "排放强度数据",
        "reduction_achievements": "已实现的减排成果"
    }},
    "environmental_performance": {{
        "energy_consumption": "能源消耗情况",
        "renewable_energy_usage": "可再生能源使用比例",
        "waste_management": "废弃物管理情况"
    }},
    "data_sources": [
        {{"name": "来源名称", "url": "链接", "type": "年报/可持续发展报告/CDP"}}
    ]
}}"""
        
        try:
            emission_response = self._call_api(emission_prompt)
            emission_data = self._parse_json_response(emission_response)
            search_process[1]['status'] = 'completed'
            search_process[1]['result'] = f"找到{len(emission_data.get('data_sources', []))}个信息源"
        except Exception as e:
            search_process[1]['status'] = 'failed'
            search_process[1]['error'] = str(e)
            emission_data = {}
        
        # Step 3: 搜索ESG评级
        search_process.append({
            'step': 3,
            'action': '搜索ESG评级和评分',
            'status': 'searching'
        })
        
        rating_prompt = f"""搜索公司"{company_name}"的ESG评级和评分信息。

请搜索以下信息并返回JSON格式：
{{
    "esg_ratings": {{
        "msci": {{"rating": "评级", "trend": "上升/下降/稳定"}},
        "sustainalytics": {{"risk_score": 分数, "risk_level": "风险等级"}},
        "cdp": {{"score": "评分", "level": "等级"}},
        "djsi": {{"member": true/false, "score": 分数}},
        "other_ratings": ["其他评级信息"]
    }},
    "esg_reporting": {{
        "reporting_frameworks": ["GRI", "TCFD", "SASB"],
        "report_frequency": "报告频率",
        "third_party_assurance": true/false
    }},
    "data_sources": [
        {{"name": "来源名称", "url": "链接"}}
    ]
}}"""
        
        try:
            rating_response = self._call_api(rating_prompt)
            rating_data = self._parse_json_response(rating_response)
            search_process[2]['status'] = 'completed'
            search_process[2]['result'] = f"找到{len(rating_data.get('data_sources', []))}个评级源"
        except Exception as e:
            search_process[2]['status'] = 'failed'
            search_process[2]['error'] = str(e)
            rating_data = {}
        
        # Step 4: 搜索新闻和争议
        search_process.append({
            'step': 4,
            'action': '搜索ESG相关新闻和争议',
            'status': 'searching'
        })
        
        news_prompt = f"""搜索公司"{company_name}"最近的ESG相关新闻和争议。

请搜索以下信息并返回JSON格式：
{{
    "news_sentiment": {{
        "overall": "正面/负面/中性",
        "positive_news": [
            {{"title": "新闻标题", "date": "日期", "summary": "摘要"}}
        ],
        "negative_news": [
            {{"title": "新闻标题", "date": "日期", "summary": "摘要", "severity": "严重/一般"}}
        ],
        "controversies": [
            {{"topic": "争议主题", "description": "描述", "status": "已解决/进行中"}}
        ]
    }},
    "greenwashing_risks": {{
        "risk_level": "高/中/低/无",
        "indicators": ["漂绿迹象1", "漂绿迹象2"],
        "accusations": ["相关指控"]
    }},
    "data_sources": [
        {{"name": "新闻来源", "url": "链接", "date": "日期"}}
    ]
}}"""
        
        try:
            news_response = self._call_api(news_prompt)
            news_data = self._parse_json_response(news_response)
            search_process[3]['status'] = 'completed'
            search_process[3]['result'] = f"找到{len(news_data.get('data_sources', []))}条新闻"
        except Exception as e:
            search_process[3]['status'] = 'failed'
            search_process[3]['error'] = str(e)
            news_data = {}
        
        # 合并所有数据
        esg_data = {
            **net_zero_data.get('net_zero_commitments', {}),
            **net_zero_data.get('climate_goals', {}),
            'emission_data': emission_data.get('emission_data', {}),
            'environmental_performance': emission_data.get('environmental_performance', {}),
            'ratings': rating_data.get('esg_ratings', {}),
            'esg_reporting': rating_data.get('esg_reporting', {}),
            'news_sentiment': news_data.get('news_sentiment', {}),
            'greenwashing_risks': news_data.get('greenwashing_risks', {})
        }
        
        # 收集所有数据来源
        all_sources = []
        for data in [net_zero_data, emission_data, rating_data, news_data]:
            all_sources.extend(data.get('data_sources', []))
        
        return {
            'search_process': search_process,
            'data_sources': all_sources,
            'esg_data': esg_data
        }
    
    def evaluate_esg(self, company_name: str, esg_data: Dict) -> Dict:
        """
        使用AI进行ESG评分
        
        Args:
            company_name: 公司名称
            esg_data: 收集到的ESG数据
            
        Returns:
            评分结果
        """
        dimensions = ESGDimensions.DIMENSIONS
        
        prompt = f"""你是一个专业的ESG分析师。请根据以下信息对公司"{company_name}"进行ESG评估。

ESG数据：
{json.dumps(esg_data, ensure_ascii=False, indent=2)}

评估维度说明：
{json.dumps({k: v for k, v in dimensions.items()}, ensure_ascii=False, indent=2)}

请按以下JSON格式返回评估结果（评分范围1-5，1=极差，5=优秀）：
{{
    "scores": {{
        "long_term_aspiration": {{
            "score": 分数,
            "reasoning": "评分理由（基于什么数据）",
            "evidence": ["证据1", "证据2"]
        }},
        "mid_short_targets": {{
            "score": 分数,
            "reasoning": "评分理由",
            "evidence": ["证据1"]
        }},
        "emission_performance": {{
            "score": 分数,
            "reasoning": "评分理由",
            "evidence": ["证据1"]
        }},
        "disclosure": {{
            "score": 分数,
            "reasoning": "评分理由",
            "evidence": ["证据1"]
        }},
        "decarbonization_strategy": {{
            "score": 分数,
            "reasoning": "评分理由",
            "evidence": ["证据1"]
        }},
        "capital_allocation": {{
            "score": 分数,
            "reasoning": "评分理由",
            "evidence": ["证据1"]
        }}
    }},
    "overall_score": 加权平均分,
    "fit_level": "not_aligned/committed/partially_aligned/aligned/achieving",
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["劣势1", "劣势2"],
    "improvement_suggestions": ["建议1", "建议2"],
    "greenwashing_risk": true/false,
    "greenwashing_indicators": ["漂绿迹象1"],
    "key_findings": "关键发现总结"
}}"""

        try:
            response = self._call_api(prompt)
            result = self._parse_json_response(response)
            return result
        except Exception as e:
            return {
                'error': str(e),
                'scores': {},
                'overall_score': 0
            }
    
    def _call_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        if not self.api_key:
            raise ValueError("未配置DeepSeek API Key")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': '你是一个专业的ESG分析师助手，擅长搜索和分析企业ESG信息。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 4000
        }
        
        response = requests.post(
            f'{self.api_base}/chat/completions',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_json_response(self, response: str) -> Dict:
        """解析API返回的JSON"""
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取JSON部分
        try:
            # 查找JSON开始和结束位置
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass
        
        # 如果都失败，返回原始文本
        return {'raw_response': response}


# 全局实例
ai_search_engine = AISearchEngine()
