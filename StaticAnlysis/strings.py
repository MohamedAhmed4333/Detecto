import re

def extract_strings(file_path, min_length=4):
    with open(file_path, "rb") as f:
        data = f.read()

    pattern = rb"[ -~]{%d,}" % min_length
    raw_strings = re.findall(pattern, data)

    return list(set(s.decode(errors="ignore") for s in raw_strings))


def extract_urls(strings):
    url_pattern = r"https?://[^\s]+"
    return [s for s in strings if re.search(url_pattern, s)]


def extract_ips(strings):
    ip_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
    return [s for s in strings if re.search(ip_pattern, s)]
