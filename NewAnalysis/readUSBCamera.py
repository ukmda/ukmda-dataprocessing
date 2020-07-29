import cv2

def ShowVideo(id=0):
# Open the device at the ID 0
	cap = cv2.VideoCapture(0)

	#Check whether user selected camera is opened successfully.
	if not (cap.isOpened()):
		print('Could not open video device')

	#To set the resolution
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

	# Capture frame-by-frame
	while(True):
		ret, frame = cap.read()
		cv2.imshow('preview',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()

def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 100
    while i > 0:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr

a=returnCameraIndexes()
print(a)

