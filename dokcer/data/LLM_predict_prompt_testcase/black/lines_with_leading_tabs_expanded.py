def lines_with_leading_tabs_expanded(s: str) -> List[str]:
    lines = []
    append_line = lines.append
    tab = " " * 8
    for line in s.splitlines():
        if line.startswith('\t') and line.strip():
            prefix_length = len(line) - len(line.lstrip('\t'))
            expanded_prefix = tab * prefix_length
            append_line(expanded_prefix + line[prefix_length:])
        else:
            append_line(line)
    if s.endswith('\n'):
        append_line('')
    return lines