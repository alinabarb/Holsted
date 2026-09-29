import re
import sys


_COMMENT_OR_LITERAL = re.compile(
    r'//.*?$'
    r'|/\*.*?\*/'
    r'|"(?:\\.|[^"\\])*"'
    r"|'(?:\\.|[^'\\])*'",
    re.DOTALL | re.MULTILINE,
)


def strip_comments_and_literals(src: str) -> str:
    def _repl(m: "re.Match[str]") -> str:
        s = m.group(0)
        if s.startswith('//') or s.startswith('/*'):
            return ' '
        if s.startswith('"'):
            return '""'
        return "''"
    return _COMMENT_OR_LITERAL.sub(_repl, src)


_TOKEN_RE = re.compile(r'[A-Za-z_]\w*|[{}();:,?]|\S')


def tokenize(src: str):
    return _TOKEN_RE.findall(src)


_LOOP_KEYWORDS = {'for', 'while', 'do'}
_STMT_START_KEYWORDS = {
    'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
    'return', 'break', 'continue', 'goto',
}


class GilbParser:
    def __init__(self, tokens):
        self.toks = tokens
        self.n = len(tokens)
        self.pos = 0

        self.CL = 0
        self.max_depth = 0
        self.total_operators = 0

    def peek(self, offset=0):
        i = self.pos + offset
        return self.toks[i] if 0 <= i < self.n else None

    def advance(self):
        t = self.toks[self.pos]
        self.pos += 1
        return t

    def skip_balanced(self, open_c, close_c):
        depth = 0
        while self.pos < self.n:
            t = self.advance()
            if t == open_c:
                depth += 1
            elif t == close_c:
                depth -= 1
                if depth == 0:
                    return

    def parse_program(self):
        while self.pos < self.n:
            self.parse_statement(depth=0)

    def parse_statement(self, depth):
        t = self.peek()
        if t is None:
            return

        nxt = self.peek(1)
        if (
            t not in _STMT_START_KEYWORDS
            and re.match(r'[A-Za-z_]\w*$', t)
            and nxt == ':'
            and self.peek(2) != ':'
        ):
            self.advance()
            self.advance()
            self.parse_statement(depth)
            return

        if t == '{':
            self.parse_compound(depth)
        elif t == 'if':
            self.parse_if(depth)
        elif t in _LOOP_KEYWORDS:
            self.parse_loop(depth, t)
        elif t == 'switch':
            self.parse_switch(depth)
        elif t in ('case', 'default'):
            self.parse_case_label(depth)
        else:
            self.parse_simple(depth)

    def parse_compound(self, depth):
        self.advance()
        while self.peek() is not None and self.peek() != '}':
            self.parse_statement(depth)
        if self.peek() == '}':
            self.advance()

    def parse_body(self, depth):
        if self.peek() == '{':
            self.parse_compound(depth)
        elif self.peek() == ';':
            self.advance()
        else:
            self.parse_statement(depth)

    def parse_if(self, depth):
        self.CL += 1
        self.total_operators += 1
        self.max_depth = max(self.max_depth, depth)

        self.advance()
        if self.peek() == '(':
            self.skip_balanced('(', ')')

        self.parse_body(depth + 1)

        if self.peek() == 'else':
            self.advance()
            self.parse_body(depth + 1)

    def count_switch_branches(self):
        if self.peek() != '{':
            return 0
        depth = 0
        count = 0
        i = self.pos
        while i < self.n:
            t = self.toks[i]
            if t == '{':
                depth += 1
            elif t == '}':
                depth -= 1
                if depth == 0:
                    break
            elif depth == 1 and t in ('case', 'default'):
                count += 1
            i += 1
        return count

    def parse_switch(self, depth):
        self.advance()
        if self.peek() == '(':
            self.skip_balanced('(', ')')

        branches = self.count_switch_branches()
        if branches >= 1:
            equiv_cl = max(branches - 1, 0)
            self.CL += equiv_cl
            self.total_operators += equiv_cl
        equiv_depth = depth + max(branches - 2, 0)
        self.max_depth = max(self.max_depth, equiv_depth)

        if self.peek() == '{':
            self.parse_compound(depth + 1)
        else:
            self.parse_body(depth + 1)

    def parse_case_label(self, depth):
        self.advance()
        while self.peek() not in (':', None):
            self.advance()
        if self.peek() == ':':
            self.advance()

    def parse_loop(self, depth, kind):
        self.total_operators += 1
        self.advance()

        if kind in ('for', 'while'):
            if self.peek() == '(':
                self.skip_balanced('(', ')')
            self.parse_body(depth)
        else:
            self.parse_body(depth)
            if self.peek() == 'while':
                self.advance()
                if self.peek() == '(':
                    self.skip_balanced('(', ')')
                if self.peek() == ';':
                    self.advance()

    def parse_simple(self, depth):
        self.total_operators += 1
        paren_depth = 0
        while self.pos < self.n:
            t = self.advance()
            if t == '?':
                self.CL += 1
                self.total_operators += 1
                self.max_depth = max(self.max_depth, depth)
            elif t == '(':
                paren_depth += 1
            elif t == ')':
                paren_depth -= 1
            elif t == ';' and paren_depth <= 0:
                break
            elif t == '{' and paren_depth <= 0:
                self.pos -= 1
                self.parse_compound(depth)
                break


def analyze_source(src: str) -> dict:
    clean = strip_comments_and_literals(src)
    tokens = tokenize(clean)
    parser = GilbParser(tokens)
    parser.parse_program()

    CL = parser.CL
    total = parser.total_operators
    cl = CL / total if total else 0.0
    CLI = parser.max_depth

    return {
        'CL': CL,
        'cl': round(cl, 4),
        'CLI': CLI,
        'total_operators': total,
    }


def analyze_file(path: str) -> dict:
    with open(path, encoding='utf-8') as f:
        return analyze_source(f.read())


if __name__ == '__main__':
    if len(sys.argv) == 2:
        cpp_path = sys.argv[1]
    else:
        cpp_path = input('Введите путь к .cpp файлу: ').strip().strip('"')

    result = analyze_file(cpp_path)
    print(f"Абсолютная сложность программы (CL)        = {result['CL']}")
    print(f"Относительная сложность программы (cl)      = {result['cl']}")
    print(f"Максимальный уровень вложенности (CLI)      = {result['CLI']}")
    print(f"(общее число операторов программы: {result['total_operators']})")
