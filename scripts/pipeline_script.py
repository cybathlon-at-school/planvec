import os
import matplotlib.pyplot as plt

from context import planvec
from planvec.common import PROJECT_ROOT_PATH
from planvec.pipeline import run_pipeline
from planvec import vizualization

ASSETS_DIR      = os.path.join(PROJECT_ROOT_PATH, '../test', 'assets')
INPUT_IMAGE     = 'fileworks.jpeg'
OUTPUT_PDF_NAME = 'sample_output.pdf'
USE_CUSTOM_FILE = True
CUSTOM_PATH     = '/home/matt/code/planvec/data/2019-11-05/matt/0_matt_2019-11-05_11-33-54-401431_original.jpeg'

if USE_CUSTOM_FILE:
    input_img = planvec.io.read_img_full_path(CUSTOM_PATH, to_bgr=True)
else:
    input_img = planvec.io.read_img(ASSETS_DIR, INPUT_IMAGE, to_bgr=True)

# Show input iamge
planvec.vizualization.imshow(input_img, axis='on', figsize=(18, 12), img_space='BGR')

# Setup output final output figure and run complete pipeline
fig, ax = vizualization.setup_figure()
ax, output_img = run_pipeline(input_img, ax, visualize_steps=True, verbose=True, return_fig=True)
plt.show()
