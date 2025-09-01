from PySide6 import QtWidgets
from PySide6 import QtCore


# Credit: https://stackoverflow.com/a/52617714
class CollapsibleBox(QtWidgets.QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QtWidgets.QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        self.content_area = QtWidgets.QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.content_area.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not checked
            else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (
            self.sizeHint().height() - self.content_area.maximumHeight()
        )
        animation_duration = 200
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(animation_duration)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(animation_duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


class QtupleDoubleSpinBox(QtWidgets.QWidget):
    def __init__(self, step=10, parent=None):
        super().__init__(parent)
        
        self.x_spinbox = QtWidgets.QDoubleSpinBox()
        self.x_spinbox.setDecimals(4)
        self.x_spinbox.setMinimumWidth(60)
        self.y_spinbox = QtWidgets.QDoubleSpinBox()
        self.y_spinbox.setDecimals(4)
        self.y_spinbox.setMinimumWidth(60)
        self.z_spinbox = QtWidgets.QDoubleSpinBox()
        self.z_spinbox.setDecimals(4)
        self.z_spinbox.setMinimumWidth(60)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.x_spinbox)
        self.layout.addWidget(self.y_spinbox)
        self.layout.addWidget(self.z_spinbox)
    
    @property
    def value(self):
        return(self.x_spinbox.value, self.y_spinbox.value, self.z_spinbox.value)
    
    @value.setter
    def value(self, value: tuple):
        self.x_spinbox.value = value[0]
        self.y_spinbox.value = value[1]
        self.z_spinbox.value = value[2]


class QTransformCheckboxGroup(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        
        self.all_checkbox = QtWidgets.QCheckBox('All')
        self.all_checkbox.setChecked(True)
        self.x_checkbox = QtWidgets.QCheckBox('X')
        self.y_checkbox = QtWidgets.QCheckBox('Y')
        self.z_checkbox = QtWidgets.QCheckBox('Z')
        
        
        self.checkbox_layout = QtWidgets.QVBoxLayout()
        self.checkbox_layout.addWidget(self.all_checkbox)
        
        self.xyz_layout = QtWidgets.QHBoxLayout()
        self.xyz_layout.addWidget(self.x_checkbox)
        self.xyz_layout.addWidget(self.y_checkbox)
        self.xyz_layout.addWidget(self.z_checkbox)
        
        self.checkbox_layout.addLayout(self.xyz_layout)
        
        self.layout.addLayout(self.checkbox_layout)
        
        self.all_checkbox.clicked.connect(self.__toggle_xyz)
        self.x_checkbox.clicked.connect(self.__toggle_all)
        self.y_checkbox.clicked.connect(self.__toggle_all)
        self.z_checkbox.clicked.connect(self.__toggle_all)
    
    def __toggle_all(self):
        if self.x_checkbox.isChecked() or self.y_checkbox.isChecked() or self.z_checkbox.isChecked():
            self.all_checkbox.setChecked(False)
    
    def __toggle_xyz(self):
        if self.all_checkbox.isChecked():
            self.x_checkbox.setChecked(False)
            self.y_checkbox.setChecked(False)
            self.z_checkbox.setChecked(False)
    
    @property
    def value(self):
        if self.all_checkbox.isChecked():
            return ['all']
        
        xyz = []
        if self.x_checkbox.isChecked():
            xyz.append('x')
        if self.y_checkbox.isChecked():
            xyz.append('y')
        if self.z_checkbox.isChecked():
            xyz.append('z')
        
        return xyz
    
    @value.setter
    def value(self, value: list):
        self.all_checkbox.setChecked(True if 'all' in value else False)
        self.x_checkbox.setChecked(True if 'x' in value and 'all' not in value else False)
        self.y_checkbox.setChecked(True if 'y' in value and 'all' not in value else False)
        self.z_checkbox.setChecked(True if 'z' in value and 'all' not in value else False)
        

class QSpinSlider(QtWidgets.QWidget):
    def __init__(self, min_val=0, max_val=1, parent=None):
        super().__init__(parent)
        
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setSingleStep(0.01)
        self.spinbox.setDecimals(4)
        self.spinbox.setMinimumWidth(60)
        self.spinbox.setKeyboardTracking(False)
        self.slider = QtWidgets.QSlider(QtCore.Orientation.Horizontal)
        self.slider.setRange(min_val*10000, max_val*10000)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.spinbox)
        self.layout.addWidget(self.slider)
        
        self.spinbox.valueChanged.connect(self.__update_slider)
        self.slider.valueChanged.connect(self.__update_spinbox)
    
    def __update_spinbox(self):
        value = self.slider.value()
        self.spinbox.setValue(value/10000)
    
    def __update_slider(self):
        value = self.spinbox.value()
        self.slider.setValue(value*10000)
    
    @property
    def value(self):
        return self.spinbox.value()
        
    @value.setter
    def value(self, value):
        self.spinbox.setValue(value)
     
     
if __name__ == "__main__":
    pass