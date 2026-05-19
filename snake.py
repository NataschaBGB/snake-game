# MARK: Imports

# OpenCV is used for camera access, drawing graphics,
# showing windows, and handling the game visuals
import cv2

# imutils helps simplify image resizing
import imutils

# NumPy is used for math calculations,
# especially distance calculations
import numpy as np

# MediaPipe is Google's hand tracking framework
# It uses AI/computer vision to detect hands and fingers
import mediapipe as mp

# Used for timers and gesture timing
import time


# MARK: Mediapipe Setup

# Create a shortcut to the MediaPipe hands module
# This module contains the hand tracking AI and utilities
mp_hands = mp.solutions.hands

# Initialize the hand tracking system
# min_detection_confidence:
#   How sure MediaPipe must be before detecting a hand
# min_tracking_confidence:
#   How stable the hand tracking should be between frames
#   This helps prevent jittery movement when the hand is detected
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Utility used for drawing the hand skeleton on screen
# This is optional and can be commented out if you don't want to see the hand skeleton
# mp_draw = mp.solutions.drawing_utils


# MARK: Game Variables

# Current player score
score = 0

# Score needed to win the game
max_score = 20

# List storing all snake body positions
# Each position is a tuple (x, y) representing a point on the screen
# Example: snake = [(100, 150), (105, 155), (110, 160)] means the snake has three segments at those coordinates.
#   These points change when the player moves their hand, and the snake follows the movement. When the player eats an apple, the snake grows longer by allowing more points to be stored in this list before old points are removed.
# The snake grows by adding new points to this list, and old points are removed when the snake exceeds its length limit.
snake = []

# Maximum allowed snake length
# This increases when the player eats apples
# The snake starts with a length of 0, meaning it will only show the head. Each time the player eats an apple, snake_limit increases by 1, allowing one more point to be stored in the snake list before old points are removed.
# This is how the snake grows longer as you eat apples.
snake_limit = 0

# Determines if the player has won
game_won = False

# Determines if the game is over (player loses)
game_over = False

# Determines if the game is paused
paused = False

# Apple position on the screen
# Starts as None because no apple exists yet
apple_x = None
apple_y = None

# Previous hand position
# Used to track movement direction and distance
prev_c = None



# MARK: Smoothing Variables

# These variables are used to smooth hand movement
# Without smoothing the snake would shake a lot

smooth_x = None
smooth_y = None

# Smoothing strength
#
# Lower number:
#   smoother movement but slower response
# Higher number:
#   faster response but more shaking
alpha = 0.5



# MARK: Fist Gesture Variables

# Stores the time when a fist gesture starts
# If a fist is detected, we start a timer. If the fist is held for a certain duration, we trigger a pause or restart action.
# This variable helps us track how long the fist has been held.
fist_start_time = None

# Number of seconds the fist must be held before pause activates
fist_hold_duration = 1.0

# Prevents the pause gesture from triggering repeatedly
# When a fist is detected and the pause action is triggered, we set this variable to True.
# It will prevent the game from toggling pause on and off rapidly while the fist is still held.
# Once the fist is released, we reset this variable to False, allowing the gesture to be detected again.
gesture_triggered = False

# Determines if the start text should be displayed
# When resuming from pause, we want to show a "START" message for a brief moment to indicate the game has resumed.
# This variable helps us control when to show that message.
show_start_text = False
# Stores the time when the start text is shown
# We want to show the "START" message for a limited time (e.g., 1 second) after resuming from pause.
# This variable helps us track when the message was shown so we can hide it after the duration has passed.
start_text_time = 0

# Number of seconds to hold fist to trigger a restart after game over
restart_hold_duration = 2.0



# MARK: Distance Function

# Calculates distance between two points
#
# Example:
#   Used to detect when the snake touches an apple
def dist(p1, p2):

    return np.linalg.norm(np.array(p1) - np.array(p2))



# MARK: Hand Closed Detection

