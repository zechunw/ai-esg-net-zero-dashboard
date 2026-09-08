# ESG 评估系统 - API 文档

## 基础信息

- **Base URL**: `http://localhost:5000`
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## API 端点

### 1. 健康检查

**端点**: `GET /health`

检查服务是否正常运行。

**响应示例**:
```json
{
    "status": "healthy",
    "service": "ESG Dashboard API",
    "version": "1.0.0"
}
```

---

### 2. 企业ESG评估

**端点**: `POST /api/evaluate`

评估企业的ESG表现。

**请求体**:
```json
{
    "company_name": "公司名称",
    "stock_code": "股票代码(可选)",
    "industry": "行业ID",
    "data_source": "auto|manual",
    "esg_data": { }  // 仅当data_source为manual时需要
}
```

**行业ID列表**:
- `financial` - 金融业
- `technology` - 科技业
- `manufacturing` - 制造业
- `energy` - 能源业
- `consumer` - 消费品业
- `healthcare` - 医疗健康
- `real_estate` - 房地产
- `transportation` - 交通运输

**手动数据格式**:
```json
{
    "net_zero_commitments": {
        "net_zero_target": true,
        "target_year": 2050,
        "sbti_committed": true
    },
    "emission_data": {
        "scope1_emissions": {"2023": {"value": 100, "unit": "ktCO2e"}},
        "scope2_emissions": {"2023": {"value": 80, "unit": "ktCO2e"}}
    },
    "capital_allocation": {
        "低碳投资比例": "30%"
    }
}
```

**响应示例**:
```json
{
    "success": true,
    "company": {
        "name": "示例公司",
        "stock_code": "1234",
        "industry": "technology"
    },
    "evaluation": {
        "scores": {
            "long_term_aspiration": {
                "score": 4.5,
                "reasoning": "已承诺净零目标并加入SBTi",
                "evidence": ["净零承诺", "SBTi认证"]
            },
            "mid_short_targets": {
                "score": 4.0,
                "reasoning": "已设定涵盖范畴1、2、3的减排目标",
                "evidence": []
            },
            "emission_performance": {
                "score": 3.5,
                "reasoning": "排放量持续下降",
                "evidence": []
            },
            "disclosure": {
                "score": 4.0,
                "reasoning": "信息披露完善",
                "evidence": []
            },
            "decarbonization_strategy": {
                "score": 3.5,
                "reasoning": "脱碳策略框架已建立",
                "evidence": []
            },
            "capital_allocation": {
                "score": 4.0,
                "reasoning": "绿色资本支出占比较高",
                "evidence": []
            }
        },
        "overall_score": 3.92,
        "fit_level": "aligned",
        "strengths": [
            {"dimension": "长期抱负", "description": "已承诺净零目标并加入SBTi"}
        ],
        "weaknesses": [
            {"dimension": "排放绩效", "description": "排放量持续下降", "score": 3.5}
        ],
        "improvement_suggestions": [
            "建议加强排放监测与管理"
        ],
        "greenwashing_risk": false,
        "greenwashing_indicators": []
    },
    "fit_status": {
        "name": "契合净零路径",
        "name_en": "Aligned",
        "color": "#388e3c",
        "icon": "O"
    },
    "collected_data": {}
}
```

**契合度状态说明**:
| 状态 | 分值范围 | 颜色 |
|------|---------|------|
| 不契合 | 0-1.5 | #d32f2f |
| 承诺契合 | 1.5-2.5 | #f57c00 |
| 部分契合 | 2.5-3.5 | #fbc02d |
| 契合净零路径 | 3.5-4.5 | #388e3c |
| 正在达成净零 | 4.5-5.0 | #1976d2 |

---

### 3. 行业基准对比

**端点**: `POST /api/benchmark`

获取行业基准数据。

**请求体**:
```json
{
    "industry": "technology"
}
```

