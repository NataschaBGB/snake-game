# Overview
Description of the project, its purpose, and what it does.


# Installation
## 1) Make sure you have Python installed on your system
Install Python 3.11 or lower from the official Python website: https://www.python.org/downloads/
Python 3.12 and above may have compatibility issues with mediapipe, which is a key dependency for this project

2) Create project folder where you want to store the code and files for this project
Name it "snake" or any name you prefer
Make sure to not create the project folder in OneDrive or any cloud-synced folder, as this can cause issues with file access and performance

3) Open project folder in VS Code

4) Create new file in the project folder
Name it "main.py" or "snake.py"

5) Create a virtual environment
This is optional but recommended to keep the project dependencies isolated from the global Python installation
In the VS Code terminal, run the following command:
```powershell
    python -m venv venv
```
- It may take a few seconds to create the virtual environment, so be patient

6) Activate the virtual environment
If VS Code prompts you to select a Python interpreter, choose the one from the virtual environment you just created (it should be located in the "venv" folder)
If VS Code does not prompt you, you can manually activate the virtual environment using the following command in the terminal
```powershell
    .\.venv\Scripts\Activate.ps1
```
- You may need to restart the terminal after activating the virtual environment
- Make sure it says (.venv) at the beginning of your terminal prompt, indicating that the virtual environment is active

7) Install the required packages
In VS Code terminal, run the following command:
```powershell
    pip install wheel mediapipe==0.10.14 opencv-python imutils numpy
```
Verify the installation of mediapipe:
- This is to ensure that mediapipe was installed correctly and is accessible in your Python environment, because mediapipe is an old package and may have compatibility issues with newer versions of Python
In the VS Code terminal, run the following command:
```powershell
    python -c "import mediapipe as mp; print(mp.solutions.hands)"
```
- If the above command runs without errors and prints the mediapipe hands solution, the installation was successful

8) Copy the code from the main Python file
Paste the copied code into the file you created in your project folder
- Make sure to save the file after pasting the code


# The Game

## Starting the Game
To start the game, run the following command in the terminal:
```powershell
    python main.py
```
- If you named your main file differently, replace "main.py" with the name of your file
This will launch the application and access your webcam to start the snake game

## Game Controls
### Moving the snake:
- 
