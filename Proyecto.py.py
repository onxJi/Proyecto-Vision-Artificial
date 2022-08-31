import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QMainWindow, QApplication,
                             QDialog, QMessageBox, QPushButton,
                             QFileDialog)
from PyQt5 import QtCore
from PyQt5.QtCore import (Qt, QPropertyAnimation, QRect,
                          QAbstractAnimation, QFile, QDir,
                          pyqtSignal)
from PyQt5.QtGui import QImage, QPixmap
import cv2
import imutils
from os import getcwd
import numpy as np
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg
                                                as FigureCanvas)
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random as rnd


    

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi("Interfaz/VentanaPrincipal.ui", self)
        self.image = None
        self.filename = None
        self.tmp = None 
        self.btn_OpenFile.clicked.connect(self.loadImage)
        self.btn_OpenFile.clicked.connect(self.habilitar_Op)
        # self.deshabilitar_controles()
        self.intensidad_brillo = 0
        self.intensidad_2 = 0
        self.deshabilitar_C()
        self.dial.setNotchesVisible(True)
        self.dial_2.setNotchesVisible(True)
        # self.radarUltrasonic = UltrasonicGrafic()
        
        self.dial.valueChanged['int'].connect(self.subir_intensidad)
        self.dial_2.valueChanged['int'].connect(self.subir_intensidad_2)
        # self.btn_Apply_clahe.clicked.connect(self.Algoritmo_Clahe)
        self.btn_1.clicked.connect(self.habilitar_C)
        self.btn_3.clicked.connect(self.Guardar_imagen)
        # self.verticalSlider_1.valueChanged['int'].
        # connect(self.subir_intensidad)
        # self.verticalSlider_2.valueChanged['int'].
        # connect(self.subir_intensidad_2)


    def loadImage(self):
        try:
            self.filename = QFileDialog.getOpenFileName(filter="Image (*.*)")[0]
            self.image = cv2.imread(self.filename)
            self.setPhoto(self.image)
        except:
            QMessageBox.warning(self, "Error", "No se puede abrir Imagen")


    def setPhoto(self, image):
        try:
            self.tmp = image
            image = imutils.resize(image, width=640)
            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0],
                           frame.strides[0], QImage.Format_RGB888)
            self.label.setPixmap(QtGui.QPixmap.fromImage(image))
        except:
            QMessageBox.warning(self, "Error", "No se puede abrir")
        

    def subir_intensidad(self, value):
        self.intensidad_brillo = value
        self.lcdNumber.display(value)
        # print("Valor: ",value)
        self.update()


    def subir_intensidad_2(self, value):
        self.intensidad_2 = value
        self.lcdNumber_2.display(value)
        self.update()


    def changeBrightness(self,img,value):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)
        lim = 255 - value
        v[v>lim] = 255
        v[v<=lim] += value
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return img


    def changeBlur(self, img, value):
        kernel_size = (value+1, value+1)  # +1 is to avoid 0
        img = cv2.blur(img, kernel_size)
        return img
    

    def update(self):
        img = self.changeBrightness(self.image, self.intensidad_brillo)
        img = self.changeBlur(img, self.intensidad_2)
        if self.rbt_Equ.isChecked():
            img = self.Apply_equalize(img)
        if self.rbt_Clahe.isChecked():
            img = self.Algoritmo_Clahe(img)

        if self.rbt_GaussMed.isChecked():
            img = self.Gauss_medium_bin(img)
        if self.rbt_MedSimple.isChecked():
            img = self.Medium_Simple_bin(img)
       
        self.setPhoto(img)


    def Apply_equalize(self, image):

        R, G, B = cv2.split(image)
        output1_R = cv2.equalizeHist(R)
        output1_G = cv2.equalizeHist(G)
        output1_B = cv2.equalizeHist(B)
        equ = cv2.merge((output1_R, output1_G, output1_B))
        img = cv2.cvtColor(equ, cv2.COLOR_BGR2RGB)
        return img


    def Algoritmo_Clahe(self, image):
        img = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        rgb_to_lab = cv2.split(img)
        valueX = self.ln_Gridzisex.text()
        valueGrid1 = int(valueX)
        valueY = self.ln_Gridzisey.text()
        valueGrid2 = int(valueY)
        if valueGrid1==0 or valueGrid2==0:
            QMessageBox.warning(self, "Advertencia",
                                " No se aceptan valores de 0")
            valueGrid2 = 1
            valueGrid1 = 1

        algorithm_clahe = cv2.createCLAHE(clipLimit=3.0,
                                          tileGridSize=(valueGrid1,
                                          valueGrid2))
        rgb_to_lab[0] = algorithm_clahe.apply(rgb_to_lab[0])
        img = cv2.merge(rgb_to_lab)
        rgb = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
             
        return rgb


    def grafica(self, img):
        ax = plt.hist(img.ravel(), bins=256)
        plt.title('Imagen original')
        plt.ion()
        

    def Gauss_medium_bin(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_binGauss = cv2.adaptiveThreshold(img, 255,
                                             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 3, 3)
        return img_binGauss


    def Medium_Simple_bin(self, img):
        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        image_bin = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, 7, 3)
        return image_bin

    
    def Guardar_imagen(self):
        try: 
            filename = QFileDialog.getSaveFileName(
                filter="JPG(*.jpg);;PNG(*.png);;TIFF(*.tiff);;BMP(*.bmp)"
            )[0]
            cv2.imwrite(filename, self.image)
            print('Image saved as:', self.filename)
        except:
            QMessageBox.warning(self, "Error", "Ha cancelado el proceso")
    def deshabilitar_C(self):
        self.dial_2.setEnabled(False)
        self.dial.setEnabled(False)
        self.btn_1.setEnabled(False)
        self.rbt_Equ.setEnabled(False)
        self.btn_3.setEnabled(False)
        self.rbt_Clahe.setEnabled(False)
        self.ln_Gridzisey.setEnabled(False)
        self.ln_Gridzisex.setEnabled(False)
        self.ln_Cliplimit.setEnabled(False)
        self.rbt_GaussMed.setEnabled(False)
        self.rbt_MedSimple.setEnabled(False)


    def habilitar_Op(self):
        self.btn_1.setEnabled(True)
        self.btn_3.setEnabled(True)


    def habilitar_C(self):
        self.rbt_Equ.setEnabled(True)
        self.dial.setEnabled(True)
        self.dial_2.setEnabled(True)
        self.rbt_Clahe.setEnabled(True)
        self.ln_Gridzisey.setEnabled(True)
        self.ln_Gridzisex.setEnabled(True)
        self.ln_Cliplimit.setEnabled(True)
        self.rbt_GaussMed.setEnabled(True)
        self.rbt_MedSimple.setEnabled(True)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = VentanaPrincipal()
    GUI.show()
    sys.exit(app.exec_())