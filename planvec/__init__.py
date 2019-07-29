import sys

# Import sub packages such that they can be used as planvec.io for example without explicit import
import planvec.io
import planvec.img_proc
import planvec.vizualization

# open cv is somehow not compatible with ROS, so if the ROS dist packages are in the python path, we remove it
if '/opt/ros/kinetic/lib/python2.7/dist-packages' in sys.path:
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
