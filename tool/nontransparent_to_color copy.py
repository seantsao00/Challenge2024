import argparse

import cv2
import numpy as np

parser = argparse.ArgumentParser(prog='nontransparent_to_color.py')
parser.add_argument(
    'image', help='the path to the image'
)
parser.add_argument('-c', '--color', default='red',
                    help='choose the color of the output image.')
parser.add_argument('-o', '--output-file', default='output.png',
                    help='the name of the output file')
args = parser.parse_args()

# (B, G, R)
color = {
    'red': np.array([0, 0, 255]),
    'blue': np.array([255, 0, 0])
}

image = cv2.imread(args.image, cv2.IMREAD_UNCHANGED)
b, g, r, a = cv2.split(image)

image[a > 0, :3] = color[args.color]

# reset obstacle regions to red
cv2.imwrite(args.output_file, image)
