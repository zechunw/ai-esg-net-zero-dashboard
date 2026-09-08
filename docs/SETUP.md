# ESG 评估系统 - 安装与部署指南

## 环境要求

- Python 3.8+
- pip 包管理器
- 网络连接（用于下载依赖）

## 快速开始

### 1. 克隆或下载项目

```bash
cd ESG_Dashboard
```

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件：

```bash
# OpenAI API配置
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4

# 应用配置
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

**获取OpenAI API Key**:
1. 访问 https://platform.openai.com/api-keys
2. 登录或注册账号
3. 创建新的API Key
4. 复制并添加到 `.env` 文件

### 5. 启动应用

```bash
python app.py
```

### 6. 访问应用

打开浏览器访问: http://localhost:5000

## 项目结构

```
ESG_Dashboard/
├── app.py                    # Flask应用入口
├── config.py                 # 配置文件
├── requirements.txt         # Python依赖
├── data_collector.py         # 数据采集模块
├── evaluation_engine.py      # AI评估引擎
├── report_generator.py      # 报告生成模块
├── static/
│   ├── css/
│   │   └── style.css         # 样式文件
│   └── js/
│       ├── main.js           # 主逻辑
│       ├── chart.js          # 图表模块
│       └── api.js           # API调用
├── templates/
│   └── index.html            # 主页面
├── data/
│   └── evaluation_history.json
├── reports/                  # 导出的报告
├── docs/
│   ├── PRD.md               # 产品需求文档
│   ├── API.md               # API文档
│   └── SETUP.md             # 本文档
└── .env                     # 环境变量（需创建）
```

## 功能使用

### 基础评估

1. 输入公司名称
2. 选择行业
3. 点击"开始评估"
4. 查看评估结果

### 手动输入数据

1. 勾选"手动输入ESG数据"
2. 填写ESG相关信息
3. 点击"开始评估"

### 导出报告

1. 完成评估后
2. 点击"导出PDF报告"或"导出Excel"
3. 报告将自动下载

### 行业对比

1. 完成评估后
2. 点击"行业对比"
3. 查看与行业平均水平的对比

## Docker 部署（可选）

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t esg-dashboard .

# 运行容器
docker run -d -p 5000:5000 --env-file .env esg-dashboard
```

## 常见问题

### 1. 依赖安装失败

确保Python版本 >= 3.8：

```bash
python --version
```

### 2. AI评估失败

- 检查网络连接
- 确认API Key正确配置
- 查看控制台错误信息

### 3. 端口被占用

修改 `config.py` 中的端口：

```python
class AppConfig:
    PORT = 5001  # 改为其他端口
```

### 4. 报告无法导出

确保 `reports/` 目录存在且有写入权限：

```bash
mkdir -p reports
chmod 755 reports
```

## 开发指南

### 运行测试

```bash
# 单元测试
pytest tests/

# 特定模块测试
python -m pytest tests/test_evaluation_engine.py -v
```

### 代码规范

遵循 PEP 8 编码规范：

```bash
# 代码格式化
black .

# 代码检查
flake8 .
```

## 技术支持

如有问题，请联系开发团队或提交Issue。

---

**文档版本**: v1.0  
**最后更新**: 2026-04-25
