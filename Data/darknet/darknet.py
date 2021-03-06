from ctypes import *
import math,os
import numpy as np
import random
import shutil
import argparse
from tqdm import tqdm

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

    

#lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib = CDLL("/home/sivananda/YOLO/darknet/libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

def detect(net, meta, image, fname='', target_base_path='', thresh=.5, hier_thresh=.5, nms=.45):
    im = load_image(image, 0, 0)
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
    num = pnum[0]
    if (nms): do_nms_obj(dets, num, meta.classes, nms);

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x-b.w/2, b.y-b.h/2, b.x+b.w/2, b.y+b.h/2)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_detections(dets, num)
    
    dict_cat_len = {}
    dict_cat = {}
   
    for i in range(len(res)):
        dict_cat_len[res[i][0].decode('utf8')] = 0
        dict_cat[res[i][0].decode('utf8')] = []
        
    
    for i in range(len(res)):
        dict_cat_len[res[i][0].decode('utf8')] += 1
        dict_cat[res[i][0].decode('utf8')].append([res[i][2][0]/im.w,res[i][2][1]/im.h,res[i][2][2]/im.w,res[i][2][3]/im.h])
       
    
    for keys in dict_cat.keys():
        cat = keys

        os.makedirs(os.path.join(target_base_path,'Labels',cat),exist_ok=True)
        with open(os.path.join(target_base_path,'Labels',cat,fname),'w') as f:
            f.write(str(dict_cat_len[keys])+'\n')
            for k in range(len(dict_cat[keys])):
                f.write(','.join(np.asarray(dict_cat[keys][k],dtype=np.str)))
                f.write('\n')
    
    return res,dict_cat_len

def main(src_path,target_path):
    net = load_net(b"cfg/yolov3.cfg", b"yolov3.weights", 0)
    files = os.listdir(src_path)
    for j in tqdm(range(len(files))):
        file = files[j]
        if not file.endswith('jpg') or file.endswith('png') or file.endswith('jpeg'):
            continue
            
        inp_file = os.path.join(src_path,file).encode('utf8')
        meta = load_meta(b"cfg/coco.data")
        r,d_cat = detect(net, meta, inp_file, fname=file.split('.')[0]+'.txt', target_base_path=target_path)
        for k in d_cat.keys():
            cat = k
            os.makedirs(os.path.join(target_path,'Images',cat),exist_ok=True)
            shutil.copy(os.path.join(src_path,file),os.path.join(target_path,'Images',cat,file))
#         print(r)
    
if __name__ == "__main__":
    #net = load_net("cfg/densenet201.cfg", "/home/pjreddie/trained/densenet201.weights", 0)
    #im = load_image("data/wolf.jpg", 0, 0)
    #meta = load_meta("cfg/imagenet1k.data")
    #r = classify(net, meta, im)
    #print r[:10]
    ap = argparse.ArgumentParser()

    ap.add_argument("-s", "--src_path", required=True,
    help="Path to the source directory")
    ap.add_argument("-t", "--target_path", required=True,
    help="Path to the target directory")

    args = vars(ap.parse_args())
    
    main(args["src_path"],args["target_path"])

    
    

