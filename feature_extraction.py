# Credit due to
# https://github.com/BVLC/caffe/blob/master/examples/00-classification.ipynb

import numpy as np
import sys, os, caffe, cv2, Queue, time
import matplotlib.pyplot as plt
from threading import Thread
from osc_handler import OSCHandler

image_queue = Queue.Queue(maxsize=25)

class CnnThread(Thread):
    def __init__(self, transformer, network):
        Thread.__init__(self)
        self.osc = OSCHandler('127.0.0.1', 57120)
        self.transformer = transformer
        self.network = network

    def sendOscMessage(self, message):
        self.osc.sendMessage('/cnn_midi', message)

    def run(self):
        transformer = self.transformer
        net = self.network

        while(True):
            caffe.set_mode_gpu()
            caffe.set_device(0)

            image = image_queue.get()
            start = time.time()

            transformed_image = transformer.preprocess('data', image)

            # copy the image data into the memory allocated for the net
            net.blobs['data'].data[...] = transformed_image

            ### perform classification
            output = net.forward(start='data', end='prob')
            # self.sendOscMessage(net.blobs['pool5/7x7_s1'])

            # output_prob = output['prob'][0]  # the output probability vector for the first image in the batch

            self.sendOscMessage(np.argmax(output['prob'][0]) % 127);

            finish = time.time()
            print 'time spent doing classification: ' + str(finish-start)

            image_queue.task_done()


caffe_root = '/home/theodore/Documents/caffe/'
model_folder = caffe_root + 'models/bvlc_googlenet/'
sys.path.insert(1, caffe_root + 'python')
model_def = model_folder + 'deploy.prototxt'
model_weights = model_folder + 'bvlc_googlenet.caffemodel'

if not os.path.isfile(model_weights):
    print "GoogleNet not found. Exiting."
    sys.exit(0)

net = caffe.Net(model_def, model_weights, caffe.TEST)

# load the mean ImageNet image (as distributed with Caffe) for subtraction
mu = np.load(caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy')
mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values

# create transformer for the input called 'data'
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR

worker_cnn = CnnThread(transformer, net)
worker_cnn.daemon = True
worker_cnn.start()

cap = cv2.VideoCapture(0)
for i in range(1, 25):
    # Capture frame-by-frame
    ret, frame = cap.read()
    image_queue.put(frame)
    time.sleep(0.25)

# When everything done, release the capture
cap.release()

image_queue.join()
print 'All webcam images consumed.'
