import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calendar_watcher.calendar_watcher import get_next_events

if __name__ == "__main__":
    events = get_next_events()
    print("Upcoming events:")
    for e in events:
        print(e)
