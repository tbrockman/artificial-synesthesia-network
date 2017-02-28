import sys, os, json, random

labeled = "labels.json"
unlabeled = "unlabeled.json"

def initialize_labels():

    file_array = []

    for root, dirs, files in os.walk('raw images'):
        for filename in files:
            if (filename.split('.')[-1] == 'jpg'):
                file_object = {
                    'path': os.path.join(root, filename),
                    'label': []
                }
                file_array.append(file_object)

    try:
        with open(unlabeled, 'w') as out:
            json.dump(file_array, out)
            out.close()

    except:
        print "Error opening file for intializing labels."
        exit(0)

def label_unlabeled():
    with open(unlabeled) as json_data:
        unlabeled_files = json.load(json_data)
        json_data.close()

    midi = ""
    while midi != "q":
        # open a random unlabled image
        index = random.randint(0, len(unlabeled_files))
        to_be_labeled = unlabeled_files[index]

        # open with outside program to avoid blocking using matplotlib/cv2
        os.system('eog "' + to_be_labeled['path'] + '" &')

        midi = str(raw_input("Midi notes (space separated integers [1, 127]): "))

        if midi == "q":
            break

        midi_notes = midi.split(' ')
        # convert midi notes to binary array
        zeros = [0] * 127
        for note in midi_notes:
            zeros[int(note)-1] = 1

        # add resulting binary array to labeled files
        label_file(to_be_labeled['path'], zeros)

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


def label_file(path, label):

    new_label = {
        'path': path,
        'label': label
    }

    try:
        with open(labeled, 'r+') as json_data:
            labeled_files = json.load(json_data)

            labeled_files.append(new_label)

            json_data.seek(0)
            json.dump(labeled_files, json_data)
            json_data.truncate()

    except:

        with open(labeled, "w") as json_data:

            labeled_files = [new_label]
            json.dump(labeled_files, json_data)


if __name__ == "__main__":
    label_unlabeled()
