from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import sys
stamp=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S IST (Asia/Kolkata)')
with Path('DEVELOPMENT_PROCESS.md').open('a') as f:
    f.write('\n### Milestone 6 step — '+stamp+'\n'+sys.stdin.read()+'\n')
print(stamp)
