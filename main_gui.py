from planvec import gui
# USAGE
# python main_gui.py --output output

# import the necessary packages
import tkinter as tk
from planvec.gui import PlanvecGui
from imutils.video import VideoStream
import argparse
import time


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_arguments():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True,
                    help="Path to output directory to store snapshots")
    ap.add_argument("-p", "--picamera", type=int, default=-1,
                    help="Whether or not the Raspberry Pi camera should be used")
    ap.add_argument("-e", "--edge", type=str2bool, nargs='?',
                    const=True, default=False,
                    help="Activate debug canny edge detection mode.")
    ap.add_argument("-d", "--debug-input", type=str2bool, nargs='?',
                    const=True, default=False,
                    help="Use debug input image.")
    args = vars(ap.parse_args())
    return args


def get_video_stream(args):
    # initialize the video stream and allow the camera sensor to warmup
    print("[INFO] warming up camera...")
    video_stream = VideoStream(usePiCamera=args["picamera"] > 0).start()
    time.sleep(0.5)
    return video_stream


def main():
    args = parse_arguments()
    video_stream = get_video_stream(args)

    root = tk.Tk()
    app = PlanvecGui(master=root, video_stream=video_stream, output_path=args["output"],
                     edge_mode=args['edge'], debug_input=args['debug_input'])
    app.mainloop()


if __name__ == '__main__':
    main()
