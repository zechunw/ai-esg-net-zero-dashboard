/**
 * ESG Dashboard - 主逻辑模块
 */

// 全局变量
let currentEvaluation = null;
let dimensions = null;

// DOM元素
const evaluateBtn = document.getElementById('evaluateBtn');
const companyNameInput = document.getElementById('companyName');
const industrySelect = document.getElementById('industry');
const manualModeCheckbox = document.getElementById('manualMode');
const manualInputSection = document.getElementById('manualInputSection');
const loadingSection = document.getElementById('loadingSection');
const resultSection = document.getElementById('resultSection');

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 加载维度定义
    try {
        const result = await getDimensions();
        dimensions = result.dimensions;
    } catch (error) {
        console.error('加载维度定义失败:', error);
    }
    
    // 绑定事件
    bindEvents();
});

// 绑定事件
function bindEvents() {
    // 评估按钮
    if (evaluateBtn) {
        evaluateBtn.addEventListener('click', handleEvaluate);
    }
    
    // 输入框回车事件
    if (companyNameInput) {
        companyNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleEvaluate();
            }
        });
    }
    
    // 手动模式切换
    if (manualModeCheckbox) {
        manualModeCheckbox.addEventListener('change', () => {
            if (manualInputSection) {
                if (manualModeCheckbox.checked) {
                    manualInputSection.classList.remove('hidden');
                } else {
                    manualInputSection.classList.add('hidden');
                }
            }
        });
    }
}

// 处理评估请求
async function handleEvaluate() {
    const companyName = companyNameInput.value.trim();
    const industry = industrySelect.value;
    
    console.log('handleEvaluate - 公司名称:', companyName);
    console.log('handleEvaluate - 输入框元素:', companyNameInput);
    
    if (!companyName) {
        alert('请输入公司名称');
        companyNameInput.focus();
        return;
    }
    
    // 手动模式直接进行评估
    if (manualModeCheckbox.checked) {
        await performManualEvaluation(companyName, industry);
        return;
    }
    
    // AI模式：先搜索公司
    showLoading(true);
    updateLoadingStep('正在验证公司信息...');
    
    try {
        // 第一步：搜索公司
        const searchResult = await searchCompany(companyName);
        console.log('搜索结果:', searchResult);
        
        // 处理错误状态
        if (searchResult.status === 'error' || !searchResult.success) {
            showLoading(false);
            alert('❌ 搜索出错: ' + (searchResult.message || '未知错误'));
            return;
        }
        
        if (searchResult.status === 'not_found') {
            showLoading(false);
            alert('❌ 公司不存在，请重新输入\n\n未找到与 "' + companyName + '" 匹配的公司。请检查公司名称是否正确。');
            return;
        }
        
        if (searchResult.status === 'multiple_matches') {
            showLoading(false);
            showCompanySelectModal(searchResult.candidates);
            return;
        }
        
        // 公司确认成功，进行AI评估
        if (searchResult.status === 'success' && searchResult.company) {
            const confirmedCompany = searchResult.company;
            console.log('确认的公司信息:', confirmedCompany);
            await performAIEvaluation(confirmedCompany.name, confirmedCompany.stock_code || '', industry);
        } else {
            showLoading(false);
            alert('❌ 无法识别的搜索状态: ' + searchResult.status);
        }
        
    } catch (error) {
        console.error('搜索失败:', error);
        showLoading(false);
        alert(`搜索失败: ${error.message}`);
    }
}

