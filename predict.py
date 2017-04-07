from keras.models import load_model
from osc_handler import OSCHandler
import numpy as np
import sys, cv2, scipy.misc, time, os, PIL
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../WarpPerspective")
import warpperspective

tempo = 120
default_threshold = 0.1
last_prediction = np.array([])
saved_predictions = []
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def load_model_and_osc(model_path, osc_params):
    model = load_model(model_path)
    osc = OSCHandler(osc_params[0], osc_params[1])
    return model, osc

def convert_midi_values_to_notes(midi_array):
    converted = []
    for midi in midi_array:
        converted.append(convert_midi_to_note(midi))
    return converted

def convert_midi_to_note(midi):
    index = midi % 12
    return notes[index]

def predict_image_and_send_osc(model, image, osc, threshold=0.035):
    highest_midi, predictions = predict_image(model, image)
    close_midi = threshold_predictions(predictions, highest_midi, threshold)
    #saved_predictions.append(convert_midi_values_to_notes(close_midi))
    #saved_predictions.append(close_midi)
    if (osc):
        send_midi_on_osc(osc, close_midi)
    return close_midi.tolist()

def threshold_predictions(predictions, highest, threshold):
    value = predictions[0][highest]
    indices = (-predictions[0]).argsort()[:5]
    # print predictions[0][indices]
    close_midi = np.where(predictions > (value - threshold))
    return close_midi[1]

def send_midi_on_osc(osc, midi):
    #global last_prediction
    #if not np.array_equal(last_prediction, midi):
    #    last_prediction = midi
        osc.sendMessage('/cnn_midi', midi.tolist())

def predict_image(model, img):
    predictions = model.predict(img, batch_size=1)
    highest_midi = np.argmax(predictions[0])
    return highest_midi, predictions

def preprocess_frame_for_prediction(frame):
    img = scipy.misc.imresize(frame, [299, 299])
    img = img[np.newaxis, ...] # turn into batch of size 1
    return img

def capture_and_preprocess_webcam_image(warper=None):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if (warper):
        frame = warper.warp(frame)

    img = preprocess_frame_for_prediction(frame)
    return img, frame

def show_image_with_overlayed_midi(img, midi):
    notes = convert_midi_values_to_notes(midi)
    cv2.putText(img,str(notes),(10,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2)
    cv2.imshow('frame',img)
    if cv2.waitKey(100) & 0xFF == ord('q'):
        return 1
    else:
        return 0

def start_video_capture(model, osc, video_path):
    vidcap = cv2.VideoCapture(video_path)
    count = 0
    while(vidcap.isOpened()):

        success, frame = vidcap.read()
        count += 1
        if success and count % 10 == 0:
            img = preprocess_frame_for_prediction(frame)
            midi = predict_image_and_send_osc(model, img, osc)
            exit = show_image_with_overlayed_midi(frame, midi)
            if (exit):
                break

    vidcap.release()
    cv2.destroyAllWindows()

def batch_predict_folder(model, osc=None, folder_path="labeled", save=False, overlay=False):
    filenames = os.listdir(folder_path)

    if (save):
        saved_predictions = []

    for i in range(len(filenames)):
        if filenames[i].endswith(".jpg"):
            image_path = os.path.join(folder_path, filenames[i])
            raw = np.asarray(PIL.Image.open(image_path))
            img = preprocess_frame_for_prediction(raw)
            midi = predict_image_and_send_osc(model, img, osc)

            if (save):
                saved_predictions.append(midi)

            if overlay:
                exit = show_image_with_overlayed_midi(raw, midi)
                if (exit):
                    cv2.destroyAllWindows()
                    break

    return saved_predictions

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Need model path for predictions.'
        sys.exit(0)

    model_path = sys.argv[1]

    model, osc = load_model_and_osc(model_path, ('127.0.0.1', 57120))

    if len(sys.argv) > 2:
        path = sys.argv[2]
        if (os.path.isfile(path)):
            start_video_capture(model, osc, path)
        elif (os.path.isdir(path)):
            batch_predict_folder(model, osc, path, False, True, default_threshold)
        else:
            print 'Second argument must be a path to a file or a folder.'
            sys.exit(0)

    else:
        img, frame = capture_and_preprocess_webcam_image()
        warped = None
        wc = warpperspective.WarpCalibrator()
        warper = wc.calibrate(frame)

        while(1):
            img, frame = capture_and_preprocess_webcam_image(warper)
            midi = predict_image_and_send_osc(model, img, osc, default_threshold)
            exit = show_image_with_overlayed_midi(frame, midi)
            if (exit):
                cv2.destroyAllWindows()
                break
