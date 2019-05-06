import cv2
import numpy as np
from PIL import Image
import os
import pytesseract as pt
from operator import itemgetter
import sqlite3
from datetime import date
import time

"""-----
def InputData( license_plate_number ):
	conn = sqlite3.connect('vehicles.db')
	c = conn.cursor()
	c.execute("INSERT INTO car_entry VALUES ('%s','%s','%s')" % (license_plate_number, date.today(), time.time()))
	conn.commit()
	a = c.execute("select * from car_entry")
	#print a.fetchall()	
-----"""

def SortContours(a):
    #print 'sort contours function'
    A = []
    #inner_a = []
    for i in xrange(-1, len(a)-1):
        x,y,w,h = cv2.boundingRect(a[i])
        A.append((x,y,w,h))


    sorted_tuples = sorted(A, key=itemgetter(0))
    del sorted_tuples[0]
    #print sorted_tuples
    
    return sorted_tuples

####################################################################################################################        


def CharacterSegmentation(roi_final_img):
    #print ' inside chracter segmentation function'
    character_segmentation_return, character_segmentation_contours, character_segmentation_hierarchy = cv2.findContours(roi_final_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cs_roi_cnt = []
    cs_roi_img = []
    character_segmentation_sorted_tuples = SortContours(character_segmentation_contours)
    code = ""
    for a in character_segmentation_sorted_tuples:    
        if a[2] > 11 and a[3] > 12:
            #print "w=",a[2],"h=",a[3]    
            cs_roi = roi_final_img[a[1]:a[1]+a[3], a[0]:a[0]+a[2]]
            cv2.imwrite("cs_roi.jpg", cs_roi)
            #print "="*50
            code_temp = pt.image_to_string(Image.open("cs_roi.jpg"),config='-psm 10')
            #print code_temp
            code = code + code_temp
	    print "A"
            cv2.imshow("cs_roi", cs_roi)
            cv2.waitKey(0)
            os.remove('cs_roi.jpg')
    code = ''.join(e for e in code if e.isalnum())    
    print 'License Plate Number: %s' % code
    #-----InputData(code)    
    os.remove('roi_final.jpg')
    return

###############################################################################################################
#os.system("fswebcam -r 640x480 -S 20 --no-banner --quiet alpr.jpg")
#to automatically pictures from webcam.
image = cv2.imread('b.jpg',0)
#print 'image read'
#reading the image with name alpr in gray scale.
ret,img_thresh = cv2.threshold(image,127,255,0)
#print 'threshold image'

img_2,contours,hierarchy = cv2.findContours(img_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#print 'found contours'
roi_cnt = []
roi_img = []
#print (len(contours))

for i in xrange(-1,len(contours)-1):
    cnt = contours[i]

    x, y, w, h = cv2.boundingRect(cnt)
    roi = img_thresh[y:y+h, x:x+w]
    
    asp_ratio = w/h
    
    if 3 <= asp_ratio <= 5  and  w > 125  and  h > 25:
        roi_cnt.append(cnt)
        roi_img.append(roi)

    
    

#imrow = roi.shape[0]
#imcol = roi.shape[1]
#print (imcol/imrow)
#print (len(roi_cnt))
for i in xrange(-1,len(roi_cnt)-1):
    #print 'inside for loop for region of interest contours'
    #showing region of interest that is number plate image or images that may have number plates.
    cv2.imshow("roi", roi_img[i])
    #wait for user to close the roi image explicitly.
    cv2.waitKey(0)
    # 3 lines below defines a box around number plate area in the image.
    rect = cv2.minAreaRect(roi_cnt[i])
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    #print "%s%s",("rect keyword value",rect)
    #print box
    # draw filtered contours on the image
    img_with_contours = cv2.drawContours(image,[box],0,(0,255,0),2)
    cv2.imshow("blob_with_noise",img_with_contours)
    cv2.waitKey(0)
    # license plate image
    roi_final = cv2.imwrite("roi_final.jpg",roi_img[i])
    # function for character by character segmentation of the image
    result = pt.image_to_string(Image.open('roi_final.jpg'))
    if len(result) > 0:
        CharacterSegmentation(roi_img[i])
    else:
        os.remove('roi_final.jpg')    

###################################################################################################################

#image: Original Image
#img_thresh: Threshold image
#img_2: Intermediate image with contours
#cnt : contour(blob) required
#roi : Region Of Interest
#img_with_contours: Image with Contours
