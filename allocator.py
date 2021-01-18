from argparse import ArgumentParser
from shutil import copy2
import os

path = './timages'


def set_parser():
    ap = ArgumentParser()
    ap.add_argument('--name', type=str, default='pk', help='Dataset Name')
    return ap.parse_args()


target_path = os.path.join('train_images', set_parser().name)
os.makedirs(target_path, exist_ok=True)
os.makedirs(os.path.join(target_path, 'val'), exist_ok=True)
os.makedirs(os.path.join(target_path, 'test'), exist_ok=True)
os.makedirs(os.path.join(target_path, 'train'), exist_ok=True)

scanObj = os.scandir(path)
counter = 0
plates = []
for item in scanObj:
    if item.name.endswith('pl.jpg'):
        counter += 1
        splits = item.name.split('_')
        plates.append({
            'old': item.name,
            'new': '_'.join([splits[0], splits[-2]])+'.'+splits[-1].split('.')[-1]
        })

for i, plate in enumerate(plates):
    if i <= 0.1 * len(plates):
        copy2(os.path.join(path, plate['old']), os.path.join(target_path, 'val', plate['new']))
    elif 0.1 * len(plates) < i <= 0.2 * len(plates):
        copy2(os.path.join(path, plate['old']), os.path.join(target_path, 'test', plate['new']))
    else:
        copy2(os.path.join(path, plate['old']), os.path.join(target_path, 'train', plate['new']))