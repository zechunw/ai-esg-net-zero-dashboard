/**
 * ESG Dashboard - 图表模块
 * 使用ECharts渲染各种图表
 */

let radarChart = null;
let benchmarkChart = null;
let historyChart = null;

// 维度中文名称映射
const dimensionNames = {
    'long_term_aspiration': '长期抱负',
    'mid_short_targets': '中短期目标',
    'emission_performance': '排放绩效',
    'disclosure': '信息披露',
    'decarbonization_strategy': '脱碳策略',
    'capital_allocation': '资本配置'
};

// 维度英文名称映射
const dimensionNamesEn = {
    'long_term_aspiration': 'Long-term Aspiration',
    'mid_short_targets': 'Mid-short Targets',
    'emission_performance': 'Emission Performance',
    'disclosure': 'Disclosure',
    'decarbonization_strategy': 'Decarbonization Strategy',
    'capital_allocation': 'Capital Allocation'
};

// 初始化雷达图
function initRadarChart(dimensions, scores, benchmark = null) {
    const chartDom = document.getElementById('radarChart');
    if (!chartDom) return;
    
    if (radarChart) {
        radarChart.dispose();
    }
    
    radarChart = echarts.init(chartDom);
    
    // 构建指标数据
    const indicator = Object.keys(dimensions).map(key => ({
        name: dimensionNames[key] || key,
        max: 5
    }));
    
    // 企业评分数据
    const companyData = Object.values(scores).map(s => typeof s === 'object' ? s.score : s);
    
    // 系列数据
    const series = [{
        value: companyData,
        name: '企业评分',
        areaStyle: {
            color: 'rgba(26, 95, 122, 0.3)'
        },
        lineStyle: {
            color: '#1a5f7a',
            width: 3
        },
        itemStyle: {
            color: '#1a5f7a'
        }
    }];
    
    // 如果有基准数据，添加基准系列
    if (benchmark && benchmark.dimension_averages) {
        const benchmarkData = Object.keys(dimensions).map(key => {
            return benchmark.dimension_averages[key] || 3;
        });
        series.push({
            value: benchmarkData,
            name: '行业平均',
            areaStyle: {
                color: 'rgba(87, 197, 182, 0.3)'
            },
            lineStyle: {
                color: '#57c5b6',
                width: 2,
                type: 'dashed'
            },
            itemStyle: {
                color: '#57c5b6'
            }
        });
    }
    
    const option = {
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e0e0e0',
            borderWidth: 1,
            textStyle: {
                color: '#333'
            },
            formatter: function(params) {
                let result = `<strong>${params.name}</strong><br/>`;
                params.value.forEach((value, index) => {
                    const dimName = Object.values(dimensionNames)[index];
                    result += `${dimName}: ${value.toFixed(1)}<br/>`;
                });
                return result;
            }
        },
        legend: {
            data: series.map(s => s.name),
            bottom: 10,
            textStyle: {
                color: '#666'
            }
        },
        radar: {
            indicator: indicator,
            center: ['50%', '50%'],
            radius: '65%',
            splitNumber: 5,
            axisName: {
                color: '#333',
                fontSize: 13,
                fontWeight: 'bold'
            },
            splitLine: {
                lineStyle: {
                    color: '#e0e0e0'
                }
            },
            splitArea: {
                areaStyle: {
                    color: ['#f8f9fa', '#ffffff']
                }
            },
            axisLine: {
                lineStyle: {
                    color: '#e0e0e0'
                }
            }
        },
        series: [{
            type: 'radar',
            data: series
        }]
    };
    
    radarChart.setOption(option);
    
    // 响应式
    window.addEventListener('resize', () => {
        if (radarChart) {
            radarChart.resize();
        }
    });
}

