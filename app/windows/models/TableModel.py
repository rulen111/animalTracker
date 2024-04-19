from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def get_data(self):
        return self._data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    # def flags(self, index):
    #     if not index.isValid():
    #         return Qt.ItemIsEnabled
    #
    #     return super().flags(index) | Qt.ItemIsEditable
    #
    # def headerData(self, section, orientation, role):
    #     # section is the index of the column/row.
    #     if role == Qt.DisplayRole:
    #         if orientation == Qt.Horizontal:
    #             return str(self._data.columns[section])
    #
    #         if orientation == Qt.Vertical:
    #             return str(self._data.index[section])
    #
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            # Set the value into the frame.
            self.beginResetModel()
            self._data[index.row()][index.column()] = value
            self.endResetModel()
            return True

        return False
