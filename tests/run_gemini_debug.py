import sys, os
repo_root = os.getcwd()
# Switch into the `malware_analyzer` package directory so package-style imports like
# `from model.static...` resolve the same way as running main.py from inside that folder.
pkg_dir = os.path.join(repo_root, 'malware_analyzer')
if not os.path.isdir(pkg_dir):
    print('Could not find package dir:', pkg_dir)
    sys.exit(1)
os.chdir(pkg_dir)
sys.path.insert(0, pkg_dir)

from model.static.static_analyzer import StaticAnalyzer
from model.report import gemini_client

# Use small sample file shipped with repo (path relative to repo root)
sample = os.path.join(repo_root, 'StaticAnlysis', 'file.txt')
if not os.path.exists(sample):
    print('Sample file not found:', sample)
    sys.exit(1)

analyzer = StaticAnalyzer()
print('Running static analysis on', sample)
static = analyzer.analyze_file(sample)
print('Static analysis done. Keys:', list(static.keys()))

dynamic = {}

# Monkeypatch requests.post to avoid calling real Gemini API
import requests
class DummyResponse:
    def __init__(self):
        self.status_code = 200
    def raise_for_status(self):
        return None
    def json(self):
        return {"candidates":[{"content":{"parts":[{"text":"DUMMY SUMMARY"}]}}]}

_orig_post = requests.post
requests.post = lambda *args, **kwargs: DummyResponse()

try:
    text = gemini_client.summarize_analysis(static, dynamic, api_key='DUMMY_KEY')
    print('Gemini returned:', text)
except Exception as e:
    print('Error calling summarize_analysis:', e)
finally:
    requests.post = _orig_post
