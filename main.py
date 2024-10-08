from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
import paho.mqtt.client as mqtt
import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import pathlib
import datetime
import json

############################
### READ JSON AND CONFIG ###
############################

f = open('setting.json')
 
# returns JSON object as
# a dictionary
setting_value = json.load(f)

##############
### CONFIG ###
##############

# CONFIG MQTT
MQTT_SERVER = "mqtt.ohstem.vn"
MQTT_PORT = 1883
MQTT_USERNAME = setting_value["mqttUsername"]
MQTT_PASSWORD = setting_value["mqttPassword"]
MQTT_TOPIC_PUB = MQTT_USERNAME + "/feeds/" + setting_value["defaultPublishFeed"]
# MQTT_TOPIC_PUB2 = MQTT_USERNAME + "/feeds/V2"
MQTT_TOPIC_SUB = MQTT_USERNAME + "/feeds/V3"

# CONFIG DEFAULT IMAGE WHEN THE CAMERA IS NOT OPEN
DEFAULT_IMG = Image.open("assets/bo.bmp")

CAM_IP = setting_value["camIP"]
CONFIDENCE_SCORE_CONFIRM = np.float64(int(setting_value["confidenScoreConfirm"]))
TIMES_CONFIRM = int(setting_value["timesConfirm"])

def change_setting():
    global MQTT_USERNAME, MQTT_PASSWORD, CONFIDENCE_SCORE_CONFIRM, TIMES_CONFIRM, CAM_IP
    MQTT_USERNAME = setting_value["mqttUsername"]
    MQTT_user_status["text"] = "MQTT user: " + setting_value["mqttUsername"]
    MQTT_PASSWORD = setting_value["mqttPassword"]
    CAM_IP = setting_value["camIP"]
    cam_IP_status["text"] = "Camera IP: " + setting_value["camIP"]
    CONFIDENCE_SCORE_CONFIRM = np.float64(int(setting_value["confidenScoreConfirm"]))
    TIMES_CONFIRM = int(setting_value["timesConfirm"])

root = tk.Tk()
root.title("Robot app")
root.resizable(False, False)
root.geometry("600x700+200+50")
container = tk.Frame(root)
container.pack(padx=10, pady=10)

# Global variable
get_image_running = 0
send_MQTT_running = 0
cam = 0
ai_result = 0
count_ai = 0
count_ai_confirm = 0
take_photo_flag = 0

arr_model = []
arr_model_name = []
arr_class_names = []
num_of_model_loaded = 0
model = 0
class_names = 0    

######################
### MODEL FUNCTION ###
######################

# Get list of models
model_list = []
get_model = pathlib.Path("models")
for item in get_model.iterdir():
    model_list.append(str(item)[7:])

# Auto load model bienbao when program start
def auto_load_model():
    global model, class_names, num_of_model_loaded
    autoLoadModel = setting_value["autoLoadModel"]
    # Load the model
    my_load_model(autoLoadModel)

# Function load model
def my_load_model(model_choose):
    global model, class_names, num_of_model_loaded
    if get_image_running == 1:
        print("Stop camera before load model")
        message["text"] = "Stop camera before load model"
        return
    model_name = str(model_choose)
    for index, loaded_model in enumerate(arr_model_name):
        if loaded_model == model_name:
            model = arr_model[index]
            class_names = arr_class_names[index]
            num_of_model_loaded += 1
            print("Load model " + model_name + " sucessfully")
            message["text"] = "Load model " + model_name + " sucessfully"
            model_status["text"] = "Model: " + model_name
            return

    # Keras path to load
    keras_path = "models/" + model_name + "/keras_Model.h5"
    # Class name path to load
    class_names_path = "models/" + model_name + "/labels.txt"
    # Check path exist
    keras_path_check = pathlib.Path(keras_path)
    class_names_path_check = pathlib.Path(class_names_path)
    if keras_path_check.exists() and class_names_path_check.exists():
        pass
    else:
        print("The path does not exist! Check your path!!\nLoad model fail")
        message["text"] = "The path does not exist! Check your path!!\nLoad model fail"
        return
    
    # Reload the model
    model = load_model(keras_path, compile=False)
    # Reload the labels
    class_names = open(class_names_path, "r").readlines()

    arr_model.append(model)
    arr_model_name.append(model_name)
    arr_class_names.append(class_names)
    num_of_model_loaded += 1
    print("Load model " + model_name + " sucessfully")
    message["text"] = "Load model " + model_name + " sucessfully"
    model_status["text"] = "Model: " + model_name

###################################
### CAMERA AND PREDICT FUNCTION ###
###################################

