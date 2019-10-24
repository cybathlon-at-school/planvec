from dotmap import DotMap

from planvec.color_range import HSVColorRange

config_dict = {
    "window": {
        "title": 'Matt\'s PlanVec GUI!',
        "left": 100,
        "top": 100,
        "width": 1200,
        "height": 700
    },
    "color_range": {
        'blue':     HSVColorRange([91,  66,  20],  [160, 255, 255]),
        'red_low':  HSVColorRange([0,   71,  71],  [5,   255, 255]),
        'red_high': HSVColorRange([165, 60,  60],  [179, 255, 255]),
        'green':    HSVColorRange([43,  87,  30],  [90,  225, 225])
    }
}

gui_config = DotMap(config_dict)
