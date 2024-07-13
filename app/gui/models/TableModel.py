from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from app.cli.tracker import calc_dist


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def get_data(self):
        return self._data

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data.iloc[index.row(), index.column()]
                return f"{value:.6}"

    def setData(self, index, value, role, dist=False):
        if role == Qt.EditRole:
            self.beginResetModel()
            self._data.iloc[index.row(), index.column()] = value
            if dist and index.row() != 0:
                xprev = self._data.iloc[index.row() - 1, 0]
                yprev = self._data.iloc[index.row() - 1, 1]
                x = self._data.iloc[index.row(), 0]
                y = self._data.iloc[index.row(), 1]
                dist = calc_dist(x, y, xprev, yprev)
                self._data.iloc[index.row(), 2] = dist

            self.endResetModel()
            return True
        return False

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section] + 1)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    # def setData(self, index, value, role):
    #     if role == Qt.EditRole:
    #         # Set the value into the frame.
    #         self.beginResetModel()
    #         self._data.iloc[index.row(), index.column()] = value
    #         self.endResetModel()
    #         return True
    #
    #     return False
