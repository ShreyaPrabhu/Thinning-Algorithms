import matplotlib.pyplot as plt
from skimage import color
import numpy as np
import cv2
from PIL import Image
from skimage.util import invert
from PIL import Image
from scipy.misc import toimage
import time
import os
import glob

def neighbourst(thin_image, i, j):
	p2 = thin_image[i-1][j-1]
	p3 = thin_image[i-1][j]
	p4 = thin_image[i-1][j+1]
	p5 = thin_image[i][j+1]
	p6 = thin_image[i+1][j+1]
	p7 = thin_image[i+1][j]
	p8 = thin_image[i+1][j-1]
	p9 = thin_image[i][j-1]
	return p2,p3,p4,p5,p6,p7,p8,p9

def thinnesscheck(image):
	row,col = image.shape
	thinny = 0
	for i in range(2, row-1):
		for j in range(2, col-1):
			if(image[i][j]==1):
				p1 = image[i][j]
				p2,p3,p4,p5,p6,p7,p8,p9 = neighbourst(image, i, j)
				compute = (p1*p9*p2) + (p1*p9*p8) + (p1*p8*p7) + (p1*p7*p6) + (p1*p6*p5) + (p1*p5*p4) + (p1*p4*p3) + (p1*p3*p2)
				thinny = thinny + compute
	denominator = (max(row,col)-1)*(max(row,col)-1)
	denominator = denominator/4
	thinness = thinny/denominator
	return thinness

def zeroToOne(thin_image,i,j):
	p2 = thin_image[i-1][j-1]
	p3 = thin_image[i-1][j]
	p4 = thin_image[i-1][j+1]
	p5 = thin_image[i][j+1]
	p6 = thin_image[i+1][j+1]
	p7 = thin_image[i+1][j]
	p8 = thin_image[i+1][j-1]
	p9 = thin_image[i][j-1]
	count = 0;
	if(p2==0 and p3==1):
		count = count + 1
	if(p3==0 and p4==1):
		count = count + 1
	if(p4==0 and p5==1):
		count = count + 1
	if(p5==0 and p6==1):
		count = count + 1
	if(p6==0 and p7==1):
		count = count + 1
	if(p7==0 and p8==1):
		count = count + 1
	if(p8==0 and p9==1):
		count = count + 1
	if(p9==0 and p2==1):
		count = count + 1
	return count

def neighbours(x,y,image):
	img = image
	x_1, y_1, x1, y1 = x-1, y-1, x+1, y+1
	return [ img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1], img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1] ]

def transitions(neighbours):
	n = neighbours + neighbours[0:1]
	return sum( (n1, n2) == (0, 1) for n1, n2 in zip(n, n[1:]) )

def foregroundPixels(image):
	fgp = 0
	row, col = image.shape
	for i in range(2, row-1):
			for j in range(2, col-1):
				if(image[i][j]==1):
					fgp = fgp + 1
	return fgp


def zsAlgoIterationOne(image):
	Image_Thinned = image.copy()
	changing1 = changing2 = 1
	i = 0
	while changing1 or changing2:
		changes_occured = 0
		changing1 = []
		rows, columns = Image_Thinned.shape
		for x in range(1, rows - 1):
			for y in range(1, columns - 1):
				P2,P3,P4,P5,P6,P7,P8,P9 = n = neighbours(x, y, Image_Thinned)
				if (Image_Thinned[x][y] == 1 and 2 <= sum(n) <= 6 and transitions(n) == 1 and P2 * P4 * P6 == 0  and P4 * P6 * P8 == 0):
					changing1.append((x,y))
		for x, y in changing1: 
			Image_Thinned[x][y] = 0
			changes_occured = changes_occured + 1
		
		changing2 = []
		for x in range(1, rows - 1):
			for y in range(1, columns - 1):
				P2,P3,P4,P5,P6,P7,P8,P9 = n = neighbours(x, y, Image_Thinned)
				if (Image_Thinned[x][y] == 1 and 2 <= sum(n) <= 6 and transitions(n) == 1 and P2 * P4 * P8 == 0  and P2 * P6 * P8 == 0):
					changing2.append((x,y))    
		for x, y in changing2: 
			Image_Thinned[x][y] = 0
			changes_occured = changes_occured + 1
		i = i + 1
		print("Iteration: ", i , "changes_occured: ", changes_occured)
	return Image_Thinned

def sensitivitycheck(image, fg):
	row,col = image.shape
	sensitivity = 0
	for i in range(2, row-1):
		for j in range(2, col-1):
			if(image[i][j]==1):
				compute = zeroToOne(image,i,j)
				sensitivity = sensitivity + compute
	sensitivity = sensitivity/fg
	sensitivity = 1 - sensitivity
	return sensitivity

if __name__ == "__main__":
	test_path = "num"
	count = 0
	reduction_rate = 0
	sensitivity = 0
	thinness = 0
	start_time = time.time()
	for file in glob.glob(test_path + "/*.png"):
		count = count+1
		image = cv2.imread(file)
		image = color.rgb2gray(image)
		print(image.shape)
		fgps = foregroundPixels(invert(image))
		print("fgps: ", fgps)
		skeleton = zsAlgoIterationOne(invert(image))
		fgpst = foregroundPixels(skeleton)
		print("fgpst: ", fgpst)
		reduction_rate = reduction_rate + (((fgps-fgpst)/fgps)*100)
		sensitivity = sensitivity + sensitivitycheck(skeleton,fgps)
		thinnesst = thinnesscheck(skeleton)
		thinnesso = thinnesscheck(image)
		thinness = thinness + (1 - (thinnesst/thinnesso))
		im = toimage(skeleton)
		im.save(str(count)+".png")
	end_time = time.time()	# Used to stop time record
	seconds=end_time - start_time
	print ("Total time: ", seconds)
	print("Average time: ", seconds/count)
	print("Reduction rate: ", reduction_rate)
	print("Average Reduction rate: ", reduction_rate/count)
	print("sensitivity: ",sensitivity)
	print("Average sensitivty: ", sensitivity/count)
	print("Average thinness: ", thinness/count)