# Reference curves for the signed normalization A(t)/B.
# The weighted trace is z = w*a_p/(2*sqrt(p)), and B = -2 times the integral
# of A(t) on [0, 1]. Both functions accept a scalar or a NumPy array.
# The figure code can draw both templates; Table 1 uses the tilt template.

import numpy as np


def tilt_template(t):
    return -8/(3*np.pi)*np.maximum(1-np.asarray(t)**2, 0)**1.5


def translation_template(t):
    return -2/np.pi*np.sqrt(np.maximum(1-np.asarray(t)**2, 0))
