from keras.models import load_model
from osc_handler import OSCHandler
import numpy as np
import sys, cv2, scipy.misc

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Need model path for predictions.'
    else:
        model_path = sys.argv[1]
        model = load_model(model_path)
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        im = scipy.misc.imresize(frame, [299, 299])
        im = im[np.newaxis, ...] # turn into batch of size 1
        predictions = model.predict(im, batch_size=1)
        print prediction > 0.7
