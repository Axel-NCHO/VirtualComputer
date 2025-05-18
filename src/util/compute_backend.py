################################################################################
import numpy as np

# --------------------------------------------------------------------------------
# Run on GPU if available. Else, run on CPU.
def get_compute_backend():
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

# --------------------------------------------------------------------------------