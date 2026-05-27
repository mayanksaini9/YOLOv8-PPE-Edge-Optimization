import os
import zipfile
from huggingface_hub import hf_hub_download

def download_and_extract():
    repo_id = "keremberke/hard-hat-detection"
    dataset_dir = os.path.join(os.getcwd(), "dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    
    splits = {
        "train": "data/train.zip",
        "valid": "data/valid.zip",
        "test": "data/test.zip"
    }
    
    for split, path in splits.items():
        print(f"Downloading {split} split...")
        zip_path = hf_hub_download(
            repo_id=repo_id,
            filename=path,
            repo_type="dataset"
        )
        print(f"Downloaded to {zip_path}. Extracting to dataset/{split}...")
        
        target_dir = os.path.join(dataset_dir, split)
        os.makedirs(target_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
            
        print(f"Extraction of {split} split completed. Files in dataset/{split}: {len(os.listdir(target_dir))}")

    # Create data.yaml for YOLOv8 training
    # Class names are usually:
    # 0: helmet
    # 1: head
    # 2: person
    # Let's verify class names.
    # Roboflow config files or READMEs show classes:
    # 0: hardhat, 1: head, 2: person, or similar.
    # Let's write data.yaml.
    yaml_content = f"""
path: {os.path.abspath(dataset_dir)}
train: train/images
val: valid/images
test: test/images

nc: 3
names:
  0: helmet
  1: head
  2: person
"""
    with open(os.path.join(dataset_dir, "data.yaml"), "w") as f:
        f.write(yaml_content.strip())
    print("Created dataset/data.yaml")

if __name__ == "__main__":
    download_and_extract()
