import cv2
import time
import numpy as np
from kivymd.uix.dialog import  MDDialog
#IMPORT DIALOG FROM KIVYMD

from kivymd.uix.button import MDFlatButton,MDRaisedButton
#IMPORT BUTTON FROM KIVYMD
import datetime #PYTHON PURE FUNCTION
#IMPORT APP TO INHERIT THE MAIN FUNCTION WITH App.get_running_app().function_name() or use variable from the main function like App.get_running_app().variable_name
from kivy.app import App
#INITIALIZE MD APP
from PIL import Image
from kivymd.app import MDApp
#IMPORT THE KIVY.APP TO INITIALIZE OR MAKING APP
from kivymd.uix.snackbar import  Snackbar
#IMPORT LAYOUT TO ASSEMBLY THE CAMERA ,LABEL,IMAGE,BUTTON,ELSE PERFECTLY
from kivy.graphics.texture import Texture
#FOR CANVAS THAT MIRRORING CAMERA
from kivymd.uix.screen import MDScreen#IMPORT SCREEN TO BE PUT ON THE SCREEN
import json #IMPORT LIBRARIES TO READ AND WRITE JSON
from kivymd.uix.list import OneLineAvatarListItem,ImageLeftWidget
#IMPORTING CAMERA
from kivy.lang import Builder
#IMPORTING BUILDER TO INITIALIZE KV LANGUAGE

from kivy.utils import platform
#USE UTILS TO CHECK WHETHER IT IS ANDROID OR OTHERS
from kivy.core.window import Window
#SIZING WINDOW
from kivy.uix.screenmanager import SlideTransition
#MAKING TRANSITION
from kivy.clock import Clock
if platform == 'macosx':

    Window.size = (450, 750)
    #IF YOUR DEVICE IS MACOS IT WILL BE RESIZED INTO X : 450 AND Y : 750
else:
    #OTHERS WILL BE PASSED
    pass


Builder.load_file("main.kv")
#LOAD THE DESIGN LANGUAGE FILE
from kivy_garden.xcamera import XCamera
from kivymd.theming import  ThemeManager
#MAKING CUSTOM BUTTON



def get_filename():
    import time

    if platform == 'android':
        return f'{App.get_running_app().user_data_dir}/{time.strftime("%y%m%d-%H%M%S")}.png'

    if platform == 'macosx':
        return f'{time.strftime("%y%m%d-%H%M%S")}.png'






#MAKING CUSTOM CAMERA
#CHANGED TO XCAMERA


