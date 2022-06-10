# DingDone: Autonomous Flight Drone for Searching Survivor with Monocular Depth Estimation and Obeject Detection  

<img src="https://user-images.githubusercontent.com/87409442/167561776-5cdf8912-b22d-45f5-82a7-e9fd01815018.png" width="400">

Requirments
--
Avoidance, Localization  
- This code is tested with Keras 2.2.4, Tensorflow 1.13, CUDA 10.0, on a machine with an NVIDIA Titan V and 16GB+ RAM running on Windows 10 or Ubuntu 16.  
- Other packages needed keras pillow matplotlib scikit-learn scikit-image opencv-python pydot and GraphViz for the model graph visualization and PyGLM PySide2 pyopengl for the GUI demo.  
- Minimum hardware tested on for inference NVIDIA GeForce 940MX (laptop) / NVIDIA GeForce GTX 950 (desktop).  
- Training takes about 24 hours on a single NVIDIA TITAN RTX with batch size 8.  


Project Overview
--
  1. avoiding obstacle with monocular depth estimation
  2. detecting survivor with object detecting
  3. estimating distance and direction of survivor from drone
   
Run  
--  
   1. Clone this repository
```
$ git clone https://github.com/Ewha-BanBanBank/DingDone_final.git
```  
   2. Connect drone to your computer
   3. Run Demo - avoiding obstacle
```
$ cd Avoidance
$ python3 DingDone_path.py
```
   4. Run Demo - detecting survivor, estimating position of survivor and showing those information to application
```
$ cd ../Localization
$ python3 localization.py
```
References
--
1. Monocular Depth Estimation
: https://github.com/ialhashim/DenseDepth
2. Object Detection
: https://github.com/ultralytics/yolov5  

Poster
--
<img src = "https://user-images.githubusercontent.com/70934572/173010737-ad33ca61-117a-4674-97d3-365f0fb8b561.jpg" width ="800"/>


## Video

[![뱅뱅뱅크_시연영상](https://img.youtube.com/vi/LXHhpUH9N5w/0.jpg)](https://youtu.be/LXHhpUH9N5w?t=0s)
