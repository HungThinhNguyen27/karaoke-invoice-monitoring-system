import threading

TEMP_STORAGE = {}
processed_file_set = set()
in_progress_file_set = set()

state_lock = threading.Lock()
