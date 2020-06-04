import pygame,sys,time,math,threading,os,random,cv2
from pygame.locals import *
import sqlite3
import json
import datetime

from src.fundamentals import *


class button_clicks:
    def __init__(self,main,surface,database,colors,buttons,dividers):
        self.main=main
        self.surface=surface
        self.database=database
        self.colors=colors
        self.buttons=buttons
        self.dividers=dividers
    def open_file(self):
        print ("file opened")
    def canvas_workspace(self):
        # print ("canvas")
        self.main.workspace_mode="canvas"
    def objects_workspace(self):
        # print ("objects")
        self.main.workspace_mode="objects"
    def add_layer(self):
        print ("layer added")
        new_layer=layer__()
        new_layer.name=str(len(self.main.animation.time_strips[self.main.current_time_strip].layers))
        self.main.animation.time_strips[self.main.current_time_strip].layers.append(new_layer)
    def export_for_canvas_button(self):
        # print ("")
        if self.main.object_selected!=None:
            new_object=self.main.objects[self.main.object_selected].copy()
            points=new_object["points"][:]
            del new_object["points"]
            new_object.update({"width":200})
            new_object.update({"height":200})
            new_object.update({"x":random.randint(200,500)})
            new_object.update({"y":random.randint(100,200)})
            new_object.update({"points":points[:]})
            # print (new_object["thickness"])[:]
            new_new_object=new_object.copy()
            # new_object[""]
            # new_new_object
            self.main.animation.time_strips[self.main.current_time_strip].layers[self.main.current_layer].objects.append(new_new_object)
    def export_as_image_button(self):
        filename='src/avatar.jpg'
        # print (os.getcwd())
        img=cv2.imread(filename)
        img=cv2.resize(img,(self.main.canvas_height,self.main.canvas_height))
        print (img,type(img))
        # cv2.imwrite(filename, img)
    def draw_line(self):
        if self.main.workspace_mode=="objects":
            if self.main.workspace_current_object!=None:
                self.main.grabbed=["draw_line",self.main.workspace_current_object]
                # self.main.clicked_first_point_for_shape=[self.main.mouse[0],self.main.mouse[1]]
                # print (self.main.workspace_current_object,len(self.main.objects))
    def pen(self):
        self.main.active_tool="pen"
    def eraser(self):
        self.main.active_tool="eraser"
    def play(self):
        self.main.play_animation=not self.main.play_animation
        # self.main.play_animation=False if self.main.play_animation else True
    def navigate(self,text):
        if text=="open":
            self.open_file()
        elif text=="canvas_workspace":
            self.canvas_workspace()
        elif text=="objects_workspace":
            self.objects_workspace()
        elif text=="add_layer":
            self.add_layer()
        elif text=="export_for_canvas_button":
            self.export_for_canvas_button()
        elif text=="export_as_image_button":
            self.export_as_image_button()
        elif text=="draw_line":
            self.draw_line()
        elif text=="pen":
            self.pen()
        elif text=="eraser":
            self.eraser()
        elif text=="play":
            self.play()




# #----------------
