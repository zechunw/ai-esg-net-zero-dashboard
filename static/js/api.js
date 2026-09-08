/**
 * ESG Dashboard - API 模块
 * 处理所有与后端的API通信
 */

const API_BASE_URL = '';

// 评估API
async function evaluateCompany(companyName, stockCode, industry, dataSource = 'auto', manualData = null) {
    const loadingSteps = [
        '正在采集企业数据...',
        '正在分析ESG报告...',
        '正在评估碳排放绩效...',
        '正在生成评估报告...'
    ];
    
    let stepIndex = 0;
    const loadingStepEl = document.getElementById('loadingStep');
    const stepInterval = setInterval(() => {
        stepIndex = (stepIndex + 1) % loadingSteps.length;
        if (loadingStepEl) {
            loadingStepEl.textContent = loadingSteps[stepIndex];
        }
    }, 1500);
    
    try {
        const requestData = {
            company_name: companyName,
            stock_code: stockCode,
            industry: industry,
            data_source: dataSource
        };
        
        if (dataSource === 'manual' && manualData) {
            requestData.esg_data = manualData;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        clearInterval(stepInterval);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '评估失败');
        }
        
        return result;
        
    } catch (error) {
        clearInterval(stepInterval);
        console.error('评估请求失败:', error);
        throw error;
    }
}

// 获取行业基准数据
async function getIndustryBenchmark(industry) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/benchmark`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ industry: industry })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '获取基准数据失败');
        }
        
        return result.benchmark;
        
    } catch (error) {
        console.error('获取行业基准失败:', error);
        throw error;
    }
}

// 获取评估历史
async function getEvaluationHistory(companyName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/history?company_name=${encodeURIComponent(companyName)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '获取历史记录失败');
        }
        
        return result.history;
        
    } catch (error) {
        console.error('获取历史记录失败:', error);
        return [];
    }
}

// 导出报告
async function exportReport(companyName, evaluationData, format) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                company_name: companyName,
                format: format,
                evaluation_data: evaluationData
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '导出失败');
        }
        
        // 下载文件
        window.location.href = result.download_url;
        
        return result;
        
    } catch (error) {
        console.error('导出报告失败:', error);
        throw error;
    }
}

// 获取行业列表
async function getIndustries() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/industries`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '获取行业列表失败');
        }
        
        return result.industries;
        
    } catch (error) {
        console.error('获取行业列表失败:', error);
        throw error;
    }
}

// 获取评估维度定义
async function getDimensions() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dimensions`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '获取维度定义失败');
        }
        
        return {
            dimensions: result.dimensions,
            fit_levels: result.fit_levels
        };
        
    } catch (error) {
        console.error('获取维度定义失败:', error);
        throw error;
    }
}

// AI搜索公司
async function searchCompany(companyName) {
    try {
        console.log('搜索公司:', companyName, '类型:', typeof companyName);
        
        // 确保 companyName 是字符串且不为空
        if (!companyName || typeof companyName !== 'string') {
            throw new Error('公司名称无效');
        }
        
        const requestBody = { company_name: companyName.trim() };
        console.log('请求体:', JSON.stringify(requestBody));
        
        const response = await fetch(`${API_BASE_URL}/api/search_company`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('搜索API错误:', response.status, errorData);
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('搜索结果:', result);
        return result;
        
    } catch (error) {
        console.error('搜索公司失败:', error);
        throw error;
    }
}

// AI评估公司
async function evaluateCompanyAI(companyName, stockCode, industry, onProgress = null) {
    try {
        console.log('AI评估公司:', companyName, stockCode, industry);
        
        const response = await fetch(`${API_BASE_URL}/api/evaluate_ai`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                company_name: companyName,
                stock_code: stockCode,
                industry: industry
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('评估API错误:', response.status, errorData);
            throw new Error(errorData.error || errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '评估失败');
        }
        
        return result;
        
    } catch (error) {
        console.error('AI评估失败:', error);
        throw error;
    }
}
