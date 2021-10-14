import os
import cv2

import numpy as np
import torch.utils.data as data

from PIL import Image

from utils.custom_transforms import *
from utils.utils import *

class RGB_Dataset(data.Dataset):
    def __init__(self, root, transform_list):
        image_root, gt_root = os.path.join(root, 'images'), os.path.join(root, 'masks')

        self.images = [os.path.join(image_root, f) for f in os.listdir(image_root) if f.endswith(('.jpg', '.png'))]
        self.images = sorted(self.images)
        
        self.gts = [os.path.join(gt_root, f) for f in os.listdir(gt_root) if f.endswith('.png')]
        self.gts = sorted(self.gts)
        
        self.filter_files()
        
        self.size = len(self.images)
        self.transform = get_transform(transform_list)

    def __getitem__(self, index):
        image = Image.open(self.images[index]).convert('RGB')
        gt = Image.open(self.gts[index]).convert('L')
        shape = gt.size[::-1]
        name = self.images[index].split(os.sep)[-1]
        if name.endswith('.jpg'):
            name = name.split('.jpg')[0] + '.png'
            
        sample = {'image': image, 'gt': gt, 'name': name, 'shape': shape}

        sample = self.transform(sample)
        return sample

    def filter_files(self):
        assert len(self.images) == len(self.gts)
        images, gts = [], []
        for img_path, gt_path in zip(self.images, self.gts):
            img, gt = Image.open(img_path), Image.open(gt_path)
            if img.size == gt.size:
                images.append(img_path)
                gts.append(gt_path)
        self.images, self.gts = images, gts

    def __len__(self):
        return self.size

class RGBD_Dataset(data.Dataset):
    def __init__(self, root, transform_list):
        image_root = os.path.join(root, 'RGB')
        gt_root = os.path.join(root, 'GT')
        depth_root = os.path.join(root, 'depth')

        self.images = [os.path.join(image_root, f) for f in os.listdir(image_root) if f.endswith(('.jpg', '.png'))]
        self.images = sorted(self.images)
        
        self.depths = [os.path.join(depth_root, f) for f in os.listdir(depth_root) if f.endswith(('.jpg', '.png'))]
        self.depths = sorted(self.depths)
        
        self.gts = [os.path.join(gt_root, f) for f in os.listdir(gt_root) if f.endswith('.png')]
        self.gts = sorted(self.gts)
        
        self.filter_files()
        
        self.size = len(self.images)
        self.transform = get_transform(transform_list)

    def __getitem__(self, index):
        image = Image.open(self.images[index]).convert('RGB')
        gt = Image.open(self.gts[index]).convert('L')
        depth = Image.open(self.depths[index]).convert('L')
        shape = gt.size[::-1]
        name = self.images[index].split(os.sep)[-1]
        if name.endswith('.jpg'):
            name = name.split('.jpg')[0] + '.png'
                
        sample = {'image': image, 'gt': gt, 'depth': depth, 'name': name, 'shape': shape}
        sample = self.transform(sample)
        return sample

    def filter_files(self):
        assert len(self.images) == len(self.gts) == len(self.depths)
        images, gts, depths = [], [], []
        for img_path, gt_path, depth_path in zip(self.images, self.gts, self.depths):
            img, gt, depth = Image.open(img_path), Image.open(gt_path), Image.open(depth_path)
            if img.size == gt.size  == depth.size:
                images.append(img_path)
                gts.append(gt_path)
                depths.append(depth_path)
        self.images, self.gts, self.depths = images, gts, depths

    def rgb_loader(self, path):
        with open(path, 'rb') as f:
            img = Image.open(f)
            return img.convert('RGB')

    def binary_loader(self, path):
        with open(path, 'rb') as f:
            img = Image.open(f)
            return img.convert('L')

    def __len__(self):
        return self.size
    
class ImageLoader:
    def __init__(self, root, transform_list):
        if os.path.isdir(root):
            self.images = [os.path.join(root, f) for f in os.listdir(root) if f.endswith(('.jpg', '.png', '.jpeg'))]
            self.images = sorted(self.images)
        elif os.path.isfile(root):
            self.images = [root]
        self.size = len(self.images)
        self.transform = get_transform(transform_list)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == self.size:
            raise StopIteration
        image = Image.open(self.images[self.index]).convert('RGB')
        shape = image.size[::-1]
        name = self.images[self.index].split(os.sep)[-1]
        if name.endswith('.jpg'):
            name = name.split('.jpg')[0] + '.png'
            
        sample = {'image': image, 'name': name, 'shape': shape, 'original': image}
        sample = self.transform(sample)
        sample['image'] = sample['image'].unsqueeze(0)
        
        self.index += 1
        return sample

    def __len__(self):
        return self.size
    
class VideoLoader:
    def __init__(self, root, transform_list):
        if os.path.isdir(root):
            self.videos = [os.path.join(root, f) for f in os.listdir(root) if f.endswith(('.mp4', '.avi', 'mov'))]
        elif os.path.isfile(root):
            self.videos = [root]
        self.size = len(self.videos)
        self.transform = get_transform(transform_list)

    def __iter__(self):
        self.index = 0
        self.cap = None
        self.fps = None
        return self

    def __next__(self):
        if self.index == self.size:
            raise StopIteration
        
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.videos[self.index])
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        ret, frame = self.cap.read()
        
        if ret is False:
            self.cap.release()
            self.cap = None
            sample = {'image': None, 'shape': None, 'name': self.videos[self.index].split(os.sep)[-1], 'original': None}
            self.index += 1
        
        else:
            image = Image.fromarray(frame).convert('RGB')
            shape = image.size[::-1]
            sample = {'image': image, 'shape': shape, 'name': self.videos[self.index].split(os.sep)[-1], 'original': image}
            sample = self.transform(sample)
            sample['image'] = sample['image'].unsqueeze(0)
            
        return sample

    def __len__(self):
        return self.size