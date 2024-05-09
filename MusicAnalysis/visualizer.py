import json
import os

import matplotlib.pyplot as plt
import pandas as pd


def load_data(path: str):
    with open(path, 'r') as file:
        return json.load(file)


def load_instrument_names(path: str):
    with open(path, 'r') as file:
        data = json.load(file)
        return data['program_instrument_map']


def extract_notes_by_instrument(data, instrument_names):
    instruments = {}
    for track in data['tracks']:
        instrument_id = track['program']
        instrument_name = instrument_names.get(str(instrument_id), f"Unknown_{instrument_id}")
        if instrument_name not in instruments:
            instruments[instrument_name] = []
        for note in track['notes']:
            instruments[instrument_name].append({
                'time': note['time'],
                'pitch': note['pitch'],
                'duration': note['duration'],
                'velocity': note['velocity']
            })
    return instruments


def save_instruments(instruments):
    if not os.path.exists('output'):
        os.makedirs('output')
    for name, notes in instruments.items():
        df = pd.DataFrame(notes)
        df.to_csv(f'output/{name}.csv', index=False)


def plot_piano_roll(path: str, title: str, output_dir: str):
    df = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(20, 6))  # 幅を長く設定
    ax.barh(df['pitch'], df['duration'], left=df['time'], height=0.8, color='gray', edgecolor='black')

    ax.set_xlabel('Time (beat)')
    ax.set_ylabel('Pitch')
    ax.set_title(title)

    # 細かいグリッド線を追加 (1ピッチごと)
    ax.set_yticks(range(0, 128), minor=True)
    ax.grid(True, which='minor', axis='y', linestyle='-', linewidth=0.1, color='gray')

    # 主要なグリッド線を追加 (5ピッチごと)
    ax.set_yticks(range(0, 128, 5))
    ax.set_yticklabels(range(0, 128, 5))
    ax.grid(True, which='major', axis='y', linestyle='-', linewidth=0.5, color='black')

    # 縦線を追加
    max_time = df['time'].max() + df['duration'].max()
    ax.set_xticks(range(0, int(max_time) + 1, 100))  # 100ビートごとに縦線を引く
    ax.set_xticklabels(range(0, int(max_time) + 1, 100))

    # x軸の最小値と最大値を設定
    ax.set_xlim(left=0, right=max_time)

    # 保存
    output_path = os.path.join(output_dir, f"{title}.png")
    plt.savefig(output_path, dpi=600)  # 解像度を高く設定
    plt.close()


def main(json_path: str, encoding_path: str):
    data = load_data(json_path)
    instrument_names = load_instrument_names(encoding_path)
    instruments = extract_notes_by_instrument(data, instrument_names)
    save_instruments(instruments)

    # JSONファイルのディレクトリを取得し、画像の保存先ディレクトリを設定
    base_dir = os.path.dirname(json_path)
    parent_dir = os.path.dirname(base_dir)  # 末尾のディレクトリを削除
    output_dir = os.path.join(parent_dir, 'png-instrument')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for instrument_file in os.listdir('output'):
        plot_piano_roll(f'output/{instrument_file}', instrument_file.split('.')[0], output_dir)


if __name__ == '__main__':
    main('exp/sod/ape/dim1024/samples/json/0_4-beat-continuation.json', 'mmt/encoding.json')
