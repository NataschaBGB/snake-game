# 🐍 Snake Game

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-Free-lightgrey)

---

## 📖 Overview
This project is an interactive **Snake game controlled by computer vision 🤖**, where you use your webcam and hand gestures to control the game in real-time.

It combines:
- 🎥 Webcam input
- ✋ Hand tracking (MediaPipe)
- 🐍 Classic Snake gameplay
- 🧠 Real-time gesture recognition
- 👁️ Computer vision with OpenCV

---

## ⚙️ Installation

### 🐍 1) Install Python
Download Python 3.11 here:
👉 https://www.python.org/downloads/

⚠️ Important:
- Use **Python 3.11 or lower**
- Python 3.12+ may break MediaPipe compatibility


### 📁 2) Create project folder
Create a folder for the project and name it "snake-game" or any name you prefer

❌ Make sure to not create the project folder in OneDrive or any cloud-synced folder, as this can cause issues with file access and performance


### 💻 3) Open in VS Code
- Right click folder → “Open with Code”
- OR open VS Code → File → Open Folder → Select your project folder


### 📄 4) Create main file
Create a Python file named `main.py` (or `snake.py` if you prefer) inside your project folder


### 🌐 5) Create virtual environment
This is optional but recommended to keep the project dependencies isolated from the global Python installation

In the VS Code terminal, run the following command:
```powershell id="venv_create"
python -m venv venv
```
⚠️ It may take a few seconds to create the virtual environment, so be patient


### 🔌 6) Activate virtual environment
If VS Code prompts you to select a Python interpreter, choose the one from the virtual environment you just created (it should be located in the "venv" folder)

If VS Code does not prompt you, you can manually activate the virtual environment using the following command in the terminal:
```powershell
    .\.venv\Scripts\Activate.ps1
```
⚠️ You may need to restart the terminal after activating the virtual environment

⚠️ Make sure it says (.venv) at the beginning of your terminal prompt, indicating that the virtual environment is active


### 📦 7) Install the required packages
In VS Code terminal, run the following command:
```powershell
    pip install wheel mediapipe==0.10.14 opencv-python imutils numpy
```
🧪 Verify MediaPipe installation
- This is to ensure that mediapipe was installed correctly and is accessible in your Python environment, because mediapipe is an old package and may have compatibility issues with newer versions of Python

In the VS Code terminal, run the following command:
```powershell
    python -c "import mediapipe as mp; print(mp.solutions.hands)"
```
✔️ If no errors appear → installation is successful


### 8) Copy the code from the snake.py file
Paste the copied code into the file you created in your project folder

⚠️ Make sure to save the file after pasting the code

---

## 🚀 Run the Game
To start the game, run the following command in the terminal:
```powershell
    python main.py
```

If you named your main file differently, replace "main.py" with the name of your file

This will launch the application and access your webcam to start the snake game

---

## 🎥 How It Works

![hand_landmarks](image.png)

The system works in 4 steps:

🎥 Webcam captures your video feed
✋ MediaPipe detects hand landmarks in real-time
🧠 Gesture position is mapped to game controls
🐍 Snake moves instantly based on your hand motion

---

## 🛠️ Tech Stack
🐍 Python
👁️ OpenCV
✋ MediaPipe
📊 NumPy
⚙️ Imutils

---

## ⚠️ Troubleshooting
🧠 MediaPipe not working?
- 🐍 Ensure Python is 3.11 or lower

- Reinstall dependencies:
```powershell
    pip uninstall mediapipe
    pip install mediapipe==0.10.14
```

👁️ Webcam not opening?
- 🔐 Check camera permissions
- 💻 Close apps using webcam (Zoom, Teams, etc.)

---

## 📄 License

Free to use for educational and personal projects 🎓
