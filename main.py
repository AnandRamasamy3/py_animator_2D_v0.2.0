import pygame,sys,time,math,threading,os,random
from pygame.locals import *
import sqlite3
import json
import datetime
import warnings

from src.button_clicks import button_clicks
from src.fundamentals import *

pygame.init()
WIDTH,HEIGHT=1220,670
surface=pygame.display.set_mode((WIDTH,HEIGHT),0,32)
fps=100
ft=pygame.time.Clock()
pygame.display.set_caption('animator v1.0.0')


class app:
    def __init__(self,surface):
        self.surface=surface
        self.database={}
        self.colors={}
        self.buttons={}
        self.dividers={}
        self.get_database()
        self.last_button_clicked=time.time()
        self.set_mouse_and_clicks()
        self.button_clicks=button_clicks(self,self.surface,self.database,self.colors,self.buttons,self.dividers)
        self.button_show_mode="text"
        self.font_family="Menlo, Consolas, DejaVu Sans Mono, monospace"
        self.number_of_time_strip_buttons=100
        self.time_strip_buttons=[]
        self.animation=None
        self.current_time_strip=0
        self.current_layer=0
        self.current_object=0
        self.layers_boxes=[]
        self.canvas_width=790
        self.canvas_height=440
        self.workspace_mode="canvas"
        # print (len(self.objects))
        self.maximum_number_of_objects=30
        self.workspace_current_object=None
        self.thickness_meter_level=12
        self.color_meter_RGB=[0,250,180]
        self.fill_shape_status=True
        self.fill_shape_box_positions=[]
        self.objects=[]
        for ___ in range(0):
            self.objects.append({
                "thickness":self.thickness_meter_level,
                "color":self.color_meter_RGB[:],
                "fill":self.fill_shape_status,
                "points":[],
            })
        self.objects_select_positions=[]
        self.objects_edit_positions=[]
        self.objects_delete_positions=[]
        self.object_selected=None
        self.export_for_canvas_button=None
        self.export_as_image_button=None
        self.current_object_for_properties=None
        self.current_object_for_properties_radius=10
        self.grabbed=[None,None]
        self.clicked_first_point_for_shape=None
        self.active_tool="pen"
        self.temporary_shape_points=[]
        self.play_animation=False
    def set_custom_database(self):
        # animation
        self.animation=animation()
        for time_index in range(self.number_of_time_strip_buttons):
            new_time_strip=time_strip()
            self.animation.time_strips.append(new_time_strip)
            self.animation.time_strips[-1].name=time_index*self.animation.unit_time
            for index in range(1):
                new_layer=layer__()
                new_layer.name=str(index)
                self.animation.time_strips[-1].layers.append(new_layer)
        self.layers_boxes=[[]]*len(self.animation.time_strips[self.current_time_strip].layers)
        # print (self.layers_boxes)
        # self.layers_boxes[self.current_layer]=
        pass
        # time_strip
        total_width=780
        x=210
        y=550
        button_width=total_width/self.number_of_time_strip_buttons
        height=50
        for time_strip_index in range(len(self.animation.time_strips)):
            self.time_strip_buttons.append([x,y,button_width,height,button_width*3/4])
            x+=button_width
    def draw_gradient(self,X,Y,width,height,color_1,color_2):
        unit=[]
        for index in range(3):
            unit.append((color_2[index]-color_1[index])/width)
        for x in range(width):
            for y in range(height):
                color=[]
                for index in range(3):
                    color.append(int((color_1[index]+x*unit[index])))
                self.surface.set_at((X+x,Y+y),color)
    def draw_curve_boxes(self,x=0,y=0,width=0,height=0,thickness=1,fill=False,radius=15,color=None,curve_accuracy=30):#25
        if color==None:
            # print (color)
            color=self.color["white"]
        final=[]
        # draw full box
        # pygame.draw.rect(self.surface,self.color["border_lines"],(x,y,width,height),1)
        x1,x2=x+radius,x+width-radius
        y1,y2=y+radius,y+height-radius
        # curve left top
        left_top_points=[
        (x1-radius,y1),
        (x1-radius,y1-radius),
        (x1,y1-radius)
        ]
        curve=curves()
        result=curve.find_curve(left_top_points,T=curve_accuracy)
        final+=result
        # curve right top
        right_top_points=[
        (x2,y1-radius),
        (x2+radius,y1-radius),
        (x2+radius,y1)
        ]
        curve=curves()
        result=curve.find_curve(right_top_points,T=curve_accuracy)
        final+=result
        # curve right bottom
        right_bottom_points=[
        (x2+radius,y2),
        (x2+radius,y2+radius),
        (x2,y2+radius)
        ]
        curve=curves()
        result=curve.find_curve(right_bottom_points,T=curve_accuracy)
        final+=result
        # curve left bottom
        left_bottom_points=[
        (x1,y2+radius),
        (x1-radius,y2+radius),
        (x1-radius,y2)
        ]
        curve=curves()
        result=curve.find_curve(left_bottom_points,T=curve_accuracy)
        final+=result
        # draw box
        if fill:
            pygame.draw.polygon(self.surface,color,final)
        else:
            pygame.draw.polygon(self.surface,color,final,1)
    def euclidean_distance(self,point_1,point_2):
        point=math.sqrt( ((point_1[0]-point_2[0])**2)+((point_1[1]-point_2[1])**2) )
        return point
    def drawDDA_without_percentage(self,point_1,point_2):
        points=[]
        # print ("drawDDA_without_percentage gotcha")
        # print ("paradise",point_1,point_2)
        # x1,y1,x2,y2=point_1[0]*100,point_1[1]*100,point_2[0]*100,point_2[1]*100
        x1,y1,x2,y2=point_1[0],point_1[1],point_2[0],point_2[1]
        x,y = x1,y1
        length=max(abs(x2-x1),abs(y2-y1))
        if length==0:length=-1
        dx=(x2-x1)/float(length)
        dy=(y2-y1)/float(length)
        points.append([int(x+0.5),int(y+0.5)])
        # print (length)
        i=0
        while i<length:
            x+=dx
            y+=dy
            points.append([int(x+0.5),int(y+0.5)])
            i+=1
        return points
    def drawDDA(self,point_1,point_2):
        points=[]
        print ("drawDDA gotcha")
        x1,y1,x2,y2=point_1[0]*100,point_1[1]*100,point_2[0]*100,point_2[1]*100
        # x1,y1,x2,y2=point_1[0],point_1[1],point_2[0],point_2[1]
        x,y = x1,y1
        length=max(abs(x2-x1),abs(y2-y1))
        if length==0:length=-1
        dx=(x2-x1)/float(length)
        dy=(y2-y1)/float(length)
        points.append([int(x+0.5)/100,int(y+0.5)/100])
        # print (length)
        i=0
        while i<length:
            x+=dx
            y+=dy
            points.append([int(x+0.5)/100,int(y+0.5)/100])
            i+=1
        return points
    def get_database(self):
        f_obj=open("src/database.json",)
        data=json.load(f_obj)
        self.color=data["general_colors"]
        self.buttons=data["buttons"]
        self.dividers=data["dividers"]
        f_obj.close()
    def onclick_events(self):
        if self.click[0]==1 and time.time()>=self.last_button_clicked+0.5:
            self.last_button_clicked=time.time()
            # print (self.buttons)
            for button in self.buttons:
                if self.buttons[button]["x"]<=self.mouse[0]<=self.buttons[button]["x"]+self.buttons[button]["width"] and self.buttons[button]["y"]<=self.mouse[1]<=self.buttons[button]["y"]+self.buttons[button]["height"]:
                    # print (self.buttons[button]["text"])
                    self.button_clicks.navigate(button)
            selective_layer=None
            for visible_layer in self.layers_boxes:
                if len(visible_layer)>0:
                    x,y,width,height=visible_layer[1],visible_layer[2],visible_layer[3],visible_layer[4]
                    if x<=self.mouse[0]<=x+width and y<=self.mouse[1]<=y+height:
                        selective_layer=visible_layer[0]
            if selective_layer!=None:
                self.current_layer=selective_layer
                self.grabbed=[None,None]
                self.current_object_for_properties=None
            if self.workspace_mode=="objects":
                if self.workspace_current_object!=None:
                    if len(self.fill_shape_box_positions)>0:
                        x,y,width,height=self.fill_shape_box_positions[0],self.fill_shape_box_positions[1],self.fill_shape_box_positions[2],self.fill_shape_box_positions[3]
                        if x<=self.mouse[0]<=x+width and y<=self.mouse[1]<=y+height:
                            pass
                            # print ("after",self.fill_shape_status)
                            self.fill_shape_status=False if self.fill_shape_status else True
                            self.objects[self.workspace_current_object]["fill"]=self.fill_shape_status
                            # print ("before",self.fill_shape_status)
                for ball in self.objects_delete_positions:
                    x,y,size=ball[1][0],ball[1][1],ball[1][2]
                    # print (self.mouse,x,y,size)
                    dist=self.euclidean_distance(self.mouse,(x,y))
                    if dist<=size:
                        # print ("deleted",ball)
                        self.objects.pop(ball[0])
                        self.object_selected=None
                        self.workspace_current_object=None#.main
                for button in self.objects_select_positions:
                    # print (button,self.object_selected)
                    x,y,size=button[1][0],button[1][1],button[1][2]
                    if x<=self.mouse[0]<=x+size and y<=self.mouse[1]<=y+size:
                        # print (button)
                        self.object_selected=button[0]
                    # print (button,self.object_selected)
                for ball in self.objects_edit_positions:
                    # print (ball,self.mouse)
                    x,y,size=ball[1][0],ball[1][1],ball[1][2]
                    # print (self.mouse,x,y,size)
                    dist=self.euclidean_distance(self.mouse,(x,y))
                    if dist<=size:
                        # print ("ooops")
                        # print (len(self.objects),ball[0])
                        if ball[0]<len(self.objects):
                            # print (ball[0])
                            # print ("")
                            self.workspace_current_object=ball[0]
                            self.thickness_meter_level=self.objects[self.workspace_current_object]["thickness"]
                            self.color_meter_RGB=self.objects[self.workspace_current_object]["color"][:]
                            # print (self.objects[self.workspace_current_object]["color"][:])
                            self.fill_shape_status=self.objects[self.workspace_current_object]["fill"]
                if self.export_for_canvas_button!=None:
                    x,y,width,height=self.export_for_canvas_button["x"],self.export_for_canvas_button["y"],self.export_for_canvas_button["width"],self.export_for_canvas_button["height"]
                    text=self.export_for_canvas_button["name"]
                    if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                        # print ("called")
                        self.button_clicks.navigate(text)
                if self.export_as_image_button!=None:
                    x,y,width,height=self.export_as_image_button["x"],self.export_as_image_button["y"],self.export_as_image_button["width"],self.export_as_image_button["height"]
                    text=self.export_as_image_button["name"]
                    if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                        # print ("called")
                        self.button_clicks.navigate(text)
            if self.current_object_for_properties!=None:
                x=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["x"]
                y=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["y"]
                width=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["width"]
                height=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["height"]
                pygame.draw.rect(self.surface,self.color["background"],(x,y,width,height),1)
                # # move
                # pygame.draw.circle(self.surface,self.color["current_object_for_properties_move"],(x+self.current_object_for_properties_radius,y+self.current_object_for_properties_radius),self.current_object_for_properties_radius)
                dist=self.euclidean_distance(self.mouse,(x+self.current_object_for_properties_radius,y+self.current_object_for_properties_radius))
                if dist<=self.current_object_for_properties_radius:
                    # print ("movable")
                    self.grabbed=["object_ball_movable",self.current_object_for_properties]
                # resize
                # pygame.draw.circle(self.surface,self.color["current_object_for_properties_resize"],(x+width-self.current_object_for_properties_radius,y+height-self.current_object_for_properties_radius),self.current_object_for_properties_radius)
                dist=self.euclidean_distance(self.mouse,(x+width-self.current_object_for_properties_radius,y+height-self.current_object_for_properties_radius))
                if dist<=self.current_object_for_properties_radius:
                    # print ("resizable")
                    self.grabbed=["object_ball_resizable",self.current_object_for_properties]
                # delete
                # pygame.draw.circle(self.surface,self.color["current_object_for_properties_delete"],(x+self.current_object_for_properties_radius,y+height-self.current_object_for_properties_radius),self.current_object_for_properties_radius)
                dist=self.euclidean_distance(self.mouse,(x+self.current_object_for_properties_radius,y+height-self.current_object_for_properties_radius))
                if dist<=self.current_object_for_properties_radius:
                    # print ("deletable")
                    # print (len(self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects),self.current_object_for_properties)
                    self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects.pop(self.current_object_for_properties)
                    self.current_object_for_properties=None
                    self.grabbed=[None,None]
            if self.workspace_mode=="canvas":
                if 205<=self.mouse[0]<=205+self.canvas_width and 55<=self.mouse[1]<=55+self.canvas_height:
                    # print (self.current_object_for_properties)
                    if self.current_object_for_properties!=None:
                        if self.grabbed[0]=="object_ball_movable":
                            self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["x"]=self.mouse[0]
                            self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["y"]=self.mouse[1]
                    if self.current_object_for_properties!=None:
                        if self.grabbed[0]=="object_ball_resizable":
                            x1=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["x"]
                            y1=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["y"]
                            x2,y2=self.mouse[0],self.mouse[1]
                            x_dist=abs(x1-x2)
                            y_dist=abs(y1-y2)
                            if x1<x2 and y1<y2:
                                pass
                                self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["width"]=x_dist
                                self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["height"]=y_dist
                            # self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["x"]=self.mouse[0]
                            # self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["y"]=self.mouse[1]
        if self.click[2]==1:
            if self.grabbed[0]=="draw_line":
                # print (len(self.temporary_shape_points))
                for point in self.temporary_shape_points:
                    self.objects[self.workspace_current_object]["points"].append([(point[0]-205)/self.canvas_height,(point[1]-55)/self.canvas_height])
                self.clicked_first_point_for_shape=None
                self.temporary_shape_points=[]
                # print ("hahahaha")
            self.grabbed=[None,None]
    def buttons_control(self):
        for button in self.buttons:
            x,y,width,height=self.buttons[button]["x"],self.buttons[button]["y"],self.buttons[button]["width"],self.buttons[button]["height"]
            button_size=30
            if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                button_size=30
                if self.button_show_mode=="text":
                    self.draw_curve_boxes(x,y,width,height,color=self.color["button_background_hover"],fill=True,radius=10)
                    temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
                    object_name_text_bottom=temp_font.render(self.buttons[button]["text"],False,self.color["button_text"])
                    surface.blit(object_name_text_bottom,(x+10,y+2))
                else:
                    self.draw_curve_boxes(x,y,button_size,button_size,radius=10)
            else:
                if self.button_show_mode=="text":
                    self.draw_curve_boxes(x,y,width,height,color=self.color["button_background"],fill=True,radius=10)
                    temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
                    object_name_text_bottom=temp_font.render(self.buttons[button]["text"],False,self.color["button_text"])
                    surface.blit(object_name_text_bottom,(x+10,y+2))
                else:
                    self.draw_curve_boxes(x,y,button_size,button_size,radius=10)
        for button in self.time_strip_buttons:
            x=button[0]
            y=button[1]
            button_size=button[2]
            height=button[3]
            radius=button[4]
            if self.current_time_strip==self.time_strip_buttons.index(button):
                self.draw_curve_boxes(x,y,button_size,height,color=self.color["button_background"],fill=True,radius=radius)
            else:
                self.draw_curve_boxes(x,y,button_size,height,color=self.color["button_background"],radius=radius)
            if x<self.mouse[0]<x+button_size and y<self.mouse[1]<y+height:
                self.draw_curve_boxes(x,y,button_size,height,color=self.color["button_background_hover"],fill=True,radius=radius)
                if self.click[0]==1:
                    self.current_time_strip=self.time_strip_buttons.index(button)
                    self.current_layer=0
                    self.grabbed=[None,None]
                    self.current_object_for_properties=None
        if self.export_for_canvas_button!=None:
            x,y,width,height=self.export_for_canvas_button["x"],self.export_for_canvas_button["y"],self.export_for_canvas_button["width"],self.export_for_canvas_button["height"]
            self.draw_curve_boxes(x,y,width,height,color=self.color["button_background"],fill=True,radius=10)
            if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                self.draw_curve_boxes(x,y,width,height,color=self.color["button_background_hover"],fill=True,radius=10)
            temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
            object_name_text_bottom=temp_font.render(self.export_for_canvas_button["text"],False,self.color["white"])
            surface.blit(object_name_text_bottom,(x+10,y+2))
        # self.export_as_image_button
        if self.export_as_image_button!=None:
            x,y,width,height=self.export_as_image_button["x"],self.export_as_image_button["y"],self.export_as_image_button["width"],self.export_as_image_button["height"]
            self.draw_curve_boxes(x,y,width,height,color=self.color["button_background"],fill=True,radius=10)
            if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                self.draw_curve_boxes(x,y,width,height,color=self.color["button_background_hover"],fill=True,radius=10)
            temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
            object_name_text_bottom=temp_font.render(self.export_as_image_button["text"],False,self.color["white"])
            surface.blit(object_name_text_bottom,(x+10,y+2))
    def draw_dividers(self):
        for divider in self.dividers:
            point_1,point_2=self.dividers[divider][0],self.dividers[divider][1]
            pygame.draw.line(self.surface,self.color["dividers"],point_1,point_2,1)
    def draw_layers(self):
        # pygame.draw.
        canvas_width_height_ratio=self.canvas_width/self.canvas_height
        main_layer_model_width=150                                                  # 150
        main_layer_model_height=main_layer_model_width/canvas_width_height_ratio    # 83.544
        # print (len(self.animation.time_strips[self.current_time_strip].layers))
        x1,y1=1010,490-main_layer_model_height
        x2,y2=x1+(10*5),y1-(20*5)
        # self.layers_boxes=[]
        self.layers_boxes=[[]]*len(self.animation.time_strips[self.current_time_strip].layers)
        if len(self.animation.time_strips[self.current_time_strip].layers)>0:
            unit_x=x2-x1
            unit_y=y1-y2
            if self.current_layer>0:
                unit_x=(x2-x1)/self.current_layer
                unit_y=(y1-y2)/self.current_layer
            # if self.current_layer
            for layer_index in range(0,self.current_layer+1):
                pygame.draw.rect(self.surface,self.color["white"],(x2,y2,main_layer_model_width,main_layer_model_height))
                pygame.draw.rect(self.surface,self.color["background"],(x2,y2,main_layer_model_width,main_layer_model_height),1)
                #
                temp_font=pygame.font.SysFont(self.font_family,11,bold=True,italic=False)
                object_name_text_bottom=temp_font.render(self.animation.time_strips[self.current_time_strip].layers[layer_index].name,False,self.color["background"])
                surface.blit(object_name_text_bottom,(x2+5,y2+2))
                #
                self.layers_boxes[layer_index]=[layer_index,x2,y2,main_layer_model_width,main_layer_model_height]
                #
                x2-=unit_x
                y2+=unit_y
                # print ("hahahaha",layer_index)
            # print ((self.current_layer+1),len(self.animation.time_strips[self.current_time_strip].layers))
            if (self.current_layer+1)<len(self.animation.time_strips[self.current_time_strip].layers):
                main_layer_model_width//=2
                main_layer_model_height//=2
                x,y=1005,490-main_layer_model_height+5
                pygame.draw.rect(self.surface,self.color["white"],(x,y,main_layer_model_width,main_layer_model_height))
                pygame.draw.rect(self.surface,self.color["background"],(x,y,main_layer_model_width,main_layer_model_height),1)
                #
                temp_font=pygame.font.SysFont(self.font_family,11,bold=True,italic=False)
                object_name_text_bottom=temp_font.render(self.animation.time_strips[self.current_time_strip].layers[layer_index+1].name,False,self.color["background"])
                surface.blit(object_name_text_bottom,(x+5,y+2))
                #
                self.layers_boxes[layer_index+1]=[layer_index+1,x,y,main_layer_model_width,main_layer_model_height]
                # print ("hahahaha---")
            # print ()
        # self.draw_curve_boxes(1010,500,40,20,color=self.color["white"],radius=10)
    def draw_canvas(self):
        if self.workspace_mode=="canvas":
            # self.current_object_for_properties=None
            selected_temp=None
            clicked=False
            pygame.draw.rect(self.surface,self.color["white"],(205,55,self.canvas_width,self.canvas_height))
            for layer in self.animation.time_strips[self.current_time_strip].layers:
                for object in layer.objects:
                    # print (object["thickness"])
                    x=object["x"]
                    y=object["y"]
                    width=object["width"]
                    height=object["height"]
                    thickness=(object["thickness"]/self.canvas_height)*width
                    # thickness=(self.objects[object_index]["thickness"]/self.canvas_height)*size
                    color=object["color"][:]
                    fill=object["fill"]
                    points=object["points"][:]
                    for point in points:
                        pixel_x=int(x+point[0]*width)
                        pixel_y=int(y+point[1]*height)
                        # pygame.draw.rect(self.surface,color,(pixel_x,pixel_y,thickness,thickness))
                        self.surface.set_at((pixel_x,pixel_y),color)
                        # print (pixel_x,pixel_y)
                        if self.click[0]==1:
                            clicked=True
                            # if pixel_x<=self.mouse[0]<=pixel_x+thickness and pixel_y<=self.mouse[1]<=pixel_y+thickness:
                            if x<=self.mouse[0]<=x+width and y<=self.mouse[1]<=y+height:
                                try:
                                    selected_temp=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects.index(object)
                                except:
                                    pass
                    # pygame.draw.rect(self.surface,color,(x,y,width,height),1)
                    pass
                    # print (self.mouse,pixel_x,pixel_y)
                    # print (self.current_object_for_properties)
                    if clicked:
                        # if selected_temp==None:
                        if self.grabbed[1]==None:
                            self.current_object_for_properties=selected_temp
        elif self.workspace_mode=="objects":
            pygame.draw.rect(self.surface,self.color["white"],(205,55,self.canvas_height,self.canvas_height))
            if self.workspace_current_object!=None:
                if len(self.temporary_shape_points)>0:
                    # print (self.temporary_shape_points[0],self.temporary_shape_points[-1])
                    for point in self.temporary_shape_points:
                        # pygame.draw.rect(self.surface,self.objects[self.workspace_current_object]["color"],(point[0],point[1],self.objects[self.workspace_current_object]["thickness"],self.objects[self.workspace_current_object]["thickness"]))
                        # self.surface.set_at([int(point[0]),int(point[1])],self.objects[self.workspace_current_object]["color"])
                        pygame.draw.rect(self.surface,self.objects[self.workspace_current_object]["color"],(point[0],point[1],1,1))
                        # pygame.draw.rect(self.surface,self.objects[self.workspace_current_object]["color"],(point[0],point[1],2,2))
                        # print (point)
                if self.click[0]==1:
                    x1,y1,size,x2,y2=205,55,self.canvas_height,205+self.canvas_height,55+self.canvas_height
                    if x1<=self.mouse[0]<=x2 and y1<=self.mouse[1]<=y2:
                        x=(pygame.mouse.get_pos()[0]-x1)/(x2-x1)
                        y=(pygame.mouse.get_pos()[1]-y1)/(y2-y1)
                        # print (x,y)
                        # print (self.objects,self.workspace_current_object)
                        if self.grabbed[0]=="draw_line":
                            if self.clicked_first_point_for_shape==None:
                                self.clicked_first_point_for_shape=[self.mouse[0],self.mouse[1]]
                                # print ("gotcha",self.mouse)
                            else:
                                # print ("",self.clicked_first_point_for_shape)
                                thickness=self.objects[self.workspace_current_object]["thickness"]
                                point_1=[self.clicked_first_point_for_shape[0],self.clicked_first_point_for_shape[1]]
                                point_2=[self.mouse[0],self.mouse[1]]
                                intermediate_points=self.drawDDA_without_percentage(point_1,point_2)
                                # print (point_1,point_2,len(intermediate_points),self.euclidean_distance(point_1,point_2))
                                self.temporary_shape_points=[]
                                for point in intermediate_points:
                                    # self.temporary_shape_points.append([point[0],point[1]])
                                    for x_ in range(point[0],point[0]+thickness):
                                        for y_ in range(point[1],point[1]+thickness):
                                            # print (x_,y_)
                                            pixel_x=(x_-x1)/(x2-x1)
                                            pixel_y=(y_-y1)/(y2-y1)
                                            if [pixel_x,pixel_y]  not in self.temporary_shape_points:
                                                self.temporary_shape_points.append([pixel_x,pixel_y])
                                    # print (point)
                                    # x_=point[0]
                                    # for ___ in range(thickness):
                                    #     y_=point[1]
                                    #     for ____ in range(thickness):
                                    #         # if [x_,y_] not in self.objects[self.workspace_current_object]["points"]:
                                    #         # self.objects[self.workspace_current_object]["points"].append([x_,y_])
                                    #         self.temporary_shape_points.append([x_,y_])
                                    #         y_+=0.01
                                    #     x_+=0.01
                                # print ("506",point,self.mouse)
                                    # pygame.draw.rect(self.surface,self.objects[self.workspace_current_object]["color"],(point[0],point[1],thickness,thickness))
                                # pygame.draw.line(self.surface,self.objects[self.workspace_current_object]["color"],point_1,point_2,5)
                        else:
                            if self.active_tool=="pen":
                                thickness=self.objects[self.workspace_current_object]["thickness"]
                                # self.objects[self.workspace_current_object]["points"].append([x,y])
                                # print (x,y)
                                # self.objects[self.workspace_current_object]["points"].append([x_,y_])
                                for x_ in range(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[0]+thickness):
                                    for y_ in range(pygame.mouse.get_pos()[1],pygame.mouse.get_pos()[1]+thickness):
                                        # print (x_,y_)
                                        pixel_x=(x_-x1)/(x2-x1)
                                        pixel_y=(y_-y1)/(y2-y1)
                                        if [pixel_x,pixel_y]  not in self.objects[self.workspace_current_object]["points"]:
                                            self.objects[self.workspace_current_object]["points"].append([pixel_x,pixel_y])
                                # print ("hahahaha")
                            else:
                                thickness=self.objects[self.workspace_current_object]["thickness"]
                                # print (x,x+thickness)
                                for x_ in range(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[0]+thickness):
                                    for y_ in range(pygame.mouse.get_pos()[1],pygame.mouse.get_pos()[1]+thickness):
                                        # print (x_,y_)
                                        pixel_x=(x_-x1)/(x2-x1)
                                        pixel_y=(y_-y1)/(y2-y1)
                                        if [pixel_x,pixel_y] in self.objects[self.workspace_current_object]["points"]:
                                            self.objects[self.workspace_current_object]["points"].remove([pixel_x,pixel_y])
                            if False:
                                if len(self.objects[self.workspace_current_object]["points"])>0:
                                    point_1=self.objects[self.workspace_current_object]["points"][-1]
                                    point_2=[x,y]
                                    # print (point_1,point_2)
                                    intermediate_points=self.drawDDA(point_1,point_2)
                                    for point in intermediate_points:
                                        self.objects[self.workspace_current_object]["points"].append(point)
                                else:
                                    self.objects[self.workspace_current_object]["points"].append([x,y])
    def draw_eraser(self):
        pass
        if self.active_tool=="eraser":
            if self.workspace_mode=="objects":
                if self.workspace_current_object!=None:
                    if 205<=self.mouse[0]<=205+self.canvas_height and 55<=self.mouse[1]<=55+self.canvas_height:
                        width=205+self.canvas_height-self.mouse[0] if 205+self.canvas_height-self.mouse[0]<self.thickness_meter_level else self.thickness_meter_level
                        height=55+self.canvas_height-self.mouse[1] if 55+self.canvas_height-self.mouse[1]<self.thickness_meter_level else self.thickness_meter_level
                        pygame.draw.rect(self.surface,self.color["black"],(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],width,height),1)
    def draw_properties_box(self):
        if self.workspace_mode=="objects":
            if self.workspace_current_object==None:
                pass
            else:
                pass
                x,y,width,height=1010,70,150,5
                # thickness
                temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
                object_name_text_bottom=temp_font.render("Thickness",False,self.color["thickness_meter_text"])
                surface.blit(object_name_text_bottom,(x,y))
                x+=20
                y+=20
                self.draw_curve_boxes(x,y,width,height,color=self.color["thickness_meter_bar"],fill=True,radius=height//2)
                thickness_scale=31#
                thickness_cursor_x=((self.thickness_meter_level-1)/thickness_scale)*width
                # print (thickness_cursor_x)
                pygame.draw.circle(self.surface,self.color["thickness_meter_bar"],(int(x+thickness_cursor_x),int(y+height//2)),int(height*1.5))
                if self.click[0]==1:
                    if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                        cursor=int(((self.mouse[0]-x)/width)*thickness_scale)+1
                        # print (cursor)
                        self.thickness_meter_level=cursor
                        self.objects[self.workspace_current_object]["thickness"]=self.thickness_meter_level
                # color
                x-=20
                y+=20
                temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
                object_name_text_bottom=temp_font.render("Color Meter",False,self.color["color_meter_text"])
                surface.blit(object_name_text_bottom,(x,y))
                x+=20
                y+=25
                color_scale=255#
                pointer_size=[2,5]
                # self.draw_curve_boxes(x,y,width,height,color=self.color["color_meter_bar"],fill=True,radius=height//2)
                self.draw_gradient(x,y,width,height,[0,0,0],[255,0,0])
                color_cursor_x=((self.color_meter_RGB[0])/color_scale)*width
                # print (thickness_cursor_x)
                pygame.draw.rect(self.surface,self.color["color_meter_bar"],(int(x+color_cursor_x),int(y-pointer_size[1]),pointer_size[0],pointer_size[1]))
                if self.click[0]==1:
                    if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                        cursor=int(((self.mouse[0]-x)/width)*color_scale)
                        # print (cursor)
                        self.color_meter_RGB[0]=cursor
                        self.objects[self.workspace_current_object]["color"][0]=self.color_meter_RGB[0]
                y+=15
                # self.draw_curve_boxes(x,y,width,height,color=self.color["color_meter_bar"],fill=True,radius=height//2)
                self.draw_gradient(x,y,width,height,[0,0,0],[0,255,0])
                color_cursor_x=((self.color_meter_RGB[1])/color_scale)*width
                # print (thickness_cursor_x)
                pygame.draw.rect(self.surface,self.color["color_meter_bar"],(int(x+color_cursor_x),int(y-pointer_size[1]),pointer_size[0],pointer_size[1]))
                if self.click[0]==1:
                    if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                        cursor=int(((self.mouse[0]-x)/width)*color_scale)
                        # print (cursor)
                        self.color_meter_RGB[1]=cursor
                        self.objects[self.workspace_current_object]["color"][1]=self.color_meter_RGB[1]
                y+=15
                # self.draw_curve_boxes(x,y,width,height,color=self.color["color_meter_bar"],fill=True,radius=height//2)
                self.draw_gradient(x,y,width,height,[0,0,0],[0,0,255])
                color_cursor_x=((self.color_meter_RGB[2])/color_scale)*width
                # print (thickness_cursor_x)
                pygame.draw.rect(self.surface,self.color["color_meter_bar"],(int(x+color_cursor_x),int(y-pointer_size[1]),pointer_size[0],pointer_size[1]))
                if self.click[0]==1:
                    if x<self.mouse[0]<x+width and y<self.mouse[1]<y+height:
                        cursor=int(((self.mouse[0]-x)/width)*color_scale)
                        # print (cursor)
                        self.color_meter_RGB[2]=cursor
                        self.objects[self.workspace_current_object]["color"][2]=self.color_meter_RGB[2]
                y+=15
                width,height=40,20
                self.draw_curve_boxes(x,y,width,height,color=self.color_meter_RGB,fill=True,radius=height//2)
                self.draw_curve_boxes(x,y,width,height,color=self.color["color_meter_bar"],radius=height//2)
                # fill
                x-=20
                y+=50
                temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
                object_name_text_bottom=temp_font.render("Fill",False,self.color["fill_shape_text"])
                surface.blit(object_name_text_bottom,(x,y))
                x+=50
                y-=5
                height,width=20,20
                self.draw_curve_boxes(x,y,width,height,color=self.color["fill_shape_box"],radius=height//2)
                self.fill_shape_box_positions=[x,y,width,height]
                if self.fill_shape_status:
                    self.draw_curve_boxes(x+width//4,y+height//4,width//2,height//2,color=self.color["fill_shape_box"],fill=True,radius=3)
        elif self.workspace_mode=="canvas_":
            # print ("ooops")
            x,y,width,height=1010,70,150,5
            # x
            temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
            object_name_text_bottom=temp_font.render("X :",False,self.color["position_x_text"])
            surface.blit(object_name_text_bottom,(x,y))
            x+=30
            width,height=60,20
            self.draw_curve_boxes(x,y,width,height,color=self.color["position_x_box"],radius=height//2)
            x+=80
            # y
            temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
            object_name_text_bottom=temp_font.render("Y :",False,self.color["position_y_text"])
            surface.blit(object_name_text_bottom,(x,y))
            x+=30
            width,height=60,20
            self.draw_curve_boxes(x,y,width,height,color=self.color["position_y_box"],radius=height//2)
            # width
            x=1010
            y+=40
            temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
            object_name_text_bottom=temp_font.render("Width :",False,self.color["position_width_text"])
            surface.blit(object_name_text_bottom,(x,y))
            x+=50
            width,height=100,20
            self.draw_curve_boxes(x,y,width,height,color=self.color["position_width_box"],radius=height//2)
            # height
            x-=50
            y+=40
            temp_font=pygame.font.SysFont(self.font_family,11,bold=False,italic=False)
            object_name_text_bottom=temp_font.render("Height :",False,self.color["position_height_text"])
            surface.blit(object_name_text_bottom,(x,y))
            x+=50
            width,height=100,20
            self.draw_curve_boxes(x,y,width,height,color=self.color["position_height_box"],radius=height//2)
    def draw_objects_list(self):
        if self.workspace_mode=="objects":
            self.objects_select_positions=[]
            self.objects_edit_positions=[]
            self.objects_delete_positions=[]
            # if self.workspace_current_object==None:
            size=50
            x,y=205+self.canvas_height+25,70
            ball_radius=5
            object_index=0
            # time_=time.time()
            # print ("before for",time.time()-time_)
            for object_index in range(len(self.objects)):
                pass
                # print (self.color["button_background"])
                # self.draw_curve_boxes(x,y,size,size,color=self.color["button_background"],radius=10)
                if self.object_selected==object_index:
                    selected=True
                    pygame.draw.rect(self.surface,self.color["white"],(x,y-5,size,size+5))
                    if self.workspace_current_object==object_index:
                        pygame.draw.circle(self.surface,self.color["objects_list_edit"],(x+size,y-5),ball_radius,1)
                    else:
                        pygame.draw.circle(self.surface,self.color["objects_list_edit"],(x+size,y-5),ball_radius)
                    self.objects_edit_positions.append([object_index,[x+size,y-5,ball_radius]])
                    pygame.draw.circle(self.surface,self.color["objects_list_delete"],(x,y+size),ball_radius)
                    self.objects_delete_positions.append([object_index,[x,y+size,ball_radius]])
                else:
                    selected=False
                    pygame.draw.rect(self.surface,self.color["white"],(x,y,size,size))
                    if self.workspace_current_object==object_index:
                        pygame.draw.circle(self.surface,self.color["objects_list_edit"],(x+size,y),ball_radius,1)
                    else:
                        pygame.draw.circle(self.surface,self.color["objects_list_edit"],(x+size,y),ball_radius)
                    self.objects_edit_positions.append([object_index,[x+size,y,ball_radius]])
                    pygame.draw.circle(self.surface,self.color["objects_list_delete"],(x,y+size),ball_radius)
                    self.objects_delete_positions.append([object_index,[x,y+size,ball_radius]])
                # print (object_index)
                thickness=(self.objects[object_index]["thickness"]/self.canvas_height)*size
                color=self.objects[object_index]["color"][:]
                fill=self.objects[object_index]["fill"]
                points=self.objects[object_index]["points"]
                for point in points:
                    pass
                    if selected:
                        pixel_x,pixel_y=x+(point[0]*size),y-5+point[1]*size
                    else:
                        pixel_x,pixel_y=x+(point[0]*size),y+point[1]*size
                    pygame.draw.rect(self.surface,color,(pixel_x,pixel_y,thickness,thickness))
                # try:
                #     print ("714",pixel_x,pixel_y,self.mouse)
                # except:
                #     pass
                self.objects_select_positions.append([object_index,[x,y,size]])
                x+=size+10
                if x>=1000-size:
                    x=205+self.canvas_height+25
                    y+=size+10
            # print ("after for",time.time()-time_)
            # time_=time.time()
            # self.draw_curve_boxes(x,y,size,size,color=self.color["button_background"],radius=10)
            if self.click[0]==1:
                if x<=self.mouse[0]<=x+size and y<=self.mouse[1]<=y+size:
                    # print ("ooops")
                    if len(self.objects)<self.maximum_number_of_objects:
                        self.objects.append({
                            "thickness":self.thickness_meter_level,
                            "color":self.color_meter_RGB[:],
                            "fill":self.fill_shape_status,
                            "points":[],
                        })
                        # print (button[0])
                        self.workspace_current_object=object_index
            if len(self.objects)<self.maximum_number_of_objects:
                temp_font=pygame.font.SysFont(self.font_family,32,bold=False,italic=False)
                object_name_text_bottom=temp_font.render("+",False,self.color["white"])
                surface.blit(object_name_text_bottom,(x+size//4,y+size//8))
                if self.object_selected==None:
                    self.objects_select_positions.append([0,[x,y,size]])
                else:
                    self.objects_select_positions.append([object_index+1,[x,y,size]])
            # print ("before selected",time.time()-time_)
            # time_=time.time()
            if self.object_selected!=None:
                # print (self.object_selected,self.mouse)
                x,y,width=650,430,340
                pygame.draw.line(self.surface,self.color["white"],(x,y),(x+width,y),1)
                #pass#
                x+=25
                # selected
                y+=20
                temp_font=pygame.font.SysFont(self.font_family,13,bold=False,italic=False)
                object_name_text_bottom=temp_font.render("Selected",False,self.color["white"])
                surface.blit(object_name_text_bottom,(x,y))
                # object
                y+=20
                temp_font=pygame.font.SysFont(self.font_family,13,bold=False,italic=False)
                object_name_text_bottom=temp_font.render("Object",False,self.color["white"])
                surface.blit(object_name_text_bottom,(x,y))
                # draw object box
                x+=80
                y-=25
                pygame.draw.rect(self.surface,self.color["white"],(x,y,size,size))
                # print (self.objects,self.object_selected)
                thickness=(self.objects[self.object_selected]["thickness"]/self.canvas_height)*size
                color=self.objects[self.object_selected]["color"][:]
                fill=self.objects[self.object_selected]["fill"]
                points=self.objects[self.object_selected]["points"]
                for point in points:
                    pass
                    pixel_x,pixel_y=x+(point[0]*size),y+point[1]*size
                    pygame.draw.rect(self.surface,color,(pixel_x,pixel_y,thickness,thickness))
                # try:
                #     print ("775",pixel_x,pixel_y,self.mouse)
                # except:
                #     pass
                x+=size+30
                y-=5
                width,height=140,20
                # draw export for canvas button
                self.export_for_canvas_button={
                  "name":"export_for_canvas_button",
                  "text":"Export for Canvas",
                  "x":x,
                  "y":y,
                  "width":width,
                  "height":height
                }
                y+=height+10
                # draw export as image button
                self.export_as_image_button={
                  "name":"export_as_image_button",
                  "text":"Export as Image",
                  "x":x,
                  "y":y,
                  "width":width,
                  "height":height
                }
            # print ("after selected",time.time()-time_)
            # time_=time.time()
    def draw_objects_plane(self):
        if self.workspace_mode=="objects":
            if self.workspace_current_object!=None:
                # print (self.objects,self.workspace_current_object)
                for point in self.objects[self.workspace_current_object]["points"]:
                    # print (point)
                    # x,y=int(205+(point[0]*self.canvas_height)),int(55+point[1]*self.canvas_height)
                    x,y=205+(point[0]*self.canvas_height),55+point[1]*self.canvas_height
                    # print (x,y,self.mouse)
                    # pygame.draw.rect(self.surface,self.objects[self.workspace_current_object]["color"],(x,y,self.objects[self.workspace_current_object]["thickness"],self.objects[self.workspace_current_object]["thickness"]))
                    # self.surface.set_at((x,y),self.objects[self.workspace_current_object]["color"])
                    pygame.draw.rect(self.surface,self.objects[self.workspace_current_object]["color"],(x,y,2,2))
                    # print (x,y,self.mouse)
                # try:
                # except:
                #     pass
    def set_object_in_canvas_for_properties(self):
        if self.workspace_mode=="canvas":
            if self.current_object_for_properties!=None:
                # print (self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties])
                x=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["x"]
                y=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["y"]
                width=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["width"]
                height=self.animation.time_strips[self.current_time_strip].layers[self.current_layer].objects[self.current_object_for_properties]["height"]
                pygame.draw.rect(self.surface,self.color["background"],(x,y,width,height),1)
                # move
                pygame.draw.circle(self.surface,self.color["current_object_for_properties_move"],(x+self.current_object_for_properties_radius,y+self.current_object_for_properties_radius),self.current_object_for_properties_radius)
                # resize
                pygame.draw.circle(self.surface,self.color["current_object_for_properties_resize"],(x+width-self.current_object_for_properties_radius,y+height-self.current_object_for_properties_radius),self.current_object_for_properties_radius)
                # delete
                pygame.draw.circle(self.surface,self.color["current_object_for_properties_delete"],(x+self.current_object_for_properties_radius,y+height-self.current_object_for_properties_radius),self.current_object_for_properties_radius)
        pass
    def do_main_operations(self):
        try:
            pass
            self.buttons_control()
            self.onclick_events()
            self.draw_dividers()
            self.draw_layers()
            self.draw_canvas()
            self.draw_properties_box()
            self.draw_objects_list()
            self.draw_objects_plane()
            self.set_object_in_canvas_for_properties()
            self.draw_eraser()
            # print (self.mouse)
            if self.play_animation:
                self.current_time_strip+=1
                if self.current_time_strip>=self.number_of_time_strip_buttons:
                    self.current_time_strip=0
        except:
            pass
            print ("unexpected error... please report this")
        # print ()
        # print (self.active_tool)
        # print (self.thickness_meter_level)
        # if self.workspace_current_object!=None:
        #     print (len(self.objects[self.workspace_current_object]["points"]))
        #     print (self.objects[self.workspace_current_object]["points"])
        # print (len(self.temporary_shape_points))
    def set_mouse_and_clicks(self):
        self.mouse=pygame.mouse.get_pos()
        self.click=pygame.mouse.get_pressed()
        # print (self.click)
    def run(self):
        play=True
        self.set_custom_database()
        while play:
            surface.fill(self.color["background"])
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==KEYDOWN:
                    if event.key==K_TAB:
                        play=False
                    if event.key==K_RIGHT:
                        pass
                    if event.key==K_LEFT:
                        pass
            #--------------------------------------------------------------
            tid1=threading.Thread(target=self.do_main_operations,args=())
            tid2=threading.Thread(target=self.set_mouse_and_clicks,args=())
            tid1.start()
            tid2.start()
            tid1.join()
            tid2.join()
            # ------------------------
            # print (self.animation.time_strips[self.current_time_strip].layers)
            # print (self.current_layer)
            #--------------------------------------------------------------
            pygame.display.update()
            ft.tick(fps)




if __name__=="__main__":
    warning_messages=[
        "\n\n\nmissing feautres: \n\n1.draw in layers boxes also\n\n2.export as image\n\n3.deleting layer\n\n4.drawing rectangle\n\n5.drawing circle\n\n\nI'm still working on this version\n\n\n\n"
    ]
    for message in warning_messages:
        warnings.warn(message)
    app(surface).run()
    pass













# #----------------
