
import cv2
import os
import numpy as np
import random
import argparse

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def select_random_patch(image, patch_size):
    height, width, _ = image.shape
    x = random.randint(0, width - patch_size[1])
    y = random.randint(0, height - patch_size[0])
    return image[y:y+patch_size[0], x:x+patch_size[1]]

def patch_replacement(ad_image, label_file, target_image_path, target_label_path, patch_fraction=0.5):
    ad = cv2.imread(ad_image)
    height, width, _ = ad.shape

    with open(label_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        _, x_center, y_center, w, h = map(float, line.split())
        x_center, y_center, w, h = x_center * width, y_center * height, w * width, h * height
        x, y = int(x_center - w / 2), int(y_center - h / 2)

        patch_size = (int(h * patch_fraction), int(w * patch_fraction))
        patch = select_random_patch(ad, patch_size)

        patch_resized = cv2.resize(patch, (patch_size[1], patch_size[0]))

        patch_x = x + random.randint(0, int(w) - patch_size[1])
        patch_y = y + random.randint(0, int(h) - patch_size[0])

        ad[patch_y:patch_y + patch_size[0], patch_x:patch_x + patch_size[1]] = patch_resized

    cv2.imwrite(target_image_path, ad)
    os.system(f'cp "{label_file}" "{target_label_path}"')

def process_images(images_path, labels_path, target_images_path, target_labels_path, patch_fraction):
    create_directory_if_not_exists(target_images_path)
    create_directory_if_not_exists(target_labels_path)

    for image_file in os.listdir(images_path):
        if image_file.endswith('.png'):
            image_path = os.path.join(images_path, image_file)
            label_file = os.path.join(labels_path, image_file.replace('.png', '.txt'))
            target_image_path = os.path.join(target_images_path, image_file)
            target_label_path = os.path.join(target_labels_path, image_file.replace('.png', '.txt'))

            patch_replacement(image_path, label_file, target_image_path, target_label_path, patch_fraction)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch Processor for Images")
    parser.add_argument("--images_path", required=True, help="Directory containing images")
    parser.add_argument("--labels_path", required=True, help="Directory containing labels")
    parser.add_argument("--target_images_path", required=True, help="Target directory for processed images")
    parser.add_argument("--target_labels_path", required=True, help="Target directory for labels")
    parser.add_argument("--patch_fraction", type=float, default=0.5, help="Fraction size of the patch")

    args = parser.parse_args()

    process_images(args.images_path, args.labels_path, args.target_images_path, args.target_labels_path, args.patch_fraction)
