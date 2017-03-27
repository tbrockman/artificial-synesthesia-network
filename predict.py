from keras.models import load_model
from osc_handler import OSCHandler
import numpy as np
import sys, cv2, scipy.misc, time, os, PIL
import mingus.core.scales as scales
import matplotlib.pyplot as plt

tempo = 120
threshold = 0.1
last_prediction = np.array([])
saved_predictions = []
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
scale_count = {}

def convert_midi_values_to_notes(midi_array):
    converted = []
    for midi in midi_array:
        converted.append(convert_midi_to_note(midi))
    return converted

def convert_midi_to_note(midi):
    index = midi % 12
    return notes[index]

def predict_image_and_send_osc(model, image, osc):
    global saved_predictions
    highest_midi, predictions = predict_image(model, image)
    close_midi = threshold_predictions(predictions, highest_midi)
    #saved_predictions.append(convert_midi_values_to_notes(close_midi))
    #saved_predictions.append(close_midi)
    send_midi_on_osc(osc, close_midi)
    # print close_midi.tolist()

def threshold_predictions(predictions, highest):
    value = predictions[0][highest]
    indices = (-predictions[0]).argsort()[:5]
    # print predictions[0][indices]
    close_midi = np.where(predictions > (value - threshold))
    return close_midi[1]

def send_midi_on_osc(osc, midi):
    global last_prediction
    if not np.array_equal(last_prediction, midi):
        last_prediction = midi
        osc.sendMessage('/cnn_midi', midi.tolist())

def predict_image(model, img):
    predictions = model.predict(img, batch_size=1)
    highest_midi = np.argmax(predictions[0])
    return highest_midi, predictions

def preprocess_frame_for_prediction(frame):
    img = scipy.misc.imresize(frame, [299, 299])
    img = img[np.newaxis, ...] # turn into batch of size 1
    return img

def capture_and_preprocess_webcam_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    img = preprocess_frame_for_prediction(frame)
    return img, frame

def start_video_capture(model, osc, video_path):
    vidcap = cv2.VideoCapture(video_path)

    while(vidcap.isOpened()):
        success, frame = vidcap.read()
        if success:
            img = preprocess_frame_for_prediction(frame)
            predict_image_and_send_osc(model, img, osc)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    vidcap.release()
    cv2.destroyAllWindows()

def batch_predict_folder(model, osc, folder_path):
    global scale_count
    filenames = os.listdir(folder_path)

    for i in range(len(filenames)):
        if filenames[i].endswith(".jpg"):
            image_path = os.path.join(folder_path, filenames[i])
            raw = np.asarray(PIL.Image.open(image_path))
            img = preprocess_frame_for_prediction(raw)
            predict_image_and_send_osc(model, img, osc)
            # imgplot = plt.imshow(raw)
            # plt.show(block=False)
            # time.sleep(1.0 / (2 * tempo / 60))
            # plt.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Need model path for predictions.'
        sys.exit(0)

    model_path = sys.argv[1]
    model = load_model(model_path)
    osc = OSCHandler('127.0.0.1', 57120)

    if len(sys.argv) > 2:
        path = sys.argv[2]
        if (os.path.isfile(path)):
            start_video_capture(model, osc, path)
        elif (os.path.isdir(path)):
            batch_predict_folder(model, osc, path)
        else:
            print 'Second argument must be a path to a file or a folder.'
            sys.exit(0)

    else:

        while(1):
            img, frame = capture_and_preprocess_webcam_image()
            predict_image_and_send_osc(model, img, osc)
            imgplot = plt.imshow(frame)
            plt.show(block=False)
            time.sleep(1.0 / (tempo / 60))
            plt.close()
