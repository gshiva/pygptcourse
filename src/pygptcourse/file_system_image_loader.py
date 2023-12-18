import os


class ImageLoader:
    def get_full_image_path(self, path):
        raise NotImplementedError


class FileSystemImageLoader(ImageLoader):
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.getcwd()

    def get_full_image_path(self, image_name):
        full_image_path = os.path.join(self.base_dir, image_name)
        return full_image_path
