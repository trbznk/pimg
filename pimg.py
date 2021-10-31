import argparse

parser = argparse.ArgumentParser(prog="pimg.py", description="pimg converts images to pixelimages.")
subparsers = parser.add_subparsers(dest="mode")

build_parser = subparsers.add_parser("build")
build_parser.add_argument("source_dir")
build_parser.add_argument("target_dir")

run_parser = subparsers.add_parser("run")
run_parser.add_argument("source_dir")
run_parser.add_argument("source_file")
run_parser.add_argument("target_file")

args = parser.parse_args()

import random
import numpy as np
import hashlib

from glob import glob
from PIL import Image
from pathlib import Path
from tqdm import tqdm

SQUARES_PER_IMG = 1
SQUARE_SIZE = 100
MAX_DISTANCE = 50
if args.mode == "build":
    SOURCE_DIR = args.source_dir
    TARGET_DIR = args.target_dir
elif args.mode == "run":
    SOURCE_DIR = args.source_dir
    SOURCE_FILE = args.source_file
    TARGET_FILE = args.target_file

COLOR_CODES = {
    0: "black",
    1: "blue",
    2: "brown",
    3: "grey",
    4: "green",
    5: "orange",
    6: "red",
    7: "violet",
    8: "yellow",
    9: "white",
}
COLORS = {
    "black": (0, 0, 0),
    "blue": (0, 0, 255),
    "brown": (165, 42, 42),
    "grey": (190, 190, 190),
    "green": (0, 255, 0),
    "orange": (255, 165, 0),
    "red": (255, 0, 0),
    "violet": (238, 130, 238),
    "yellow": (255, 255, 0),
    "white": (255, 255, 255)
}
COLORS = {color: np.array(rgb) for color, rgb in COLORS.items()}


def create_folders():
    
    Path(TARGET_DIR).mkdir(exist_ok=True)

    for color in COLORS.keys():
        Path(f"{TARGET_DIR}/{color}").mkdir(exist_ok=True)


def generate_squares(img_path):
    with Image.open(img_path) as img:
        if img.width > SQUARE_SIZE and img.height > SQUARE_SIZE:
            for _ in range(SQUARES_PER_IMG):
                left = random.randrange(img.width-SQUARE_SIZE)
                upper = random.randrange(img.height-SQUARE_SIZE)

                right = left+SQUARE_SIZE
                lower = upper+SQUARE_SIZE

                square_img = img.crop(box=(left, upper, right, lower))
                square_img_array = np.array(square_img)
                
                mean_color = square_img_array.T.mean(axis=1).mean(axis=1)
                
                min_distance, min_color = 1000, None
                for color, rgb in COLORS.items():
                    #distance = np.linalg.norm(mean_color-COLORS["green"])
                    distance = np.sqrt(np.abs(mean_color-rgb).sum())
                    if distance < MAX_DISTANCE and distance < min_distance:
                        min_distance = distance
                        min_color = color

                if min_color is not None:
                    square_img_hash = hashlib.md5(square_img_array.tobytes()).hexdigest()
                    square_img.save(f"{TARGET_DIR}/{min_color}/{square_img_hash}.png", "PNG")


def create_image(lines):
    paths = glob(f"{SOURCE_DIR}/**/*.png")

    with Image.open(paths[0]) as img:
        square_width, square_height = img.width, img.height

    width, height = square_width*len(lines[0]), square_height*len(lines)

    img = Image.new("RGB", (width, height))

    for i, v in enumerate(range(0, height, square_height)):
        for j, h in enumerate(range(0, width, square_width)):
            color = COLOR_CODES[int(lines[i][j])]
            path = random.choice(glob(f"{SOURCE_DIR}/{color}/*.png"))
            with Image.open(path) as random_square:
                img.paste(random_square, box=(h, v))

    return img


def source_dir_is_valid():
    paths = glob(f"{SOURCE_DIR}/**/*.png")
    boxes = []
    for path in paths:
        with Image.open(path) as img:
            boxes.append((img.width, img.height))

    return all([box == boxes[0] for box in boxes])


if args.mode == "build":
    paths = glob(f"{SOURCE_DIR}/*.jpg")
    print(f"Found {len(paths)} image in SOURCE_DIR")
    create_folders()
    for path in tqdm(paths):
        generate_squares(path)
elif args.mode == "run":
    # DEV:
    #assert source_dir_is_valid(), "SOURCE_DIR has images with different sizes."

    with open(SOURCE_FILE) as f:
        lines = []
        for line in f.readlines():
            line = line.replace("\n", "")
            if len(line) > 0:
                for char in line:
                    assert int(char) in COLOR_CODES, f"'{char}' is not allowed."
                lines.append(line)
 
    assert all([len(line) == len(lines[0]) for line in lines]), "Lines are not equal length."

    img = create_image(lines)

    img_type = TARGET_FILE.rsplit(".", 1)[-1]
    img.save(TARGET_FILE, img_type.upper())
    img.show()
