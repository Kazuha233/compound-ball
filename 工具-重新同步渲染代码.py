# -*- coding: utf-8 -*-
"""重新同步「球堆放编辑器.html」里的球体渲染代码（从游戏 index.html 抽取）
   用法：游戏球体外观改动后，双击/运行本脚本即可让编辑器跟上。
"""
import io, os, re, subprocess, sys

GAME = r'D:\R\Desktop\合成球球(B站)\index.html'
TOOL = r'D:\R\Desktop\合成球球(B站)\工具-球堆放编辑器.html'
BEGIN = '/* ===== 以下渲染代码由构建脚本从游戏 index.html 原样抽取 ===== */'
END = '/* ===== 抽取结束 ===== */'

s = io.open(GAME, encoding='utf-8').read()

def fn_block(name):
    """先配平参数括号，再取函数体（避免把默认参数 source={} 当函数体）"""
    i = s.index('function ' + name + '(')
    k = s.index('(', i); depth = 0
    while True:
        c = s[k]
        if c == '(': depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0: break
        k += 1
    b = s.index('{', k); depth = 0; j = b
    while True:
        c = s[j]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    return s[i:j+1]

def balanced_const(marker):
    """取 const <name>= {...}; （内含嵌套大括号）"""
    i = s.index(marker)
    b = s.index('{', i + len(marker)); depth = 0; k = b
    while True:
        c = s[k]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
        k += 1
    return marker + s[b:k+1] + ';'

parts = []
parts.append(re.search(r'const\s+BALL_TYPES\s*=\s*\[.*?\];', s, re.S).group(0))
m = re.search(r'const\s+radiusFor\s*=\s*([A-Za-z_$][\w$]*)\s*=>\s*([^;]+);', s)
parts.append('const radiusFor=%s=>%s;' % (m.group(1), m.group(2).strip()))
parts.append(balanced_const('const DEFAULT_CUSTOMIZATIONS='))
for name in ['withDefaultCustomizations', 'shade', 'mixColor', 'drawBall', 'ballName']:
    parts.append(fn_block(name))
extracted = '\n'.join(parts)

t = io.open(TOOL, encoding='utf-8').read()
assert t.count(BEGIN) == 1 and t.count(END) == 1, '编辑器里的抽取标记异常'
head, rest = t.split(BEGIN, 1)
_, tail = rest.split(END, 1)
new = head + BEGIN + '\n' + extracted + '\n' + END + tail

js = re.search(r'<script>(.*?)</script>', new, re.S).group(1)
tmp = os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'resync_check.js')
io.open(tmp, 'w', encoding='utf-8').write(js)
code = subprocess.run(['node', '--check', tmp], capture_output=True, text=True).returncode
if code != 0:
    print('❌ 语法检查失败，未写入'); sys.exit(1)

if new == t:
    print('✅ 已是最新（渲染代码与游戏一致，未改动）')
else:
    io.open(TOOL, 'w', encoding='utf-8').write(new)
    print('✅ 已同步渲染代码：%d 字符 → 编辑器 %.0f KB' % (len(extracted), len(new.encode('utf-8')) / 1024))