# Update frame and prediction
def show_img():
    global cam, ai_result, count_ai, count_ai_confirm, take_photo_flag
    ret, frame = cam.read()  # type: ignore
    if take_photo_flag == 1:
        now = datetime.datetime.now().strftime("%Hh%Mm%Ss%B-%d-%Y")
        cv2.imwrite("photo/" + now + ".png", frame)
        message["text"] = "Your photo is saved in photo folder"
        take_photo_flag = 0
    cv2_img = DEFAULT_IMG
    if get_image_running:
        cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        cv2_img = Image.fromarray(cv2_img)
        width, height = cv2_img.size
        count_ai += 1

        if count_ai == 15:
            image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)

            # Make the image a numpy array and reshape it to the models input shape.
            image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

            # Normalize the image array
            image = (image / 127.5) - 1

            # Predicts the model
            prediction = model.predict(image)  # type: ignore
            index = np.argmax(prediction)
            class_name = class_names[index]  # type: ignore
            confidence_score = prediction[0][index]

            # Print prediction and confidence score
            print("Class:", class_name[2:], end="")
            print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
            ai_message["text"] = "Class:" + class_name[2:] + " Value:" + str(np.round(confidence_score * 100))[:-2] + "%"
            if send_MQTT_running:
                print("confirm running ...")
                if confidence_score * 100 > CONFIDENCE_SCORE_CONFIRM and class_name[2:] == ai_result:
                    count_ai_confirm += 1
                    if count_ai_confirm >= TIMES_CONFIRM:
                        print("#$%^&*()1234 GUI LEN MQTT FEED: " + MQTT_TOPIC_PUB + "#$%^&*()1234")
                        mqttClient.publish(MQTT_TOPIC_PUB, ai_result, 0, True)
                        count_ai_confirm = 0
                else:
                    count_ai_confirm = 0

            ai_result = class_name[2:]
            count_ai = 0

    cv2_img = cv2_img.resize((430, 320))
    cv2_img = ImageTk.PhotoImage(cv2_img)
    label_cv.config(image=cv2_img)
    label_cv.image = cv2_img  # type: ignore #VERY IMPORTANT

    if get_image_running:
        root.after(5, show_img)


# Show camera
def start_cam():
    global get_image_running, cam, num_of_model_loaded
    if get_image_running == 1:
        return
    if num_of_model_loaded == 0:
        print("Load model before start camera")
        message["text"] = "Load model before start camera"
        return
    get_image_running = 1
    ##############
    ### CAM IP ###
    ##############
    if CAM_IP == "0":
        cam = cv2.VideoCapture(0)
    else:
        # http://192.168.137.101:4747/video
        cam = cv2.VideoCapture("http://" + CAM_IP + ":81/stream")
    if not cam.isOpened():
        print("Fail to start camera. Check your camera IP")
        message["text"] = "Fail to start camera. Check your camera IP"
        return
    print("Camera is running")
    message["text"] = "Camera is running"
    camera_status["text"] = "Camera: ON"
    show_img()


# Stop camera
def stop_cam():
    global get_image_running, cam, send_MQTT_running
    if get_image_running == 0:
        return
    get_image_running = 0
    cam.release()  # type: ignore
    cv2.destroyAllWindows()
    print("Stop camera")
    message["text"] = "Stop camera"
    camera_status["text"] = "Camera: OFF"

    if send_MQTT_running == 1:
        send_MQTT_running = 0
        print("Stop sending to MQTT")
        message["text"] = "Stop camera\nStop sending to MQTT"
        MQTT_status["text"] = "MQTT: OFF"


def take_photo():
    global take_photo_flag
    if get_image_running == 0:
        print("Start camera to take photo")
        message["text"] = "Start camera to take photo"
        return
    take_photo_flag = 1

#####################
### MQTT FUNCTION ###
#####################

def mqtt_connected(client, userdata, flags, rc):
    print("Connected succesfully!!")
    client.subscribe(MQTT_TOPIC_SUB)


def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")


mqttClient = mqtt.Client()
mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqttClient.connect(MQTT_SERVER, int(MQTT_PORT), 60)

# Register mqtt events
mqttClient.on_connect = mqtt_connected
mqttClient.on_subscribe = mqtt_subscribed


# mqttClient.loop_start()

# while True:
#     # time.sleep(5)
#     ai_result = ai_detector()
#     if not ai_result:
#         break
#     print(ai_result)
#     mqttClient.publish(MQTT_TOPIC_PUB, ai_result, 0, True)