// 执行AI评估
async function performAIEvaluation(companyName, stockCode, industry) {
    showLoading(true);
    showSearchProcess(true);
    
    try {
        // 模拟搜索步骤展示
        const searchSteps = [
            { step: 1, text: '正在搜索公司基本信息...', time: 500 },
            { step: 2, text: '正在查找ESG报告和可持续发展报告...', time: 1000 },
            { step: 3, text: '正在搜索碳排放和气候相关新闻...', time: 1500 },
            { step: 4, text: '正在分析资本配置和绿色投资信息...', time: 2000 },
            { step: 5, text: '正在使用AI进行ESG评分...', time: 3000 }
        ];
        
        // 展示搜索步骤
        for (const step of searchSteps) {
            await new Promise(resolve => setTimeout(resolve, step.time));
            addSearchStep(step.step, step.text);
        }
        
        // 调用AI评估API
        const result = await evaluateCompanyAI(companyName, stockCode, industry);
        
        currentEvaluation = result;
        
        // 渲染结果
        renderResults(result);
        
        // 显示数据源
        if (result.data_sources && result.data_sources.length > 0) {
            renderDataSources(result.data_sources);
        }
        
    } catch (error) {
        console.error('AI评估失败:', error);
        alert(`AI评估失败: ${error.message}`);
    } finally {
        showLoading(false);
        showSearchProcess(false);
    }
}

