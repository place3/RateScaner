import re

def parse_dropped_files(data):
    pattern = r'\{.*?\x7d|\S+}'
    files = re.findall(pattern, data)

    clean_files = []
    for f in files:
        if f.startswith("{") and f.endswith("}"):
            f = f[1:-1]
        clean_files.append(f)
    return clean_files