def send_to_MQTT(feed):
    global send_MQTT_running, MQTT_TOPIC_PUB
    if get_image_running == 0:
        print("Start camera before send")
        message["text"] = "Start camera before send"
        return
    MQTT_TOPIC_PUB = MQTT_USERNAME + "/feeds/" + feed
    feed_status["text"] = "Feed: " + feed
    send_MQTT_running = 1
    print("Start sending to MQTT (Feed " + feed + ")")
    message["text"] = "Start sending to MQTT (Feed " + feed + ")"
    MQTT_status["text"] = "MQTT: ON"
    # MQTT_loop()


# def MQTT_loop():
#     global ai_result, send_MQTT_running
#     mqttClient.publish(MQTT_TOPIC_PUB, ai_result, 0, True)
#     print("SEND TO MQTT")
#     if send_MQTT_running:
#         root.after(50, MQTT_loop)
#     else:
#         print("STOP SENDING TO MQTT")
#         message["text"] = "STOP SENDING TO MQTT"

def close_send_MQTT():
    global send_MQTT_running
    if send_MQTT_running == 0:
        return
    send_MQTT_running = 0
    print("Stop sending to MQTT")
    message["text"] = "Stop sending to MQTT"
    MQTT_status["text"] = "MQTT: OFF"

#####################
### Reset program ###
#####################

def reset_program():
    global get_image_running
    close_send_MQTT()
    stop_cam()
    change_setting()
    message["text"] = "Settings saved successfully"

#################
### tkinter #####
#################

def setting_popup():
    global setting_value

    f = open('setting.json')
    setting_value = json.load(f)

    setting_window = tk.Toplevel(root)
    setting_window.title("Setting")

    number_of_var = len(setting_value)
    variable_frame = [tk.Frame(setting_window) for i in range(number_of_var)]
    setting_key = list(setting_value.keys())
    var = [tk.StringVar() for i in range(number_of_var)]
    for i in range(number_of_var):
        variable_frame[i].grid(row=i, column=0, pady=5)
        variable_label = ttk.Label(variable_frame[i], text=setting_key[i], width=25)
        variable_label.pack(side="left", fill="both", padx=(15, 0))
        var[i].set(setting_value[setting_key[i]])
        variable_value = tk.Entry(variable_frame[i], textvariable=var[i], width=15)
        variable_value.pack(side="left", fill="both", padx=(0, 15))

    def change_setting():
        for i in range(number_of_var):
            setting_value[setting_key[i]] = var[i].get()

        # Modify json file
        with open("setting.json", "w") as outfile:
            json.dump(setting_value, outfile)

        reset_program()
        setting_window.destroy()

    button_save = ttk.Button(setting_window, text="Save", width=15, command=change_setting)
    button_save.grid(row=number_of_var, column=0, pady=10)
    
### Menu bar ###

# create a menubar
menubar = ttk.Menu(root)
root.config(menu=menubar)

# create the file_menu
file_menu = ttk.Menu(menubar, tearoff=False)

# add menu items to the File menu
file_menu.add_command(label='New', command=lambda: print("New"))
file_menu.add_command(label='Open', command=lambda: print("Open"))
file_menu.add_command(label='Close', command=lambda: print("Close"))
# file_menu.add_separator()

# # add a submenu
# sub_menu = ttk.Menu(file_menu, tearoff=False)
# sub_menu.add_command(label='Keyboard Shortcuts')
# sub_menu.add_command(label='Color Themes')

# # add the File menu to the menubar
# file_menu.add_cascade(label="Preferences", menu=sub_menu)

# add Exit menu item
file_menu.add_separator()
file_menu.add_command(label='Exit', command=root.destroy)

menubar.add_cascade(label="File", menu=file_menu, underline=0)
# create the Setting menu
setting_menu = ttk.Menu(menubar, tearoff=False)

setting_menu.add_command(label='Setting value', command=setting_popup)

# add the Setting menu to the menubar
menubar.add_cascade(label="Setting", menu=setting_menu, underline=0)

# create the Help menu
help_menu = ttk.Menu(menubar, tearoff=False)

help_menu.add_command(label='Tutorial', command=setting_popup)
# add the Help menu to the menubar
menubar.add_cascade(label="Help", menu=help_menu, underline=0)

### Main screen ###
main_screen = ttk.Frame(container)
main_screen.grid(row=0, column=0)

main_screen_label = ttk.Label(main_screen, text="Ohstem robot GUI", font=("Arial", 16))
main_screen_label.pack(side="top", pady=(0, 10))

button_frame = tk.Frame(main_screen)
button_frame.pack(side="top", pady=(0, 10))

# 320 240
cv2_img = DEFAULT_IMG.resize((430, 320))
cv2_img = ImageTk.PhotoImage(cv2_img)
label_cv = ttk.Label(main_screen, image=cv2_img)
label_cv.pack(side="top", pady=(0, 10))

