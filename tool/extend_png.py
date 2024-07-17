import argparse
import os

import cv2
import numpy as np


def extend_transparent(img_path, direction, extension_size):
    assert os.path.exists(img_path), f'{img_path} does not exist'

    loaded_image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if loaded_image.dtype == np.uint16:
        loaded_image = (loaded_image / 256).astype(np.uint8)
    h, w, _ = loaded_image.shape
    print(f'original size: ({w}, {h})')

    if direction in ['up', 'down']:
        new_h, new_w = h + extension_size, w
    elif direction in ['left', 'right']:
        new_h, new_w = h, w + extension_size
    else:
        raise ValueError("Direction must be 'up', 'down', 'left', or 'right'")

    # Create a new image with the new dimensions, filled with transparent pixels

    if extension_size >= 0:
        new_image = np.zeros((new_h, new_w, 4), dtype=np.uint8)
        # Place the original image in the new image based on the direction
        if direction == 'up':
            new_image[extension_size:, :] = loaded_image
        elif direction == 'down':
            new_image[:h, :] = loaded_image
        elif direction == 'left':
            new_image[:, extension_size:] = loaded_image
        elif direction == 'right':
            new_image[:, :w] = loaded_image
    else:
        if direction == 'up':
            new_image = loaded_image[-extension_size:]
        elif direction == 'down':
            new_image = loaded_image[:h+extension_size, :]
        elif direction == 'left':
            new_image = loaded_image[:, -extension_size:]
        elif direction == 'right':
            new_image = loaded_image[:, :w+extension_size]

    h, w, _ = new_image.shape
    print(f'original size: ({w}, {h})')
    return new_image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='extend_png.py')
    parser.add_argument('img_path', help='The path of the image.')
    parser.add_argument('direction',
                        help='The direction you want to extend. Must be one of "up", "down", "left", "right"')
    parser.add_argument('extension_size',
                        help='The length you want to extend. Must be a int. A negative number will result in trimming the image',
                        type=int)
    parser.add_argument('-o', '--output',
                        help='The name of output the file.',
                        default='extended_image.png')
    args = parser.parse_args()

    img_path, direction, extension_size = args.img_path, args.direction, args.extension_size
    extended_image = extend_transparent(img_path, direction, extension_size)

    # Save the result
    cv2.imwrite(args.output, extended_image)
