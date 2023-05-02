class CodeAnalyzer:
    def __init__(self, file):
        self.file = file
        self.lines = self.get_lines()

    def get_lines(self):
        with open(self.file, 'rt') as f:
            return f.readlines()

    def check_length(self, lim=79, code='S001', msg='Too long'):
        for i, line in enumerate(self.lines, start=1):
            if len(line) > lim:
                print(f'Line {i}: {code} {msg}')


def main():
    analyzer = CodeAnalyzer(input())
    analyzer.check_length()


if __name__ == '__main__':
    main()
