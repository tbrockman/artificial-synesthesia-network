from keras.models import load_model
from osc_handler import OSCHandler
import numpy as np
import sys, cv2, scipy.misc, time

def capture_and_preprocess_webcam_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    img = scipy.misc.imresize(frame, [299, 299])
    img = img[np.newaxis, ...] # turn into batch of size 1
    return img

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Need model path for predictions.'

    else:
        model_path = sys.argv[1]
        model = load_model(model_path)
        osc = OSCHandler('127.0.0.1', 57120)

        while(1):

            img = capture_and_preprocess_webcam_image()
            predictions = model.predict(img, batch_size=1)
            highest_midi = np.argmax(predictions[0])
            value = predictions[0][highest_midi]
            close_midi = np.where(predictions > value - 0.01)
            osc.sendMessage('/cnn_midi', close_midi[1].tolist())
            print close_midi[1].tolist(), highest_midi
            time.sleep(0.5)
