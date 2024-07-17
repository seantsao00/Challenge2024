import argparse
import glob
import os

import cv2
import numpy as np


def extend_transparent(img_path, direction, extension_size):
    assert os.path.exists(img_path), f'{img_path} does not exist'
    print(f'image: {img_path}')

    loaded_image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if loaded_image.dtype == np.uint16:
        loaded_image = (loaded_image / 256).astype(np.uint8)
    h, w, _ = loaded_image.shape
    print(f'original size: ({w}, {h})', end='\t')

    if direction in ['up', 'down']:
        new_h, new_w = h + extension_size, w
    elif direction in ['left', 'right']:
        new_h, new_w = h, w + extension_size
    else:
        raise ValueError('Direction must be "up", "down", "left", or "right"')

    if extension_size >= 0:
        # Create a new image with the new dimensions, filled with transparent pixels
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
    parser.add_argument('images', help='The path of the images. Can be regex.'
                        'If multiple images are given, the result image will replace the original images.', nargs='+')
    parser.add_argument('direction',
                        help='The direction you want to extend. Must be one of "up", "down", "left", "right"')
    parser.add_argument('extension_size',
                        help='The length you want to extend. Must be a int. A negative number will result in trimming the image',
                        type=int)
    parser.add_argument('-o', '--output',
                        help='If this is not specified, the original image will be replaced. The name of output the file. Can only be specified when the number of images is one.',
                        default=None)
    args = parser.parse_args()
    images, direction, extension_size = args.images, args.direction, args.extension_size
    output_name = args.output
    images = [file for pattern in images for file in glob.iglob(pattern, recursive=True)]
    if len(images) > 1 and output_name is not None:
        raise ValueError('You should not specify output name when extending multiple images.')
    for img in images:
        extended_images = extend_transparent(img, direction, extension_size)
        if output_name is None:
            print(img)
            cv2.imwrite(img, extended_images)
        else:
            cv2.imwrite(output_name, extended_images)
