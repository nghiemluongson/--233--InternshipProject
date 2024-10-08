# RoverESP32CAM Using GoogleTeachableMachine
* Author: KKS Group - Ho Chi Minh University of Technology
  - Trần Văn Kiên -- 2013552
  - Nghiêm Lương Sơn -- 2014373
  - Trương Mạnh Khôi -- 2013536
* Description:
  * This is an experimental project that integrates the robot rover of AITT company with the ESP32CAM device, supported by Google Teachable Machine. The project aims to leverage AI in constructing movement behaviors for the robot rover through ESP32 CAM.
  * You also have the option to purchase the same device from here:
    - [Robot Rover](https://ohstem.vn/product/robot-stem-rover/)
    - [ESP32 Cam](https://hshop.vn/products/kit-rf-thu-phat-wifi-ble-esp32-cam)
  * You can see a sample in our project here:
![Robot Rover](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/rover.jpg)
* Tutorial Settings:
  * First, you must clone this Project.
  * Before you should install some library (we use python 3.11) to run programs provided by Google Teachable Machine:
  ### `pip install keras`
  ### `pip install tensorflow`
  ### `pip install Pillow`
  ### `pip install numpy`
  ### `pip install opencv-python`
  * You should also install some library for our GUI:
  ### `pip install opencv-python`
  ### `pip install paho-mqtt`
  ### `pip install tkinter`
  ### `pip install ttkbootstrap`
  ### `pip install pathlib`
  ### `pip install DateTime`
* Ohstem Settings:
  ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Server1.png)
  * First, you open website [App Ohstem](https://app.ohstem.vn/), Click "Bảng điều khiển IoT" -> "Tạo Mới".
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Server2.png)
  * In new Ohstem server, you click and hold it move to the space. You will have a Feed. This Feed will receive informations from the Python software in the future.
  ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Server3.png)
   * After that, you will enter some information to "Bảng điều khiển" and "Username". You should use a unique name to avoid duplicates. You must remember it to enter in the Python Software in next time. if everything is ok, you can click button "play" in the top right corner and go back by click "<-" in the top left corner.
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Server4.png)
   * Second, you will upload json file to ohstem programming. You choose like this picture and click "Lập trình thiết bị" -> Yolo:bit -> "Lập trình".
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Server5.png)
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Block1.png)
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Block2.png)
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Block4.png)
   * You will upload by click like this picture, choose "import project" and choose file "RoverProject.json.json" in folder rover. Wait until this file import complete. In this time, you can set up your rover and connect with laptop. before click run, you should install [firmware](https://fw.ohstem.vn/) and necessary library.
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/Block3.png)
* Block Code:
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/BlockCode.png)
*  Tutorials:
    * First, You click run on Ohstem Programming. If it has problem, you should restart programming and Rover.
    * When Ohstem Programming is running. You can start the Python Software Programming. You has the UI like this:
    ![Ohstem App](https://github.com/kientr2002/TeachableMachineGoogleWithESP32CAM/blob/main/image/GUI.png)
    * You can click Setting, choose Setting Value, enter some information and click "start camera". if everything is ok and you want to send the information to Ohstem Server, click "Send to MQTT". You can give some testcase (using samples in AIModelPicture) and test in Ohstem server you created.
   * In rover, you must place in the map and click button A to start Rover. 
 
  
  
  
  
