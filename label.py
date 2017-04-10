import sys, os, json, random, cv2, rtmidi
from scipy import misc
from osc_handler import OSCHandler
import image_augmentation

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../WarpPerspective")
import warpperspective

labeled = ""
unlabeled = "performance_unlabeled.txt"
unlabeled_folder = "wikicommon_images"
labeled_folder = "performance_training_set"
held_notes = []
osc_handler = None

class MidiConnection:

    def __init__(self, port, callback):
        self.midi = rtmidi.MidiIn()
        available_ports = self.midi.get_ports()
        if len(available_ports) > port:
            self.midi.set_callback(callback)
            self.midi.open_port(port)

def initialize_labels():

    file_array = []

    for root, dirs, files in os.walk(unlabeled_folder):
        for filename in files:
            if (filename.split('.')[-1] == 'jpg'):
                file_string = os.path.join(root, filename) + ' ' + str([])
                file_array.append(file_string)

    try:
        with open(unlabeled, 'w') as out:
            json.dump(file_array, out)
            out.close()

    except:
        print "Error opening file for intializing labels."
        exit(0)

def to_binary_array_label(label, length):
    binary_array = [0] * length
    for note in label:
        binary_array[note] = 1
    return binary_array

def label_unlabeled(folder):
    global osc_handler
    global held_notes

    osc_handler = OSCHandler('127.0.0.1', 57120)
    midi_connection = MidiConnection(1, midi_callback)
    file_array = []

    if folder:
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if (filename.split('.')[-1] == 'jpg'):
                    file_string = os.path.join(root, filename) + ' ' + str([])
                    file_array.append(file_string)

    while len(file_array[:]) > 0:
        # open a random unlabled image
        index = random.randint(0, len(file_array))
        to_be_labeled = file_array[index]
        [path, label] = to_be_labeled.split(' ', 1)

        frame = cv2.imread(path)

        if not frame == None:
            frame = misc.imresize(frame, [299, 299])
            cv2.imshow('frame', frame)
            key = cv2.waitKey()

            if key & 0xFF == ord('q'):
                break

            else:

                print held_notes
                label = to_binary_array_label(held_notes, 8)

                # add resulting binary array to labeled files
                label_file(path, label)
                file_array.pop(index)

        else:
            file_array.pop(index)
            continue

    print "Exiting labeling program"
    sys.exit(0)

def remove_from_unlabeled_file(index):
    with open(unlabeled, 'r') as read_json:
        unlabeled_files = json.load(read_json)
        read_json.close()

    unlabeled_files.pop(index)

    with open(unlabeled, 'w') as write_json:
        json.dump(unlabeled_files, write_json)
        write_json.close()

def create_augmented_images_in_folder(original_name, images, folder):
    paths = []
    for i in range(len(images)):
        path = os.path.join(folder, original_name + '_' + str(i) + '.jpg')
        misc.imsave(path, images[i])
        paths.append(path)
    return paths

def move_original_file_to_folder(original_path, filename, folder):
    new_path = os.path.join(folder, filename + '.jpg')
    os.rename(original_path, new_path)
    return new_path

def midi_callback(midi_tuple, data):
    global held_notes

    midi_data = midi_tuple[0]
    velocity = midi_data[2]
    note = midi_data[1] - 65 # because we dont have a midi keyboard that goes to 0

    if (note >= 0 and note < 8 ): # only accept notes [0, 8)
        if (velocity == 0):
            held_notes.remove(note)
            osc_handler.sendMessage('/noteoff', note)
        else:
            held_notes.append(note)
            osc_handler.sendMessage('/noteon', note)

def label_video(video_path):
    global osc_handler
    global held_notes

    vidcap = cv2.VideoCapture(video_path)
    count = 0
    warped = None
    success, frame = vidcap.read()
    wc = warpperspective.WarpCalibrator()
    warper = wc.calibrate(frame)
    osc_handler = OSCHandler('127.0.0.1', 57120)
    midi_connection = MidiConnection(1, midi_callback)

    while(vidcap.isOpened()):

        success, frame = vidcap.read()
        count += 1
        if success and count % 100 == 0:

            frame = warper.warp(frame)
            cv2.imshow('frame', frame)
            key = cv2.waitKey(100)

            if key & 0xFF == ord('q'):
                break
            else:

                augmented_images = image_augmentation.augment_image(frame)
                videoname = video_path.split("/")[-1].split(".")[0]
                filename = videoname + "_" + str(count) + ".jpg"
                paths = create_augmented_images_in_folder(videoname, augmented_images, labeled_folder)
                # save original image as well
                cv2.imwrite(os.path.join(labeled_folder, filename), frame)
                paths.append(os.path.join(labeled_folder, filename))

                label = to_binary_array_label(held_notes, 8)

                try:
                    with open(labeled, 'r+') as f:
                        labeled_files = json.load(f)
                        for path in paths:
                            labeled_files.append(path + ' ' + str(label))

                        f.seek(0)
                        json.dump(labeled_files, f)
                        f.truncate()
                        f.close()

                except:

                    with open(labeled, "w") as f:
                        labeled_files = []
                        for path in paths:
                            labeled_files.append(path + ' ' + str(label))
                        json.dump(labeled_files, f)

                continue
        elif not success:
            break


def label_file(path, label):

    # change this
    new_label = path + ' ' + str(label)

    # read image
    image = misc.imread(path)
    image = misc.imresize(image, [299, 299])

    # apply image augmentation
    augmented_images = image_augmentation.augment_image(image)
    filename = path.split('/')[-1].strip('.jpg')
    paths = create_augmented_images_in_folder(filename, augmented_images, labeled_folder)
    new_path = move_original_file_to_folder(path, filename, labeled_folder)
    paths.append(new_path)

    try:
        with open(labeled, 'r+') as f:
            labeled_files = json.load(f)
            for path in paths:
                labeled_files.append(path + ' ' + str(label))

            f.seek(0)
            json.dump(labeled_files, f)
            f.truncate()
            f.close()

    except:

        with open(labeled, "w") as f:
            labeled_files = []
            for path in paths:
                labeled_files.append(path + ' ' + str(label))
            json.dump(labeled_files, f)


if __name__ == "__main__":
    if (len(sys.argv) > 1):
        labeled += sys.argv[1]
        label_unlabeled(sys.argv[2])
        #label_video(sys.argv[2])

    else:
        initialize_labels()
