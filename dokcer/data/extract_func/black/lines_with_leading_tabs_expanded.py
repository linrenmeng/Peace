'\n    Splits string into lines and expands only leading tabs (following the normal\n    Python rules)\n    '
lines = []
for line in s.splitlines():
    stripped_line = line.lstrip()
    if not stripped_line or stripped_line == line:
        lines.append(line)
    else:
        prefix_length = len(line) - len(stripped_line)
        prefix = line[:prefix_length].expandtabs()
        lines.append(prefix + stripped_line)
if s.endswith('\n'):
    lines.append('')
return lines