from huggingface_hub import HfApi

def list_files():
    api = HfApi()
    try:
        files = api.list_repo_files(repo_id="keremberke/hard-hat-detection", repo_type="dataset")
        print(f"Total files: {len(files)}")
        print("First 30 files:")
        for f in files[:30]:
            print(f)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_files()
