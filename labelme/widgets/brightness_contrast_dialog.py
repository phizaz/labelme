import PIL.Image
import PIL.ImageEnhance
from qtpy.QtCore import Qt
from qtpy import QtGui
from qtpy import QtWidgets, QtCore
from qtpy.QtWidgets import QCheckBox

from .. import utils
import numpy as np
from PIL import Image

STEP_SIZE_WL = 50
STEP_SIZE_WW = 50
WL_RANGE = int(4000 / STEP_SIZE_WL)
WW_RANGE = int(4000 / STEP_SIZE_WW)


class BrightnessContrastDialog(QtWidgets.QDialog):
    def __init__(self, img, callback, parent=None):
        super(BrightnessContrastDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Window Level/Window Width")

        self.slider_window_level = self._create_slider_WL()
        self.slider_window_width = self._create_slider_WW()
        self.box_invert = self._create_box_invert()

        self.box_invert.stateChanged.connect(self.clickBox)

        formLayout = QtWidgets.QFormLayout()
        formLayout.addRow(self.tr("Window Level"), self.slider_window_level)
        formLayout.addRow(self.tr("Window Width"), self.slider_window_width)
        formLayout.addRow(self.tr("Invert"), self.box_invert)
        self.setLayout(formLayout)

        assert isinstance(img, PIL.Image.Image)
        self.img = img
        self.callback = callback

    def onNewValue(self, value):
        window_level = self.slider_window_level.value() * STEP_SIZE_WL
        window_width = self.slider_window_width.value() * STEP_SIZE_WW
        print('Window Level:', window_level)
        print('Window Width:', window_width)

        # https://www.tutorialspoint.com/pyqt/pyqt_qcheckbox_widget.htm
        print('ClickBox', self.box_invert.isChecked())

        low = window_level - window_width / 2
        high = window_level + window_width / 2
        img_data = change_window_from_pil(self.img, low, high,
                                          self.box_invert.isChecked())
        qimage = QtGui.QImage.fromData(img_data)
        self.callback(qimage)

    def _create_slider_WL(self):
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setRange(int(STEP_SIZE_WW / 2), WL_RANGE)
        slider.setValue(2000 / STEP_SIZE_WW)  # default value
        # slider.setTickInterval(100)
        # slider.setSingleStep(100)
        slider.valueChanged.connect(self.onNewValue)
        return slider

    def _create_slider_WW(self):
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setRange(STEP_SIZE_WW, WW_RANGE)
        slider.setValue(4000 / STEP_SIZE_WW)  # default value
        # slider.setTickInterval(100)
        # slider.setSingleStep(100)
        slider.valueChanged.connect(self.onNewValue)
        return slider

    def _create_box_invert(self):
        # https://pythonprogramminglanguage.com/pyqt-checkbox/
        box = QCheckBox("", self)
        return box

    def clickBox(self, state):

        if state == QtCore.Qt.Checked:
            print('Invert Checked')
            return True
        else:
            print('Invert Unchecked')
            return False


def change_window(img, low, high):
    img = (img.clip(min=low, max=high) - low) / (high - low) * 255
    return img.astype(np.uint8)


def change_window_from_bytes(img, low=None, high=None, invert=False):
    img = utils.img_data_to_pil(img)
    return change_window_from_pil(img, low, high, invert)


def change_window_from_pil(img, low, high, invert):
    img = np.asarray(img)

    if low is None:
        low = img.min()
    if high is None:
        high = img.max()
    img = change_window(img, low, high)

    if invert:
        img = np.max(img) - img

    img = Image.fromarray(img)
    img = utils.img_pil_to_data(img)
    return img