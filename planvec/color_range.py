"""
This file stores the HSV color ranges for colors which we need to process / filter.
"""

# Default HSV value range for openCV
H_MIN, H_MAX = 0, 179
S_MIN, S_MAX = 0, 255
V_MIN, V_MAX = 0, 255


class HSVColorRange:
    def __init__(self, start, end):
        assert len(start) == 3 and len(end) == 3, "Need input of lengths 3 for HSV values."
        for idx, (start_val, end_val) in enumerate(zip(start, end)):
            if idx == 0:
                assert all((H_MIN <= start_val, end_val <= H_MAX)), f'H value out of range [{H_MIN} {H_MAX}]'
            elif idx == 1:
                assert all((S_MIN <= start_val, end_val <= S_MAX)), f'S value out of range [{S_MIN} {S_MAX}]'
            elif idx == 1:
                assert all((V_MIN <= start_val, end_val <= V_MAX)), f'V value out of range [{V_MIN} {V_MAX}]'
        self.start = start
        self.end = end

    @property
    def h_min(self):
        return self.start[0]

    @property
    def s_min(self):
        return self.start[1]

    @property
    def v_min(self):
        return self.start[2]

    @property
    def h_max(self):
        return self.end[0]

    @property
    def s_max(self):
        return self.end[1]

    @property
    def v_max(self):
        return self.end[2]


# Those values have been found empirically by using the interactive filtering tool from planvec.img_proc.
BLUE = HSVColorRange(       [91, 66, 145],  [160, 255, 255])
RED_LOW = HSVColorRange(    [0, 71, 71],    [5, 255, 255])
RED_HIGH = HSVColorRange(   [170, 60, 60],  [179, 255, 255])
GREEN = HSVColorRange(      [43, 87, 87],  [90, 225, 225])