# Show massage
message_frame = ttk.Labelframe(main_screen, text="Message", padding=5)
message_frame.pack(side="top", pady=(0, 10), fill="both")
message = ttk.Label(message_frame, text="", font=("Arial", 12))
message.pack()

# Show AI result
ai_result_frame = ttk.Labelframe(main_screen, text="AI result", padding=5)
ai_result_frame.pack(side="top", pady=(0, 10), fill="both")
ai_message = ttk.Label(ai_result_frame, text="", font=("Arial", 12))
ai_message.pack()

# chuphinh = ttk.Button(main_screen, text="Chup hinh")
# chuphinh.grid(row=0, column=0)

### Model button ###
# Choose model
button_model_frame = ttk.Labelframe(button_frame, text="Models", padding=5)
button_model_frame.grid(row=0, column=0, padx=(0, 10))

model_choose = tk.StringVar()
option_menu = ttk.OptionMenu(
    button_model_frame,
    model_choose,
    "Not selected",
    *model_list,
    bootstyle="secondary"  # type: ignore
)
option_menu.pack(side="top", fill="both", pady=(0, 10), ipady=2)

# Button to load model
button_select_model = ttk.Button(button_model_frame, text="Select Model", command=lambda: my_load_model(model_choose.get()))
button_select_model.pack(side="top", fill="both", ipady=2)
#####

### Camera button ###
button_cam_frame = ttk.Labelframe(button_frame, text="Camera", padding=5)
button_cam_frame.grid(row=0, column=1, padx=(0, 10))

button_start_cam = ttk.Button(
    button_cam_frame,
    text="Start camera",
    bootstyle="success",  # type: ignore
    command=start_cam
)
button_start_cam.pack(side="top", fill="both", pady=(0, 10), ipady=2)

button_stop_cam = ttk.Button(
    button_cam_frame,
    text="Stop camera",
    bootstyle="danger",  # type: ignore
    command=stop_cam
)
button_stop_cam.pack(side="top", fill="both", pady=(0, 10), ipady=2)

button_take_photo = ttk.Button(
    button_cam_frame,
    text="Take photo",
    bootstyle="warning",  # type: ignore
    command=take_photo
)
button_take_photo.pack(side="top", fill="both", ipady=2)

#####

### MQTT button ###
button_MQTT_frame = ttk.Labelframe(button_frame, text="MQTT", padding=5)
button_MQTT_frame.grid(row=0, column=2, padx=(0, 10))

feed_list = []
default_feed = setting_value["defaultPublishFeed"]
for i in range(20):
    feed_list.append("V" + str(i + 1))
feed_choose = tk.StringVar()
option_menu = ttk.OptionMenu(
    button_MQTT_frame,
    feed_choose,
    default_feed,
    *feed_list,
)
option_menu.pack(side="top", fill="both", pady=(0, 10), ipady=2)

button_send_to_MQTT = ttk.Button(button_MQTT_frame, text="Send to MQTT", command=lambda: send_to_MQTT(feed_choose.get()))
button_send_to_MQTT.pack(side="top", fill="both", pady=(0, 10), ipady=2)

button_close_send_MQTT = ttk.Button(
    button_MQTT_frame, 
    text="Close send", 
    bootstyle="danger",  # type: ignore
    command=close_send_MQTT
)
button_close_send_MQTT.pack(side="top", fill="both", ipady=2)
#####

### Status screen ###
status_screen = ttk.Labelframe(button_frame, text="Status", padding=5)
status_screen.grid(row=0, column=3)

model_status = ttk.Label(status_screen, text="Model: " + setting_value["autoLoadModel"], font=("Arial", 10))
model_status.pack(side="top", fill="both")

cam_IP_status = ttk.Label(status_screen, text="Camera IP: " + setting_value["camIP"], font=("Arial", 10))
cam_IP_status.pack(side="top", fill="both")

camera_status = ttk.Label(status_screen, text="Camera: OFF", font=("Arial", 10))
camera_status.pack(side="top", fill="both")

MQTT_user_status = ttk.Label(status_screen, text="MQTT user: " + setting_value["mqttUsername"], font=("Arial", 10))
MQTT_user_status.pack(side="top", fill="both")

feed_status = ttk.Label(status_screen, text="Feed: " + setting_value["defaultPublishFeed"], font=("Arial", 10))
feed_status.pack(side="top", fill="both")

MQTT_status = ttk.Label(status_screen, text="MQTT: OFF", font=("Arial", 10))
MQTT_status.pack(side="top", fill="both") 
#####

auto_load_model()

root.mainloop()
