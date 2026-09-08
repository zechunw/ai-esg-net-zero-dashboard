# -*- coding: utf-8 -*-
"""
ESG 评估引擎
基于AI的企业ESG净零契合度评估
"""

import json
import os
from datetime import datetime
from config import ESGDimensions, PromptTemplates, APIConfig


class EvaluationEngine:
    """ESG评估引擎"""
    
    def __init__(self):
        self.dimensions = ESGDimensions.DIMENSIONS
        self.fit_levels = ESGDimensions.FIT_LEVELS
        self.prompt_template = PromptTemplates.EVALUATION_PROMPT
        
        # 尝试初始化AI客户端
        self.ai_client = None
        self._init_ai_client()
        
        # 评估历史记录存储
        self.history_file = 'data/evaluation_history.json'
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _init_ai_client(self):
        """初始化AI客户端"""
        try:
            # 尝试使用OpenAI
            if APIConfig.OPENAI_API_KEY:
                from openai import OpenAI
                self.ai_client = OpenAI(api_key=APIConfig.OPENAI_API_KEY)
                self.ai_model = APIConfig.OPENAI_MODEL
        except Exception as e:
            print(f"AI客户端初始化警告: {e}")
            self.ai_client = None
    
    def evaluate(self, company_name, stock_code='', industry='', collected_data=None):
        """
        评估企业ESG表现
        
        Args:
            company_name: 公司名称
            stock_code: 股票代码
            industry: 行业
            collected_data: 采集到的ESG数据
            
        Returns:
            dict: 评估结果
        """
        if collected_data is None:
            collected_data = {}
        
        # 如果有AI客户端，使用AI评估
        if self.ai_client:
            evaluation = self._ai_evaluate(
                company_name, stock_code, industry, collected_data
            )
        else:
            # 使用规则引擎评估
            evaluation = self._rule_based_evaluate(
                company_name, stock_code, industry, collected_data
            )
        
        # 应用高影响力调整机制
        evaluation = self._apply_dynamic_adjustments(evaluation, collected_data)
        
        # 计算最终评分和契合度状态
        evaluation = self._calculate_final_status(evaluation)
        
        # 保存评估历史
        self._save_evaluation(company_name, evaluation)
        
        return evaluation
    
    def _ai_evaluate(self, company_name, stock_code, industry, collected_data):
        """使用AI进行评估"""
        try:
            # 构建提示词
            prompt = self.prompt_template.format(
                company_name=company_name,
                stock_code=stock_code or 'N/A',
                industry=industry or 'N/A',
                data=json.dumps(collected_data, ensure_ascii=False, indent=2)
            )
            
            # 调用AI
            response = self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的ESG分析师。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # 解析JSON结果
            # 尝试提取JSON部分
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                result_json = json.loads(result_text[json_start:json_end])
                return result_json
            else:
                raise ValueError("无法解析AI响应")
                
        except Exception as e:
            print(f"AI评估失败，回退到规则引擎: {e}")
            return self._rule_based_evaluate(
                company_name, stock_code, industry, collected_data
            )
    
    def _rule_based_evaluate(self, company_name, stock_code, industry, collected_data):
        """
        基于规则的企业ESG评估（备用方案）
        
        当AI服务不可用时，使用规则引擎进行基础评估
        """
        # 根据采集到的数据进行评分
        scores = {}
        
        # 1. 评估长期抱负
        net_zero = collected_data.get('net_zero_commitments', {})
        if net_zero.get('net_zero_target'):
            if net_zero.get('sbti_committed'):
                scores['long_term_aspiration'] = {
                    'score': 4.5,
                    'reasoning': '已承诺净零目标并加入SBTi',
                    'evidence': ['净零承诺', 'SBTi认证']
                }
            else:
                scores['long_term_aspiration'] = {
                    'score': 3.5,
                    'reasoning': '已有净零承诺',
                    'evidence': ['净零承诺']
                }
        else:
            scores['long_term_aspiration'] = {
                'score': 2.0,
                'reasoning': '暂无净零承诺或承诺不明确',
                'evidence': []
            }
        
        # 2. 评估中短期目标
        emissions = collected_data.get('emission_data', {})
        targets = emissions.get('reduction_targets', {})
        if targets.get('scope1_2_2030') and targets.get('scope3_2030'):
            scores['mid_short_targets'] = {
                'score': 4.0,
                'reasoning': '已设定涵盖范畴1、2、3的减排目标',
                'evidence': ['目标覆盖三大范畴']
            }
        elif targets.get('scope1_2_2030'):
            scores['mid_short_targets'] = {
                'score': 3.0,
                'reasoning': '仅有范畴1、2减排目标',
                'evidence': ['仅覆盖范畴1、2']
            }
        else:
            scores['mid_short_targets'] = {
                'score': 2.0,
                'reasoning': '缺少明确的短期减排目标',
                'evidence': []
            }
        
        # 3. 评估排放绩效
        scope1 = emissions.get('scope1_emissions', {})
        if scope1:
            years = sorted(scope1.keys())
            if len(years) >= 2:
                latest = scope1[years[-1]]['value']
                previous = scope1[years[-2]]['value']
                if latest < previous:
                    reduction = (previous - latest) / previous * 100
                    scores['emission_performance'] = {
                        'score': min(5.0, 3.0 + reduction / 10),
                        'reasoning': f'范畴1排放同比下降{reduction:.1f}%',
                        'evidence': [f'{years[-1]}年排放量下降']
                    }
                else:
                    scores['emission_performance'] = {
                        'score': 2.5,
                        'reasoning': '排放量未显示下降趋势',
                        'evidence': []
                    }
            else:
                scores['emission_performance'] = {
                    'score': 3.0,
                    'reasoning': '有排放数据但趋势不明',
                    'evidence': ['有数据披露']
                }
        else:
            scores['emission_performance'] = {
                'score': 1.5,
                'reasoning': '缺少排放数据',
                'evidence': []
            }
        
        # 4. 评估信息披露
        ratings = collected_data.get('ratings', {})
        disclosure_score = 3.0
        
        if ratings.get('msci', {}).get('rating'):
            disclosure_score += 0.5
        if ratings.get('sustainalytics', {}).get('risk_rating'):
            disclosure_score += 0.5
        if ratings.get('cdp', {}).get('score'):
            disclosure_score += 0.5
        
        scores['disclosure'] = {
            'score': min(5.0, disclosure_score),
            'reasoning': '信息披露较为完善',
            'evidence': ['有第三方评级']
        }
        
        # 5. 评估脱碳策略
        scores['decarbonization_strategy'] = {
            'score': 3.5,
            'reasoning': '脱碳策略框架已建立',
            'evidence': ['策略文件存在']
        }
        
        # 6. 评估资本配置
        capital = collected_data.get('capital_allocation', {})
        green_ratio = capital.get('低碳投资比例')
        
        if green_ratio:
            try:
                ratio_value = float(green_ratio.replace('%', ''))
                if ratio_value >= 30:
                    scores['capital_allocation'] = {
                        'score': 4.5,
                        'reasoning': f'绿色资本支出占比{green_ratio}',
                        'evidence': ['绿色投资较高']
                    }
                else:
                    scores['capital_allocation'] = {
                        'score': 3.0 + ratio_value / 30,
                        'reasoning': f'绿色资本支出占比{green_ratio}',
                        'evidence': []
                    }
            except:
                scores['capital_allocation'] = {
                    'score': 3.0,
                    'reasoning': '资本配置信息有限',
                    'evidence': []
                }
        else:
            scores['capital_allocation'] = {
                'score': 2.5,
                'reasoning': '缺少绿色资本配置数据',
                'evidence': []
            }
        
        # 计算总得分
        total_score = sum(s['score'] for s in scores.values()) / len(scores)
        
        return {
            'scores': scores,
            'overall_score': round(total_score, 2),
            'alignment_status': '',
            'strengths': [],
            'weaknesses': [],
            'improvement_suggestions': [],
            'greenwashing_risk': False,
            'greenwashing_indicators': []
        }
    
    def _apply_dynamic_adjustments(self, evaluation, collected_data):
        """
        应用AI动态定性调整（高影响力调整机制）
        
        检测企业"言行不一"的情况并调整评分
        """
        scores = evaluation.get('scores', {})
        
        # 检测漂绿风险
        greenwashing_indicators = collected_data.get('greenwashing_indicators', [])
        if greenwashing_indicators:
            # 降低相关维度评分
            if 'greenwashing_risk' not in evaluation:
                evaluation['greenwashing_risk'] = True
                evaluation['greenwashing_indicators'] = greenwashing_indicators
            
            # 降低脱碳策略评分
            if 'decarbonization_strategy' in scores:
                current = scores['decarbonization_strategy']['score']
                scores['decarbonization_strategy']['score'] = max(1.0, current - 0.5)
                scores['decarbonization_strategy']['reasoning'] += \
                    f' (存在漂绿风险)'
            
            # 降低资本配置评分
            if 'capital_allocation' in scores:
                current = scores['capital_allocation']['score']
                scores['capital_allocation']['score'] = max(1.0, current - 0.5)
                scores['capital_allocation']['reasoning'] += \
                    f' (存在漂绿风险)'
        
        # 检测减排承诺与实际行动不符
        net_zero = collected_data.get('net_zero_commitments', {})
        capital = collected_data.get('capital_allocation', {})
        
        if net_zero.get('net_zero_target'):
            green_ratio = capital.get('低碳投资比例')
            if green_ratio:
                try:
                    ratio = float(str(green_ratio).replace('%', ''))
                    # 承诺净零但绿色投资低于20%
                    if ratio < 20:
                        if 'decarbonization_strategy' in scores:
                            current = scores['decarbonization_strategy']['score']
                            scores['decarbonization_strategy']['score'] = max(1.0, current - 0.3)
                except:
                    pass
        
        evaluation['scores'] = scores
        return evaluation
    
    def _calculate_final_status(self, evaluation):
        """
        计算最终评分和契合度状态
        """
        scores = evaluation.get('scores', {})
        
        if not scores:
            return evaluation
        
        # 加权平均计算总得分
        total_weighted = 0
        total_weight = 0
        
        for dim_key, dim_info in self.dimensions.items():
            if dim_key in scores:
                score_data = scores[dim_key]
                weight = dim_info.get('weight', 1.0)
                total_weighted += score_data['score'] * weight
                total_weight += weight
        
        final_score = total_weighted / total_weight if total_weight > 0 else 0
        evaluation['overall_score'] = round(final_score, 2)
        
        # 确定契合度状态
        fit_level = 'partially_aligned'
        for level_key, level_info in self.fit_levels.items():
            min_score, max_score = level_info['score_range']
            if min_score <= final_score < max_score:
                fit_level = level_key
                break
        
        evaluation['fit_level'] = fit_level
        
        # 生成优劣势分析
        evaluation = self._generate_strengths_weaknesses(evaluation)
        
        return evaluation
    
    def _generate_strengths_weaknesses(self, evaluation):
        """
        生成优劣势分析和改进建议
        """
        scores = evaluation.get('scores', {})
        strengths = []
        weaknesses = []
        suggestions = []
        
        for dim_key, score_data in scores.items():
            dim_name = self.dimensions.get(dim_key, {}).get('name', dim_key)
            score = score_data['score']
            reasoning = score_data.get('reasoning', '')
            
            if score >= 4.0:
                strengths.append({
                    'dimension': dim_name,
                    'description': reasoning
                })
            elif score <= 2.5:
                weaknesses.append({
                    'dimension': dim_name,
                    'description': reasoning,
                    'score': score
                })
                # 生成改进建议
                suggestion = self._generate_suggestion(dim_key, score)
                if suggestion:
                    suggestions.append(suggestion)
        
        evaluation['strengths'] = strengths
        evaluation['weaknesses'] = weaknesses
        evaluation['improvement_suggestions'] = suggestions
        
        return evaluation
    
    def _generate_suggestion(self, dimension, score):
        """为特定维度生成改进建议"""
        suggestions = {
            'long_term_aspiration': '建议设定符合《巴黎协定》的净零目标，并考虑加入SBTi倡议',
            'mid_short_targets': '建议明确中短期减排目标，覆盖范畴1、2、3排放',
            'emission_performance': '建议加强排放监测与管理，制定年度减排计划',
            'disclosure': '建议遵循TCFD、GRI、IFRS S1/S2标准，提升信息披露透明度',
            'decarbonization_strategy': '建议完善转型路线图，增加可再生能源使用比例',
            'capital_allocation': '建议加大绿色资本支出，将投资向低碳技术倾斜'
        }
        
        if score <= 2.0:
            return suggestions.get(dimension, '建议全面提升该维度的ESG表现')
        return None
    
    def _save_evaluation(self, company_name, evaluation):
        """保存评估历史"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if company_name not in history:
                history[company_name] = []
            
            evaluation['timestamp'] = datetime.now().isoformat()
            history[company_name].append(evaluation)
            
            # 只保留最近10次评估
            if len(history[company_name]) > 10:
                history[company_name] = history[company_name][-10:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存评估历史失败: {e}")
    
    def get_evaluation_history(self, company_name):
        """获取企业评估历史"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history.get(company_name, [])
        except:
            return []
