import ast
import os
import re
import sys


class CodeAnalyzer:
    """Check file or files for stylistic issues."""
    def __init__(self, path):
        """Initialize object with path. Contains dictionary of checks."""
        self.path = path
        self.lines = None
        self.issues = []
        self.checks = {'length': {'cond': self.cond_length, 'code': 'S001',
                                  'msg': 'Too long'},
                       'indent': {'cond': self.cond_indent, 'code': 'S002',
                                  'msg': 'Indentation is not a multiple of four'},
                       'semicolon': {'cond': self.cond_semicolon, 'code': 'S003',
                                     'msg': 'Unnecessary semicolon'},
                       'comment': {'cond': self.cond_comment, 'code': 'S004',
                                   'msg': 'Less than two spaces before inline comments'},
                       'todo': {'cond': self.cond_todo, 'code': 'S005',
                                'msg': 'TODO found'},
                       'blank': {'cond': self.cond_blank, 'code': 'S006',
                                 'msg': 'More than two blank lines preceding a code line'},
                       'construction': {'cond': self.cond_constr, 'code': 'S007',
                                        'msg': 'Too many spaces after def/class'},
                       'class': {'cond': self.cond_class, 'code': 'S008',
                                 'msg': 'Class name should be written in CamelCase'},
                       'function': {'cond': self.cond_function, 'code': 'S009',
                                    'msg': 'Function name should be written in snake_case'}}
        self.ast_checks = {'arg_name': {'cond': self.check_arg_name, 'code': 'S010',
                                        'msg': 'Argument name "{}" should be written in snake_case'},
                           'var_name': {'cond': self.check_var_name, 'code': 'S011',
                                        'msg': 'Variable "{}" should be written in snake_case'},
                           'mut_arg': {'cond': self.check_mut_arg, 'code': 'S012',
                                       'msg': 'The default argument value is mutable'}}

    def get_lines(self, path):
        """Read file lines into class field."""
        with open(path, 'rt') as f:
            self.lines = f.readlines()

    @staticmethod
    def cond_length(line, lim=79):
        """Condition for line too long."""
        return len(line) > lim

    @staticmethod
    def cond_indent(line, val=4):
        """Condition for wrong indentation."""
        indent = line.index(line.strip()[0]) if line.strip() else 0
        return indent % val != 0

    @staticmethod
    def cond_semicolon(line):
        """Condition for unnecessary semicolon at the end of line."""
        return line.split('#')[0].strip().endswith(';')

    @staticmethod
    def cond_comment(line):
        """Condition for in-line comment without double whitespace."""
        return '#' in line[1:] and not line.split('#')[0].endswith('  ')

    @staticmethod
    def cond_todo(line):
        """Condition for to do found in comment."""
        return '#' in line and 'todo' in line.split('#')[1].lower()

    def cond_blank(self, line):
        """Condition for three or more blank lines in a row."""
        i = self.lines.index(line)
        return line.strip() and i > 2 and self.lines[i - 1] == '\n' and self.lines[i - 2] == '\n' \
            and self.lines[i - 3] == '\n'

    @staticmethod
    def cond_constr(line):
        """Condition for more than one space before function/class name."""
        return re.match(r'\s*(def|class) {2,}', line) is not None

    @staticmethod
    def cond_class(line):
        """Condition for class name not written in camel case."""
        return line.strip().startswith('class ') and re.match(r'class +[A-Z][a-zA-Z0-9]*[(:]', line.strip()) is None

    @staticmethod
    def cond_function(line):
        """Condition for function name not written in snake case."""
        return line.strip().startswith('def ') and re.match(r'def +[_a-z0-9]+\(', line.strip()) is None

    def check(self, func, i, line, path):
        """Check given line for each issue, print found issues."""
        if func['cond'](line):
            self.issues.append({'path': path, 'line': i, 'code': func['code'], 'msg': func['msg']})

    def check_arg_name(self, tree, path, code, msg):
        """Condition for argument name not written in snake case."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for arg in node.args.args:
                    if re.match(r'[_a-z0-9]+$', arg.arg) is None:
                        self.issues.append({'path': path, 'line': node.lineno, 'code': code,
                                            'msg': msg.format(arg.arg)})

    def check_var_name(self, tree, path, code, msg):
        """Condition for variable name not written in snake case."""
        for f_node in ast.walk(tree):
            if isinstance(f_node, ast.FunctionDef):
                for node in f_node.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and re.match(r'[_a-z0-9]+$', target.id) is None:
                                self.issues.append({'path': path, 'line': node.lineno, 'code': code,
                                                    'msg': msg.format(target.id)})

    def check_mut_arg(self, tree, path, code, msg):
        """Condition for default argument being mutable."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for arg in node.args.defaults:
                    if type(arg) in (ast.List, ast.Set, ast.Dict):
                        self.issues.append({'path': path, 'line': node.lineno, 'code': code, 'msg': msg})

    def check_file(self, path):
        """Check every line of file and nodes of parse tree."""
        self.issues.clear()
        self.get_lines(path)
        for i, line in enumerate(self.lines, start=1):
            for check in self.checks.values():
                self.check(check, i, line, path)
        with open(path, 'rt') as f:
            tree = ast.parse(f.read())
        for check in self.ast_checks.values():
            check['cond'](tree, path, check['code'], check['msg'])
        self.issues.sort(key=lambda x: x['code'])
        self.issues.sort(key=lambda x: x['line'])
        print(*[f"{x['path']}: Line {x['line']}: {x['code']} {x['msg']}" for x in self.issues], sep='\n')

    def analyze(self):
        """Check if given path is directory or file, traverse directory for .py files."""
        if os.path.isfile(self.path):
            self.check_file(self.path)
        else:
            for path, dirs, files in os.walk(self.path):
                for file in files:
                    if file.endswith('.py') and file != 'tests.py':
                        self.check_file(os.path.join(path, file))


def main():
    """Get path from command-line argument and analyze file/files."""
    analyzer = CodeAnalyzer(sys.argv[1])
    analyzer.analyze()


if __name__ == '__main__':
    main()
