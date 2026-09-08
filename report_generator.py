# -*- coding: utf-8 -*-
"""
ESG 报告生成模块
支持PDF和Excel格式的报告导出
"""

import os
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from xml.sax.saxutils import escape as html_escape
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import RadarChart, Reference


# 注册中文字体（使用CID字体，无需外部字体文件）
try:
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    CHINESE_FONT = 'STSong-Light'
    print("成功加载CID中文字体: STSong-Light")
except Exception as e:
    print(f"CID字体加载失败: {e}，尝试其他方案...")
    try:
        # 尝试使用系统字体（Windows）
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        font_path = 'C:/Windows/Fonts/simsun.ttc'
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('SimSun', font_path))
            CHINESE_FONT = 'SimSun'
            print("成功加载系统字体: SimSun")
        else:
            CHINESE_FONT = 'Helvetica'
            print("警告: 未找到中文字体，使用 Helvetica（中文可能无法显示）")
    except Exception as e2:
        print(f"字体加载失败: {e2}")
        CHINESE_FONT = 'Helvetica'


class ReportGenerator:
    """ESG报告生成器"""
    
    def __init__(self):
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_pdf(self, company_name, evaluation_data):
        """
        生成PDF格式的评估报告
        
        Args:
            company_name: 公司名称
            evaluation_data: 评估数据
            
        Returns:
            str: 生成的PDF文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{company_name}_ESG_Report_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # 获取样式
        styles = getSampleStyleSheet()
        
        # 自定义样式（使用中文字体）
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=CHINESE_FONT,
            fontSize=24,
            spaceAfter=30,
            alignment=1  # 居中
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=CHINESE_FONT,
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#1a5f7a')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=CHINESE_FONT,
            fontSize=10,
            spaceAfter=6
        )
        
        # 构建文档内容
        story = []
        
        # 标题
        story.append(Paragraph(html_escape("ESG 净零契合度评估报告"), title_style))
        story.append(Paragraph(f"<b>企业名称：</b>{html_escape(company_name)}", normal_style))
        story.append(Paragraph(f"<b>评估日期：</b>{datetime.now().strftime('%Y年%m月%d日')}", normal_style))
        story.append(Spacer(1, 20))
        
        # 总体评分
        overall_score = evaluation_data.get('overall_score', 0)
        fit_level = evaluation_data.get('fit_level', 'partially_aligned')
        fit_status_map = {
            'not_aligned': '不契合',
            'committed': '承诺契合',
            'partially_aligned': '部分契合',
            'aligned': '契合净零路径',
            'achieving': '正在达成净零'
        }
        
        story.append(Paragraph("一、总体评估", heading_style))
        
        summary_data = [
            ['综合评分', f'{overall_score:.2f} / 5.00'],
            ['契合度状态', fit_status_map.get(fit_level, '部分契合')],
            ['漂绿风险', '是' if evaluation_data.get('greenwashing_risk') else '否']
        ]
        
        summary_table = Table(summary_data, colWidths=[100, 300])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), CHINESE_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(summary_table)
        
        # 维度评分
        story.append(Paragraph("二、六维评估详情", heading_style))
        
        scores = evaluation_data.get('scores', {})
        dimension_names = {
            'long_term_aspiration': '长期抱负',
            'mid_short_targets': '中短期目标',
            'emission_performance': '排放绩效',
            'disclosure': '信息披露',
            'decarbonization_strategy': '脱碳策略',
            'capital_allocation': '资本配置'
        }
        
        score_data = [['评估维度', '评分', '评分理由']]
        for dim_key, dim_name in dimension_names.items():
            if dim_key in scores:
                score_info = scores[dim_key]
                score_data.append([
                    dim_name,
                    f"{score_info['score']:.1f} / 5.0",
                    html_escape(score_info.get('reasoning', '')[:50])
                ])
        
        score_table = Table(score_data, colWidths=[80, 60, 260])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5f7a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), CHINESE_FONT),
            ('FONTNAME', (0, 1), (-1, -1), CHINESE_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        # 启用自动换行
        story.append(score_table)
        
        # 优势分析
        story.append(Paragraph("三、优势分析", heading_style))
        strengths = evaluation_data.get('strengths', [])
        if strengths:
            for s in strengths[:3]:
                # 支持两种格式：字符串 或 {dimension, description}
                if isinstance(s, dict):
                    story.append(Paragraph(f"<b>{html_escape(s.get('dimension', ''))}</b>：{html_escape(s.get('description', ''))}", normal_style))
                else:
                    story.append(Paragraph(html_escape(str(s)), normal_style))
        else:
            story.append(Paragraph("暂无明显优势", normal_style))
        
        # 劣势分析
        story.append(Paragraph("四、劣势分析", heading_style))
        weaknesses = evaluation_data.get('weaknesses', [])
        if weaknesses:
            for w in weaknesses[:3]:
                # 支持两种格式：字符串 或 {dimension, description}
                if isinstance(w, dict):
                    story.append(Paragraph(f"<b>{html_escape(w.get('dimension', ''))}</b>：{html_escape(w.get('description', ''))}", normal_style))
                else:
                    story.append(Paragraph(html_escape(str(w)), normal_style))
        else:
            story.append(Paragraph("暂无明显劣势", normal_style))
        
        # 改进建议
        story.append(Paragraph("五、改进建议", heading_style))
        suggestions = evaluation_data.get('improvement_suggestions', [])
        if suggestions:
            for i, s in enumerate(suggestions[:5], 1):
                story.append(Paragraph(f"{i}. {html_escape(s)}", normal_style))
        else:
            story.append(Paragraph("当前表现良好，建议继续保持", normal_style))
        
        # 页脚
        story.append(Spacer(1, 30))
        footer_text = Paragraph(
            f"<i>本报告由ESG净零契合度评估系统自动生成 | 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
        )
        story.append(footer_text)
        
        # 生成PDF
        doc.build(story)
        
        return filepath
    
    def generate_excel(self, company_name, evaluation_data):
        """
        生成Excel格式的评估报告
        
        Args:
            company_name: 公司名称
            evaluation_data: 评估数据
            
        Returns:
            str: 生成的Excel文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{company_name}_ESG_Report_{timestamp}.xlsx"
        filepath = os.path.join(self.reports_dir, filename)
        
        # 创建工作簿
        wb = Workbook()
        
        # 样式定义
        header_fill = PatternFill(start_color="1a5f7a", end_color="1a5f7a", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        title_font = Font(size=16, bold=True)
        subtitle_font = Font(size=12, bold=True)
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Sheet 1: 总览
        ws1 = wb.active
        ws1.title = "评估总览"
        
        # 标题
        ws1.merge_cells('A1:D1')
        ws1['A1'] = f"ESG净零契合度评估报告 - {company_name}"
        ws1['A1'].font = title_font
        ws1['A1'].alignment = Alignment(horizontal='center')
        
        # 基本信息
        ws1['A3'] = '企业名称'
        ws1['B3'] = company_name
        ws1['A4'] = '评估日期'
        ws1['B4'] = datetime.now().strftime('%Y-%m-%d')
        ws1['A5'] = '综合评分'
        ws1['B5'] = f"{evaluation_data.get('overall_score', 0):.2f} / 5.00"
        ws1['A6'] = '契合度状态'
        
        fit_level = evaluation_data.get('fit_level', 'partially_aligned')
        fit_status_map = {
            'not_aligned': '不契合',
            'committed': '承诺契合',
            'partially_aligned': '部分契合',
            'aligned': '契合净零路径',
            'achieving': '正在达成净零'
        }
        ws1['B6'] = fit_status_map.get(fit_level, '部分契合')
        ws1['A7'] = '漂绿风险'
        ws1['B7'] = '是' if evaluation_data.get('greenwashing_risk') else '否'
        
        for row in range(3, 8):
            ws1[f'A{row}'].font = subtitle_font
            ws1[f'A{row}'].fill = PatternFill(start_color="f0f0f0", end_color="f0f0f0", fill_type="solid")
            ws1[f'A{row}'].border = thin_border
            ws1[f'B{row}'].border = thin_border
        
        # Sheet 2: 维度评分
        ws2 = wb.create_sheet("维度评分")
        
        scores = evaluation_data.get('scores', {})
        dimension_names = {
            'long_term_aspiration': '长期抱负',
            'mid_short_targets': '中短期目标',
            'emission_performance': '排放绩效',
            'disclosure': '信息披露',
            'decarbonization_strategy': '脱碳策略',
            'capital_allocation': '资本配置'
        }
        
        # 表头
        headers = ['评估维度', '评分', '评分理由', '证据']
        for col, header in enumerate(headers, 1):
            cell = ws2.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center')
        
        # 数据
        row_num = 2
        for dim_key, dim_name in dimension_names.items():
            if dim_key in scores:
                score_info = scores[dim_key]
                ws2.cell(row=row_num, column=1, value=dim_name).border = thin_border
                ws2.cell(row=row_num, column=2, value=score_info['score']).border = thin_border
                ws2.cell(row=row_num, column=3, value=score_info.get('reasoning', '')).border = thin_border
                ws2.cell(row=row_num, column=4, value=', '.join(score_info.get('evidence', []))).border = thin_border
                row_num += 1
        
        # 设置列宽
        ws2.column_dimensions['A'].width = 20
        ws2.column_dimensions['B'].width = 10
        ws2.column_dimensions['C'].width = 50
        ws2.column_dimensions['D'].width = 30
        
        # Sheet 3: 优劣势分析
        ws3 = wb.create_sheet("优劣势分析")
        
        ws3['A1'] = '优势分析'
        ws3['A1'].font = subtitle_font
        ws3['A2'] = '维度'
        ws3['B2'] = '描述'
        ws3['A2'].font = header_font
        ws3['A2'].fill = header_fill
        ws3['B2'].font = header_font
        ws3['B2'].fill = header_fill
        
        strengths = evaluation_data.get('strengths', [])
        row_num = 3
        for s in strengths:
            # 支持两种格式：字符串 或 {dimension, description}
            if isinstance(s, dict):
                ws3.cell(row=row_num, column=1, value=s.get('dimension', '')).border = thin_border
                ws3.cell(row=row_num, column=2, value=s.get('description', '')).border = thin_border
            else:
                ws3.cell(row=row_num, column=1, value=str(s)).border = thin_border
                ws3.cell(row=row_num, column=2, value='').border = thin_border
            row_num += 1
        
        row_num += 2
        ws3.cell(row=row_num, column=1, value='劣势分析').font = subtitle_font
        row_num += 1
        ws3.cell(row=row_num, column=1, value='维度').font = header_font
        ws3.cell(row=row_num, column=1).fill = header_fill
        ws3.cell(row=row_num, column=2, value='描述').font = header_font
        ws3.cell(row=row_num, column=2).fill = header_fill
        
        row_num += 1
        weaknesses = evaluation_data.get('weaknesses', [])
        for w in weaknesses:
            # 支持两种格式：字符串 或 {dimension, description}
            if isinstance(w, dict):
                ws3.cell(row=row_num, column=1, value=w.get('dimension', '')).border = thin_border
                ws3.cell(row=row_num, column=2, value=w.get('description', '')).border = thin_border
            else:
                ws3.cell(row=row_num, column=1, value=str(w)).border = thin_border
                ws3.cell(row=row_num, column=2, value='').border = thin_border
            row_num += 1
        
        # Sheet 4: 改进建议
        ws4 = wb.create_sheet("改进建议")
        
        ws4['A1'] = '序号'
        ws4['B1'] = '改进建议'
        ws4['A1'].font = header_font
        ws4['A1'].fill = header_fill
        ws4['B1'].font = header_font
        ws4['B1'].fill = header_fill
        
        suggestions = evaluation_data.get('improvement_suggestions', [])
        for i, suggestion in enumerate(suggestions, 1):
            ws4.cell(row=i+1, column=1, value=i).border = thin_border
            ws4.cell(row=i+1, column=2, value=suggestion).border = thin_border
        
        ws4.column_dimensions['A'].width = 10
        ws4.column_dimensions['B'].width = 60
        
        # 保存文件
        wb.save(filepath)
        
        return filepath
