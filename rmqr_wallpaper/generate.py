import cv2
import rmqrcode
from rmqrcode import rMQR
from rmqrcode import QRImage
import sys
import os
import argparse
import numpy as np


class wallpaper_propaties:
    def __init__(self, mode: str = "4:3"):
        self.mode = mode
        if self.mode == "4:3":
            self.width = 1280
            self.height = 960
            self.x_offset_left = int(self.width/2) + 10
            self.x_offset_right = 10
            self.y_offset_under = 10
        elif self.mode == "16:9":
            self.width = 1920
            self.height = 1080
            self.x_offset_left = int(self.width/2) + 10
            self.x_offset_right = 10
            self.y_offset_under = 10


def genearate_black(_mode="4:3"):
    wallpaper_properties = wallpaper_propaties(_mode)
    img = np.zeros((wallpaper_properties.height,
                   wallpaper_properties.width, 3), np.uint8)
    return img

def image_overlay(img1, img2, top, left) -> np.ndarray:

    height, width = img1.shape[:2]
    img2[top:height + top, left:width + left] = img1

    return img2


def resize_width(_img, _width):
    return cv2.resize(_img, (_width, int(_width * _img.shape[0] / _img.shape[1])))

def resize_height(_img, _height):
    return cv2.resize(_img, (int(_height * _img.shape[1] / _img.shape[0]), _height))


def generate(output_filename, text, wallpaper_base_dir, mode="4:3", flip=False):
    wallpaper_properties = wallpaper_propaties(mode)
    wallpaper_base_dir = wallpaper_base_dir.replace(
        "~", os.path.expanduser("~"))
    wallpaper_base_dir = os.path.abspath(wallpaper_base_dir)
    wallpaper = cv2.imread(wallpaper_base_dir)

    if mode == "4:3":
        if wallpaper.shape[0] // wallpaper.shape[1] > 4 / 3:
            wallpaper = resize_height(wallpaper, wallpaper_properties.height)
        else:
            wallpaper = resize_width(wallpaper, wallpaper_properties.width)
    elif mode == "16:9":
        if wallpaper.shape[0] // wallpaper.shape[1] > 16 / 9:
            wallpaper = resize_height(wallpaper, wallpaper_properties.height)
        else:
            wallpaper = resize_width(wallpaper, wallpaper_properties.width)

    black_wallpaper = genearate_black(mode)
    wallpaper = image_overlay(wallpaper, black_wallpaper, 0, 0)

    rmqr = rMQR.fit(
        text,
        ecc=rmqrcode.ErrorCorrectionLevel.M,
        fit_strategy=rmqrcode.FitStrategy.MINIMIZE_HEIGHT
    )
    image = QRImage(rmqr, module_size=8)
    image.save(".my_qr.png")

    rmqr_img = cv2.imread(".my_qr.png")
    os.remove(".my_qr.png")


    rmqr_img = resize_width(rmqr_img, wallpaper_properties.width -
                            wallpaper_properties.x_offset_left - wallpaper_properties.x_offset_right)

    wallpaper = image_overlay(rmqr_img, wallpaper,
                                wallpaper.shape[0] - rmqr_img.shape[0] - wallpaper_properties.y_offset_under,
                                wallpaper_properties.x_offset_left)

    if flip:
        wallpaper = cv2.flip(wallpaper, 1)

    cv2.imwrite(output_filename, wallpaper)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate a wallpaper from a text string")
    parser.add_argument(
        "--text",
        help="The text to be encoded in the wallpaper")
    parser.add_argument(
        "--wallpaper",
        help="The wallpaper to use"
    )
    parser.add_argument(
        "--output",
        help="The output file name (png, jpg)"
    )
    parser.add_argument(
        "--mode",
        help="The mode of the wallpaper (4:3, 16:9)",
        default="16:9"
    )
    parser.add_argument(
        "--flip",
        help="Flip the wallpaper horizontally",
        action="store_true"
    )

    args = parser.parse_args()

    if args.text is None:
        print("Please provide a text string")
        sys.exit(1)

    if args.wallpaper is None:
        print("Please provide a wallpaper path")
        sys.exit(1)

    if args.output is None:
        print("Please provide an output file name")
        sys.exit(1)

    generate(args.output, args.text, args.wallpaper, args.mode, args.flip)
