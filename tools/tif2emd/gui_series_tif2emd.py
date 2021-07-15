'''
GUI tool to convert TIF files to EMD file.
'''


import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets

import numpy as np
from PIL import Image

import ncempy.io.emd

class Converter(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        #self.statusBar().showMessage('Welcome')
        
        self.resize(600,250)
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        tif_lbl = QtWidgets.QLabel('input folder:', self) 
        
        self.tif_txt = QtWidgets.QLineEdit(self)
        self.tif_txt.setReadOnly(True)
        self.tifButton = QtWidgets.QPushButton('Open', self)
        
        hbox_tif = QtWidgets.QHBoxLayout()
        hbox_tif.addWidget(self.tif_txt)
        hbox_tif.addWidget(self.tifButton)
        
        tif_help_label = QtWidgets.QLabel('files are expected to start with "basename" and end with four digits (basename0000.tif - basename9999.tif)!')
        
        self.tif_basename_txt = QtWidgets.QLineEdit(self)
        self.tif_basename_txt.setText('basename')
        
        tif_sep = QtWidgets.QFrame()
        tif_sep.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)

        
        emd_lbl = QtWidgets.QLabel('output EMD file:', self) 
        
        self.emd_txt = QtWidgets.QLineEdit(self)
        self.emd_txt.setReadOnly(True)
        self.emdButton = QtWidgets.QPushButton('Save', self)
        
        hbox_emd = QtWidgets.QHBoxLayout()
        hbox_emd.addWidget(self.emd_txt)
        hbox_emd.addWidget(self.emdButton)
        
        emd_sep = QtWidgets.QFrame()
        emd_sep.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)
        
        
        self.msg = QtWidgets.QLabel('Ready', self)
        self.convButton = QtWidgets.QPushButton('Convert', self)
        self.exitButton = QtWidgets.QPushButton('Exit', self)
        
        hbox_buttons = QtWidgets.QHBoxLayout()
        hbox_buttons.addWidget(self.msg)
        hbox_buttons.addStretch(1)
        hbox_buttons.addWidget(self.convButton)
        hbox_buttons.addWidget(self.exitButton)
  
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(tif_lbl)
        vbox.addLayout(hbox_tif)
        vbox.addWidget(tif_help_label)
        vbox.addWidget(self.tif_basename_txt)
        vbox.addWidget(tif_sep)     
        vbox.addWidget(emd_lbl)
        vbox.addLayout(hbox_emd)
        vbox.addWidget(emd_sep)
        vbox.addStretch(1)
        vbox.addLayout(hbox_buttons)
        
        self.setLayout(vbox)
        
        self.setWindowTitle('Convert TIF to EMD')
        self.show()
        
        
        self.tifButton.clicked.connect(self.clicked_tifButton)
        self.emdButton.clicked.connect(self.clicked_emdButton)
        
        self.convButton.clicked.connect(self.convert)
        self.exitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        
        
        
    def keyPressEvent(self, e):
        
        # esc to close
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
    def clicked_tifButton(self):
        self.msg.setText('Ready')
        fname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open folder with multiple TIF files')
        if type(fname)==tuple:
            fname = fname[0]
        self.tif_txt.setText(fname)
        
    def clicked_emdButton(self):
        self.msg.setText('Ready')
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save EMD file')
        if type(fname)==tuple:
            fname = fname[0]
        self.emd_txt.setText(fname)
        
    def convert(self):
        tif_name = self.tif_txt.text()
        base = self.tif_basename_txt.text()
        
        if os.path.isfile(self.emd_txt.text()):
            os.remove(self.emd_txt.text())
        
        temp_dim = []
        
        list1 = os.listdir(tif_name)
        filelist = []
        for i in range(10000):
            name = base + '{:04d}'.format(i)
            for file1 in list1:
                if file1.startswith(name) and file1.endswith('.tif'):
                    filelist.append(tif_name + os.path.sep + file1)
                    temp_dim.append(i)
        list1 = filelist
        
        if list1:
            
            img = np.array(Image.open(list1[0])).transpose()
            dims = []
            dims.append( (np.array(temp_dim), 'n', '') )
            dims.append( (np.array(range(img.shape[1])), 'y', 'px'))
            dims.append( (np.array(range(img.shape[0])), 'x', 'px'))
            
            femd = ncempy.io.emd.fileEMD(self.emd_txt.text(), readonly=False)
            
            grp = femd.file_hdl['data'].create_group(os.path.basename(tif_name))
            grp.attrs['emd_group_type'] = 1
            
            dset = grp.create_dataset( 'data', (len(list1), img.shape[1], img.shape[0]), dtype=img.dtype)
            
            for i in range(len(list1)):
                img = np.array(Image.open(list1[i])).transpose()
                dset[i,:,:] = img[:,:].transpose((1,0))
            
            
            for i in range(len(dims)):
                femd.write_dim('dim{:d}'.format(i+1), dims[i], grp)

            femd.put_comment('Converted TIF files to EMD using the openNCEM tools.')    

            
            self.msg.setText('Done')
        
        else:
            self.msg.setTex('No files found')        
        
    
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    con = Converter()
    sys.exit(app.exec_())
