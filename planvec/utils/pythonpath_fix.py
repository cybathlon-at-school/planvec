import sys


def fix_ros_cv_path() -> None:
    """
    The ROS sourcing of setup.bash alters the PYTHONPATH and breaks OpenCV. This is an ugly
    fix in case it has been sourced and polluted the sys path.
    """
    ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
    if ros_path in sys.path:
        sys.path.remove(ros_path)
