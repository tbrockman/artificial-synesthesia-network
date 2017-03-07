import sys, os, json, random
from scipy import misc
import image_augmentation

labeled = ""
unlabeled = "unlabeled.txt"
labeled_folder = "labeled"

def initialize_labels():

    file_array = []

    for root, dirs, files in os.walk('data'):
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

def label_unlabeled():
    with open(unlabeled) as f:
        unlabeled_files = json.load(f)
        f.close()

    midi = ""
    while midi != "q":
        # open a random unlabled image
        index = random.randint(0, len(unlabeled_files))
        to_be_labeled = unlabeled_files[index]
        [path, label] = to_be_labeled.split(' ', 1)

        # open with outside program to avoid blocking using matplotlib/cv2
        os.system('eog "' + path + '" &')

        midi = str(raw_input("Midi notes (space separated integers [0, 127]): "))

        if midi == "q":
            break

        midi_notes = midi.split(' ')
        # convert midi notes to binary array
        zeros = [0] * 128
        for note in midi_notes:
            zeros[int(note)] = 1

        # add resulting binary array to labeled files
        label_file(path, zeros)

        # remove from unlabeled list and unlabeled json file
        unlabeled_files.pop(index)
        remove_from_unlabeled_file(index)

        # kill image window
        os.system("killall -9 eog")

    print "Exitting labeling program"
    os.system("killall -9 eog")
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

def label_file(path, label):

    # change this
    new_label = path + ' ' + str(label)

    # read image
    image = misc.imread(path)

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
    # if program started with optional argument of filename for
    # label output, output to that file
    # otherwise assum we want to add to training
    if (len(sys.argv) > 1):
        labeled += sys.argv[1] + '.txt'
    else:
        labeled += 'train.txt'

    label_unlabeled()
    #initialize_labels()
