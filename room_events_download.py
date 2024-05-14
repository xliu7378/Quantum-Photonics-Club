import os
import errno
import time
import json
import requests
from tqdm import tqdm, trange

ROOM_INFO_DIR = "room_info"
ROOM_CHUNK_DIR = "room_chunk"


def make_dir(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_room(room_id):
    make_dir(ROOM_INFO_DIR)
    make_dir(ROOM_CHUNK_DIR)

    headers = {
        'authority': 'www.clubhouse.com',
        'accept': 'application/json',
        'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'body': '{}',
        'content-type': 'application/json',
        'dnt': '1',
        'referer': f'https://www.clubhouse.com/room/{room_id}',
        'requestmode': 'same-origin',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    }

    response = requests.get(f'https://www.clubhouse.com/web_api/get_replay_channel/{room_id}/', headers=headers)
    content = response.content

    with open(os.path.join(ROOM_INFO_DIR, room_id + ".json"), "wb") as f1:
        f1.write(response.content)

    j = response.json()

    chunk_summaries = j["replay"]["chunk_summaries"]

    chunks = [x["chunk_id"] for x in chunk_summaries]
    #print(chunks)

    for chunk in tqdm(chunks):
        response = requests.get(f'https://www.clubhouse.com/web_api/get_replay_channel_chunk/{room_id}/{chunk}/', headers=headers)
        j1 = response.json()
        #print(j1)

        with open(os.path.join(ROOM_CHUNK_DIR, chunk.replace(":", "_") + ".json"), "wb") as f2:
            f2.write(response.content)

        time.sleep(10)


if __name__ == '__main__':
    #rooms_list = ['PGzNz8DV', 'M43V3Ewk', 'xLznR9D6', 'xjXyLNlN', 'ma4QAdeq', 'PGXBGddg', 'xnJYaeV3', 'mW1dOd9p', 'MzjNK9n4', 'M4rQlNAl', 'xLlpzQ66', 'PbLQD06Z', 'xkL17rlV', 'Md89gyn8', 'm78BzreW', 'xoBWj1jl', 'M6KqK29o', 'Mwa0zBAB', 'xegdywOQ', 'myj6gwvL', 'Pra664vl', 'mW4DkpEP', 'M8nGYqVA', 'mJ6zXo3d', 'my4XykqV', 'MRyYkqKb', 'xjj9Jw3g', 'M1LJeYQv', 'Mz925oVx', 'xnKpEkeQ', 'M5Y37yYl', 'xLjlbL0d', 'PYLponnO', 'MdRBQWAq', 'MwrORaOO', 'Mz5NdbRB', 'M6EkOp5J', 'xBJ6Lvqd', 'mZWdqJGw', 'PAJLV3G1', 'xew80a5b', 'M8LqDO5a', 'MRnqZOlA']
    with open("room_list.json") as fjson:
        rooms_list = json.load(fjson).get("rooms", [])
    for room_id in tqdm(rooms_list):
        try:
            get_room(room_id)
        except Exception as e:
            with open("ERROR.log", "a", encoding="utf-8") as f:
                f.write(f"{room_id},{e}\n")
        finally:
            time.sleep(10)
