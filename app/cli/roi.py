import pathlib
import pickle
import shelve


class ROI(object):

    def __init__(self, *args, **kwargs):
        self.roi_dict = kwargs.get("roi_dict", {})

    def save(self, fpath):
        # with shelve.open(fpath) as db:
        #     db["ROI"] = {
        #         "roi_dict": self.roi_dict,
        #     }

        if pathlib.Path(fpath).exists():
            with open(fpath, "rb") as f:
                temp = pickle.load(f)
        else:
            temp = {}

        temp.update({
            "ROI": {
                "roi_dict": self.roi_dict,
            }
        })

        with open(fpath, "wb") as f:
            pickle.dump(temp, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, fpath):
        # with shelve.open(fpath) as db:
        #     if "ROI" in db:
        #         self.__dict__.update(db["ROI"])

        if pathlib.Path(fpath).exists():
            with open(fpath, "rb") as f:
                entries = pickle.load(f)
        else:
            return

        if "ROI" in entries:
            self.__dict__.update(entries["ROI"])
