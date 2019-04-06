#!/usr/bin/env python

import os
import cv2
import numpy as np
from tqdm import tqdm
import shutil
import matplotlib.pyplot as plt
import Image

        
def main(src_path):
#     src_path = '/home/sivananda/Something-Inc1/Data/'
    target_path = os.path.join(src_path,'Visualize/')
    folders = os.listdir(os.path.join(src_path,'Images'))
    np.random.shuffle(folders)

    for i in tqdm(range(len(folders[:]))):
        folder = folders[i]
        if target_path:
            os.makedirs(os.path.join(target_path,folder),exist_ok=True)
        image_files = os.listdir(os.path.join(src_path,'Images',folder))
        for file in image_files[:]:
            I = Image(src_path,folder,file)
            I.save_visual(target_path)

if __name__ == "__main__":
    
    ap = argparse.ArgumentParser()

    ap.add_argument("-s", "--src_path", required=True,
    help="Path to the source directory")

    args = vars(ap.parse_args())
    
    main(args["src_path"])