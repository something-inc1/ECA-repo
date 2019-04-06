import os,cv2
import matplotlib.pyplot as plt



class Image:

    def __init__(self,src_path,folder,file):
        self.img = cv2.imread(os.path.join(src_path,'Images',folder,file))
        self.src_path = src_path
        self.folder = folder
        self.file = file
        self.w = self.img.shape[1]
        self.h = self.img.shape[0]
        
    def write(self,tPath):
        self.check = cv2.imwrite(tPath,self.img)
    
    def show(self):
        plt.imshow(self.img)
        plt.show()
    
    def read_boxes(self):
        with open(os.path.join(self.src_path,'Labels',self.folder,self.file.split('.')[0]+'.txt'),'r') as f:
            lines = []
            boxes = []
            for line in f.readlines():
                lines.append(line)

            for i in range(1,int(lines[0])+1):
                box = [float(k) for k in lines[i].rstrip().split(',')]
                box[0] *= self.w
                box[1] *= self.h
                box[2] *= self.w
                box[3] *= self.h
                boxes.append(box)
            
            return boxes
    
    def draw(self):
        boxes = self.read_boxes()
        for i in range(len(boxes)):
            box = boxes[i]
            cv2.rectangle(self.img,(int(box[0]),int(box[1])),(int(box[2]),int(box[3])),color=(0,0,255),thickness=4)
            
    def save_visual(self,tPath):
        self.draw()
        self.write(os.path.join(tPath,self.folder,self.file))
