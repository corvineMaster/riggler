import sys
import importlib.util
from pathlib import Path

from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

from riggler.core import custom_widgets

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import cmds, mel, OpenMayaUI as omui

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

    
class riggler(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    dialog_instance = None
    current_module = None
    
    modules_path = Path('D:/Users/Bailey Cohen/Documents/maya/scripts/riggler/modules')
    @classmethod
    def show_dialog(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = riggler()
        
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()
        
    def __init__(self, parent=maya_main_window()):
        super(riggler, self).__init__(parent)

        self.setWindowTitle("Show Constraints")
        self.setMinimumWidth(275)
        self.setMinimumHeight(430)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.prepare_page = QtWidgets.QWidget()
        self.build_page = QtWidgets.QWidget()
        self.work_page = QtWidgets.QWidget()
        self.publish_page = QtWidgets.QWidget()
        
        self.components_tree = QtWidgets.QTreeWidget()
        self.components_tree.setHeaderHidden(True)
        self.component_description_box = QtWidgets.QTextEdit()
        self.component_description_box.setReadOnly(True)
        
    def create_layout(self):
        self.createPrepareLayout()

        self.build_layout = QtWidgets.QVBoxLayout()
        self.build_page.setLayout(self.build_layout)
        
        self.work_layout = QtWidgets.QVBoxLayout()
        self.work_page.setLayout(self.work_layout)
        
        self.publish_layout = QtWidgets.QVBoxLayout()
        self.publish_page.setLayout(self.publish_layout)
        
        self.steps_tab_layout = QtWidgets.QTabWidget()
        self.steps_tab_layout.setStyleSheet("QTabWidget::pane {border-top: 2px;}")
        self.prepare_tab = self.steps_tab_layout.addTab(self.prepare_page, 'Prepare')
        self.build_tab = self.steps_tab_layout.addTab(self.build_page, 'Build')
        self.work_tab = self.steps_tab_layout.addTab(self.work_page, 'Work')
        self.publish_tab = self.steps_tab_layout.addTab(self.publish_page, 'Publish')

        main_layout = QtWidgets.QFormLayout(self)
        main_layout.addWidget(self.steps_tab_layout)

    def createPrepareLayout(self):
        prepare_layout = QtWidgets.QHBoxLayout()
        self.prepare_page.setLayout(prepare_layout)
        
        # Left side
        modules_list_layout = QtWidgets.QVBoxLayout()
        prepare_layout.addLayout(modules_list_layout)
        modules_list_layout.addWidget(self.components_tree)
        for folder in self.modules_path.iterdir():
            category = QtWidgets.QTreeWidgetItem(self.components_tree, [str(folder).split('\\')[-1]])
            for sub_folder in folder.iterdir():
                module = str(sub_folder).split('\\')[-1]
                if [x for x in sub_folder.iterdir()]:
                    QtWidgets.QTreeWidgetItem(category, [module])
        modules_list_layout.addWidget(self.component_description_box)

        # Right side
        groupBox = QtWidgets.QGroupBox("Scrollable GroupBox")
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)

        contentWidget = QtWidgets.QWidget()
        contentLayout = QtWidgets.QVBoxLayout(contentWidget)
        # contentLayout.addStretch()

        '''for i in range(10):
            box = custom_widgets.CollapsibleBox(f"Collapsible Box Header-{i}")
            contentLayout.addWidget(box)
            lay = QtWidgets.QVBoxLayout()
            for j in range(12):
                button = QtWidgets.QPushButton(f'button #{j}')
                lay.addWidget(button)
            
            box.setContentLayout(lay)'''
        
        scrollArea.setWidget(contentWidget)

        group_layout = QtWidgets.QVBoxLayout()
        group_layout.addWidget(scrollArea)
        group_layout.addStretch(1)
        prepare_layout.addLayout(group_layout)
        

    def create_connections(self):
        self.components_tree.clicked.connect(self.updateComponentDescription)
        self.components_tree.doubleClicked.connect(self.createComponent)
    
    def createComponent(self):
        clicked_widget = self.components_tree.selectedItems()[0]
        parent = clicked_widget.parent()
        if not parent:
            return
    
    def addParameters(self):
        # Get the appropriate sub-setting and fill out the guide drop down menu
        # Should also add attributes to the root guide object for future reference
        # Organize by separating widgets into specified groupBoxes
        widget_layout = QtWidgets.QVBoxLayout()
        for settings in self.settings:
            current_layout = QtWidgets.QHBoxLayout()

            widget_type = settings['widget']
            if widget_type == 'label':  # Just text, doesn't represent a kwarg
                widget = QtWidgets.QLabel(settings['label'], parent=current_layout)
            if widget_type == 'spinBox':
                QtWidgets.QLabel(settings['label'], parent=current_layout)
                widget = QtWidgets.QSpinBox(parent=current_layout)
                min_max = settings['min_max']
                if min_max[0]:
                    widget.setMinimum(min_max[0])
                if min_max[1]:
                    widget.setMaximum(min_max[1])
                widget.setValue(settings['default'])
            elif widget_type == 'slider':
                QtWidgets.QLabel(settings['label'], parent=current_layout)
                widget = QtWidgets.QSlider(parent=current_layout)
                min_max = settings['min_max']
                if min_max[0]:
                    widget.setMinimum(min_max[0])
                if min_max[1]:
                    widget.setMaximum(min_max[1])
                widget.setValue(settings['default'])
            elif widget_type == 'spinSlider':  # Custom widget, combination of spinBox and slider
                pass
            elif widget_type == 'comboBox':
                QtWidgets.QLabel(settings['label'], parent=current_layout)
                widget = QtWidgets.QCheckBox(parent=current_layout)
                widget.setChecked(settings['default'])
            elif widget_type == 'checkBox':
                widget = QtWidgets.QComboBox(settings['label'], parent=current_layout)
                items = settings['items']
                widget.addItems(items)
                default = settings['default']
                if default:
                    widget.setCurrentText(default)
            elif widget_type == 'input_single':  # Press button to input single selection into textField
                widget = QtWidgets.QTextField(parent=current_layout)
                input_button = QtWidgets.QPushButton('<<', parent=current_layout)
                input_button.clicked.connect(partial(self.addSelectionToField, widget))
            elif widget_type == 'input_list':  # Press button to input multi selection into listWidget
                widget = QtWidgets.QListWidget(parent=current_layout)
                widget.setDragDropOverwriteMode(True)
                widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
                widget.setDefaultDropAction(QtCore.Qt.MoveAction)
                widget.setAlternatingRowColors(True)
                widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
                widget.setSelectionRectVisible(False)
                button_layout = QtWidgets.QVBoxLayout(current_layout)
                input_button = QtWidgets.QPushButton('<<', parent=button_layout)
                input_button.clicked.connect(partial(self.addSelectionToField, widget))
                remove_button = QtWidgets.QPushButton('>>', parent=button_layout)
                remove_button.clicked.connect(partial(self.removeSelectionFromList, widget))
            
            widget_layout.addLayout(current_layout)

    def addSelectionToField(self, field: object):
        selections = cmds.ls(selection=True)
        if isinstance(field, QtWidgets.QTextField):
            field.setText(selections[0])
        else:
            existing_items = [field.item(x).text() for x in range(field.count())]
            for selection in selections:
                if selection not in existing_items:
                    field.addItem(selection)
    
    def removeSelectionFromList(self, field):
        selected_items = field.selectedItems()
        for item in selected_items:
            row = field.row(item)
            field.takeItem(row)

    def updateComponentDescription(self):
        clicked_widget = self.components_tree.selectedItems()[0]
        parent = clicked_widget.parent()
        if not parent:
            return
        self.importModule(parent.text(0), clicked_widget.text(0), "guide")
        self.component_description_box.setText(self.current_module.DESCRIPTION or '')
    
    def importModule(self, category, name, file):
        path_to_module = self.modules_path.joinpath(category, name, f'{file}.py')
        if path_to_module.exists():
            self.current_module = __import__(f'riggler.modules.{category}.{name}.{file}', globals(), locals(), ["*"])
        else:
            cmds.error(f'"{name}" module does not have the appropriate python files')

if __name__ == "__main__":
    try:
        riggler_window.close()
        riggler_window.deleteLater()
    except:
        pass

    riggler_window = riggler()
    riggler_window.show()
