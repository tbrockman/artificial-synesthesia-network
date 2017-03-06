# imports
import json
import time
import pickle
import scipy.misc
import skimage.io
import caffe
import ast

import numpy as np
import os.path as osp

from xml.dom import minidom
from random import shuffle
from threading import Thread
from PIL import Image

from tools import SimpleTransformer

class PascalMultilabelDataLayerSync(caffe.Layer):

    """
    This is a simple synchronous datalayer for training a multilabel model on
    PASCAL.
    """

    def setup(self, bottom, top):

        self.top_names = ['data', 'label']

        # === Read input parameters ===

        # params is a python dictionary with layer parameters.
        params = eval(self.param_str)

        # Check the parameters for validity.
        check_params(params)

        # store input as class variables
        self.batch_size = params['batch_size']

        # Create a batch loader to load the images.
        self.batch_loader = BatchLoader(params, None)

        # === reshape tops ===
        # since we use a fixed input image size, we can shape the data layer
        # once. Else, we'd have to do it in the reshape call.
        top[0].reshape(
            self.batch_size, 3, params['im_shape'][0], params['im_shape'][1])
        # 128 for num of classes
        top[1].reshape(self.batch_size, 128)

        print_info("PascalMultilabelDataLayerSync", params)

    def forward(self, bottom, top):
        """
        Load data.
        """
        for itt in range(self.batch_size):
            # Use the batch loader to load the next image.
            im, multilabel = self.batch_loader.load_next_image()
            if im is not None:
                # Add directly to the caffe data layer
                top[0].data[itt, ...] = im
                top[1].data[itt, ...] = multilabel

    def reshape(self, bottom, top):
        """
        There is no need to reshape the data, since the input is of fixed size
        (rows and columns)
        """
        pass

    def backward(self, top, propagate_down, bottom):
        """
        These layers does not back propagate
        """
        pass


class BatchLoader(object):

    """
    This class abstracts away the loading of images.
    Images can either be loaded singly, or in a batch. The latter is used for
    the asyncronous data layer to preload batches while other processing is
    performed.
    """

    def __init__(self, params, result):
        self.result = result
        self.batch_size = params['batch_size']
        self.data_path = params['data_path']
        self.im_shape = params['im_shape']
        # get list of image indexes.
        list_file = params['split'] + '.txt'
        f = open(osp.join(self.data_path, list_file))
        self.imagelist = json.load(f)
        self._cur = 0  # current image
        # this class does some simple data-manipulations
        self.transformer = SimpleTransformer()

        print "BatchLoader initialized with {} images".format(
            len(self.imagelist))

    def load_next_image(self):
        """
        Load the next image in a batch.
        """

        if len(self.imagelist) == 0:
            return None, None

        # Did we finish an epoch?
        if self._cur == len(self.imagelist):
            self._cur = 0
            shuffle(self.imagelist)

        # Load an image
        image_tuple = self.imagelist[self._cur]  # Get the image tuple
        [path, string_label_list] = image_tuple.split(' ', 1)
        label_list = ast.literal_eval(string_label_list)

        im = np.asarray(Image.open(path))
        im = scipy.misc.imresize(im, self.im_shape)  # resize

        # do a simple horizontal flip as data augmentation
        flip = np.random.choice(2)*2-1
        im = im[:, ::flip, :]

        # Load and prepare ground truth
        multilabel = np.array(map(float, label_list)).astype(np.float32)

        self._cur += 1
        return self.transformer.preprocess(im), multilabel

def check_params(params):
    """
    A utility function to check the parameters for the data layers.
    """
    assert 'split' in params.keys(
    ), 'Params must include split (train, val, or test).'

    required = ['batch_size', 'data_path', 'im_shape']
    for r in required:
        assert r in params.keys(), 'Params must include {}'.format(r)


def print_info(name, params):
    """
    Output some info regarding the class
    """
    print "{} initialized for split: {}, with bs: {}, im_shape: {}.".format(
        name,
        params['split'],
        params['batch_size'],
        params['im_shape'])
