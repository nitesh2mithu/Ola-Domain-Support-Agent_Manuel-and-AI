"""Append an actual timestamped development note from stdin."""
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import sys
if __name__=='__main__':
    note=sys.stdin.read().strip()
    timestamp=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S %Z')
    with Path('DEVELOPMENT_PROCESS.md').open('a') as f:
        f.write(f'\n### Milestone 5 step — {timestamp}\n{note}\n')