# This function checks whether the hand is closed
#
# MediaPipe gives us 21 hand points (landmarks)
#
# We compare:
#   fingertip positions
# with:
#   finger joint positions
#
# If fingertips are lower than joints,
# the fingers are folded -> closed hand
def is_hand_closed(hand_landmarks):

    # Fingertip landmark IDs
    tips = [8, 12, 16, 20]

    # Finger joint landmark IDs
    pip = [6, 10, 14, 18]

    # Counter for folded fingers
    closed_fingers = 0

    # Check every finger
    for tip, pip_joint in zip(tips, pip):

        # If fingertip is below its joint,
        # the finger is folded
        # If the y-coordinate of the fingertip is greater than the y-coordinate of the joint, it means the fingertip is lower on the screen than the joint, which indicates that the finger is folded.
        # The origin (0, 0) is at the top-left corner. So a larger y value means a lower position on the screen.
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip_joint].y:
            # If the fingertip is below the joint, we consider that finger to be closed and increment our closed_fingers counter.
            closed_fingers += 1

    # If 4 or more fingers are folded (thumb is ignored, this way you can hold your pointer finger up a bit for better control without breaking the pause gesture),
    # treat the hand as closed
    return closed_fingers >= 4

# This function resets all game variables to their initial state
# It is called when the player holds a fist after game over to restart the game
def reset_game():
    global score
    global snake
    global snake_limit
    global apple_x
    global apple_y
    global prev_c
    global paused
    global game_over
    global game_won

    score = 0

    snake = []

    snake_limit = 0

    apple_x = None
    apple_y = None

    prev_c = None

    paused = False

    game_over = False
    game_won = False



# MARK: Camera Setup

# Start webcam
#
# 0 means default webcam
# If you have multiple cameras and want to use a different one, you can change this number to 1, 2, etc. depending on which camera you want to access.
cap = cv2.VideoCapture(0)



# MARK: Main Game

