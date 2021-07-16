# import everything from tkinter module
from datetime import datetime
from tkinter import Button, Tk, Label

import cv2
import pandas
from PIL import ImageTk, Image


class MotionDetector():

    def __init__(self):
        self.static_back = None
        self.motion_list = [None, None]
        self.time = []
        self.df = pandas.DataFrame(columns=["Start", "End"])
        self.video = cv2.VideoCapture(0)

    def start(self):

        while True:
            check, frame = self.video.read()
            motion = 0
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            if self.static_back is None:
                self.static_back = gray
                continue
            diff_frame = cv2.absdiff(self.static_back, gray)

            thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
            thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

            cnts, _ = cv2.findContours(thresh_frame.copy(),
                                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in cnts:
                if cv2.contourArea(contour) < 10000:
                    continue
                motion = 1

                (x, y, w, h) = cv2.boundingRect(contour)
                # making green rectangle around the moving object
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            self.motion_list.append(motion)
            self.motion_list = self.motion_list[-2:]
            if self.motion_list[-1] == 1 and self.motion_list[-2] == 0:
                self.time.append(datetime.now())
            if self.motion_list[-1] == 0 and self.motion_list[-2] == 1:
                self.time.append(datetime.now())

            cv2.imshow("Gray Frame", gray)
            cv2.imshow("Difference Frame", diff_frame)

            cv2.imshow("Threshold Frame", thresh_frame)
            cv2.imshow("Color Frame", frame)

            key = cv2.waitKey(1)
            # if q entered whole process will stop
            if key == ord('q'):
                # if something is moving then it append the end time of movement
                if motion == 1:
                    self.time.append(datetime.now())
                break

        cv2.destroyAllWindows()

    def write_file(self):
        for i in range(0, len(self.time), 2):
            self.df = self.df.append(
                {"Start": self.time[i], "End": self.time[i + 1]},
                ignore_index=True)
        self.df.to_csv("Time_of_movements.csv")
        self.video.release()
        # cv2.destroyAllWindows()


md = MotionDetector()

# create a tkinter window
root = Tk()

root.title("MOTION DETECTOR")

load = Image.open('download1.jpg')
render = ImageTk.PhotoImage(load)
img = Label(root, image=render)
img.place(x=0, y=0)

# Open window having dimension 100x100
root.geometry('750x536')

#Labels
##text = Label(root, text="I AM WATCHING YOU......")
#text.place(x=70,y=90)

#label = Label(root, text="Tkinter", fg="White")
#label = Label(root, text="Helvetica", font=("Helvetica", 30))


# Create a Button
btn = Button(root, text='START', bd='12',
             command=md.start, bg='silver')

btn1 = Button(root, text='CREATE FILE', bd='12',
              command=md.write_file, bg='silver')

# Set the position of button on the top of window.
# pack(side = 'top')
btn.place(x=150, y=300)
btn1.place(x=300, y=300)

root.mainloop()
