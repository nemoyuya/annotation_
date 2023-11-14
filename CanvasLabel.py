# -*- coding: utf-8 -*-
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import cv2
import numpy as np

def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None
    
class CanvasLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True) #画像のドロップを受け付ける

        self.rectX,self.rectY,self.rectW,self.rectH = 0,0,0,0
        #self.img = None
        self.shape = (16, 16)
        self.copytime_shape = self.shape # コピー時の画像サイズ
        self.img = np.zeros((self.shape[0],self.shape[1],4),dtype="uint8")
        self.make_color_list()
        
        self.last_img = None
        self.clip_img = None

        self.set_pixmap()
        
        self.lblX_pressed,self.lblY_pressed = 0,0
        self.lblX_clipstart,self.lblY_clipstart = 0,0
        self.lblX_pasteoffset,self.lblY_pasteoffset = 0,0
        self.imgX,self.imgY,self.imgW,self.imgH = 0,0,0,0

        self.paint_bool = False
        self.clip_bool = False
        self.copy_paste_bool = True #コピーのときTrue、ペーストのときFalse

        self.clip_lblX = 0
        self.clip_lblY = 0
        self.clip_lblW = 0
        self.clip_lblH = 0
        self.paste_lblX = 0
        self.paste_lblY = 0
        self.paste_lblW = 0
        self.paste_lblH = 0
        self.clip_imgX = 0
        self.clip_imgY = 0
        self.clip_imgW = 0
        self.clip_imgH = 0
        self.paste_imgX = 0
        self.paste_imgY = 0
        self.paste_imgXW = 0
        self.paste_imgYH = 0
        
        #self.palette_width = 512
        #self.palette_height = 512
        self.palette_width = 512 + 256
        self.palette_height = 512 + 256
        self.resize(self.palette_width,self.palette_height)
        self.update_WHratio()

        self.color = "#ffffffff"
        self.bg_color = "#000000"
        self.change_bg_color()

        self.pen_size = (1, 1)
        self.toolkind = "pen"
        
        self.imgX = 0
        self.imgY = 0
        self.imgW = 0
        self.imgH = 0
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.palette_width, self.palette_height, self.pixmap)
        if self.bg_color == "#000000":
            painter.setPen(Qt.white)
        else:
            painter.setPen(Qt.black)
        
        painter.drawRect(self.palette_width/2-1, 0, 1, self.palette_height)
        painter.drawRect(0, self.palette_height/2-1, self.palette_width, 1)
        
        if self.clip_bool:
            if self.copy_paste_bool:
                painter.setPen(Qt.green)
                painter.drawRect(self.clip_lblX, self.clip_lblY, self.clip_lblW - 1, self.clip_lblH - 1)
            else:
                painter.setPen(Qt.red)
                painter.drawRect(self.paste_lblX, self.paste_lblY, self.paste_lblW - 1, self.paste_lblH - 1)
            
    def mousePressEvent(self, event):
        pos_x = event.pos().x() 
        pos_y = event.pos().y() 
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.paint_bool = True
                self.clip_bool = False
                self.copy_paste_bool = True
                self.last_img = self.img.copy()
                self.lblX_pressed = pos_x
                self.lblY_pressed = pos_y
                self.calc_xywh()
                self.paint()
            if event.button() == Qt.RightButton:
                if self.copy_paste_bool:#コピー
                    self.paint_bool = False
                    self.clip_bool = True
                    self.lblX_clipstart = self.w_ratio*int(pos_x/self.w_ratio)
                    self.lblY_clipstart = self.h_ratio*int(pos_y/self.h_ratio)
                else:#ペースト
                    self.paste_lblX = self.w_ratio*int(pos_x/self.w_ratio)
                    self.paste_lblY = self.h_ratio*int(pos_y/self.h_ratio)
                    self.update()
        elif event.type() == QEvent.MouseButtonDblClick:
            self.copy_paste_bool = True
            self.clip_bool = False
            self.update()
                
    def mouseMoveEvent(self, event):
        pos_x = event.pos().x() 
        pos_y = event.pos().y()
        if 0 > pos_x or 0 > pos_y:
            return
        if self.paint_bool and self.toolkind == "pen":
            self.lblX_pressed = pos_x
            self.lblY_pressed = pos_y
            self.calc_xywh()
            self.paint()
        if self.clip_bool and self.copy_paste_bool:
            self.lblX_pressed = self.w_ratio*int(pos_x/self.w_ratio)
            self.lblY_pressed = self.h_ratio*int(pos_y/self.h_ratio)
            self.surround()
        if self.clip_bool and not self.copy_paste_bool:
            self.paste_lblX = self.w_ratio*int(pos_x/self.w_ratio)
            self.paste_lblY = self.h_ratio*int(pos_y/self.h_ratio)
            self.update()
            
    def mouseReleaseEvent(self, event):
        self.paint_bool = False
        
    def create_qpixmap(self,img): 
        #変更が加えられた画像を再表示する
        qimage = QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*img.shape[2], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap
        
    def set_pixmap(self):
        self.pixmap = self.create_qpixmap(self.img)
        self.update()

    def calc_xywh(self):
        self.update_WHratio()
        self.imgX_pressed = self.lblX_pressed/self.w_ratio
        self.imgY_pressed = self.lblY_pressed/self.h_ratio
        self.imgX = int(self.imgX_pressed) - self.pen_size[0]//2
        self.imgY = int(self.imgY_pressed) - self.pen_size[1]//2
        self.imgW = self.pen_size[0]
        self.imgH = self.pen_size[1]

    def surround(self):
        self.clip_lblX = min(self.lblX_clipstart, self.lblX_pressed)
        self.clip_lblY = min(self.lblY_clipstart, self.lblY_pressed)
        self.clip_lblX_offset = min(self.clip_lblX, 0)
        self.clip_lblY_offset = min(self.clip_lblY, 0)
        self.clip_lblW = abs(self.lblX_clipstart - self.lblX_pressed)
        self.clip_lblH = abs(self.lblY_clipstart - self.lblY_pressed)
        
        self.clip_lblX = self.clip_lblX - self.clip_lblX_offset
        self.clip_lblY = self.clip_lblY - self.clip_lblY_offset
        self.clip_lblW = self.clip_lblW + self.clip_lblX_offset
        self.clip_lblW = min(self.clip_lblW, self.palette_width - self.clip_lblX)
        self.clip_lblH = self.clip_lblH + self.clip_lblY_offset
        self.clip_lblH = min(self.clip_lblH, self.palette_height - self.clip_lblY)

        self.update()

    def paint(self):
        if self.toolkind == "pen":
            x = self.imgX if self.imgX>=0 else 0
            y = self.imgY if self.imgY>=0 else 0
            xw = self.imgX+self.imgW if self.imgX+self.imgW<=self.img.shape[1] else self.img.shape[1]
            yh = self.imgY+self.imgH if self.imgY+self.imgH<=self.img.shape[0] else self.img.shape[0]
            blue = int(self.color[5:7], 16)
            green = int(self.color[3:5], 16)
            red = int(self.color[1:3], 16)
            alpha = int(self.color[7:], 16)
            self.img[y:yh,x:xw] = (blue, green, red, alpha)
        elif self.toolkind == "bucket":
            x = max(int(self.imgX_pressed),0)
            x = min(x,self.img.shape[1]-1)
            y = max(int(self.imgY_pressed),0)
            y = min(y,self.img.shape[0]-1)
            self.fill_by_bucket(y, x)
            
        self.pixmap = self.create_qpixmap(self.img)
        self.update()

    def clear_image(self, height, width):
        self.last_img = self.img.copy()
        self.img = np.zeros((height, width, 4),dtype="uint8")
        self.set_pixmap()

    def undo_image(self):
        self.img = self.last_img.copy()
        self.set_pixmap()
                
    def resizeEvent(self,event):
        self.update_WHratio()
        self.resize(self.palette_width, self.palette_height)

    def change_bg_color(self):
        s = 'background-color: %s;' % self.bg_color
        self.setStyleSheet(s)
        
    def dropEvent(self, event):
        """
        png,jpg画像をドロップした場合、読み込んで表示する。
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            path = urls[0].toLocalFile()
            if not path[-4:] == ".png":
                return
            self.last_img = self.img.copy()
            tmp_img = imread(path, -1)
            self.adjust_image(tmp_img)
            self.set_pixmap()
            event.accept()
            
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            
    def fill_by_bucket(self, y, x):
        color = self.img[y,x].copy()
        blue = int(self.color[5:7], 16)
        green = int(self.color[3:5], 16)
        red = int(self.color[1:3], 16)
        alpha = int(self.color[7:], 16)
        bool_img = np.zeros((self.shape[0],self.shape[1],1),dtype="uint8")
        color = self.img[y,x].copy()
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if (self.img[i,j] == self.img[y,x]).all():
                    bool_img[i,j] = 255
        nlabels, labels = cv2.connectedComponents(bool_img)
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if labels[i,j] == labels[y,x]:
                    self.img[i,j] = (blue, green, red, alpha)

    def hflip_image(self):
        self.last_img = self.img.copy()
        self.img = cv2.flip(self.img, 1)
        self.set_pixmap()

    def vflip_image(self):
        self.last_img = self.img.copy()
        self.img = cv2.flip(self.img, 0)
        self.set_pixmap()

    def copy_image(self):
        if not self.clip_bool and not self.copy_paste_bool:
            return
        self.clip_imgX = int(self.clip_lblX/self.w_ratio)
        self.clip_imgY = int(self.clip_lblY/self.h_ratio)
        self.clip_imgW = int(self.clip_lblW/self.w_ratio)
        self.clip_imgH = int(self.clip_lblH/self.h_ratio)
        self.clip_img = self.img[self.clip_imgY:self.clip_imgY+self.clip_imgH,self.clip_imgX:self.clip_imgX+self.clip_imgW].copy()

        self.paste_lblX = self.clip_lblX
        self.paste_lblY = self.clip_lblY
        self.paste_lblW = self.clip_lblW
        self.paste_lblH = self.clip_lblH

        self.copy_paste_bool = False
        self.copytime_shape = self.shape
        
        self.update()

    def cut_image(self):
        self.copy_image()
        
        if not self.clip_bool and not self.copy_paste_bool:
            return
        
        self.last_img = self.img.copy()
        self.img[self.clip_imgY:self.clip_imgY+self.clip_imgH,self.clip_imgX:self.clip_imgX+self.clip_imgW]=(0,0,0,0)
        self.set_pixmap()
        
    def paste_image(self):
        if self.copy_paste_bool:
            return
        
        self.paste_imgX = int(self.paste_lblX/self.w_ratio)
        self.paste_imgY = int(self.paste_lblY/self.h_ratio)
        self.paste_imgXW = min(self.img.shape[1],self.paste_imgX+self.clip_imgW)
        self.paste_imgYH = min(self.img.shape[0],self.paste_imgY+self.clip_imgH)
        
        self.last_img = self.img.copy()
        #self.img[self.paste_imgY:self.paste_imgYH,self.paste_imgX:self.paste_imgXW] = self.clip_img[:self.paste_imgYH-self.paste_imgY,:self.paste_imgXW-self.paste_imgX].copy()
        tmp_img = self.clip_img[:self.paste_imgYH-self.paste_imgY,:self.paste_imgXW-self.paste_imgX].copy()
        tmp_img_alpha = tmp_img[:,:,3].copy()
        org_img = self.img[self.paste_imgY:self.paste_imgYH,self.paste_imgX:self.paste_imgXW].copy()
        self.img[self.paste_imgY:self.paste_imgYH,self.paste_imgX:self.paste_imgXW][:,:,0] = np.where(tmp_img[:,:,3]==0,org_img[:,:,0],tmp_img[:,:,0])
        self.img[self.paste_imgY:self.paste_imgYH,self.paste_imgX:self.paste_imgXW][:,:,1] = np.where(tmp_img[:,:,3]==0,org_img[:,:,1],tmp_img[:,:,1])
        self.img[self.paste_imgY:self.paste_imgYH,self.paste_imgX:self.paste_imgXW][:,:,2] = np.where(tmp_img[:,:,3]==0,org_img[:,:,2],tmp_img[:,:,2])
        self.img[self.paste_imgY:self.paste_imgYH,self.paste_imgX:self.paste_imgXW][:,:,3] = np.where(tmp_img[:,:,3]==0,org_img[:,:,3],tmp_img[:,:,3])
        self.set_pixmap()

    def update_WHratio(self):
        self.w_ratio = self.palette_width/self.img.shape[1]
        self.h_ratio = self.palette_height/self.img.shape[0]

    def update_paintrect(self):
        self.paste_lblW = self.clip_lblW*self.copytime_shape[1]/self.shape[1]
        self.paste_lblH = self.clip_lblH*self.copytime_shape[0]/self.shape[0]
                
    def adjust_image(self, tmp_img):
        if tmp_img.shape[2] == 3:
            tmp_img = cv2.cvtColor(tmp_img, cv2.COLOR_RGB2RGBA)

        if tmp_img.shape[0] > self.shape[0]:
            tmp_ys = tmp_img.shape[0]//2 - self.shape[0]//2
            tmp_ye = tmp_img.shape[0]//2 + self.shape[0]//2
            img_ys = 0
            img_ye = self.shape[0]
        else:
            tmp_ys = 0
            tmp_ye = self.shape[0]
            img_ys = (self.shape[0]-tmp_img.shape[0])//2
            img_ye = self.shape[0] - img_ys - tmp_img.shape[0]%2
            
        if tmp_img.shape[1] > self.shape[1]:
            tmp_xs = tmp_img.shape[1]//2 - self.shape[1]//2
            tmp_xe = tmp_img.shape[1]//2 + self.shape[1]//2
            img_xs = 0
            img_xe = self.shape[1]
        else:
            tmp_xs = 0
            tmp_xe = self.shape[1]
            img_xs = (self.shape[1]-tmp_img.shape[1])//2
            img_xe = self.shape[1] - img_xs - tmp_img.shape[1]%2
            
        self.img = np.zeros(((self.shape[0],self.shape[1],4)),dtype="uint8")
        self.img[img_ys:img_ye, img_xs:img_xe, :] = tmp_img[tmp_ys:tmp_ye,tmp_xs:tmp_xe,:].copy()
                        
    def make_color_list(self):
        self.color_list=[
            "#000000ff",
            "#0000ffff",
            "#00ff00ff",
            "#808080ff",
            "#00000000"]
