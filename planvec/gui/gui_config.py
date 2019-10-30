from dotmap import DotMap

from planvec.color_range import HSVColorRange

config_dict = {
    'window': {
        'title': 'Matt\'s PlanVec GUI!',
        'left': 50,
        'top': 50,
        'width': 1700,
        'height': 700
    },
    'video': {
        'camera': 'USB',  # either 'USB' or 'BUILTIN'
        'max_input_width': 1920,  # high res: 1920, low res: 640
        'max_input_height': 1080,  # high res: 1080, low res: 480
        'display_width': 850,
        'display_height': 900
    },
    'color_range': {
        'blue':     HSVColorRange([91,  66,  20],  [160, 255, 255]),
        'red_low':  HSVColorRange([0,   71,  71],  [5,   255, 255]),
        'red_high': HSVColorRange([165, 60,  60],  [179, 255, 255]),
        'green':    HSVColorRange([43,  87,  30],  [90,  225, 225])
    },
    'processing': {
        'rectify_shape': (600, 350),
        'gaussian_blur': (3, 3),
        'img_threshold': (110, 255),
        'area_threshold': 5000,
        'contours_n_points_threshold': 100,
        'polygon_tolerance': 1
    }
}

gui_config = DotMap(config_dict)
