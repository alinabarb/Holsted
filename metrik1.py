from collections import Counter
import re
from math import log2
def parsecpp(code):#функция, которая парсит код
    #счетчики
    operators = Counter()#арифметичесие знаки, присваивание, ключевые слова, разелители, имена функций и скобки(пара скобок считается за один операнд)
    operands = Counter()#переменные, константы и строки
    #удаление комментариев и директив
    code=re.sub(r'//.*', '', code)
    code=re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code=re.sub(r'#.*', '', code)

    #считает количество операндов
    string = re.findall(r'".*?"|\'.*?\'', code)
    for s in string:
        operands[s]+=1
    code = re.sub(r'".*?"|\'.*?\'','', code)

    nums = re.findall(r'\b\d+(?:\.\d+)?\b', code)
    for n in nums:
        operands[n]+=1
    code = re.sub(r'\b\d+(?:\.\d+)?\b','', code)

    skobki_keywords = ['for', 'while', 'if', 'switch', 'catch']
    kolvo_skobok = 0
    for kw in skobki_keywords:
        matches = re.findall(r'\b'+kw+r'\b', code)
        count = len(matches)
        if count>0:
            operators[kw]+=count
            kolvo_skobok+=count

            code = re.sub(r'\b'+kw+r'\b','',code)

    keywords = {
        'else', 'do', 'case', 'default', 'return', 'break', 'continue',
        'goto', 'try', 'throw', 'new', 'delete'
    }

    indetifiters = re.finditer(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)

    for match in indetifiters:
        word = match.group()
        next_char = match.end()
        while next_char<len(code) and code[next_char].isspace():#для пропуска пробелов между словом и скобкой
            next_char+=1

        if word in keywords:
            operators[word]+=1
        elif next_char<len(code) and code[next_char] == '(':
            operators[word+"()"]+=1
        else:
            operands[word]+=1 #то есть это обычная пременная - операнд
    code = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', ' ', code)

    operatorscpp=['<<', '>>', '==', '!=', '<=', '>=', '&&', '||', '++', '--',
        '+=', '-=', '*=', '/=', '%=', '->', '::',
        '+', '-', '*', '/', '%', '=', '<', '>', '!', '&', '|', '^', '~',
        ';', ',', '.', '?', ':']

    for op in operatorscpp:
        esc=re.escape(op)#добаялкт \ перед оператором
        count = len(re.findall(esc, code))

        if count>0:
            operators[op]+=count

        code=code.replace(op,'')

    total_parentheses=len(re.findall(r'\(', code))
    parentheses=total_parentheses-kolvo_skobok
    if parentheses>0:
        operators['()']=parentheses

    operators['{}']+=len(re.findall(r'\{',code))
    operators['[]'] += len(re.findall(r'\[', code))
    types_to_ignore = [
        'int', 'double', 'float', 'char', 'void', 'bool', 'long',
        'struct', 'enum', 'using', 'namespace'
    ]

    for t in types_to_ignore:
        operands.pop(t, None)

    if_else_count = operators.get('else', 0)
    if if_else_count > 0:
        operators['if...else'] = if_else_count
        operators['if'] -= if_else_count
        if operators['if'] <= 0:
            del operators['if']
        del operators['else']

    do_count = operators.get('do', 0)
    if do_count > 0:
        operators['do...while'] = do_count
        operators['while'] -= do_count
        if operators['while'] <= 0:
            del operators['while']
        del operators['do']

    return operators, operands

def calculate_metrics(operators, operands):
    n1=len(operators)
    n2=len(operands)
    N1=sum(operators.values())
    N2=sum(operands.values())
    n=n1+n2
    N=N1+N2
    V=N*log2(n) if n>0 else 0
    metrics = {
        "n1": n1, "n2": n2,
        "N1": N1, "N2": N2,
        "n": n, "N": N, "V": round(V, 2)
    }
    return operators, operands, metrics


if __name__ == '__main__':
    # открываем файл с кодом С++ на чтение
    with open('syntaxC++.cpp', 'r', encoding='utf-8') as file:
        cpp_code = file.read()

    ops, opds = parsecpp(cpp_code)
    ops, opds, metrics = calculate_metrics(ops, opds)

    print("Полученные метрики:")
    for key, value in metrics.items():
        print(f"{key}: {value}")