import shelve


class ROI(object):

    def __init__(self, *args, **kwargs):
        self.roi_dict = kwargs.get("roi_dict", {})

    def save(self, fpath):
        with shelve.open(fpath) as db:
            db["ROI"] = {
                "roi_dict": self.roi_dict,
            }

    def load(self, fpath):
        with shelve.open(fpath) as db:
            if "ROI" in db:
                self.__dict__.update(db["ROI"])
