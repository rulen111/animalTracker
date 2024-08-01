import pickle


class SaveLoadHandler(object):
    def __init__(self, fpath):
        self.fpath = fpath

    def write(self, entries):
        with open(self.fpath, "rb") as f:
            temp = pickle.load(f)

        temp.update(entries)

        with open(self.fpath, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def read(self):
        with open(self.fpath, "rb") as f:
            entries = pickle.load(f)

        return entries
