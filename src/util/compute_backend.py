################################################################################
import numpy as np

################################################################################
def get_compute_backend():
    """
    Returns Cupy module if an Nvidia GPU is detected and the CUDA Toolkit is installed.
    If not, the Numpy module is returned."
    """
    try:
        import cupy as cp
        try:
            if cp.cuda.runtime.getDeviceCount() > 0:
                # Try a basic GPU operation to ensure CUDA libraries are available
                _ = cp.arange(1)
                print("Using Nvidia GPU")
                return cp
            else:
                print("No Nvidia GPU detected. Falling back to CPU.")
                return np
        except Exception as e:
            print(f"CUDA error: {e}. \nMake sure the CUDA Toolkit is correctly installed. \nFalling back to CPU.")
            return np
    except ImportError:
        print("CuPy not installed. Falling back to CPU.")
        return np

xp = get_compute_backend()
