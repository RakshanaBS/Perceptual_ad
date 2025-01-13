
import cv2
import os
import numpy as np
import random
import argparse

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def add_invisible_noise(image, intensity=100):
    noise = np.random.normal(loc=0, scale=1, size=image.shape)
    return np.clip(image + noise * intensity, 0, 255).astype(np.uint8)

def apply_noise_to_ad_regions(ad_image, label_file, target_image_path, target_label_path):
    ad = cv2.imread(ad_image)
    height, width, _ = ad.shape

    with open(label_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        _, x_center, y_center, w, h = map(float, line.split())
        x_center, y_center, w, h = x_center * width, y_center * height, w * width, h * height
        x, y = int(x_center - w / 2), int(y_center - h / 2)

        ad_region = ad[y:y + int(h), x:x + int(w)]
        ad_region_noisy = add_invisible_noise(ad_region)
        ad[y:y + int(h), x:x + int(w)] = ad_region_noisy

    cv2.imwrite(target_image_path, ad)
    os.system(f'cp "{label_file}" "{target_label_path}"')

def process_images(images_path, labels_path, target_images_path, target_labels_path):
    create_directory_if_not_exists(target_images_path)
    create_directory_if_not_exists(target_labels_path)

    for image_file in os.listdir(images_path):
        if image_file.endswith('.png'):
            image_path = os.path.join(images_path, image_file)
            label_file = os.path.join(labels_path, image_file.replace('.png', '.txt'))
            target_image_path = os.path.join(target_images_path, image_file)
            target_label_path = os.path.join(target_labels_path, image_file.replace('.png', '.txt'))

            apply_noise_to_ad_regions(image_path, label_file, target_image_path, target_label_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Noise Addition Script for Ad Regions")
    parser.add_argument("--images_path", required=True, help="Directory containing images")
    parser.add_argument("--labels_path", required=True, help="Directory containing labels")
    parser.add_argument("--target_images_path", required=True, help="Target directory for processed images")
    parser.add_argument("--target_labels_path", required=True, help="Target directory for labels")

    args = parser.parse_args()

    process_images(args.images_path, args.labels_path, args.target_images_path, args.target_labels_path)
