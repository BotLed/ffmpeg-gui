from collections import deque
import os
import json

class RecentFiles:
    def __init__(self, max_files=5):
        self.max_files = max_files
        self.files = deque(maxlen=max_files)  # Deque with a max length

    def add_file(self, file_path):
        # Prevent adding the same file twice
        if file_path not in self.files:
            self.files.appendleft(file_path)  # Add to the front (most recently accessed)

    def get_files(self):
        return list(self.files)  # Convert deque to a list for easy viewing
    
    def load_files(self, file_path="saves/save.json"):
        if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        self.files = deque(data.get("recent_files", []), maxlen=self.max_files)

    
recent_files = RecentFiles(max_files=5)

# Simulate adding files
recent_files.add_file("/path/to/file1.txt")
recent_files.add_file("/path/to/file2.txt")
recent_files.add_file("/path/to/file3.txt")
recent_files.add_file("/path/to/file4.txt")
recent_files.add_file("/path/to/file5.txt")

# Adding a duplicate, this won't be added again
recent_files.add_file("/path/to/file1.txt")

# Adding a new file when the list is full, the oldest will be removed
recent_files.add_file("/path/to/file6.txt")

# Print the recent files
print(recent_files.get_files())