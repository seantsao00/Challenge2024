import argparse
import json
import random
import time

mapping = {}


def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 主程式


def main(reset):
    file_path = 'tool/picked.json'

    data_dict = read_json(file_path)

    if reset:
        for key in data_dict:
            data_dict[key] = 0
    else:
        print("這是第幾場比賽")
        num = int(input())
        print("這一場要 ban 哪些圖呢（請輸入對應的編號以空白隔開，輸入0代表不需要）")
        map_name = {1: "破房了，段蓉刪掉", 2: "煉獄的沙朗牛排", 3: "爛台大，台大什麼了不起", 4: "九橋問題",
                    5: "台灣街道", 6: "喔就沙漠，呀咧呀咧", 7: "這是一張無向圖", 8: "乙種建築用地", 9: "臺南"}
        for k, v in map_name.items():
            print(f"{k}: {v}")
        chosen_dict = read_json("tool/special_picked")
        banned = list(map(int, input().split()))
        if str(num) in chosen_dict and num not in banned:
            result = chosen_dict[str(num)]
        elif banned == [0]:
            weight = [1] * 9
        else:
            cnt = len(banned)
            weight = []
            for i in range(1, 10):
                if i in banned:
                    weight.append(0)
                else:
                    weight.append(1+(3-data_dict[map_name[i]]))
        result = random.choices(list(map_name.values()), weights=weight)[0]
        print("後臺精密計算中...")
        time.sleep(0.5)
        print("正在處理地圖...")
        time.sleep(0.5)
        print("正在處理禁圖...")
        time.sleep(0.5)
        print(f"本場比賽選擇的圖: {result}")
        data_dict[result] += 1

    write_json(file_path, data_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='JSON dictionary manager')
    parser.add_argument('-r', '--reset', action='store_true', help='reset', )
    args = parser.parse_args()

    main(args.reset)
