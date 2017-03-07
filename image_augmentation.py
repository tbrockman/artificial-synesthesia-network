import imgaug as ia
import numpy as np
from imgaug import augmenters as iaa


# take numpy image and augment
def augment_image(image, times=10):
    st = lambda aug: iaa.Sometimes(0.5, aug)

    seq = iaa.Sequential([
            iaa.Fliplr(0.5),
            st(iaa.Crop(percent=(0, 0.1))),
            st(iaa.GaussianBlur((0, 3.0))),
            st(iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.05), per_channel=0.5)),
            st(iaa.Add((-10, 10), per_channel=0.5)),
            st(iaa.Multiply((0.9, 1.1), per_channel=0.5)),
            st(iaa.ContrastNormalization((0.5, 2.0), per_channel=0.5)),
            st(iaa.Affine(
                scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
                translate_px={"x": (-16, 16), "y": (-16, 16)},
                rotate=(-45, 45),
                shear=(-16, 16),
                order=[0, 1],
                cval=(0, 1.0),
                mode=ia.ALL
            )),
        ],
        random_order=True
    )

    augmented = []
    for i in range(times):
        augmented.append(image)

    aug_list = seq.augment_images(augmented)
    return aug_list
