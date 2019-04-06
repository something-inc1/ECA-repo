Get pretrained YOLO model and weights:
	
	1.	git clone https://github.com/pjreddie/darknet

	2.	cd darknet

	3.	make

	4.	wget https://pjreddie.com/media/files/yolov3.weights	


Now, cd python

Replace darknet.py with this file.

Instructions for execution:

	parameters: 

		--src_path	:	Path to the source directory
	
		--target_path	:	Path to the target directory

	command line (from darknet directory):
	
 		python python/darknet.py --src_path /path/to/your/image/dir --target_path /path/to/your/annotation/dir

	example usage: python3 python/darknet.py  --src_path data/ --target_path ~/Something-Inc1/Data/

This script will sort the dataset based on the categories also annotating bounding boxes of the items in those categories.

Target directory format:

	target_base_path
		|
		|---Images/
		|-----|
		|-----|---cat1/
		|-----|---cat2/
		|-----|  ...
		|-----|---catn/
		|--- Labels/
		|-----|
		|-----|---cat1/
		|-----|---cat2/
		|-----|  ...
		|-----|---catn/

