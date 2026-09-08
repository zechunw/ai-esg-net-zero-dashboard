# -*- coding: utf-8 -*-
"""修复 report_generator.py 中的严重错误"""
filepath = r'd:/Documents/留学/Cityu/IS5542 Gen ai for business/Group Project/ESG_Dashboard/report_generator.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到并修复错误的行
fixed = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 修复1：删除 score_table.style.add(...) 这一行
    if 'score_table.style.add(' in line:
        print(f"删除无效行 {i+1}: {line.strip()}")
        i += 1
        continue
    
    # 修复2：在 TableStyle 列表中添加 WORDWRAP
    # 找到 ('ROWBACKGROUNDS', ...) 这一行，在其后添加 WORDWRAP
    if "('ROWBACKGROUNDS'" in line and 'score_table' in ''.join(lines[max(0,i-5):i+1]):
        fixed.append(line)
        # 下一行应该是 ]))，我们在 ])) 之前添加 WORDWRAP
        if i+1 < len(lines) and ']))' in lines[i+1]:
            indent = ' ' * (len(line) - len(line.lstrip()) + 4)
            fixed.append(f"{indent}('WORDWRAP', (0, 1), (-1, -1)),\n")
            print(f"添加 WORDWRAP 到第 {i+1} 行")
    else:
        fixed.append(line)
    
    i += 1

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(fixed)

print("\n✅ 修复完成！")
print("请重启 Flask 服务后重试。")
