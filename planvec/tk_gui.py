import os
import cv2
import tkinter as tk
from PIL import Image
import matplotlib.pyplot as plt

import threading
import datetime
import numpy as np

import planvec
from planvec import pipeline
from planvec import conversions
from planvec.common import PROJECT_ROOT_PATH

ASSETS_DIR = os.path.join(PROJECT_ROOT_PATH, 'test', 'assets')
PANEL_POSITIONS = {'video': 'left', 'processed': 'right'}


class PlanvecGui(tk.Frame):
    """Tkinter-based GUI for the planvec package. Starts the webcam and let's the user take a picture to run the
    planvec processing pipeline over the image."""

    def __init__(self, master, video_stream, output_path, edge_mode, debug_input, test_img):
        """Constructor for PlanvecGui class.
        Arguments
        ---------
            video_stream: instance of imutils.video.Videostream
            output_path: path to output directory
        """
        super().__init__(master)
        self.master = master

        self.video_stream = video_stream
        self.output_path = output_path
        self.edge_mode = edge_mode
        self.debug_input = debug_input
        self.thread = None
        self.stop_event = None
        print(ASSETS_DIR)
        print(test_img)
        self.debug_img = planvec.io.read_img(ASSETS_DIR, test_img, to_bgr=True)

        # initialize panels, buttons and such
        self.panel_content = {'video': None, 'processed': None}
        self.panels = {'video': None, 'processed': None}
        self.buttons = self.setup_buttons()
        self.video_panel = None
        self.processed_panel = None
        self.pack()

        # start a thread that constantly pools the video sensor for the most recently read current_frame
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.video_loop, args=())
        self.thread.start()

        # set a callback to handle when the window is closed
        self.master.wm_title("Planvec. Converting hand written gripper plans to vectorized graphics.")
        self.master.wm_protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_buttons(self):
        buttons = {}
        buttons['process'] = tk.Button(self, text="Process!", command=self.process)
        buttons['process'].grid(row=0, column=0)
        buttons['edge_mode'] = tk.Button(self, text="Canny Toggle!", command=self.toggle_edge_mode)
        buttons['edge_mode'].grid(row=0, column=1)
        buttons['debug_mode'] = tk.Button(self, text="Debug Toggle!", command=self.toggle_debug_mode)
        buttons['debug_mode'].grid(row=0, column=2)
        return buttons

    def video_loop(self):
        # pretty ugly but well
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stop_event.is_set():
                img_pil = conversions.bgr2imgpil(self.current_frame)
                if self.debug_input:
                    img_pil = img_pil.resize((600, 350), Image.ANTIALIAS)
                self.panel_content['video'] = conversions.imgpil2imgtk(img_pil)

                if self.edge_mode:
                    gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
                    edged = cv2.Canny(gray, 50, 100)
                    self.panel_content['processed'] = conversions.imgpil2imgtk(conversions.np_ndarray2imgpil(edged).resize((600, 350), Image.ANTIALIAS))
                else:
                    processed_img = conversions.fig2img(pipeline.run_pipeline(self.current_frame, verbose=False))
                    plt.clf()
                    if self.debug_input:
                        processed_img = processed_img.resize((600, 350), Image.ANTIALIAS)
                    self.panel_content['processed'] = conversions.imgpil2imgtk(processed_img)

                for panel_key, panel in self.panels.items():
                    if panel is None:
                        self.init_panel(panel_key, self.panel_content[panel_key], PANEL_POSITIONS[panel_key])
                    else:
                        self.update_panel(panel_key, self.panel_content[panel_key])
                plt.close('all')
        except RuntimeError as e:
            print(f'RunTime error caught in video_loop: {e}')

    def init_panel(self, panel_key, image, side):
        self.panels[panel_key] = tk.Label(image=image)
        self.panels[panel_key].image = image
        self.panels[panel_key].pack(side=side, padx=10, pady=10)

    def update_panel(self, panel_key, image):
        self.panels[panel_key].configure(image=image)
        self.panels[panel_key].image = image

    def construct_file_name_from_timestamp(self):
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        return os.path.join(self.output_path, filename)

    def process(self):
        """Callback function for 'process' button.
        Runs the planvec pipeline over the current input frame and stores it in the data folder.
        """
        output_fig = pipeline.run_pipeline(self.current_frame, verbose=True)
        output_path = self.construct_file_name_from_timestamp()
        output_fig.savefig(output_path)
        output_fig.close()
        print(f'Stored processed fig at {output_path}.')

    def toggle_edge_mode(self):
        """Callback function for the canny edge detection mode."""
        self.edge_mode = not self.edge_mode

    def toggle_debug_mode(self):
        self.debug_input = not self.debug_input

    def on_close(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stop_event.set()
        self.video_stream.stop()
        self.master.quit()

    @property
    def current_frame(self):
        """Returns a BGR image."""
        if self.debug_input:
            return self.debug_img
        else:
            return self.video_stream.read()