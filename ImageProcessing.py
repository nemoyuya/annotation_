# -*- coding: utf-8 -*-
import sys, os
from PySide2.QtWidgets import * 
from PySide2.QtGui import * 
from PySide2.QtCore import *
from CanvasLabel import CanvasLabel
import cv2
import numpy as np

def resourcePath(filename):
  if hasattr(sys, "_MEIPASS"):
      return os.path.join(sys._MEIPASS, filename)
  return os.path.join(filename)
        
class CanvasTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.tab_num = 0
        
    def add_tab(self, widget):
        self.tab_num +=1
        self.addTab(widget,"キャンバス-その"+str(self.tab_num))
        
    def remove_tab(self, index):
        self.removeTab(index)

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        #self.setGeometry(0, 0, 950, 650)
        self.setGeometry(0, 0,1350, 950)

        self.saveimg_shape = (16, 16)
        
        #左側のレイアウト作成
        self.make_leftdock_layout()

        #右側のレイアウト作成
        self.make_rightdock_layout()
        
        #self.dock_r.setFixedSize(400,650)
        #self.dock_l.setFixedSize(550,650)
        self.dock_r.setFixedSize(400,950)
        self.dock_l.setFixedSize(950,950)
        self.dock_r.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_l.setFeatures(QDockWidget.NoDockWidgetFeatures)
        
        self.setWindowTitle('ドット絵キャンバス')
        self.show()

    def transfer_infomation(self):
        last_canvas = self.canvas_list[self.lasttab_index]
        current_index = self.widget_l.currentIndex()
        current_canvas = self.canvas_list[self.widget_l.currentIndex()]
        
        current_canvas.toolkind = last_canvas.toolkind
        current_canvas.color = last_canvas.color
        current_canvas.clip_img = last_canvas.clip_img
        current_canvas.paint_bool = last_canvas.paint_bool
        current_canvas.clip_bool = last_canvas.clip_bool
        current_canvas.copy_paste_bool = last_canvas.copy_paste_bool
        current_canvas.clip_lblX = last_canvas.clip_lblX
        current_canvas.clip_lblY = last_canvas.clip_lblY
        current_canvas.clip_lblW = last_canvas.clip_lblW
        current_canvas.clip_lblH = last_canvas.clip_lblH
        current_canvas.paste_lblX = last_canvas.paste_lblX
        current_canvas.paste_lblY = last_canvas.paste_lblY
        current_canvas.paste_lblW = last_canvas.paste_lblW
        current_canvas.paste_lblH = last_canvas.paste_lblH
        current_canvas.clip_imgX = last_canvas.clip_imgX
        current_canvas.clip_imgY = last_canvas.clip_imgY
        current_canvas.clip_imgW = last_canvas.clip_imgW
        current_canvas.clip_imgH = last_canvas.clip_imgH
        current_canvas.paste_imgX = last_canvas.paste_imgX
        current_canvas.paste_imgY = last_canvas.paste_imgY
        current_canvas.paste_imgXW = last_canvas.paste_imgXW
        current_canvas.paste_imgYH = last_canvas.paste_imgYH
        current_canvas.copytime_shape = last_canvas.copytime_shape
        
        self.canvas_list[current_index].update_WHratio()
        self.canvas_list[current_index].update_paintrect()
        self.lasttab_index = current_index
        
    def make_leftdock_layout(self):
        #キャンバス用ラベル
        self.canvas_list = []
        self.canvas_list.append(CanvasLabel())
        self.color_list = self.canvas_list[0].color_list
        
        #キャンバスを並べるタブウィジェット
        self.widget_l = CanvasTabWidget()
        widget = QWidget()
        self.widget_l.add_tab(widget)
        self.lasttab_index = self.widget_l.currentIndex()
        self.widget_l.currentChanged.connect(self.transfer_infomation)
        
        self.make_leftwidget_layout(widget)
        
        self.dock_l = QDockWidget("キャンバス", self)
        self.dock_l.setWidget(self.widget_l)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.dock_l)
        
    def make_leftwidget_layout(self, widget):
        
        canvas_box = QHBoxLayout()
        current_widget = self.widget_l.currentWidget()
        current_index = self.widget_l.currentIndex()
        canvas_box.addWidget(self.canvas_list[current_index])
        
        # 画像サイズ設定
        current_widget.imgsize_lbl = QLabel('画像サイズ：')
        current_widget.imgsize_combo = QComboBox(self)
        current_widget.imgsize_combo.addItem("16x16")
        current_widget.imgsize_combo.addItem("32x32")
        current_widget.imgsize_combo.addItem("64x64")
        current_widget.imgsize_combo.addItem("128x128")
        current_widget.imgsize_combo.addItem("256x256")
        current_widget.imgsize_combo.addItem("512x512")
        current_widget.imgsize_combo.addItem("1024x1024")
        current_widget.imgsize_combo.addItem("2048x2048")
        current_widget.imgsize_combo.addItem("4096x4096")
        current_widget.imgsize_combo.activated.connect(self.resize_img)
        
        imgsize_box = QHBoxLayout()
        imgsize_box.addWidget(current_widget.imgsize_lbl)
        imgsize_box.addWidget(current_widget.imgsize_combo)

        # 背景色設定
        current_widget.bg_color_lbl = QLabel('キャンバスの色：')
        current_widget.bg_color_combo = QComboBox(self)
        current_widget.bg_color_combo.addItem("黒")
        current_widget.bg_color_combo.addItem("グレー")
        current_widget.bg_color_combo.addItem("白")
        current_widget.bg_color_combo.activated.connect(self.change_bg_color)
        self.change_bg_color()
        
        bg_color_box = QHBoxLayout()
        bg_color_box.addWidget(current_widget.bg_color_lbl)
        bg_color_box.addWidget(current_widget.bg_color_combo)
        
        #マスターレイアウト
        master_box_l = QVBoxLayout()
        master_box_l.addLayout(canvas_box)
        master_box_l.addLayout(imgsize_box)
        master_box_l.addLayout(bg_color_box)
        
        widget.setLayout(master_box_l)
        
    def make_rightdock_layout(self):
        self.widget_r = QWidget()
        self.make_rightwidget_layout(self.widget_r)

        self.dock_r = QDockWidget("機能", self)
        self.dock_r.setWidget(self.widget_r)
        self.addDockWidget(Qt.RightDockWidgetArea,self.dock_r)
        
    def make_rightwidget_layout(self, widget):

        # キャンバスの追加
        self.addcanvas_btn = QPushButton('キャンバスの追加',self)
        self.addcanvas_btn.clicked.connect(self.add_tab)
        # キャンバスの削除
        self.delcanvas_btn = QPushButton('キャンバスの削除',self)
        self.delcanvas_btn.clicked.connect(self.remove_tab)
        
        adddelcanvas_box = QHBoxLayout()
        adddelcanvas_box.addWidget(self.addcanvas_btn)
        adddelcanvas_box.addWidget(self.delcanvas_btn)

        # 道具の種類設定
        toolkind_lbl = QLabel('道具の種類：')
        self.toolkind_combo = QComboBox(self)
        self.toolkind_combo.addItem("ふで")
        self.toolkind_combo.addItem("バケツ")
        self.toolkind_list = ["pen", "bucket"]
        self.toolkind_combo.activated.connect(self.set_tool)
        
        toolkind_box = QHBoxLayout()
        toolkind_box.addWidget(toolkind_lbl)
        toolkind_box.addWidget(self.toolkind_combo)

        #コピー
        copy_action = QAction(self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.copy_image)
        self.addAction(copy_action)
        
        #カット
        cut_action = QAction(self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.cut_image)
        self.addAction(cut_action)
        
        #ペースト
        paste_action = QAction(self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.paste_image)
        self.addAction(paste_action)
        
        #左右反転ボタン
        self.hflip_btn = QPushButton('左右反転',self)
        self.hflip_btn.clicked.connect(self.hflip_image)
        
        #上下反転ボタン
        self.vflip_btn = QPushButton('上下反転',self)
        self.vflip_btn.clicked.connect(self.vflip_image)
        
        #undoボタン
        self.undo_btn = QPushButton('1つ戻る',self)
        self.undo_btn.clicked.connect(self.undo_image)
        ctrl_z = "Ctrl+Z"
        key_seq_undo = QKeySequence(ctrl_z)
        self.undo_btn.setShortcut(key_seq_undo)
        
        #クリアボタン
        self.clear_btn = QPushButton('クリア',self)
        self.clear_btn.clicked.connect(self.clear_image)
        
        manip_box = QHBoxLayout()
        manip_box.addWidget(self.hflip_btn)
        manip_box.addWidget(self.vflip_btn)
        manip_box.addWidget(self.undo_btn)
        manip_box.addWidget(self.clear_btn)

        #保存ボタン
        self.save_btn = QPushButton('保存',self)
        self.save_btn.clicked.connect(self.save_image)

        #トリム&保存ボタン
        self.trimsave_btn = QPushButton('トリムして保存',self)
        self.trimsave_btn.clicked.connect(self.trimsave_image)
        
        #保存サイズ
        self.savesize_combo = QComboBox(self)
        self.savesize_combo.addItem("保存サイズ：16x16")
        self.savesize_combo.addItem("保存サイズ：32x32")
        self.savesize_combo.addItem("保存サイズ：64x64")
        self.savesize_combo.addItem("保存サイズ：128x128")
        self.savesize_combo.addItem("保存サイズ：256x256")
        self.savesize_combo.addItem("保存サイズ：512x512")
        self.savesize_combo.addItem("保存サイズ：1024x1024")
        self.savesize_combo.addItem("保存サイズ：2048x2048")
        self.savesize_combo.addItem("保存サイズ：4096x4096")
        self.savesize_combo.activated.connect(self.set_savesize)
        save_box = QHBoxLayout()
        save_box.addWidget(self.savesize_combo)
        save_box.addWidget(self.save_btn)
        save_box.addWidget(self.trimsave_btn)

        #色設定ボタン
        self.ButtonGroup = QButtonGroup()
        self.btns = []
        for i in range(len(self.color_list)):
            self.btns.append(QPushButton())
            s = 'background-color: %s;' % self.color_list[i][:-2]
            self.btns[i].setCheckable(True)
            self.btns[i].setStyleSheet(s)
            #self.btns[i].setFixedWidth(50)
            self.btns[i].setFixedHeight(30)
            self.ButtonGroup.addButton(self.btns[i], i)
        self.ButtonGroup.buttonClicked[int].connect(self.set_color)
        self.btns[0].setChecked(True)
        self.btns[len(self.color_list)-1].setIcon(QIcon(resourcePath('eraser.png')))
        self.btns[len(self.color_list)-1].setIconSize(QSize(32,32))
        self.canvas_list[self.widget_l.currentIndex()].color = self.color_list[0]
        
        color_btn_box = QGridLayout()
        color_btn_box.setSpacing(0)
        color_btn_box.setMargin(0)
        col_num = 6
        for i in range(len(self.color_list)//col_num+1):
            for j in range(col_num):
                if i*col_num+j>=len(self.color_list):
                    continue
                color_btn_box.addWidget(self.btns[i*col_num+j],i,j)

        #色表示エディタ
        self.colorname_edit = QLineEdit("")
        colorname_lbl = QLabel('絵具の色：')
        self.colorname_edit.setFixedWidth(100)
        self.colorname_edit.setReadOnly(True)
        s = 'background-color: %s;' % self.canvas_list[self.widget_l.currentIndex()].color[:-2]
        self.colorname_edit.setStyleSheet(s)
        self.colorname_edit.clear()
        self.colorname_edit.insert(self.canvas_list[self.widget_l.currentIndex()].color[:-2])
        
        color_name_box = QHBoxLayout()
        color_name_box.addWidget(colorname_lbl)
        color_name_box.addWidget(self.colorname_edit)
        
        master_box_r = QVBoxLayout()
        master_box_r.addLayout(adddelcanvas_box)
        master_box_r.addLayout(toolkind_box)
        master_box_r.addLayout(color_name_box)
        master_box_r.addLayout(color_btn_box)
        master_box_r.addLayout(manip_box)
        master_box_r.addLayout(save_box)

        widget.setLayout(master_box_r)
            
    def save_image(self):
        img = cv2.resize(self.canvas_list[self.widget_l.currentIndex()].img, self.saveimg_shape, interpolation=cv2.INTER_NEAREST)
        cv2.imwrite("image.png",img)
            
    def trimsave_image(self):
        img = cv2.resize(self.canvas_list[self.widget_l.currentIndex()].img, self.saveimg_shape, interpolation=cv2.INTER_NEAREST)
        y_start = 0
        y_end = img.shape[0]
        x_start = 0
        x_end = img.shape[1]
        for i in range(y_end):
          if np.sum(img[i,:]) != 0:
              y_start = i
              break
        for i in range(x_end):
          if np.sum(img[:,i]) != 0:
              x_start = i
              break
        for i in range(y_end-1,-1,-1):
          if np.sum(img[i,:]) != 0:
              y_end = i + 1
              break
        for i in range(x_end-1,-1,-1):
          if np.sum(img[:,i]) != 0:
              x_end = i + 1
              break
            
        cv2.imwrite("image.png",img[y_start:y_end,x_start:x_end])

    def clear_image(self):
        self.canvas_list[self.widget_l.currentIndex()].clear_image(self.canvas_list[self.widget_l.currentIndex()].shape[0],self.canvas_list[self.widget_l.currentIndex()].shape[1])

    def undo_image(self):
        self.canvas_list[self.widget_l.currentIndex()].undo_image()

    def hflip_image(self):
        self.canvas_list[self.widget_l.currentIndex()].hflip_image()

    def vflip_image(self):
        self.canvas_list[self.widget_l.currentIndex()].vflip_image()

    def copy_image(self):
        self.canvas_list[self.widget_l.currentIndex()].copy_image()
        
    def cut_image(self):
        self.canvas_list[self.widget_l.currentIndex()].cut_image()

    def paste_image(self):
        self.canvas_list[self.widget_l.currentIndex()].paste_image()

    def set_color(self, id):
        self.canvas_list[self.widget_l.currentIndex()].color = self.color_list[id]
        if id == len(self.color_list)-1:
            s = 'background-color: %s;' % self.canvas_list[self.widget_l.currentIndex()].color[0]
            self.colorname_edit.setStyleSheet(s)
            self.colorname_edit.clear()
            self.colorname_edit.insert("透明")
        else:
            s = 'background-color: %s;' % self.canvas_list[self.widget_l.currentIndex()].color[:-2]
            self.colorname_edit.setStyleSheet(s)
            self.colorname_edit.clear()
            self.colorname_edit.insert(self.canvas_list[self.widget_l.currentIndex()].color[:-2])
            
    def set_savesize(self):
        if self.savesize_combo.currentIndex() == 0:
            self.saveimg_shape = (16, 16)
        elif self.savesize_combo.currentIndex() == 1:
            self.saveimg_shape = (32, 32)
        elif self.savesize_combo.currentIndex() == 2:
            self.saveimg_shape = (64, 64)
        elif self.savesize_combo.currentIndex() == 3:
            self.saveimg_shape = (128, 128)
        elif self.savesize_combo.currentIndex() == 4:
            self.saveimg_shape = (256, 256)
        elif self.savesize_combo.currentIndex() == 5:
            self.saveimg_shape = (512, 512)
        elif self.savesize_combo.currentIndex() == 6:
            self.saveimg_shape = (1024, 1024)
        elif self.savesize_combo.currentIndex() == 7:
            self.saveimg_shape = (2048, 2048)
        elif self.savesize_combo.currentIndex() == 8:
            self.saveimg_shape = (4096, 4096)
                    
    def resize_img(self):
        current_widget = self.widget_l.currentWidget()
        current_index = self.widget_l.currentIndex()
        if current_widget.imgsize_combo.currentIndex() == 0:
            self.canvas_list[current_index].shape = (16, 16)
        elif current_widget.imgsize_combo.currentIndex() == 1:
            self.canvas_list[current_index].shape = (32, 32)
        elif current_widget.imgsize_combo.currentIndex() == 2:
            self.canvas_list[current_index].shape = (64, 64)
        elif current_widget.imgsize_combo.currentIndex() == 3:
            self.canvas_list[current_index].shape = (128, 128)
        elif current_widget.imgsize_combo.currentIndex() == 4:
            self.canvas_list[current_index].shape = (256, 256)
        elif current_widget.imgsize_combo.currentIndex() == 5:
            self.canvas_list[current_index].shape = (512, 512)
        elif current_widget.imgsize_combo.currentIndex() == 6:
            self.canvas_list[current_index].shape = (1024, 1024)
        elif current_widget.imgsize_combo.currentIndex() == 7:
            self.canvas_list[current_index].shape = (2048, 2048)
        elif current_widget.imgsize_combo.currentIndex() == 8:
            self.canvas_list[current_index].shape = (4096, 4096)
            
        self.canvas_list[current_index].img = cv2.resize(self.canvas_list[current_index].img, self.canvas_list[current_index].shape, interpolation=cv2.INTER_NEAREST)
        self.canvas_list[current_index].set_pixmap()
        self.canvas_list[current_index].update_WHratio()
        self.canvas_list[current_index].update_paintrect()
        
    def change_bg_color(self):
        current_widget = self.widget_l.currentWidget()
        current_index = self.widget_l.currentIndex()
        if current_widget.bg_color_combo.currentIndex() == 0:
            self.bg_color = "#000000"
        elif current_widget.bg_color_combo.currentIndex() == 1:
            self.bg_color = "#c6c6c6"
        elif current_widget.bg_color_combo.currentIndex() == 2:
            self.bg_color = "#ffffff"
        s = 'background-color: %s;' % self.bg_color
        self.canvas_list[current_index].bg_color = self.bg_color
        self.canvas_list[current_index].change_bg_color()

    def set_tool(self, id):
        current_index = self.widget_l.currentIndex()
        self.canvas_list[current_index].toolkind = self.toolkind_list[self.toolkind_combo.currentIndex()]

    def add_tab(self):
        self.canvas_list.append(CanvasLabel())
        widget = QWidget()
        self.widget_l.add_tab(widget)
        self.widget_l.setCurrentIndex(len(self.canvas_list)-1)
        self.make_leftwidget_layout(widget)
        
    def remove_tab(self):
        if len(self.canvas_list) <= 1:
          return
        current_index = self.widget_l.currentIndex()
        self.canvas_list.pop(current_index)
        self.widget_l.remove_tab(current_index)
        self.lasttab_index = current_index
        
def main():
    app = QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
