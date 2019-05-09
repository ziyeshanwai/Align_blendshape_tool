import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
from UI import Form
from Util.util import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QThread


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))  # 实现系统输出的重定向


class MyThread(QThread):
    finish_signal = QtCore.pyqtSignal(str)  # 信号类型：int

    def __init__(self, blendshapes_path, baseMesh_v, Aligned_blendshapes_path, align_points_index):
        super().__init__()
        self.blendshapes_path = blendshapes_path
        self.baseMesh_v = baseMesh_v
        self.Aligned_blendshapes_path = Aligned_blendshapes_path
        self.align_points_index = align_points_index

    def run(self):
        BatchAlignFacewithFixedPoints(self.blendshapes_path, self.baseMesh_v, self.Aligned_blendshapes_path, self.align_points_index)
        self.finish_signal.emit("finished")

class AlignBlendshapeTool(QtWidgets.QWidget, Form):
    def __init__(self):
        super(AlignBlendshapeTool, self).__init__()
        super(Form, self).__init__()
        self.setupUi(self)
        self.blendshapes_path = None
        self.Aligned_blendshapes_path = None
        self.base_blenshape_name = None
        self.Align_points_file = None
        self.baseMesh_v = None
        self.aling_index = None
        self.workThread = None
        self.textEdit.setReadOnly(True)
        sys.stdout = EmittingStream(textWritten=self.outputWritten)
        sys.stderr = EmittingStream(textWritten=self.outputWritten)

    def Button_clicked(self):
        self.baseMesh_v, baseMesh_f = loadObj(self.base_blenshape_name)
        self.aling_index = find_cloest_index_in_obj_withV(self.baseMesh_v, self.Align_points_file, matlab=False)
        self.workThread = MyThread(self.blendshapes_path, self.baseMesh_v, self.Aligned_blendshapes_path, self.aling_index)
        self.workThread.start()
        self.workThread.finish_signal.connect(self.outputWritten)

    def Button1_clicked(self):
        fname = QFileDialog.getOpenFileName(self, '选择Basemesh', '/')
        self.lineEdit.setText(fname[0])
        self.base_blenshape_name = fname[0]

    def Button2_clicked(self):
        file_path = QFileDialog.getExistingDirectory(self, "选择Blendshape路径", "/")
        self.lineEdit_2.setText(file_path)
        self.blendshapes_path = file_path

    def Button3_clicked(self):
        fname = QFileDialog.getOpenFileName(self, "选择对齐点文件", "/")
        self.lineEdit_3.setText(fname[0])
        self.Align_points_file = fname[0]

    def Button4_clicked(self):
        file_path = QFileDialog.getExistingDirectory(self, "选择对齐后保存文件的路径", "/")
        self.lineEdit_4.setText(file_path)
        self.Aligned_blendshapes_path = file_path


    def outputWritten(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tool_form = AlignBlendshapeTool()
    tool_form.show()
    sys.exit(app.exec_())