// 执行手动评估
async function performManualEvaluation(companyName, industry) {
    showLoading(true);
    
    try {
        const manualData = collectManualData();
        
        const result = await evaluateCompany(
            companyName,
            '',
            industry,
            'manual',
            manualData
        );
        
        currentEvaluation = result;
        renderResults(result);
        
    } catch (error) {
        console.error('评估失败:', error);
        alert(`评估失败: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// 显示/隐藏搜索过程
function showSearchProcess(show) {
    const section = document.getElementById('searchProcessSection');
    if (section) {
        if (show) {
            section.classList.remove('hidden');
            document.getElementById('searchSteps').innerHTML = '';
        } else {
            section.classList.add('hidden');
        }
    }
}

// 添加搜索步骤
function addSearchStep(stepNumber, text) {
    const container = document.getElementById('searchSteps');
    if (!container) return;
    
    const stepDiv = document.createElement('div');
    stepDiv.className = 'search-step-item';
    stepDiv.innerHTML = `
        <span class="step-number">${stepNumber}</span>
        <span class="step-text">${text}</span>
        <span class="step-status">✓</span>
    `;
    container.appendChild(stepDiv);
    
    // 自动滚动到底部
    container.scrollTop = container.scrollHeight;
}

// 更新加载步骤文字
function updateLoadingStep(text) {
    const el = document.getElementById('loadingStep');
    if (el) {
        el.textContent = text;
    }
}

// 显示公司选择模态框
function showCompanySelectModal(candidates) {
    const modal = document.getElementById('companySelectModal');
    const optionsContainer = document.getElementById('companyOptions');
    
    if (!modal || !optionsContainer) return;
    
    optionsContainer.innerHTML = '';
    
    candidates.forEach(company => {
        const btn = document.createElement('button');
        btn.className = 'company-option-btn';
        btn.innerHTML = `
            <div class="company-name">${company.name}</div>
            <div class="company-info">
                ${company.stock_code ? `股票代码: ${company.stock_code} | ` : ''}
                相似度: ${(company.confidence * 100).toFixed(0)}%
            </div>
        `;
        btn.onclick = () => {
            closeCompanySelectModal();
            companyNameInput.value = company.name;
            performAIEvaluation(company.name, company.stock_code || '', industrySelect.value);
        };
        optionsContainer.appendChild(btn);
    });
    
    modal.classList.remove('hidden');
}

// 关闭公司选择模态框
function closeCompanySelectModal() {
    const modal = document.getElementById('companySelectModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// 渲染数据源
function renderDataSources(sources) {
    const section = document.getElementById('dataSourcesSection');
    const list = document.getElementById('dataSourcesList');
    
    if (!section || !list) return;
    
    list.innerHTML = '';
    
    sources.forEach(source => {
        const item = document.createElement('div');
        item.className = 'data-source-item';
        
        // 兼容两种格式：name/title, url/link
        const sourceName = source.name || source.title || '未知来源';
        const sourceUrl = source.url || source.link || '#';
        const sourceType = source.type || '其他';
        const sourceDate = source.date || source.pub_date || '';
        
        if (sourceUrl && sourceUrl !== '#') {
            item.innerHTML = `
                <a href="${sourceUrl}" target="_blank" class="source-link">
                    <span class="source-type">${sourceType}</span>
                    <span class="source-title">${sourceName}</span>
                    <span class="source-date">${sourceDate}</span>
                </a>
            `;
        } else {
            item.innerHTML = `
                <span class="source-type">${sourceType}</span>
                <span class="source-title">${sourceName}</span>
                <span class="source-date">${sourceDate}</span>
            `;
        }
        
        list.appendChild(item);
    });
    
    section.classList.remove('hidden');
}

// 收集手动输入的数据
function collectManualData() {
    return {
        net_zero_commitments: {
            net_zero_target: document.getElementById('netZeroYear').value ? true : false,
            target_year: parseInt(document.getElementById('netZeroYear').value) || null,
            sbti_committed: document.getElementById('sbtiCertified').value === 'true'
        },
        emission_data: {
            scope1_emissions: {
                '2023': {
                    value: parseFloat(document.getElementById('scope1Emissions').value) || 0,
                    unit: '吨CO2e'
                }
            },
            scope2_emissions: {
                '2023': {
                    value: parseFloat(document.getElementById('scope2Emissions').value) || 0,
                    unit: '吨CO2e'
                }
            },
            reduction_targets: {
                scope1_2_2030: document.getElementById('reductionTargets').value
            }
        },
        capital_allocation: {
            '低碳投资比例': (parseFloat(document.getElementById('greenCapex').value) || 0) + '%'
        },
        green_revenue: {
            '绿色收入占比': (parseFloat(document.getElementById('greenRevenue').value) || 0) + '%'
        }
    };
}

// 显示/隐藏加载状态
function showLoading(show) {
    if (loadingSection) {
        if (show) {
            loadingSection.classList.remove('hidden');
            resultSection.classList.add('hidden');
        } else {
            loadingSection.classList.add('hidden');
        }
    }
}

// 渲染评估结果
function renderResults(result) {
    console.log('渲染评估结果:', result);
    
    resultSection.classList.remove('hidden');
    
    const { company, evaluation, fit_status } = result;
    
    console.log('公司:', company);
    console.log('评估:', evaluation);
    console.log('契合度状态:', fit_status);
    
    // 更新公司信息
    document.getElementById('companyTitle').textContent = company?.name || '未知公司';
    document.getElementById('industryTag').textContent = company?.industry || '未指定行业';
    
    // 更新总体评分
    document.getElementById('overallScore').textContent = evaluation.overall_score.toFixed(2);
    updateStatusRing(evaluation.overall_score, evaluation.fit_level);
    
    // 更新契合度状态
    document.getElementById('statusLabel').textContent = fit_status.name;
    document.getElementById('statusLabel').style.color = fit_status.color;
    document.getElementById('statusDescription').textContent = getFitDescription(evaluation.fit_level);
    
    // 更新漂绿风险标识
    const riskBadge = document.getElementById('greenwashingBadge');
    if (evaluation.greenwashing_risk) {
        riskBadge.classList.remove('safe');
        riskBadge.innerHTML = '<span class="badge-icon">⚠️</span><span class="badge-text">漂绿风险: 有</span>';
    } else {
        riskBadge.classList.add('safe');
        riskBadge.innerHTML = '<span class="badge-icon">✅</span><span class="badge-text">漂绿风险: 无</span>';
    }
    
    // 渲染雷达图
    if (dimensions) {
        initRadarChart(dimensions, evaluation.scores);
    }
    
    // 渲染维度详情表格
    renderDimensionTable(evaluation.scores);
    
    // 渲染优劣势分析
    console.log('优势:', evaluation?.strengths);
    console.log('劣势:', evaluation?.weaknesses);
    renderStrengthsWeaknesses(evaluation?.strengths || [], evaluation?.weaknesses || []);
    
    // 渲染改进建议
    console.log('改进建议:', evaluation?.improvement_suggestions);
    renderSuggestions(evaluation?.improvement_suggestions || []);
    
    // 加载历史数据
    loadHistory(company.name);
}

// 获取契合度描述
function getFitDescription(fitLevel) {
    const descriptions = {
        'not_aligned': '该企业的ESG表现与净零路径严重偏离，需要立即采取行动进行改进。',
        'committed': '该企业已做出净零承诺，但实际行动尚不明确，需要持续跟进。',
        'partially_aligned': '该企业部分契合净零路径，在某些维度表现良好，但仍有提升空间。',
        'aligned': '该企业整体契合净零路径，表现良好，继续保持当前策略。',
        'achieving': '该企业正在积极达成净零目标，表现优秀，是行业的领导者。'
    };
    return descriptions[fitLevel] || descriptions['partially_aligned'];
}

// 渲染维度详情表格
function renderDimensionTable(scores) {
    const tbody = document.getElementById('dimensionTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const dimensionNames = {
        'long_term_aspiration': '长期抱负',
        'mid_short_targets': '中短期目标',
        'emission_performance': '排放绩效',
        'disclosure': '信息披露',
        'decarbonization_strategy': '脱碳策略',
        'capital_allocation': '资本配置'
    };
    
    for (const [key, data] of Object.entries(scores)) {
        const row = document.createElement('tr');
        
        const score = typeof data === 'object' ? data.score : data;
        const reasoning = typeof data === 'object' ? data.reasoning : '';
        
        // 根据分数设置颜色
        let scoreColor = '#333';
        if (score >= 4.0) scoreColor = '#388e3c';
        else if (score >= 3.0) scoreColor = '#1a5f7a';
        else if (score <= 2.0) scoreColor = '#d32f2f';
        
        row.innerHTML = `
            <td>${dimensionNames[key] || key}</td>
            <td style="color: ${scoreColor}; font-weight: bold;">${score.toFixed(1)} / 5.0</td>
            <td>${reasoning}</td>
        `;
        
        tbody.appendChild(row);
    }
}

// 渲染优劣势分析
function renderStrengthsWeaknesses(strengths, weaknesses) {
    const strengthsList = document.getElementById('strengthsList');
    const weaknessesList = document.getElementById('weaknessesList');
    
    // 渲染优势
    if (strengthsList) {
        strengthsList.innerHTML = '';
        if (strengths && strengths.length > 0) {
            strengths.forEach(s => {
                const li = document.createElement('li');
                // 处理两种格式：字符串 或 对象{dimension, description}
                if (typeof s === 'string') {
                    li.textContent = s;
                } else {
                    li.innerHTML = `<strong>${s.dimension || ''}</strong>: ${s.description || ''}`;
                }
                strengthsList.appendChild(li);
            });
        } else {
            strengthsList.innerHTML = '<li>暂无明显优势</li>';
        }
    }
    
    // 渲染劣势
    if (weaknessesList) {
        weaknessesList.innerHTML = '';
        if (weaknesses && weaknesses.length > 0) {
            weaknesses.forEach(w => {
                const li = document.createElement('li');
                // 处理两种格式：字符串 或 对象{dimension, description}
                if (typeof w === 'string') {
                    li.textContent = w;
                } else {
                    li.innerHTML = `<strong>${w.dimension || ''}</strong>: ${w.description || ''}`;
                }
                weaknessesList.appendChild(li);
            });
        } else {
            weaknessesList.innerHTML = '<li>暂无明显劣势</li>';
        }
    }
}

// 渲染改进建议
function renderSuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestionsList');
    if (!suggestionsList) return;
    
    suggestionsList.innerHTML = '';
    
    if (suggestions && suggestions.length > 0) {
        suggestions.forEach(s => {
            const li = document.createElement('li');
            li.textContent = s;
            suggestionsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = '当前表现良好，建议继续保持';
        suggestionsList.appendChild(li);
    }
}

// 加载历史数据
async function loadHistory(companyName) {
    try {
        const history = await getEvaluationHistory(companyName);
        
        const historySection = document.getElementById('historySection');
        if (history && history.length > 1) {
            historySection.classList.remove('hidden');
            initHistoryChart(history);
        } else {
            historySection.classList.add('hidden');
        }
    } catch (error) {
        console.error('加载历史数据失败:', error);
    }
}

// 导出报告
async function downloadReport(format) {
    if (!currentEvaluation) {
        alert('请先进行评估');
        return;
    }
    
    try {
        const result = await exportReport(
            currentEvaluation.company.name,
            currentEvaluation.evaluation,
            format
        );
        
        alert(`${format.toUpperCase()} 报告已生成，开始下载`);
    } catch (error) {
        alert(`导出失败: ${error.message}`);
    }
}

// 行业对比
async function compareWithIndustry() {
    if (!currentEvaluation || !currentEvaluation.company.industry) {
        alert('请先进行评估并选择行业');
        return;
    }
    
    try {
        const benchmark = await getIndustryBenchmark(currentEvaluation.company.industry);
        
        // 初始化对比图表
        if (dimensions && currentEvaluation.evaluation.scores) {
            initBenchmarkChart(dimensions, currentEvaluation.evaluation.scores, benchmark);
        }
        
        // 生成对比摘要
        const summary = generateBenchmarkSummary(currentEvaluation.evaluation.scores, benchmark);
        document.getElementById('benchmarkSummary').innerHTML = summary;
        
        // 显示模态框
        document.getElementById('benchmarkModal').classList.remove('hidden');
        
    } catch (error) {
        console.error('行业对比失败:', error);
        alert(`行业对比失败: ${error.message}`);
    }
}

// 生成基准对比摘要
function generateBenchmarkSummary(scores, benchmark) {
    let html = '<h4>对比分析</h4><ul>';
    
    // 计算总体差异
    let totalScore = 0;
    let totalAvg = 0;
    let count = 0;
    
    for (const [key, data] of Object.entries(scores)) {
        const score = typeof data === 'object' ? data.score : data;
        const avgScore = benchmark.dimension_averages[key] || 3;
        totalScore += score;
        totalAvg += avgScore;
        count++;
        const diff = score - avgScore;
        
        const dimensionNames = {
            'long_term_aspiration': '长期抱负',
            'mid_short_targets': '中短期目标',
            'emission_performance': '排放绩效',
            'disclosure': '信息披露',
            'decarbonization_strategy': '脱碳策略',
            'capital_allocation': '资本配置'
        };
        
        let statusIcon = '';
        let statusClass = '';
        
        if (diff > 0.5) {
            statusIcon = '⬆️';
            statusClass = 'style="color: #388e3c;"';
        } else if (diff < -0.5) {
            statusIcon = '⬇️';
            statusClass = 'style="color: #d32f2f;"';
        } else {
            statusIcon = '➡️';
            statusClass = 'style="color: #f57c00;"';
        }
        
        html += `<li ${statusClass}>
            <strong>${dimensionNames[key] || key}</strong>: 
            您的企业 ${score.toFixed(1)} vs 行业平均 ${avgScore.toFixed(1)} 
            ${statusIcon} ${diff > 0 ? '+' : ''}${diff.toFixed(1)}
        </li>`;
    }
    
    html += '</ul>';
    
    // 总体评价
    const overallScore = count > 0 ? totalScore / count : 0;
    const overallAvg = count > 0 ? totalAvg / count : 0;
    const overallDiff = overallScore - overallAvg;
    
    if (overallDiff > 0.5) {
        html += '<p style="margin-top: 16px; color: #388e3c;">✅ 您的企业ESG表现在行业中处于领先水平</p>';
    } else if (overallDiff < -0.5) {
        html += '<p style="margin-top: 16px; color: #d32f2f;">⚠️ 您的企业ESG表现在行业中需要提升</p>';
    } else {
        html += '<p style="margin-top: 16px; color: #1a5f7a;">📊 您的企业ESG表现在行业中处于平均水平</p>';
    }
    
    return html;
}

// 关闭行业对比模态框
function closeBenchmarkModal() {
    document.getElementById('benchmarkModal').classList.add('hidden');
}

// 点击模态框外部关闭
document.getElementById('benchmarkModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'benchmarkModal') {
        closeBenchmarkModal();
    }
});
