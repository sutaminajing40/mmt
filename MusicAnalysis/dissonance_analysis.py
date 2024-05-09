import json
from itertools import combinations

# 不協和音と見なされるピッチの差
DISSONANT_INTERVALS = {
    1, 2, 6, 10, 11, 13, 14, 18, 22, 23,
    25, 26, 30, 34, 35, 37, 38, 42, 46, 47
    }

# 調査するtimeの閾値
TIME_THRESHOLD = 6  # この値以下のtimeのみを分析対象とする


def count_dissonances_in_tracks(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    dissonance_count = 0
    notes_with_duration = []
    counted_combinations = set()

    # 各トラックのノートを時間範囲とともにリスト化
    for track in data['tracks']:
        for note in track['notes']:
            start_time = note['time']
            end_time = start_time + note['duration']
            if start_time <= TIME_THRESHOLD:
                notes_with_duration.append((start_time, end_time, note['pitch']))

    # 時間範囲が重なるノートのピッチ間で不協和音をカウント
    for (start1, end1, pitch1), (start2, end2, pitch2) in combinations(notes_with_duration, 2):
        if start1 <= end2 and start2 <= end1:  # 時間範囲が重なる条件
            pitch_pair = tuple(sorted((pitch1, pitch2)))
            time_overlap = (max(start1, start2), min(end1, end2))
            if abs(pitch1 - pitch2) in DISSONANT_INTERVALS and (pitch_pair, time_overlap) not in counted_combinations:
                counted_combinations.add((pitch_pair, time_overlap))
                dissonance_count += 1

    return dissonance_count


if __name__ == "__main__":
    dimensions = [64, 128, 256, 512, 1024]
    for dim in dimensions:
        # ファイルパス
        file_path = f'exp/sod/ape/dim{dim}/samples/json/0_4-beat-continuation.json'
        # 不協和音の数を計算
        dissonance_count = count_dissonances_in_tracks(file_path)
        print(f"Total dissonances found(dim={dim}): {dissonance_count}")