// 初始化行业对比图表
function initBenchmarkChart(dimensions, companyScores, benchmark) {
    const chartDom = document.getElementById('benchmarkChart');
    if (!chartDom) return;
    
    if (benchmarkChart) {
        benchmarkChart.dispose();
    }
    
    benchmarkChart = echarts.init(chartDom);
    
    const categories = Object.keys(dimensions).map(key => dimensionNames[key]);
    const companyData = Object.values(companyScores).map(s => typeof s === 'object' ? s.score : s);
    const benchmarkData = Object.keys(dimensions).map(key => {
        return benchmark.dimension_averages[key] || 3;
    });
    
    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['企业评分', '行业平均'],
            bottom: 10
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            top: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: categories,
            axisLabel: {
                interval: 0,
                rotate: 0,
                fontSize: 11
            }
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 5,
            axisLabel: {
                formatter: '{value} 分'
            }
        },
        series: [
            {
                name: '企业评分',
                type: 'bar',
                data: companyData,
                itemStyle: {
                    color: '#1a5f7a',
                    borderRadius: [4, 4, 0, 0]
                },
                barWidth: '35%'
            },
            {
                name: '行业平均',
                type: 'bar',
                data: benchmarkData,
                itemStyle: {
                    color: '#57c5b6',
                    borderRadius: [4, 4, 0, 0]
                },
                barWidth: '35%'
            }
        ]
    };
    
    benchmarkChart.setOption(option);
    
    window.addEventListener('resize', () => {
        if (benchmarkChart) {
            benchmarkChart.resize();
        }
    });
}

// 初始化历史趋势图表
function initHistoryChart(historyData) {
    const chartDom = document.getElementById('historyChart');
    if (!chartDom) return;
    
    if (historyChart) {
        historyChart.dispose();
    }
    
    if (!historyData || historyData.length === 0) {
        chartDom.innerHTML = '<p style="text-align: center; color: #666;">暂无历史数据</p>';
        return;
    }
    
    historyChart = echarts.init(chartDom);
    
    // 提取日期和评分
    const dates = historyData.map(h => {
        const date = new Date(h.timestamp);
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    });
    const scores = historyData.map(h => h.overall_score);
    
    const option = {
        tooltip: {
            trigger: 'axis'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            top: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: dates,
            boundaryGap: false
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 5,
            axisLabel: {
                formatter: '{value} 分'
            }
        },
        series: [{
            name: 'ESG评分',
            type: 'line',
            data: scores,
            smooth: true,
            areaStyle: {
                color: 'rgba(26, 95, 122, 0.3)'
            },
            lineStyle: {
                color: '#1a5f7a',
                width: 3
            },
            itemStyle: {
                color: '#1a5f7a'
            },
            markPoint: {
                data: [
                    { type: 'max', name: '最高分' },
                    { type: 'min', name: '最低分' }
                ]
            }
        }]
    };
    
    historyChart.setOption(option);
    
    window.addEventListener('resize', () => {
        if (historyChart) {
            historyChart.resize();
        }
    });
}

// 更新契合度状态环形图
function updateStatusRing(overallScore, fitLevel) {
    const ring = document.getElementById('statusRing');
    if (!ring) return;
    
    // 根据评分计算百分比
    const percentage = (overallScore / 5) * 100;
    
    // 根据契合度状态设置颜色
    const colors = {
        'not_aligned': '#d32f2f',
        'committed': '#f57c00',
        'partially_aligned': '#fbc02d',
        'aligned': '#388e3c',
        'achieving': '#1976d2'
    };
    
    const color = colors[fitLevel] || colors['partially_aligned'];
    
    ring.style.borderColor = color;
    ring.style.borderTopColor = `${color}33`;
    ring.style.borderRightColor = `${color}33`;
    ring.style.borderBottomColor = `${color}33`;
    
    // 添加动画效果
    ring.style.transition = 'border-color 0.5s ease';
    
    // 动画效果
    let currentAngle = 0;
    const animate = () => {
        currentAngle += 2;
        ring.style.transform = `rotate(${currentAngle}deg)`;
        if (currentAngle < percentage * 3.6) {
            requestAnimationFrame(animate);
        }
    };
    
    // 重置并开始动画
    ring.style.transform = 'rotate(0deg)';
    setTimeout(animate, 100);
}
