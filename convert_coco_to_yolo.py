import os
import json
import shutil

def convert_split(src_dir, dest_img_dir, dest_lbl_dir, num_images):
    json_path = os.path.join(src_dir, "_annotations.coco.json")
    if not os.path.exists(json_path):
        print(f"Error: Annotations file not found in {src_dir}")
        return {}
        
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    # Categories mapping
    categories = {cat['id']: cat['name'] for cat in data['categories']}
    print(f"Categories found in {src_dir}: {categories}")
    
    # Map category IDs to YOLO class indices (0-indexed)
    # We want a standard mapping. Let's sort categories to be consistent
    cat_ids = sorted(list(categories.keys()))
    cat_id_to_yolo_idx = {cat_id: idx for idx, cat_id in enumerate(cat_ids)}
    
    # Group annotations by image_id
    img_to_ann = {}
    for ann in data['annotations']:
        img_id = ann['image_id']
        if img_id not in img_to_ann:
            img_to_ann[img_id] = []
        img_to_ann[img_id].append(ann)
        
    # Process images
    images = data['images']
    # Limit number of images to save training time
    selected_images = images[:num_images]
    print(f"Processing {len(selected_images)} out of {len(images)} images in {src_dir}...")
    
    os.makedirs(dest_img_dir, exist_ok=True)
    os.makedirs(dest_lbl_dir, exist_ok=True)
    
    copied_count = 0
    for img in selected_images:
        img_id = img['id']
        file_name = img['file_name']
        img_w = img['width']
        img_h = img['height']
        
        src_img_path = os.path.join(src_dir, file_name)
        if not os.path.exists(src_img_path):
            # Sometimes file names have issues, try to find matching file
            continue
            
        dest_img_path = os.path.join(dest_img_dir, file_name)
        shutil.copy(src_img_path, dest_img_path)
        copied_count += 1
        
        # Write YOLO label file
        file_name_no_ext = os.path.splitext(file_name)[0]
        lbl_path = os.path.join(dest_lbl_dir, f"{file_name_no_ext}.txt")
        
        anns = img_to_ann.get(img_id, [])
        with open(lbl_path, 'w') as lf:
            for ann in anns:
                cat_id = ann['category_id']
                yolo_idx = cat_id_to_yolo_idx[cat_id]
                bbox = ann['bbox'] # [x_min, y_min, width, height]
                
                # Convert to normalized center x, center y, width, height
                x_min, y_min, w, h = bbox
                x_center = x_min + w / 2.0
                y_center = y_min + h / 2.0
                
                # Normalize
                x_center /= img_w
                y_center /= img_h
                w /= img_w
                h /= img_h
                
                lf.write(f"{yolo_idx} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")
                
    print(f"Copied {copied_count} images and created labels.")
    return {yolo_idx: categories[cat_id] for cat_id, yolo_idx in cat_id_to_yolo_idx.items()}

def main():
    base_dir = os.path.join(os.getcwd(), "dataset")
    processed_dir = os.path.join(base_dir, "processed")
    
    # Class mapping from the conversion
    class_mapping = {}
    
    # Process Train (500 images)
    train_mapping = convert_split(
        os.path.join(base_dir, "train"),
        os.path.join(processed_dir, "images", "train"),
        os.path.join(processed_dir, "labels", "train"),
        500
    )
    class_mapping.update(train_mapping)
    
    # Process Val (100 images)
    val_mapping = convert_split(
        os.path.join(base_dir, "valid"),
        os.path.join(processed_dir, "images", "val"),
        os.path.join(processed_dir, "labels", "val"),
        100
    )
    class_mapping.update(val_mapping)
    
    # Process Test (50 images)
    test_mapping = convert_split(
        os.path.join(base_dir, "test"),
        os.path.join(processed_dir, "images", "test"),
        os.path.join(processed_dir, "labels", "test"),
        50
    )
    class_mapping.update(test_mapping)
    
    # Create data.yaml
    yaml_content = f"""
path: {os.path.abspath(processed_dir)}
train: images/train
val: images/val
test: images/test

nc: {len(class_mapping)}
names:
"""
    for idx in sorted(list(class_mapping.keys())):
        yaml_content += f"  {idx}: {class_mapping[idx]}\n"
        
    with open(os.path.join(processed_dir, "data.yaml"), "w") as f:
        f.write(yaml_content.strip())
    print("Created data.yaml for processed dataset:")
    print(yaml_content)

if __name__ == "__main__":
    main()