**响应示例**:
```json
{
    "success": true,
    "benchmark": {
        "name": "科技业",
        "avg_score": 3.5,
        "dimension_averages": {
            "long_term_aspiration": 3.8,
            "mid_short_targets": 3.5,
            "emission_performance": 3.2,
            "disclosure": 3.7,
            "decarbonization_strategy": 3.6,
            "capital_allocation": 3.4
        }
    }
}
```

---

### 4. 评估历史记录

**端点**: `GET /api/history?company_name=公司名称`

获取企业的历史评估记录。

**查询参数**:
- `company_name` (必填): 公司名称

**响应示例**:
```json
{
    "success": true,
    "history": [
        {
            "overall_score": 3.8,
            "fit_level": "aligned",
            "timestamp": "2026-04-25T10:30:00"
        },
        {
            "overall_score": 3.6,
            "fit_level": "aligned",
            "timestamp": "2026-04-20T14:20:00"
        }
    ]
}
```

---

### 5. 导出报告

**端点**: `POST /api/export`

导出评估报告。

**请求体**:
```json
{
    "company_name": "公司名称",
    "format": "pdf|excel",
    "evaluation_data": {
        "scores": {},
        "overall_score": 3.92,
        "fit_level": "aligned",
        "strengths": [],
        "weaknesses": [],
        "improvement_suggestions": []
    }
}
```

**响应示例**:
```json
{
    "success": true,
    "download_url": "/download/公司名称_ESG_Report_20260425_103000.pdf"
}
```

---

### 6. 行业列表

**端点**: `GET /api/industries`

获取支持的行业列表。

**响应示例**:
```json
{
    "success": true,
    "industries": [
        {"id": "financial", "name": "金融业", "name_en": "Financial Services"},
        {"id": "technology", "name": "科技业", "name_en": "Technology"},
        {"id": "manufacturing", "name": "制造业", "name_en": "Manufacturing"},
        {"id": "energy", "name": "能源业", "name_en": "Energy"},
        {"id": "consumer", "name": "消费品业", "name_en": "Consumer Goods"},
        {"id": "healthcare", "name": "医疗健康", "name_en": "Healthcare"},
        {"id": "real_estate", "name": "房地产", "name_en": "Real Estate"},
        {"id": "transportation", "name": "交通运输", "name_en": "Transportation"}
    ]
}
```

---

### 7. 评估维度定义

**端点**: `GET /api/dimensions`

获取评估维度定义和契合度等级说明。

**响应示例**:
```json
{
    "success": true,
    "dimensions": {
        "long_term_aspiration": {
            "name": "长期抱负",
            "name_en": "Long-term Aspiration",
            "description": "是否有符合《巴黎协定》的长期净零目标",
            "weight": 1.2,
            "indicators": ["净零承诺年份", "与1.5°C路径一致性", "SBTi认证状态"]
        }
        // ... 其他维度
    },
    "fit_levels": {
        "not_aligned": {
            "name": "不契合",
            "name_en": "Not Aligned",
            "score_range": [0, 1.5],
            "color": "#d32f2f",
            "icon": "X"
        }
        // ... 其他状态
    }
}
```

---

## 错误响应

所有API在出错时返回以下格式：

```json
{
    "success": false,
    "error": "错误描述信息"
}
```

**HTTP状态码**:
- `200` - 请求成功
- `400` - 请求参数错误
- `500` - 服务器内部错误

---

## 调用示例

### cURL
```bash
# 企业评估
curl -X POST http://localhost:5000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Apple", "industry": "technology"}'

# 导出PDF报告
curl -X POST http://localhost:5000/api/export \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Apple", "format": "pdf", "evaluation_data": {}}'
```

### Python
```python
import requests

# 企业评估
response = requests.post('http://localhost:5000/api/evaluate', json={
    'company_name': 'Apple',
    'industry': 'technology'
})
result = response.json()
print(result)
```

### JavaScript
```javascript
// 企业评估
fetch('/api/evaluate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        company_name: 'Apple',
        industry: 'technology'
    })
})
.then(res => res.json())
.then(data => console.log(data));
```
