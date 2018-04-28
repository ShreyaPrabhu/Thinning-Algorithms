from skimage import color
import numpy as np
import cv2
from PIL import Image
from skimage.util import invert
import matplotlib.pyplot as plt
import cv2
from scipy.misc import toimage
import time
import os
import glob


""" Check the Continuity and if given point is Endpoint 
		1.Continuity refers to transition from 0 to 1 of the 8 neighbour of given point(i,j), 
		considering the neighbours in clockwise 
		2.A given point(i,j) is said to be Endpoint if it is connected to just one another pixel.
		That is only one neighbouring pixel is black(or 1)
"""
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
	endpoint = 0;
	if(p2+p3+p4+p5+p6+p7+p8+p9 == 1):
		endpoint = 1
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
	return count,endpoint


def zeroToOneOne(thin_image,i,j):
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

# To plot image during iterations (Can be removed later)
def showImage(image, newImage):
	fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4),
                         sharex=True, sharey=True,
                         subplot_kw={'adjustable': 'box-forced'})

	ax = axes.ravel()

	ax[0].imshow(image, cmap=plt.cm.gray)
	ax[0].axis('off')
	ax[0].set_title('original', fontsize=20)

	ax[1].imshow(newImage, cmap=plt.cm.gray)
	ax[1].axis('off')
	ax[1].set_title('newImage', fontsize=20)

	fig.tight_layout()
	plt.show()

"""
	Stentiford Algorithm
		1.Find a pixel location (i,j) where the pixels in the image match those in T1.
		2.If central pixel is not an endpoint and has connectivity number as 1, then mark
		the pixel for deletion
		3.Update the output image by deleting the pixels marked in previous step
		4.Repeat same with the rest of the Templates
		
		
	Templates
		T1				T2					T3					T4
	
		X  0  X			X  X  X				X  1  X				X  X  X
		X  1  X			0  1  1				X  1  X				1  1  0
		X  1  X			X  X  X				X  0  X				X  X  X
		
	8 Neighbours 
	
					P2   P3   P4   |   (i-1,j-1)   (i-1,j)   (i-1,j+1)
					P9   P1   P5   |   (i,j-1)     (i,j)     (i,j+1)
					P8   P7   P6   |   (i+1,j-1)   (i+1,j)   (i+1,j+1)
	
"""

def stentiford(image):
	# Make copy of the image so that original image is not lost
	thin_image = image.copy()
	row, col = thin_image.shape
	check = 2
	template = 1
	outImage = 1
	# Perform iterations as long as there are pixels marked for deletion
	iteration = 0
	total_changes = 0
	while(outImage):
		# Make outImage empty
		outImage = []
		changes = 0
		iteration = iteration + 1 
		# Loop through the pixels of the thin_image
		for i in range(2, row-1):
			for j in range(2, col-1):
				# Proceed only if pixel in consideration is Black(1)
				if(thin_image[i][j]==1):
					p0 = thin_image[i][j]
					p1 = thin_image[i-1][j]
					p2 = thin_image[i][j+1]
					p3 = thin_image[i+1][j]
					p4 = thin_image[i][j-1]
					if(template==1):
						template_match = (p1==0 and p3==1)
					if(template==2):
						template_match = (p2==1 and p4==0)
					if(template==3):
						template_match = (p1==1 and p3==0)
					if(template==4):
						template_match = (p2==0 and p4==1)
					connectivity, isEndpoint = zeroToOne(thin_image,i,j)
					if(template_match==1):
						if(connectivity == 1):
							if(isEndpoint== 0):
								outImage.append((i,j))
		

		# Delete the pixels marked for deletion
		for i,j in outImage:
			thin_image[i][j] = 0
			changes = changes + 1
		template = template+1
		if(template==5):
			template = 1
		print("iteration: ", iteration, "changes: ", changes)
		total_changes = total_changes + changes

	print("total_changes: ", total_changes)
	return thin_image

def sensitivitycheck(image, fg):
	sensitivity = 0
	row,col = image.shape
	for i in range(2, row-1):
		for j in range(2, col-1):
			if(image[i][j]==1):
				compute = zeroToOneOne(image,i,j)
				sensitivity = sensitivity + compute
	sensitivity = sensitivity/fg
	sensitivity = 1 - sensitivity
	return sensitivity


def foregroundPixels(image):
	fgp = 0
	row, col = image.shape
	for i in range(2, row-1):
			for j in range(2, col-1):
				if(image[i][j]==1):
					fgp = fgp + 1
	return fgp

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
		fgps = foregroundPixels(invert(image))
		print("fgps: ", fgps)
		skeleton = stentiford(invert(image))
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
