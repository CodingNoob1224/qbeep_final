import os
import shutil

def clear_pycache(start_path='.'):
    for root, dirs, files in os.walk(start_path):
        for d in dirs:
            if d == '__pycache__':
                dir_path = os.path.join(root, d)
                shutil.rmtree(dir_path)
                print(f"Deleted: {dir_path}")

clear_pycache()
