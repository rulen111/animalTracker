import pickle
from pyforms.controls import ControlPlayer


def save_videobj(vid, fpath):
    with open(fpath, 'wb') as f:
        pickle.dump(vid, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_videobj(fpath, vid):
    with open(fpath, 'rb') as f:
        pass
