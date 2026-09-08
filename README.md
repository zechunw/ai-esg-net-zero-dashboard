# ESG 评估系统 - 净零契合度诊断平台

## 项目概述

这是一个基于AI的ESG（环境、社会、治理）评估系统，结合路博迈（Neuberger Berman）的「净零契合度」方法论，提供动态、可视化的企业ESG评估服务。

### 核心功能

- **🔍 AI智能搜索** - 自动搜索公司信息，支持模糊匹配，智能识别公司名称
- **🤖 AI数据采集** - 自动搜集ESG报告、碳排放数据、ESG评级、相关新闻
- **📊 六维评估引擎** - 基于长期抱负、中短期目标、排放绩效、信息披露、脱碳策略、资本配置六大维度进行1-5分量化评分
- **⚠️ AI漂绿识别** - 自动识别"漂绿"行为并调整评分
- **📈 可视化看板** - 六维雷达图、契合度状态标签、优劣势深度解析
- **📚 数据来源透明** - 展示AI搜索过程和参考数据来源
- **💡 改进建议** - 转型偏离预警、具体改进路径建议
- **📄 报告导出** - PDF/Excel报告导出、同业基准对比

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5 + CSS3 + JavaScript
- **图表库**: ECharts
- **AI模型**: DeepSeek API (免费) / OpenAI GPT / Claude API

## 目录结构

```
ESG_Dashboard/
├── app.py                    # Flask应用主入口
├── config.py                 # 配置文件
├── ai_search_engine.py       # AI搜索引擎模块
├── data_collector.py         # 数据采集模块
├── evaluation_engine.py      # 评估引擎
├── report_generator.py       # 报告生成器
├── requirements.txt          # Python依赖
├── .env.example              # 环境变量配置模板
├── README.md
├── static/
│   ├── css/
│   │   └── style.css         # 样式文件
│   └── js/
│       ├── main.js           # 主逻辑
│       ├── chart.js          # 图表配置
│       └── api.js            # API调用
├── templates/
│   └── index.html            # 主页面
├── data/                     # 数据目录
├── reports/                  # 报告导出目录
├── docs/                     # 文档目录
├── 启动ESG系统.bat           # Windows启动脚本
└── 一键启动.bat              # 一键启动脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置AI API（推荐DeepSeek，免费额度充足）

1. 访问 [DeepSeek Platform](https://platform.deepseek.com/) 注册账号
2. 创建API Key
3. 用文本文档的方式打开 `.env`文件 并填入你的API Key：

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. 启动服务

**方式一：使用一键启动脚本（Windows）**
```bash
一键启动.bat
```

**方式二：命令行启动**
```bash
python app.py
```

访问 http://localhost:5000 查看应用

## AI功能使用说明

### 公司搜索
- 输入公司名称（支持模糊搜索）
- AI会自动验证公司是否存在
- 如果存在多个相似公司，会提示用户选择
- 如果不存在，会提示"公司不存在，请重新输入"

### AI搜索过程
- 评估时会实时显示AI的搜索进度
- 包括：公司信息搜索、ESG报告查找、碳排放数据搜索、新闻分析等步骤

### 数据来源
- 评估结果页面会显示AI参考的所有数据来源
- 包括ESG报告、新闻、评级机构等
- 点击链接可直接访问原始资料

## 开发团队

| 团队 | 职责 | 成员数 |
|------|------|--------|
| Task Force A | 数据与AI后端 | 2人 |
| Task Force B | 前端与可视化 | 2人 |
| Task Force C | 系统整合与敏捷管理 | 3人 |

## License

MIT License
