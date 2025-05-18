################################################################################
import numpy as np

################################################################################
def get_compute_backend():
    """Returns Cupy module if an Nvidia GPU is detected. If not, the Numpy module is returned."""
    try:
        import cupy as cp
        if cp.cuda.runtime.getDeviceCount() > 0:
            print("Using Nvidia GPU")
            return cp
        else:
            print("No Nvidia GPU detected. Falling back to CPU.")
            return np
    except ImportError:
        print("CuPy or Cuda not installed. Falling back to CPU.")
        return np
xp = get_compute_backend()
