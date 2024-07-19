# obstacle: red #FF0000
# puddle: blue #0000FF
# road: other (prefer white)
# be careful that the alpha channel is ignored

# from challenge 2023

import argparse
import sys

import cv2

MAP_ROAD = 0
MAP_PUDDLE = 1
MAP_OBSTACLE = 2


def gen_map_file_from_image(img_path: str, width: int, height: int, margin: int, threshold: float = 0.8, distance: int = 10):
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    image_width = img.shape[1]
    image_height = img.shape[0]

    assert image_height >= height and image_width >= width

    map_list = [[0 for _ in range(height)] for _ in range(width)]
    visited = [[None for _ in range(height)] for _ in range(width)]

    for x in range(width):
        for y in range(height):
            obstacle = 0
            puddle = 0
            total = 0
            for i in range(int(image_width / width * x), int(image_width / width * (x + 1))):
                for j in range(int(image_height / height * y), int(image_height / height * (y + 1))):
                    total += 1
                    # OpenCV uses BGR
                    b, g, r = [int(v) for v in img[j][i]]
                    if b + g + (255 - r) <= distance:
                        obstacle += 1
                    elif (255 - b) + g + r <= distance:
                        puddle += 1
            if obstacle / total >= threshold:
                map_list[x][y] = MAP_OBSTACLE
            elif puddle / total >= threshold:
                map_list[x][y] = MAP_PUDDLE
            else:
                map_list[x][y] = MAP_ROAD
            if x < margin or x >= width - margin or y < margin*2 or y == height-1:
                map_list[x][y] = MAP_OBSTACLE

    transpose = [[0 for j in range(width)] for i in range(height)]

    connected = {}

    def BFS(start):
        idx = 0
        queue = [start]
        visited[start[0]][start[1]] = start
        while idx < len(queue):
            def check_unvisited(x, y):
                if map_list[x][y] != MAP_OBSTACLE and not visited[x][y]:
                    visited[x][y] = start
                    queue.append((x, y))
            x, y = queue[idx]
            check_unvisited(x, y + 1)
            check_unvisited(x, y - 1)
            check_unvisited(x + 1, y)
            check_unvisited(x - 1, y)
            idx += 1
        connected[start] = len(queue)

    start = (0, 0)
    for i in range(int(width)):
        for j in range(int(height)):
            if map_list[i][j] != MAP_OBSTACLE and visited[i][j] is None:
                BFS((i, j))
    max_connected = max(connected.values())

    count = 0
    for i in range(int(width)):
        for j in range(int(height)):
            if map_list[i][j] != MAP_OBSTACLE and connected[visited[i][j]] != max_connected:
                map_list[i][j] = MAP_OBSTACLE
                count += 1
    print(f"Smart converted {count} obstacles", file=sys.stderr)

    for i in range(int(width)):
        for j in range(int(height)):
            transpose[j][i] = map_list[i][j]

    for i in transpose:
        print(','.join([str(j) for j in i]))


def print_help():
    print('Usage: python MapTool.py <img path> <width> <height> [threshold] [distance]')


parser = argparse.ArgumentParser(prog='map_too.py')
parser.add_argument('layout_path', help='The path of layout image.')
parser.add_argument('width', help='The width of the result csv.', type=int)
parser.add_argument('height', help='The height of the result csv.', type=int)
parser.add_argument(
    '-m', '--margin', help='The thickness of the margin of the result map.', type=int, default=5)
parser.add_argument('-t', '--threshold', type=float, default=0.8)
parser.add_argument('-d', '--distance', type=int, default=10)
args = parser.parse_args()

path, width, height = args.layout_path, args.width, args.height
margin, threshold, distance = args.margin, args.threshold, args.distance
gen_map_file_from_image(path, width, height, margin, threshold, distance)
