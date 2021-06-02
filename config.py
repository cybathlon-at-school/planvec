from dotmap import DotMap

from planvec.color_range import HSVColorRange

config_dict = {
    'window': {
        'title':                    'Matt\'s PlanVec GUI!',
        'left':                     50,
        'top':                      50,
        'full_screen':              True,
        'width':                    1700,  # if not full screen
        'height':                   700  # if not full screen
    },
    'video': {
        'camera':                   'USB',  # either 'USB' or 'BUILTIN'
        'max_input_width':          640,   # high res: 1920, low res: 640
        'max_input_height':         480,   # high res: 1080, low res: 480
        'raw_display_width':        250,
        'raw_display_height':       181,
        'processed_display_width':  650,
        'processed_display_height': 650,
        'frame_buffer_size':        1
    },
    'color_range': {
        # 'blue':                     #HSVColorRange([91,  100,  20],  [160, 255, 255]),
        'red_low':                  HSVColorRange([0,   71,  71],  [5,   255, 255]),
        'red_high':                 HSVColorRange([165, 60,  60],  [179, 255, 255]),
        'green':                    HSVColorRange([15,  20,  30],  [60,  225, 225]),
    },
    'processing': {
        'img_hw_ratio':             0.7,  # This is the ratio of the w/h of drawing area
        'rectify_shape':            (1920, int(1920 * 0.7)),
        'gaussian_blur':            (3, 3),
        'img_threshold':            (100, 255),
        'area_threshold':           5000,
        'contours_size_threshold':  100,
        'polygon_tolerance':        1,
        'line_width':               1,
        'out_size_inches':          (7.87402, 5.51181),  # TODO: fix scaling
    },
    'pdf_output': {
        'plate_width_cm':           80,
        'plate_height_cm':          50,
        'draw_area_width_cm':       20,
        'draw_area_height_cm':      14
    },
    'data': {
        'overwrite_output':         False
    }
}

# DotMap: This enables config access like...
#     from planvec.config import CONFIG
#     x_blur, y_blur = CONFIG.processing.gaussian_blur
# TODO: This is not really satisfactory
planvec_config = DotMap(config_dict)
