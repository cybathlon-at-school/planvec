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
    'color_range': {
        'blue':     HSVColorRange([91,  66,  20],  [160, 255, 255]),
        'red_low':  HSVColorRange([0,   71,  71],  [5,   255, 255]),
        'red_high': HSVColorRange([165, 60,  60],  [179, 255, 255]),
        'green':    HSVColorRange([43,  87,  30],  [90,  225, 225])
    },
    'video': {
        'camera': 'USB',  # either 'USB' or 'BUILTIN'
        'max_input_width': 640,
        'max_input_height': 480,
        'display_width': 850,
        'display_height': 900
    },
    'style': {

    }
}

gui_config = DotMap(config_dict)