# This loop runs forever until ESC is pressed
# while true means from the moment the program starts, it will continuously read frames from the webcam, process them, and update the game state until the user decides to exit by pressing the ESC key.
while True:

    # Read one frame from webcam
    # ret is a boolean indicating if the frame was read successfully
    # frame is the actual image captured from the webcam
    # cap.read() captures a single frame from the webcam.
    # If the capture is successful, ret will be True and frame will contain the image data.
    # If it fails (e.g., webcam is not accessible), ret will be False, and we can use this to break the loop and exit the program gracefully.
    ret, frame = cap.read()

    # If camera fails, stop program
    if not ret:
        break



    # MARK: Frame Preperation

    # Resize frame for better performance
    # without setting the frame size manually, the game window will be too small on high resolution cameras, because the snake moves based on hand movement in the camera feed. 
    # If the feed is too large, the snake will move too much and be hard to control.
    frame = imutils.resize(frame, width=600)

    # Flip frame horizontally like a mirror
    # This makes it more intuitive to control the snake, because your hand movement will match the snake movement on screen.
    frame = cv2.flip(frame, 1)

    # Get frame height and width
    # the shape is determined by the camera resolution and the resizing we do with imutils
    # example: if the camera resolution is 1280x720 and we resize to width=600, the new height will be 337 (keeping the aspect ratio)
    h, w, _ = frame.shape



    # MARK: Apple Logic

    # Create a new apple if none exists
    if apple_x is None or apple_y is None:

        # Generate random x position
        # We use a margin of 50 pixels from the edges to prevent the apple from spawning too close to the wall, which would make it impossible to eat without colliding with the wall.
        apple_x = np.random.randint(50, w - 50)

        # Generate random y position
        # We use a margin of 50 pixels from the edges to prevent the apple from spawning too close to the wall, which would make it impossible to eat without colliding with the wall.
        apple_y = np.random.randint(50, h - 50)

    # Draw apple as a red circle
    # cv2.circle() draws a filled circle on the frame at the apple's coordinates. The circle has a radius of 10 pixels and is colored red (0, 0, 255 in BGR color space).
    # Use the frame inside the main loop to draw the apple on every frame, so it appears on the screen until the snake eats it.
    # When the snake eats the apple (when the snakes head has the same coordinates as the apple), we set apple_x and apple_y to None, which triggers the creation of a new apple in a random location on the next frame.
    cv2.circle(frame, (apple_x, apple_y), 10, (0, 0, 255), -1)



    # MARK: Hand Tracking

    # Convert image from BGR to RGB
    # OpenCV uses BGR
    # MediaPipe expects RGB
    # cv2.cvtColor() is used to convert the color space of the image from BGR (which is the default color format used by OpenCV) to RGB (which is the color format expected by MediaPipe for hand tracking).
    # This conversion is necessary because if we pass a BGR image to MediaPipe, it will not detect the hands correctly, since the color channels will be interpreted incorrectly.
    # By converting to RGB, we ensure that the hand tracking AI receives the image in the correct format for accurate detection.
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process image with MediaPipe AI
    # process() returns hand landmark positions if a hand is detected
    # example: if a hand is detected, result.multi_hand_landmarks will contain a list of hand landmarks, where each landmark has x and y coordinates normalized to the image size.
    # If no hand is detected, result.multi_hand_landmarks will be None.
    # every landmark represents a specific point on the hand, such as fingertips, joints, and the wrist. For example, landmark 8 is the tip of the index finger, and landmark 6 is the joint below it. By comparing the y-coordinates of these landmarks, we can determine if the finger is folded or extended.
    result = hands.process(rgb)

    # Current hand/finger position
    # This is the main point we track to control the snake.
    # If center is None, it means no hand is currently detected, and the snake will not move.
    # Once a hand is detected (when result.multi_hand_landmarks is not None) and we calculate the smoothed position, we store it in center, which is then used to update the snake's position on the screen.
    center = None

    # Determines whether a fist is currently detected
    # This variable is used to control the pause and restart gestures.
    # If a fist is detected, we set hand_closed to True, which triggers the timing logic for pausing or restarting the game.
    # If no fist is detected, we reset hand_closed to False, allowing the game to detect a new fist gesture when the player makes one.
    hand_closed = False


    # MARK: Hand Detected

    # if result.multi_hand_landmarks is not None, it means that MediaPipe has detected at least one hand in the current frame and has provided the landmark positions for that hand
    if result.multi_hand_landmarks:

        # Loop through all detected hands
        # We can then loop through the detected hands and access their landmarks to control the game.
        for hand_landmarks in result.multi_hand_landmarks:


            # MARK: Fist Detection

            # If hand is closed, - this comes from the is_hand_closed() function which checks if 4 or more fingers are folded
            # If the hand is closed, we set hand_closed to True, which will trigger the pause or restart logic later in the code
            if is_hand_closed(hand_landmarks):
                hand_closed = True


            # MARK: Hand Position Tracking

            # Landmark 8 = index finger tip
            # Multiply normalized landmark position by frame width and height to get pixel coordinates
            # MediaPipe gives us the hand landmark positions as normalized values between 0 and 1, where (0, 0) is the top-left corner of the image and (1, 1) is the bottom-right corner
            # To convert these normalized coordinates to actual pixel coordinates on the screen, we multiply the normalized x value by the width of the frame (w) and the normalized y value by the height of the frame (h)
            # This allows us to get the exact position of the index fingertip in pixels, which we can then use to control the snake's movement.
            raw_x = int(hand_landmarks.landmark[8].x * w)
            raw_y = int(hand_landmarks.landmark[8].y * h)


            # MARK: Smoothing

            # First frame setup
            # On the first frame where we detect a hand, we don't have any previous smoothed position to blend with, so we just set the smoothed position to be the same as the raw position
            # This initializes our smoothing variables and prevents any erratic movement on the first detection.
            # if smooth_x is None, it means this is the first time we are detecting a hand and calculating the position.
            # We set smooth_x and smooth_y to the raw_x and raw_y values to initialize our smoothed position.
            # On subsequent frames, we will have a smoothed position to blend with the new raw position, which allows us to create a smoother movement for the snake.
            if smooth_x is None:
                smooth_x, smooth_y = raw_x, raw_y

            # if smooth_x is not None, it means we have a previous smoothed position that we can blend with the new raw position to create a smoother movement.
            else:

                # Blend raw position with previous smoothed position
                # The alpha variable controls how much of the new raw position we use versus how much of the previous smoothed position we keep.
                # A higher alpha means we rely more on the new raw position, which makes the movement more responsive but also shakier.
                # A lower alpha means we rely more on the previous smoothed position, which makes the movement smoother but less responsive.
                # More smoothing (lower alpha) can help make the snake easier to control, especially if the hand tracking is a bit jittery.
                # However, too much smoothing (very low alpha) can make the snake feel sluggish and unresponsive to quick hand movements.
                smooth_x = int(
                    alpha * raw_x +
                    (1 - alpha) * smooth_x
                )

                smooth_y = int(
                    alpha * raw_y +
                    (1 - alpha) * smooth_y
                )

            # Set center to smoothed position
            # After calculating the smoothed position of the index fingertip, we set the center variable to this smoothed position
            # This center variable is what we will use to control the snake's movement on the screen 
            #   - the center is essentially the "head" of the snake that follows the player's hand and is calculated based on the smoothed position of the index fingertip.
            # By using the smoothed position, we can create a more stable and visually appealing movement for the snake, as it will follow the general direction of the hand without reacting to every small jitter in the hand tracking data.
            center = (smooth_x, smooth_y)


            # MARK: Draw fingertip position

            # Use the center variable to draw a green circle on the screen at the position of the index fingertip
            # This serves as a visual indicator of where the snake's head is and helps the player see how their hand movement is controlling the snake
            cv2.circle(frame, center, 10, (0, 255, 0), -1)



            # MARK: Draw hand landmarks
            # (optional)

            # Draw full hand landmark structure
            # This is optional and can be commented out if you don't want to see the hand skeleton
            # mp_draw.draw_landmarks() is a utility function provided by MediaPipe that allows us to draw the detected hand landmarks and connections on the frame for visualization purposes.
            # mp_draw.draw_landmarks(
            #     frame,
            #     hand_landmarks,
            #     mp_hands.HAND_CONNECTIONS
            # )



    # MARK: Fist Gesture Timing Logic

    # Current system time
    # We use this to track how long a fist has been held for pausing or restarting the game.
    # time.time returns the current time in seconds since January 1, 1970
    # We use this to calculate how long the player has been holding a fist gesture by comparing the current time to the time when the fist was first detected (fist_start_time).
    current_time = time.time()

    # If a fist is detected
    if hand_closed:

        # If fist_start_time is None, this is the first frame where the fist is detected
        if fist_start_time is None:
            # We set fist_start_time to the current time to start the timer for how long the fist has been held.
            fist_start_time = current_time

        # Prevent repeated triggering
        # We only want to trigger the pause or restart action once per fist gesture, so we check if gesture_triggered is False before allowing the logic to run.
        # If the gesture_triggered is true, it means we have already triggered the action for this fist gesture, and we will skip the timing logic until the fist is released and a new gesture can be detected.
        # If the gesture_triggered is false, it means we have not yet triggered the pause or restart action for the current fist gesture, and we can proceed to check how long the fist has been held.
        # If not gesture_triggered means that the bool is false
        if not gesture_triggered:

            # Calculate how long fist has been held
            # We calculate the hold time by subtracting the time when the fist was first detected (fist_start_time) from the current time
            # This gives us the duration in seconds that the player has been holding the fist gesture.
            hold_time = current_time - fist_start_time

            # If game is over or won, hold fist longer to restart
            if game_over or game_won:

                # if the hold time is greater than or equal to the restart_hold_duration (2 seconds)
                if hold_time >= restart_hold_duration:

                    # call the reset_game() function to reset all game variables to their initial state and start a new game
                    reset_game()

                    # set gesture_triggered to True to prevent the restart action from being triggered multiple times while the fist is still held
                    gesture_triggered = True

            # If game is not over or won, hold fist to pause/resume
            else:
                
                # if the hold time is greater than or equal to the fist_hold_duration (1 second)
                if hold_time >= fist_hold_duration:

                    # Toggle paused state
                    # # If the game is currently paused, this will unpause it, and if it is currently unpaused, this will pause it
                    # This allows the player to control the pause and resume functionality of the game using the fist gesture.
                    paused = not paused

                    # if the game is not paused after toggling, it means we just resumed the game, so we want to show the "START" text to indicate that the game has resumed
                    if not paused:
                        # We set show_start_text to True
                        show_start_text = True
                        # We also set start_text_time to the current time so that we can track how long the "START" message has been displayed and hide it after a certain duration (e.g., 1 second).
                        start_text_time = current_time

                    # Set gesture_triggered to True to prevent the pause/resume action from being triggered multiple times while the fist is still held
                    # This ensures that the game will only toggle between paused and unpaused once per fist gesture, and won't rapidly toggle if the player holds the fist for an extended period.
                    gesture_triggered = True
    
    # If no fist is detected
    else:

        # Reset timer when hand opens
        # If the player releases the fist, we reset fist_start_time to None, which allows us to detect a new fist gesture the next time the player makes one.
        fist_start_time = None

        # Allow gesture again
        # When the player releases the fist, we also reset gesture_triggered to False, which allows the game to detect a new fist gesture and trigger the pause or restart action again when the player makes another fist.
        gesture_triggered = False



    # MARK: Fist Gesture UI Feedback

    # if hand_closed is True and fist_start_time is not None and gesture_triggered is False, 
    #   it means that a fist gesture is currently being detected and we are in the process of timing how long the fist has been held to determine if we should trigger a pause or restart action.
    if hand_closed and fist_start_time is not None and not gesture_triggered:

        # Calculate loading progress
        # We calculate the progress of the loading bar by taking the current time, subtracting the time when the fist was first detected (fist_start_time), and dividing by the required hold duration (fist_hold_duration).
        # This gives us a value between 0 and 1 that represents how much of the required hold time has been completed
        # We also use min() to ensure that the progress does not exceed 1.0, which would represent the full hold duration being completed.
        progress = min(
            1.0,
            (current_time - fist_start_time) / fist_hold_duration
        )

        # MARK: Draw Loading Bar
        # choose loading bar color
        # Default color is green (0, 0, 255 in BGR)
        # If game is over or won, change color to red (0, 255, 0 in BGR)
        bar_color = (0, 0, 255) if game_over or game_won else (0, 255, 0)

        # Draw a rectangle representing the loading bar
        cv2.rectangle(
            frame,
            # The top-left corner of the rectangle is fixed at (50, 50), which means the loading bar will always start at this position on the screen
            (50, 50),
            # (50 + int(200 * progress), 70) - x position starts at 50 and grows 200 pixels as progress goes from 0 to 1, y position is fixed at 70, so the bottom edge of the bar will be at y=70
            (50 + int(200 * progress), 70),
            # set the color to the bar_color variable, which is green for pausing and red for restarting
            bar_color,
            # -1 means the rectangle will be filled in with the specified color, creating a solid loading bar that fills up as the player holds the fist gesture.
            # setting it to a positive number would just draw the outline of the rectangle with that thickness, but by setting it to -1, we fill the entire rectangle with the color, which visually represents the loading progress more clearly.
            -1
        )

        # Show helper text
        # We also display the text "FIST DETECTED" on the screen to provide feedback to the player that their fist gesture has been recognized and the loading bar is filling up.
        cv2.putText(
            frame,
            # Text to display on the screen
            "FIST DETECTED",
            # Position of the text on the screen (x=50, y=100 to place it below the loading bar)
            (50, 100),
            # Font type (using a simple built-in font provided by OpenCV)
            cv2.FONT_HERSHEY_SIMPLEX,
            # Font scale (1 means normal size, you can adjust this to make the text larger or smaller)
            1,
            # Text color (0, 0, 255 in BGR for red)
            (0, 0, 255),
            # Thickness of the text (2 pixels)
            2
        )



    # MARK: Snake Logic

    # Only move snake if:
    #   a hand exists - center is not None
    #   AND game is not paused - paused is False
    #   AND game is not over - game_over is False
    #   AND game is not won - game_won is False
    if (
        center is not None
        and not paused
        and not game_over
        and not game_won
    ):

        # check wall collision
        # set a margin of 20 pixels from the edges of the screen to prevent the snake from colliding with the wall when the hand is near the edge
        # This gives the player a small buffer zone to control the snake without immediately losing when they get close to the wall.
        margin = 20

        # if the center of the snake (the index fingertip position) is within the margin distance from any edge of the screen,
        # we consider it a collision with the wall and set game_over to True,
        # which will trigger the game over state and display the "GAME OVER" message on the screen.
        if (
            center[0] <= margin or
            center[0] >= w - margin or
            center[1] <= margin or
            center[1] >= h - margin
        ):
            game_over = True

        # Add new snake point if movement is large enough
        # We check the distance between the previous position of the snake's head (prev_c) and the current position (center).
        #   If the distance is greater than 3 pixels, we add the current position to the snake list.
        # This prevents the snake from adding a new point for every tiny movement of the hand, which would make the snake look very jittery and be hard to control.
        #   By only adding a new point when the hand has moved a certain distance, we create smoother movement for the snake.
        if prev_c and dist(prev_c, center) > 3:
            snake.append(center)

        # Remove oldest snake point if snake is too long
        # If the length of the snake list exceeds the snake_limit, we remove the oldest point (the first point in the list) using snake.pop(0).
        # This way, the snake will only grow when the player eats an apple (which increases snake_limit), and otherwise will maintain its current length by removing the tail as new points are added to the head.
        if len(snake) > snake_limit:
            snake.pop(0)

        # only check collision if apple exists
        # We check if apple_x and apple_y are not None before checking for collision with the apple, because if they are None, it means there is no apple currently on the screen to collide with.
        if apple_x is not None and apple_y is not None:

            # if the distance between the snake's head (center) and the apple's position (apple_x, apple_y) is less than 20 pixels, we consider that the snake has eaten the apple.
            if dist(center, (apple_x, apple_y)) < 20:
                # When the snake eats the apple, we increase the score by 1 and also increase the snake_limit by 1,
                #   which allows the snake to grow longer on the next frames as new points are added to the snake list without removing old points until it exceeds the new limit.
                score += 1
                snake_limit += 1
                # We then set apple_x and apple_y to None, which will trigger the creation of a new apple in a random location on the next frame.
                # This is done on line 265 where we check if apple_x or apple_y is None to create a new apple.
                apple_x = None
                apple_y = None

                # If the current score is greater than or equal to the max_score, we set game_won to True, which will trigger the win state and display the "YOU WIN !!" message on the screen.
                if score >= max_score:
                    game_won = True

        # Save current position for next frame
        # After processing the current frame and updating the snake's position, we save the current center position to prev_c so that on the next frame, we can calculate the distance moved and determine if we should add a new point to the snake.
        # This allows us to track the movement of the snake's head across frames and control when new points are added to the snake based on how far the hand has moved.
        prev_c = center



    # MARK: Draw Snake

    # Draw lines between all snake points
    # the snake variable is a list of points representing the segments of the snake's body, where each point is a tuple (x, y) of pixel coordinates on the screen.
    # loop through the snake list starting from the second point (index 1 because 0 is the head) to the end of the list, 
    # and for each point, we draw a line from the previous point (snake[i - 1]) to the current point (snake[i]) using cv2.line().
    for i in range(1, len(snake)):

        # Snake thickness grows slightly with size
        # As the snake grows longer, we increase the thickness of the lines that represent the snake's body to make it visually more appealing and easier to see as it gets bigger.
        thickness = int(len(snake) / 10 + 2)

        # Draw snake segment
        # Draw a line between the previous point (snake[i - 1]) and the current point (snake[i]) with the specified thickness and color (0, 255, 0 in BGR for green).
        cv2.line(
            frame,
            snake[i - 1],
            snake[i],
            (0, 255, 0),
            thickness
        )



    # MARK: UI Elements

    # Draw score text
    # We display the current score in the top-right corner of the screen using cv2.putText()
    cv2.putText(
        # the frame on which to draw the text
        frame,
        # the text to display, which includes the current score variable
        f"Score: {score}",
        # the position of the text on the screen (x=400, y=50 to place it in the top-right corner)
        (400, 50),
        # the font type (using a simple built-in font provided by OpenCV)
        cv2.FONT_HERSHEY_SIMPLEX,
        # the font scale (1 means normal size, you can adjust this to make the text larger or smaller)
        1,
        # the text color (255, 0, 200 in BGR for a pinkish color)
        (255, 0, 200),
        # the thickness of the text
        2
    )

    # Show paused text
    # If the game is currently paused, we display the text "PAUSED" in the center of the screen to indicate to the player that the game is paused and they can use the fist gesture to resume.
    if paused:

        cv2.putText(
            frame,
            "PAUSED",
            (160, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 255, 255),
            4
        )

    # show START text
    # When the player resumes the game from a paused state, we set show_start_text to True and start a timer (start_text_time) to track how long the "START" message has been displayed.
    if show_start_text:

        cv2.putText(
            frame,
            "START",
            (180, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 255, 0),
            4
        )

        # remove text after 1 second
        # if the current time minus the time when the "START" text was shown is greater than 1 second, we set show_start_text to False to hide the message from the screen.
        if current_time - start_text_time > 1:
            show_start_text = False

    # Show win message
    # If the player has won the game by reaching the max score, we set game_won to True, which triggers this block of code to display the "YOU WIN !!" message on the screen along with instructions to hold a fist to restart the game.
    if game_won:

        cv2.putText(
            frame,
            "YOU WIN !!",
            (100, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (255, 255, 0),
            4
        )
        cv2.putText(
            frame,
            "HOLD FIST TO RESTART",
            (40, 320),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

    # Show game over message
    # If the player collides with the wall, we set game_over to True, which triggers this block of code to display the "GAME OVER" message on the screen along with instructions to hold a fist to restart the game.
    if game_over:

        cv2.putText(
            frame,
            "GAME OVER",
            (100, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 255),
            4
        )
        cv2.putText(
            frame,
            "HOLD FIST TO RESTART",
            (40, 320),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )



    # MARK: Display Frame

    # Display the final game window
    # After processing all the game logic, drawing the snake, apple, and UI elements on the frame, we use cv2.imshow() to display the frame in a window titled "Snake Game (MediaPipe)"
    # This will show the live video feed from the webcam with the game elements overlaid on top, allowing the player to see their hand controlling the snake and interact with the game in real-time
    cv2.imshow("Snake Game (MediaPipe)", frame)



    # MARK: Exit Game

    # If ESC key is pressed, stop program
    if cv2.waitKey(1) & 0xFF == 27:
        break



# MARK: Cleanup

# Release webcam
# cap.release() is called to release the webcam resource when the game loop ends (e.g., when the player presses the ESC key to exit the game)
# This is important to free up the camera for other applications and to ensure that it is properly closed when we are done using it.
cap.release()

# Close all OpenCV windows
# cv2.destroyAllWindows() is called to close any OpenCV windows that were opened during the game, such as the game window displaying the webcam feed and game elements.
# This ensures that all windows are properly closed and the program exits cleanly without leaving any open windows or resources hanging
cv2.destroyAllWindows()
