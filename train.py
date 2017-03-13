from keras.applications.inception_v3 import InceptionV3
from keras.preprocessing import image
from keras.models import Model, load_model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.utils import np_utils
from keras import backend as K
from PIL import Image
import numpy as np
import sys, os, json, ast
import scipy.misc

num_epochs = 50
batch_size = 32

def initialize_model(model_path):

    # create the base pre-trained model
    base_model = InceptionV3(weights='imagenet', include_top=False)

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    prediction_layer = Dense(128, activation='sigmoid')(x)
    model = Model(input=base_model.input, output=prediction_layer)

    for layer in base_model.layers:
        layer.trainable = False

    model.compile(optimizer='sgd', loss='binary_crossentropy', metrics=['accuracy'])
    model.save(model_path)

def train(model_path, batch_path):
    model = load_model(model_path)
    train_x, train_y = load_training_set(batch_path)
    model.fit(train_x, train_y, nb_epoch=num_epochs, batch_size=batch_size)
    model.save(model_path)

def load_training_set(batch_path):
    with open(batch_path, 'r') as data:
        labeled_files = json.load(data)
        num_samples = len(labeled_files)

        train_x = np.ndarray(shape=(num_samples, 299, 299, 3), dtype='float')
        train_y = np.ndarray(shape=(num_samples, 128), dtype='uint8')

        for i in range(num_samples):
            [image, label] = extract_image_data(labeled_files[i])
            train_x[i] = image
            train_y[i] = label

        # print num_samples, train_x.shape, train_y.shape
        # train_y = train_y.reshape([num_samples, 128, 1, 1])

        return train_x, train_y

def extract_image_data(image_tuple):
    [path, string_label_list] = image_tuple.split(' ', 1)
    label_list = ast.literal_eval(string_label_list)

    im = np.asarray(Image.open(path))

    # resize to our input shape
    im = scipy.misc.imresize(im, [299, 299])

    # Load and prepare ground truth
    multilabel = np.array(map(float, label_list)).astype(np.float32)
    return im, multilabel


if (__name__ == "__main__"):
    if (len(sys.argv) < 3):
        print "Require model and batch file path, exitting.\n"
        exit(0)

    else:
        model_path = sys.argv[1]
        batch_path = sys.argv[2]

    if (os.path.isfile(model_path)):
        train(model_path, batch_path)

    else:
        initialize_model(model_path)
