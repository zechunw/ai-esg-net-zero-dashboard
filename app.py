# -*- coding: utf-8 -*-
"""
ESG 评估系统 - Flask应用主入口
IS5542 Group Project - ESG Dashboard
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from config import AppConfig, ESGDimensions
from data_collector import DataCollector
from evaluation_engine import EvaluationEngine
from report_generator import ReportGenerator
from ai_search_engine import ai_search_engine

# 初始化Flask应用
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.logger.setLevel(logging.DEBUG)
CORS(app)

# 初始化组件
data_collector = DataCollector()
evaluation_engine = EvaluationEngine()
report_generator = ReportGenerator()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/search_company', methods=['POST'])
def search_company():
    """
    搜索公司信息（支持模糊匹配）
    
    请求体:
    {
        "query": "用户输入的公司名称"
    }
    
    响应:
    {
        "success": true/false,
        "status": "success/not_found/multiple_matches/error",
        "company": {...},  // 匹配到的公司信息
        "candidates": [...],  // 多个候选时返回
        "message": "提示信息"
    }
    """
    try:
        # 强制解析JSON
        data = request.get_json(force=True, silent=True)
        logger.debug(f"搜索公司请求数据: {data}")
        logger.debug(f"请求头 Content-Type: {request.content_type}")
        logger.debug(f"请求方法: {request.method}")
        logger.debug(f"请求路径: {request.path}")
        
        if data is None:
            # 尝试从表单数据获取
            data = request.form.to_dict() or request.args.to_dict()
            logger.debug(f"从表单/参数获取数据: {data}")
        
        if not data:
            logger.error("无法解析请求数据")
            return jsonify({
                'success': False,
                'status': 'error',
                'message': '无法解析请求数据'
            }), 400
        
        # 支持 query 或 company_name 字段
        query = data.get('query', '').strip() or data.get('company_name', '').strip()
        logger.debug(f"提取的公司名称: '{query}'")
        
        if not query:
            return jsonify({
                'success': False,
                'status': 'error',
                'message': '请输入公司名称'
            }), 400
        
        # 使用AI搜索引擎搜索公司
        logger.debug(f"开始调用AI搜索引擎: {query}")
        result = ai_search_engine.search_company(query)
        logger.debug(f"AI搜索引擎返回: {result}")
        
        return jsonify({
            'success': result['status'] == 'success',
            'status': result['status'],
            'company': result.get('company'),
            'candidates': result.get('candidates'),
            'message': result.get('message', '')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'message': f'搜索出错: {str(e)}'
        }), 500


@app.route('/api/evaluate_ai', methods=['POST'])
def evaluate_company_ai():
    """
    使用AI进行企业ESG评估（包含搜索过程）
    
    请求体:
    {
        "company_name": "准确的公司名称",
        "industry": "行业"
    }
    
    响应:
    {
        "success": true/false,
        "search_process": [...],  // AI搜索过程
        "data_sources": [...],     // 数据来源
        "company": {...},
        "evaluation": {...},
        "fit_status": {...}
    }
    """
    try:
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        industry = data.get('industry', '')
        
        if not company_name:
            return jsonify({
                'success': False,
                'error': '公司名称不能为空'
            }), 400
        
        # 步骤1: AI搜索ESG信息
        search_result = ai_search_engine.search_esg_info(company_name)
        
        # 步骤2: AI评估
        evaluation = ai_search_engine.evaluate_esg(
            company_name=company_name,
            esg_data=search_result['esg_data']
        )
        
        # 步骤3: 确定契合度状态
        fit_level = evaluation.get('fit_level', 'partially_aligned')
        fit_status = ESGDimensions.FIT_LEVELS.get(
            fit_level,
            ESGDimensions.FIT_LEVELS['partially_aligned']
        )
        
        return jsonify({
            'success': True,
            'search_process': search_result['search_process'],
            'data_sources': search_result['data_sources'],
            'company': {
                'name': company_name,
                'industry': industry
            },
            'evaluation': evaluation,
            'fit_status': {
                'name': fit_status['name'],
                'name_en': fit_status['name_en'],
                'color': fit_status['color'],
                'icon': fit_status['icon']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/evaluate', methods=['POST'])
def evaluate_company():
    """
    评估企业ESG表现（传统方式，使用本地规则引擎）
    
    请求体:
    {
        "company_name": "公司名称",
        "stock_code": "股票代码",
        "industry": "行业",
        "data_source": "manual|auto"  // 手动输入数据或自动采集
    }
    """
    try:
        data = request.get_json()
        
        company_name = data.get('company_name', '')
        stock_code = data.get('stock_code', '')
        industry = data.get('industry', '')
        data_source = data.get('data_source', 'auto')
        
        if not company_name:
            return jsonify({
                'success': False,
                'error': '公司名称不能为空'
            }), 400
        
        # 步骤1: 收集数据
        if data_source == 'auto':
            collected_data = data_collector.collect(company_name, stock_code, industry)
        else:
            # 使用用户提供的ESG数据
            collected_data = data.get('esg_data', {})
        
        # 步骤2: AI评估
        evaluation = evaluation_engine.evaluate(
            company_name=company_name,
            stock_code=stock_code,
            industry=industry,
            collected_data=collected_data
        )
        
        # 步骤3: 确定契合度状态
        fit_status = ESGDimensions.FIT_LEVELS.get(
            evaluation.get('fit_level', 'partially_aligned'),
            ESGDimensions.FIT_LEVELS['partially_aligned']
        )
        
        return jsonify({
            'success': True,
            'company': {
                'name': company_name,
                'stock_code': stock_code,
                'industry': industry
            },
            'evaluation': evaluation,
            'fit_status': {
                'name': fit_status['name'],
                'name_en': fit_status['name_en'],
                'color': fit_status['color'],
                'icon': fit_status['icon']
            },
            'collected_data': collected_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/benchmark', methods=['POST'])
def get_benchmark():
    """
    获取行业基准对比数据
    
    请求体:
    {
        "industry": "行业"
    }
    """
    try:
        data = request.get_json()
        industry = data.get('industry', '')
        
        benchmark = data_collector.get_industry_benchmark(industry)
        
        return jsonify({
            'success': True,
            'benchmark': benchmark
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """
    获取企业历史评估记录
    
    查询参数:
    - company_name: 公司名称
    """
    try:
        company_name = request.args.get('company_name', '')
        
        if not company_name:
            return jsonify({
                'success': False,
                'error': '公司名称不能为空'
            }), 400
        
        history = evaluation_engine.get_evaluation_history(company_name)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export', methods=['POST'])
def export_report():
    """
    导出评估报告
    
    请求体:
    {
        "company_name": "公司名称",
        "format": "pdf|excel",
        "evaluation_data": {...}  // 评估数据
    }
    """
    try:
        data = request.get_json()
        logger.debug(f"导出请求数据: {data}")
        
        company_name = data.get('company_name', '')
        export_format = data.get('format', 'pdf')
        evaluation_data = data.get('evaluation_data', {})
        
        logger.debug(f"导出格式: {export_format}, 公司: {company_name}")
        logger.debug(f"评估数据: {evaluation_data}")
        
        if export_format == 'pdf':
            file_path = report_generator.generate_pdf(company_name, evaluation_data)
        else:
            file_path = report_generator.generate_excel(company_name, evaluation_data)
        
        logger.debug(f"生成文件: {file_path}")
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{os.path.basename(file_path)}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/industries', methods=['GET'])
def get_industries():
    """获取支持的行业列表"""
    industries = [
        {'id': 'financial', 'name': '金融业', 'name_en': 'Financial Services'},
        {'id': 'technology', 'name': '科技业', 'name_en': 'Technology'},
        {'id': 'manufacturing', 'name': '制造业', 'name_en': 'Manufacturing'},
        {'id': 'energy', 'name': '能源业', 'name_en': 'Energy'},
        {'id': 'consumer', 'name': '消费品业', 'name_en': 'Consumer Goods'},
        {'id': 'healthcare', 'name': '医疗健康', 'name_en': 'Healthcare'},
        {'id': 'real_estate', 'name': '房地产', 'name_en': 'Real Estate'},
        {'id': 'transportation', 'name': '交通运输', 'name_en': 'Transportation'}
    ]
    
    return jsonify({
        'success': True,
        'industries': industries
    })


@app.route('/api/dimensions', methods=['GET'])
def get_dimensions():
    """获取评估维度定义"""
    return jsonify({
        'success': True,
        'dimensions': ESGDimensions.DIMENSIONS,
        'fit_levels': ESGDimensions.FIT_LEVELS
    })


# ==================== 静态文件路由 ====================

@app.route('/download/<filename>')
def download_file(filename):
    """下载报告文件"""
    from flask import send_from_directory
    
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    return send_from_directory(reports_dir, filename, as_attachment=True)


# ==================== 健康检查 ====================

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'ESG Dashboard API',
        'version': '1.0.0'
    })


# ==================== 启动应用 ====================

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('reports', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("=" * 60)
    print("ESG 评估系统启动中...")
    print(f"访问地址: http://{AppConfig.HOST}:{AppConfig.PORT}")
    print("=" * 60)
    
    app.run(
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        debug=AppConfig.DEBUG
    )
