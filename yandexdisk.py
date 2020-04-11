import os
import re

import yadisk


class YandexDisk:
    def __init__(self, token: str = None, photo_path=r"/ProjectEva/photos/"):
        if token is None:
            token = os.environ["YADISKTOKEN"]
        self.disk = yadisk.YaDisk(token=token)
        self.photo_path = photo_path

    def upload(self, filepath: str, name: str = None):
        if name is None:
            name = re.search(r"[^\\]+$", filepath).group(0)
        self.disk.upload(filepath, self.photo_path + name, overwrite=True)
        return self.photo_path + name

    def download(self, filepath: str, to_path: str):
        self.disk.download(filepath, to_path)

    def delete(self, filepath: str):
        self.disk.remove(filepath)
