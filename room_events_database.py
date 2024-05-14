import sqlite3
import os
import json
import datetime

conn = sqlite3.connect("room_events.db")
cursor = conn.cursor()

room_info_dir = os.path.join("room_info")
room_chunk_dir = os.path.join("room_chunk")

for room_info_file in os.listdir(room_info_dir):
    if not room_info_file.endswith(".json"):
        continue
    with open(os.path.join(room_info_dir, room_info_file), "r", encoding="utf-8") as f:
        data = json.load(f)
    rp = data.get("replay")
    if not rp:
        print(f"{room_info_file} is invalid")
        continue
    sc = rp["source_channel"]
    params = (
        sc["channel"],
        sc["topic"],
        sc["club"]["club_id"],
        sc["creator_user_profile_id"],
        rp["time_live_started"],
        rp["time_live_ended"],
    )
    cursor.execute("INSERT INTO rooms "
                   "(room_id, topic, club_id, creator_user_id, time_live_started, time_live_ended) "
                   "VALUES (?,?,?,?,?,?)", params)

for room_chunk_file in os.listdir(room_chunk_dir):
    if not room_chunk_file.endswith(".json"):
        continue
    with open(os.path.join(room_chunk_dir, room_chunk_file)) as f:
        data = json.load(f)
    room_id = data["chunk"]["chunk_id"].split(":")[0]

    time_live_started = cursor.execute("SELECT time_live_started FROM rooms WHERE room_id = ?", (room_id,)).fetchone()
    if not time_live_started:
        print(f"can\'t get time_live_started for room {room_id}")
    time_live_started = time_live_started[0]

    events = data["chunk"]["events"]
    for event in events:
        time_delta = event[0]
        action_type = event[1]
        more_info = event[2]
        user_id = None
        if action_type == "JOIN_SECTION":
            user_id = more_info["user_profile"]["user_id"]
        elif action_type == "LEAVE_SECTION":
            user_id = more_info["user_profile_id"]
        else:
            continue

        final_timestamp = None
        if time_live_started is not None:
            timestamp = datetime.datetime.fromisoformat(time_live_started)
            timestamp += datetime.timedelta(milliseconds=time_delta)
            final_timestamp = timestamp.isoformat()

        cursor.execute("INSERT INTO events (room_id, timestamp, millisecond, action, user_id) "
                       "VALUES (?, ?, ?, ?, ?)",
                       (room_id, final_timestamp, time_delta, action_type, user_id))

conn.commit()