class AndroidCamera(XCamera):

    with open ('data/date.json') as f:
        data =  json.load (f)

    #LOAD THE MODEL
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_righteye_2splits.xml')

    camera_resolution = (640, 480)
    #CAMERA RESOLUTION

    #SETTING UP SOME VITAL VARIABLES
    prev,b,g,r,a,m,B,G,R,list_data = 0,0,0,0,0,0,0,0,0,{}






    def _camera_loaded(self, *largs):
        #MIRRORING THE CAMERA TO TEXTURE

        self.texture = Texture.create(size=np.flip(self.camera_resolution), colorfmt='rgb')
        #READ AS RGB
        self.texture_size = list(self.texture.size)

        Clock.schedule_interval(lambda df:self.canvas.ask_update(),0.1)

        #SAVE TEXTURE_SIZE AS LIST

    def on_tex(self, *l):
        #EXECUTING BELOW METHODS WHEN THE CAMERA IS USED


        if self._camera._buffer is None:
            return None

        frame = self.frame_from_buf()
        #MAKING FRAME FROM BUFFER
        self.frame_to_screen(frame)
        #PUT FRAME TO SCREEN
        super(AndroidCamera, self).on_tex(*l)


    def frame_from_buf(self):
        #MAKE A FRAME FROM BUFFER
        w, h = self.resolution
        #INITIALIZE WIDTH AND HEIGHT OF THE CAMERA
        frame = np.frombuffer(self._camera._buffer.tostring(), 'uint8').reshape((h + h // 2, w))


        frame_bgr = cv2.cvtColor(frame, 93)

        return np.rot90(frame_bgr, 3)
        #ROTATE THE FRAME 90 DEGREES


    def frame_to_screen(self, frame):
        #MAKE A FRAME TO SCREEN

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #MAKING FRAME TO RGB
        if self.index == 1:
            #IF ON SELFIE ROTATE 180 DEGREES
            frame_rgb = cv2.rotate(frame_rgb,cv2.ROTATE_180)
        #DETECTING THE EYES

        self.face_det(frame_rgb)

        flipped = np.flip(frame_rgb, 0)
        buf = flipped.tostring()
        #CHANGE TO STRING
        self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')


    def face_det(self, frame):
        #DETECTING FACE

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)






        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)






        if len(faces) != 0:

            for (x, y, w, h) in faces:

                # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                roi_gray = gray[int(y + 0.1 * h):int(y + 0.55 * h), x:x + w]
                roi_color = frame[int(y + 0.1 * h):int(y + 0.55 * h), x:x + w]

                eyes = self.eye_cascade.detectMultiScale(roi_gray)
                for (ex, ey, ew, eh) in eyes:
                    #DETECTING EYES
                    # cv2.line(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                    height, width = roi_color.shape[:2]


                    if round(ex + 0.5 * ew) < height:

                        self.r,self.g, self.b =  roi_color[int(ex + 0.5*ew),int(ey + 0.7*eh)]
                        #MAKING IT TO BE INTEGGER
                        self.r,self.g,self.b = int(self.r),int(self.g),int(self.b)



                if w in range(300, 350):
                    cv2.rectangle(frame, (0, 0), (250, 60), (255, 255, 255), -1)
                    #EXECUTED WHEN A IS 1
                    if self.a == 1:

                        if time.time() - self.prev > 1:




                            FORMAT = '%Y-%m-%d %H:%M:%S '

                            isi = {str(datetime.datetime.now().strftime(FORMAT)):" B:%d G:%d R:%d" % (self.b, self.g, self.r)}

                            self.list_data.update(isi)

                            self.prev = time.time()
                            self.B += self.b
                            self.G += self.g
                            self.R += self.r

                            self.m += 1


                        X = "B=" + str(self.b) + " " + "G=" + str(self.g) + " " + "R=" + str(self.r)
                        cv2.putText(frame, X, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)


                    cv2.putText(frame, "Position Correct", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                if w > 350:

                    X = "Move backward"
                    cv2.rectangle(frame, (0, 0), (250, 60), (255, 255, 255), -1)
                    cv2.putText(frame, X, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                if w < 300:

                    X = "Move forward"
                    cv2.rectangle(frame, (0, 0), (250, 60), (255, 255, 255), -1)
                    cv2.putText(frame, X, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            if self.m == 2:
                #EXECUTED WHEN THE CAMERA ALREADY DETECT IT FOR 5 TIMES
                B_mean,G_mean,R_mean,nama,im = self.B/2,self.G/2,self.R/2,get_filename(),Image.new("RGB", (255, 100))

                data = [(round(R_mean),round(G_mean), round(B_mean)) for y in range(im.size[1]) for x in range(im.size[0])]
                im.putdata(data)

                im.save(nama)
                file = {"lokasi":nama}
                #SAVED TO UR SDCARD
                with open ('data/date.json','w') as f:
                    self.list_data.update(file)

                    self.data[f"B_avg:{B_mean}  G_avg: {G_mean} R_avg: {R_mean} "] = self.list_data
                    json.dump(self.data,f)

                    key = list(self.list_data.keys())
                    data = f"{self.list_data[key[0]]}\n{self.list_data[key[1]]}\n{self.list_data[key[2]]}\n{self.list_data[key[3]]}\n{self.list_data[key[4]]}\nB_avg: {B_mean} G_avg: {G_mean} R_avg: {R_mean}"

                    App.get_running_app().show_snackbar(data)








                self.m,self.B,self.R,self.G,self.a,self.list_data = 0,0,0,0,0,{}


                print(self.data)
                #RESET ALL THE VARIABLE VALUE


class MyLayout(MDScreen):
    #INITIALIZE THE MAINSCREEN/PARENT FOR THE CAMERA

    pass



class MyApp(MDApp):
    def __init__(self,**kwargs):

        super().__init__(**kwargs)
        self.theme_cls = ThemeManager()
        #INHERIT BASIC FUNCTION ON KIVYMD
        self.theme_cls.primary_palette = 'Orange'
        #MAKING THE THEME PRIMARY PALETTE TO BE ORANGE

        self.theme_cls.primary_style = 'Light'
        #CHANGE THE THEME TO LIGHT


    def build(self):

        #APP SETUP
        self.layout = MyLayout()
        #APP VALUE TO CHANGE TO SELFIE OR FRONT
        self.value = 0

        return self.layout
        #RETURNING THE LAYOUT
    def go_back(self):
        #GO BACK FROM OTHER SCREEN TO MAINSCREEN
        self.layout.ids.screen_manager.transition  = SlideTransition(direction="right")
        self.change_screen("mainscreen")
        self.layout.ids.screen_manager.transition = SlideTransition(direction="left")
    def show_dialog5(self, *args, text):
        #CHANGE DICT_KEYS TO LIST
        a = list(self.layout.ids.camera.data[text].keys())
        #SHOWING ALL THE LOGS TO THE DIALOGS
        self.dialog = MDDialog(title='RESULTS', text=f'FIRST: {self.layout.ids.camera.data[text][a[0]]}\n'
                                                     f'SECOND: {self.layout.ids.camera.data[text][a[1]]}\n'
                                                     f'THIRD: {self.layout.ids.camera.data[text][a[2]]}\n'
                                                     f'FOURTH: {self.layout.ids.camera.data[text][a[3]]}\n'
                                                     f'FIFTH: {self.layout.ids.camera.data[text][a[4]]}\n'

                               ,

                               size_hint=(0.8, 1),
                               buttons=[MDFlatButton(text='Close', on_release=self.close_dialog),
                                        MDRaisedButton(text='Delete', on_release=lambda x, item=text: self.delete(item))
                                        ])

        self.dialog.open()
        #OPEN DIALOG

    def close_dialog(self, *args):
        #CLOSE DIALOGS
        self.dialog.dismiss()

    def delete(self, *name):
        #DELETE THE TEST THAT HAD BEEN CHOSEN

        name = name[0]
        self.close_dialog()
        print(name)
        from kivymd.toast import toast
        toast('Delete Success')
        del self.layout.ids.camera.data[name]
        with open('data/date.json', 'w') as f:

            json.dump(self.layout.ids.camera.data, f)
        self.visualize_json()

    def reset(self,*args):
        self.layout.ids.label.text = ''
    def change_screen(self,text):
        #CHANGE_SCREEN TO THE SPECIFIC SCREEN THAT CAN BE WRITTEN self.change_screen("yourscreenname"),or in kv language app.change_screen("yourscreenname")
        self.layout.ids.screen_manager.current = text
    def go_friend(self,*args):

        #it will be executed when u want to see the logs
        self.change_screen("log_list")
        if list(self.layout.ids.camera.data.keys()) == []:
            snackbar = Snackbar(text="You Haven't Test Anything Yet", duration=0.8)
            snackbar.show()
        if list(self.layout.ids.camera.data.keys()) != []:

            self.layout.ids.container.clear_widgets()
            for i in self.layout.ids.camera.data.keys():

                image = ImageLeftWidget(source=self.layout.ids.camera.data[i]["lokasi"])

                isi = OneLineAvatarListItem(text=i, on_press=lambda x, item=i: self.show_dialog5(text=i))
                isi.add_widget(image)
                self.layout.ids.container.add_widget(isi)


    def visualize_json(self,*args):


        #refresh the widget after deleting some items
        self.layout.ids.container.clear_widgets()
        if list(self.layout.ids.camera.data.keys()) != []:
            for i in self.layout.ids.camera.data.keys():
                image = ImageLeftWidget(source=self.layout.ids.camera.data[i]["lokasi"])
                isi = OneLineAvatarListItem(text=i, on_press=lambda x, item=i: self.show_dialog5(text=i))
                isi.add_widget(image)
                self.layout.ids.container.add_widget(isi)
                #put the widget back to the screen if there are some value in the dict
    def swap(self):

        self.value+=1
        #IF VALUE MODULO  BY 2 IS NOT 0 THEN IT CHANGED TO SELFIE
        if self.value % 2 != 0 :

            self.layout.ids.camera.index = 1
        #IF VALUE MODULO BY 2 IS 0 IT CHANGED TO FRONT CAMERA
        if self.value % 2 == 0 :
            self.layout.ids.camera.index = 0
    def activate(self):
        #TRIGGERING APP TO SCAN IRIS
        self.layout.ids.camera.a = 1

    def show_snackbar(self,text):

        self.layout.ids.label.text = text








if __name__ == '__main__':
    #PREVENT APP FROM OTHER DISRUPTION
    MyApp().run()





    # Detect the faces




# Release the VideoCapture object




