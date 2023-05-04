class CodeAnalyzer:
    def __init__(self, file):
        self.file = file
        self.lines = self.get_lines()
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

    def get_lines(self):
        with open(self.file, 'rt') as f:
            return f.readlines()

    @staticmethod
    def cond_length(line, lim=79):
        return len(line) > lim

    @staticmethod
    def cond_indent(line, val=4):
        indent = line.index(line.strip()[0]) if line.strip() else 0
        return indent % val != 0

    @staticmethod
    def cond_semicolon(line):
        return line.split('#')[0].strip().endswith(';')

    @staticmethod
    def cond_comment(line):
        return '#' in line[1:] and not line.split('#')[0].endswith('  ')

    @staticmethod
    def cond_todo(line):
        return '#' in line and 'todo' in line.split('#')[1].lower()

    def cond_blank(self, line):
        i = self.lines.index(line)
        return line.strip() and i > 2 and self.lines[i - 1] == '\n' and self.lines[i - 2] == '\n' \
            and self.lines[i - 3] == '\n'

    @staticmethod
    def check(func, i, line):
        if func['cond'](line):
            print(f"Line {i}: {func['code']} {func['msg']}")

    def analyze(self):
        for i, line in enumerate(self.lines, start=1):
            for check in self.checks.values():
                self.check(check, i, line)


def main():
    analyzer = CodeAnalyzer(input())
    analyzer.analyze()


if __name__ == '__main__':
    main()
