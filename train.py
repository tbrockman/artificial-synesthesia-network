import caffe
import os
import sys

sys.path.append("pycaffe/layers") # the datalayers we will use are in this directory.
sys.path.append("pycaffe") # the tools file is in this folder

workdir = './pascal_multilabel_with_datalayer'
if not os.path.isdir(workdir):
    os.makedirs(workdir)

caffe_root = '/home/theodore/Documents/caffe/'
sys.path.insert(1, caffe_root + 'python')

caffe.set_mode_gpu()
caffe.set_device(0)

solver = caffe.SGDSolver(os.path.join(workdir, 'solver.prototxt'))
solver.net.copy_from(caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel')
solver.test_nets[0].share_with(solver.net)
solver.solve()
