import sys, os
os.chdir('malware_analyzer')
sys.path.insert(0, os.getcwd())
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
app = QApplication([])
win = MainWindow()
static = {'file_info': {'file_name':'f','file_size_human':'1 KB','file_type':'exe'}, 'hashes':{'sha256':'abc'}, 'pe_analysis':{}, 'strings':{}, 'entropy':{}, 'threat_assessment':{}}
win.show_result(static)
print('gemini_started:', getattr(win, '_gemini_started', None))
print('gemini_wait_timer:', hasattr(win, '_gemini_wait_timer'))
# simulate dynamic arriving
win.show_dynamic_results({'verdict':'malicious','threat_score':90,'signatures':[{'name':'sig1','severity':'high'}]})
print('after dynamic - gemini_started:', getattr(win, '_gemini_started', None))
