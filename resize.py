
import cv2
import numpy as np
import os
import shutil
import argparse

def load_image(image_path):
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

def load_labels(label_path):
    with open(label_path, 'r') as file:
        labels = file.readlines()
    return [list(map(float, line.split())) for line in labels]

def create_oval_mask(size):
    mask = np.zeros(size, dtype=np.uint8)
    cv2.ellipse(mask, (size[1]//2, size[0]//2), (size[1]//2, size[0]//2), 0, 0, 360, 255, -1)
    return mask

def shape_ad_with_inpainting(image, labels):
    inpainted_image = image.copy()
    inpainting_mask = np.zeros_like(image[:,:,0])

    for label in labels:
        _, x_center, y_center, width, height = label
        w, h = image.shape[1], image.shape[0]
        x_center, y_center, width, height = x_center * w, y_center * h, width * w, height * h

        x1, y1 = int(x_center - width / 2), int(y_center - height / 2)
        x2, y2 = int(x_center + width / 2), int(y_center + height / 2)

        mask = create_oval_mask((y2 - y1, x2 - x1))
        mask_inv = cv2.bitwise_not(mask)

        inpainting_mask[y1:y2, x1:x2] = cv2.bitwise_or(inpainting_mask[y1:y2, x1:x2], mask_inv)

    inpainted_image = cv2.inpaint(inpainted_image, inpainting_mask, 3, cv2.INPAINT_TELEA)

    return inpainted_image

def main(image_dir, label_dir, output_image_dir, output_label_dir):
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_label_dir, exist_ok=True)

    for image_name in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_name)
        label_path = os.path.join(label_dir, image_name.replace('.png', '.txt'))

        if os.path.exists(label_path):
            image = load_image(image_path)
            labels = load_labels(label_path)
            inpainted_image = shape_ad_with_inpainting(image, labels)

            output_image_path = os.path.join(output_image_dir, image_name)
            output_label_path = os.path.join(output_label_dir, image_name.replace('.png', '.txt'))

            cv2.imwrite(output_image_path, inpainted_image)
            shutil.copy(label_path, output_label_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ad Blend Inpainting Script")
    parser.add_argument("--image_dir", required=True, help="Directory containing images")
    parser.add_argument("--label_dir", required=True, help="Directory containing labels")
    parser.add_argument("--output_image_dir", required=True, help="Output directory for images")
    parser.add_argument("--output_label_dir", required=True, help="Output directory for labels")

    args = parser.parse_args()

    main(args.image_dir, args.label_dir, args.output_image_dir, args.output_label_dir)
