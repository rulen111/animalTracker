import pickle


def save_videobj(vid, fpath):
    with open(fpath, 'wb') as f:
        pickle.dump(vid, f)


def load_videobj(fpath, vid):
    with open(fpath, 'rb') as f:
        vid = pickle.load(f)
