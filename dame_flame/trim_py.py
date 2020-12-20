import os


def trim_py_files(*directories):
    """Remove trailing whitespace on all .py files in the given directories.
    """
    nchanged = 0
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for fname in files:
                filename = os.path.join(root, fname)
                if fname.endswith('.py'):
                    with open(filename, 'rb') as f:
                        code1 = f.read().decode()
                    lines = [line.rstrip() for line in code1.splitlines()]
                    while lines and not lines[-1]:
                        lines.pop(-1)
                    lines.append('')  # always end with a newline
                    code2 = '\n'.join(lines)
                    if code1 != code2:
                        nchanged += 1
                        print('  Removing trailing whitespace on', filename)
                        with open(filename, 'wb') as f:
                            f.write(code2.encode())
    print('Removed trailing whitespace on {} files.'.format(nchanged))


if __name__ == '__main__':
    trim_py_files(os.path.dirname("C:/Users/angik/ANGIKAR/ANGIKAR_DUKE/Work/Work_AME/DAME-FLAME-Python-Package/dame_flame/dame_algorithm.py"))
