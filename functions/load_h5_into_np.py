import numpy as np
import h5py


def load_h5_into_np(file):
    """
    Loads h5 file into numpy

    Parameters
    ----------
    file: str, path to an h5 file

    Returns
    -------
    x: np array
    """

    # load file
    hf = h5py.File(file, "r")
    # add keys to list
    list_of_names = []
    hf.visit(list_of_names.append)
    # check for the given key which we expect and if not found, take the one lowest in the tree
    try:
        x = np.array(hf["tada"])
    except KeyError:
        x = np.array(hf[list_of_names[-1]])
    print(f"Matrix shape: {x.shape}")

    return x
