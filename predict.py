from keras.models import load_model
from osc_handler import OSCHandler
import numpy as np
import sys, cv2, scipy.misc, time
import matplotlib.pyplot as plt

tempo = 240
threshold = 0.1

def predict_image_and_send_osc(image, osc):
    highest_midi, predictions = predict_image(model, img)
    close_midi = threshold_predictions(predictions, highest_midi)
    send_midi_on_osc(osc, close_midi[1].tolist())
    print close_midi[1].tolist()

def threshold_predictions(predictions, highest):
    value = predictions[0][highest]
    close_midi = np.where(predictions > value - threshold)
    return close_midi

def send_midi_on_osc(osc, midi):
    return osc.sendMessage('/cnn_midi', midi)

def predict_image(model, img):
    predictions = model.predict(img, batch_size=1)
    highest_midi = np.argmax(predictions[0])
    return highest_midi, predictions

def preprocess_frame(frame):
    img = scipy.misc.imresize(frame, [299, 299])
    img = img[np.newaxis, ...] # turn into batch of size 1
    return img

def capture_and_preprocess_webcam_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    img = preprocess_frame(frame)
    return img, frame

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Need model path for predictions.'
        sys.exit(0)

    model_path = sys.argv[1]
    model = load_model(model_path)
    osc = OSCHandler('127.0.0.1', 57120)

    if len(sys.argv) > 2:
        video_path = sys.argv[2]
        vidcap = cv2.VideoCapture(video_path)
        success, frame = vidcap.read()
        success = True
        while success:
          success, frame = vidcap.read()
          img = preprocess_frame(frame)
          predict_image_and_send_osc(img, osc)
          imgplot = plt.imshow(frame)
          plt.show(block=False)
          time.sleep(1.0 / (tempo / 60))
          plt.close()

    else:

        while(1):
            img, frame = capture_and_preprocess_webcam_image()
            predict_image_and_send_osc(img, osc)
            imgplot = plt.imshow(frame)
            plt.show(block=False)
            time.sleep(1.0 / (tempo / 60))
            plt.close()
