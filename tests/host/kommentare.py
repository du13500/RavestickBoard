"""Kommentare in C++ (.ino/.h) und web/index.html (CSS/JS/HTML) finden (fuer den Build-Test gegen Versionsmarken).
Liefert Liste (start, end, kind, text) mit Positionen im Gesamttext."""
import re, sys

def cpp_comments(s, start=0, end=None):
    end = len(s) if end is None else end
    i = start; out = []
    while i < end:
        c = s[i]
        if c == '/' and i + 1 < end and s[i+1] == '/':
            j = s.find('\n', i); j = end if j < 0 or j > end else j
            out.append((i, j, 'line', s[i:j])); i = j; continue
        if c == '/' and i + 1 < end and s[i+1] == '*':
            j = s.find('*/', i + 2); j = end if j < 0 else j + 2
            out.append((i, j, 'block', s[i:j])); i = j; continue
        if c == 'R' and s.startswith('R"', i) and (i == 0 or not (s[i-1].isalnum() or s[i-1] == '_')):
            k = s.find('(', i); delim = s[i+2:k]
            j = s.find(')' + delim + '"', k); i = j + len(delim) + 2; continue
        if c in '"\'':
            q = c; i += 1
            while i < end and s[i] != q:
                if s[i] == '\\': i += 1
                elif s[i] == '\n' and q == "'": break
                i += 1
            i += 1; continue
        i += 1
    return out

REGEX_PREV = set('(,=:[!&|?{};+-*%<>~^')
def js_comments(s, start, end):
    i = start; out = []; last = ''   # letztes signifikantes Zeichen
    lastword = ''
    while i < end:
        c = s[i]
        if c == '/' and s[i+1] == '/':
            j = s.find('\n', i); j = end if j < 0 or j > end else j
            out.append((i, j, 'line', s[i:j])); i = j; continue
        if c == '/' and s[i+1] == '*':
            j = s.find('*/', i + 2) + 2
            out.append((i, j, 'block', s[i:j])); i = j; continue
        if c == '/' and (last in REGEX_PREV or last == '' or lastword in ('return', 'typeof', 'case', 'of', 'in')):
            # Regex-Literal
            i += 1; incls = False
            while i < end:
                ch = s[i]
                if ch == '\\': i += 2; continue
                if ch == '[': incls = True
                elif ch == ']': incls = False
                elif ch == '/' and not incls: break
                elif ch == '\n': break
                i += 1
            i += 1
            while i < end and s[i].isalpha(): i += 1
            last = 'x'; lastword = ''; continue
        if c in '"\'':
            q = c; i += 1
            while i < end and s[i] != q:
                if s[i] == '\\': i += 1
                i += 1
            i += 1; last = 'x'; lastword = ''; continue
        if c == '`':
            i += 1; depth = 0
            while i < end:
                ch = s[i]
                if ch == '\\': i += 2; continue
                if ch == '`' and depth == 0: break
                if ch == '$' and s[i+1] == '{': depth += 1; i += 2; continue
                if ch == '}' and depth: depth -= 1
                i += 1
            i += 1; last = 'x'; lastword = ''; continue
        if c.isspace(): i += 1; continue
        if c.isalnum() or c in '_$':
            j = i
            while j < end and (s[j].isalnum() or s[j] in '_$'): j += 1
            lastword = s[i:j]; last = 'x' if lastword not in ('return','typeof','case') else '('; i = j; continue
        last = c; lastword = ''; i += 1
    return out

def css_comments(s, start, end):
    out = []; i = start
    while True:
        a = s.find('/*', i, end)
        if a < 0: break
        b = s.find('*/', a + 2) + 2
        out.append((a, b, 'block', s[a:b])); i = b
    return out

def html_comments(s):
    out = []
    for m in re.finditer(r'<!--.*?-->', s, re.S):
        out.append((m.start(), m.end(), 'html', m.group(0)))
    return out

def web_comments(s):
    out = []
    for m in re.finditer(r'<style[^>]*>(.*?)</style>', s, re.S):
        out += css_comments(s, m.start(1), m.end(1))
    for m in re.finditer(r'<script[^>]*>(.*?)</script>', s, re.S):
        out += js_comments(s, m.start(1), m.end(1))
    out += html_comments(s)
    return sorted(out)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        s = open(p, encoding='utf8').read()
        cs = web_comments(s) if p.endswith('.html') else cpp_comments(s)
        ver = [c for c in cs if re.search(r'\b0\.[1-9]\.\d+', c[3])]
        print(p, len(cs), 'Kommentare,', len(ver), 'mit Versionsnummer')
