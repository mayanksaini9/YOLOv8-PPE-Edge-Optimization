import os
import shutil
from huggingface_hub import snapshot_download

def download_data():
    print("Starting dataset download from Hugging Face...")
    local_dir = os.path.join(os.getcwd(), "raw_dataset")
    
    # Download the dataset repository
    snapshot_download(
        repo_id="keremberke/hard-hat-detection",
        repo_type="dataset",
        local_dir=local_dir,
        ignore_patterns=["*.git*", "*.md"]
    )
    print(f"Dataset downloaded to {local_dir}")
    
    # List the files in the directory
    for root, dirs, files in os.walk(local_dir):
        level = root.replace(local_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files[:5]: # Show first 5 files
            print(f"{subindent}{f}")
        if len(files) > 5:
            print(f"{subindent}... and {len(files) - 5} more files")

if __name__ == "__main__":
    download_data()
