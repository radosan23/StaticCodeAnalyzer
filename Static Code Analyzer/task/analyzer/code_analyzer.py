import os
import sys


class CodeAnalyzer:
    """Check file or files for stylistic issues."""
    def __init__(self, path):
        """Initialize object with path. Contains dictionary of checks."""
        self.path = path
        self.lines = None
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
                                 'msg': 'More than two blank lines preceding a code line'}}

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
        """Condition for unnecessary semicolon at the end of line"""
        return line.split('#')[0].strip().endswith(';')

    @staticmethod
    def cond_comment(line):
        """Condition for in-line comment without double whitespace"""
        return '#' in line[1:] and not line.split('#')[0].endswith('  ')

    @staticmethod
    def cond_todo(line):
        """Condition for to do found in comment """
        return '#' in line and 'todo' in line.split('#')[1].lower()

    def cond_blank(self, line):
        """Condition for three or more blank lines in a row."""
        i = self.lines.index(line)
        return line.strip() and i > 2 and self.lines[i - 1] == '\n' and self.lines[i - 2] == '\n' \
            and self.lines[i - 3] == '\n'

    @staticmethod
    def check(func, i, line, path):
        """Check given line for each issue, print found issues."""
        if func['cond'](line):
            print(f"{path}: Line {i}: {func['code']} {func['msg']}")

    def check_file(self, path):
        """Check every line of file."""
        self.get_lines(path)
        for i, line in enumerate(self.lines, start=1):
            for check in self.checks.values():
                self.check(check, i, line, path)

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
