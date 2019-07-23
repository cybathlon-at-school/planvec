import sys

# open cv is somehow not compatible with ROS, so if the ROS dist packages are in the python path, we remove it
if '/opt/ros/kinetic/lib/python2.7/dist-packages' in sys.path:
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
