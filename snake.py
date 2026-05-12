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


# =========================================================
# MEDIAPIPE SETUP
# =========================================================

# Create a shortcut to the MediaPipe hands module
mp_hands = mp.solutions.hands

# Initialize the hand tracking system
# min_detection_confidence:
#   How sure MediaPipe must be before detecting a hand
#
# min_tracking_confidence:
#   How stable the hand tracking should be between frames
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Utility used for drawing the hand skeleton on screen
# This is optional and can be commented out if you don't want to see the hand skeleton
mp_draw = mp.solutions.drawing_utils


# =========================================================
# GAME VARIABLES
# =========================================================

# Current player score
score = 0

# Score needed to win the game
max_score = 20

# List storing all snake body positions
snake = []

# Maximum allowed snake length
# This increases when the player eats apples
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
# Used to track movement direction
prev_c = None


# =========================================================
# SMOOTHING VARIABLES
# =========================================================

# These variables are used to smooth hand movement
# Without smoothing the snake would shake a lot

smooth_x = None
smooth_y = None

# Smoothing strength
#
# Lower number:
#   smoother movement but slower response
#
# Higher number:
#   faster response but more shaking
alpha = 0.5


# =========================================================
# FIST GESTURE VARIABLES
# =========================================================

# Stores the time when a fist gesture starts
fist_start_time = None

# Number of seconds the fist must be held
# before pause activates
fist_hold_duration = 1.0

# Prevents the pause gesture from triggering repeatedly
gesture_triggered = False

# Determines if the start text should be displayed
show_start_text = False
# Stores the time when the start text is shown
start_text_time = 0

# Number of seconds to hold fist to trigger a restart after game over
restart_hold_duration = 2.0


# =========================================================
# DISTANCE FUNCTION
# =========================================================

# Calculates distance between two points
#
# Example:
#   Used to detect when the snake touches an apple
def dist(p1, p2):

    return np.linalg.norm(np.array(p1) - np.array(p2))


# =========================================================
# HAND CLOSED DETECTION
# =========================================================

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

        # In image coordinates:
        # Larger y-value means lower on screen
        #
        # If fingertip is below its joint,
        # the finger is folded
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip_joint].y:
            closed_fingers += 1

    # If 4 or more fingers are folded (thumb is ignored, this way you can hold your pointer finger up a bit for better control without breaking the pause gesture),
    # treat the hand as closed
    return closed_fingers >= 4

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


# =========================================================
# CAMERA SETUP
# =========================================================

# Start webcam
#
# 0 means default webcam
cap = cv2.VideoCapture(0)


# =========================================================
# MAIN GAME LOOP
# =========================================================

# This loop runs forever until ESC is pressed
while True:

    # Read one frame from webcam
    ret, frame = cap.read()

    # If camera fails, stop program
    if not ret:
        break


    # =====================================================
    # FRAME PREPARATION
    # =====================================================

    # Resize frame for better performance
    # without setting the frame size manually, the game window will be too small on high resolution cameras, because the snake moves based on hand movement in the camera feed. 
    # If the feed is too large, the snake will move too much and be hard to control.
    frame = imutils.resize(frame, width=600)

    # Flip frame horizontally like a mirror
    # Makes movement feel natural
    frame = cv2.flip(frame, 1)

    # Get frame height and width
    # the shape is determined by the camera resolution and the resizing we do with imutils
    # example: if the camera resolution is 1280x720 and we resize to width=600, the new height will be 337 (keeping the aspect ratio)
    h, w, _ = frame.shape


    # =====================================================
    # APPLE SPAWNING
    # =====================================================

    # Create a new apple if none exists
    if apple_x is None or apple_y is None:

        # Generate random x position
        apple_x = np.random.randint(50, w - 50)

        # Generate random y position
        apple_y = np.random.randint(50, h - 50)

    # Draw apple as a red circle
    cv2.circle(frame, (apple_x, apple_y), 10, (0, 0, 255), -1)


    # =====================================================
    # HAND TRACKING
    # =====================================================

    # Convert image from BGR to RGB
    #
    # OpenCV uses BGR
    # MediaPipe expects RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process image with MediaPipe AI
    # process() returns hand landmark positions if a hand is detected
    # example: if a hand is detected, result.multi_hand_landmarks will contain a list of hand landmarks, where each landmark has x and y coordinates normalized to the image size. If no hand is detected, result.multi_hand_landmarks will be None.
    # every landmark represents a specific point on the hand, such as fingertips, joints, and the wrist. For example, landmark 8 is the tip of the index finger, and landmark 6 is the joint below it. By comparing the y-coordinates of these landmarks, we can determine if the finger is folded or extended.
    result = hands.process(rgb)

    # Current hand/finger position
    center = None

    # Determines whether a fist is currently detected
    hand_closed = False


    # =====================================================
    # IF A HAND IS DETECTED
    # =====================================================

    if result.multi_hand_landmarks:

        # Loop through all detected hands
        for hand_landmarks in result.multi_hand_landmarks:


            # =============================================
            # CHECK FOR FIST GESTURE
            # =============================================

            # If hand is closed,
            # activate fist state
            if is_hand_closed(hand_landmarks):
                hand_closed = True


            # =============================================
            # GET INDEX FINGER POSITION
            # =============================================

            # Landmark 8 = index finger tip
            raw_x = int(hand_landmarks.landmark[8].x * w)
            raw_y = int(hand_landmarks.landmark[8].y * h)


            # =============================================
            # MOVEMENT SMOOTHING
            # =============================================

            # First frame setup
            if smooth_x is None:
                smooth_x, smooth_y = raw_x, raw_y

            # Smooth movement using EMA filter
            else:

                smooth_x = int(
                    alpha * raw_x +
                    (1 - alpha) * smooth_x
                )

                smooth_y = int(
                    alpha * raw_y +
                    (1 - alpha) * smooth_y
                )

            # Final smoothed position
            center = (smooth_x, smooth_y)


            # =============================================
            # DRAW TRACKING POINT
            # =============================================

            # Draw green circle on fingertip
            cv2.circle(frame, center, 10, (0, 255, 0), -1)


            # =============================================
            # DRAW HAND SKELETON
            # =============================================

            # Draw full hand landmark structure
            # This is optional and can be commented out if you don't want to see the hand skeleton
            # mp_draw.draw_landmarks(
            #     frame,
            #     hand_landmarks,
            #     mp_hands.HAND_CONNECTIONS
            # )


    # =====================================================
    # PAUSE GESTURE LOGIC
    # =====================================================

    # Current system time
    current_time = time.time()

    # If a fist is detected
    if hand_closed:

        # Start timer if this is first frame
        if fist_start_time is None:
            fist_start_time = current_time

        # Prevent repeated triggering
        if not gesture_triggered:

            # Calculate how long fist has been held
            hold_time = current_time - fist_start_time

            # GAME OVER -> restart game
            if game_over or game_won:

                if hold_time >= restart_hold_duration:

                    reset_game()

                    gesture_triggered = True

            # NORMAL pause toggle
            else:

                if hold_time >= fist_hold_duration:

                    paused = not paused

                    # show START text when resuming
                    if not paused:
                        show_start_text = True
                        start_text_time = current_time

                    gesture_triggered = True

    else:

        # Reset timer when hand opens
        fist_start_time = None

        # Allow gesture again
        gesture_triggered = False


    # =====================================================
    # LOADING BAR VISUAL
    # =====================================================

    # Show loading bar while fist is being held
    if hand_closed and fist_start_time is not None and not gesture_triggered:

        # Calculate loading progress
        progress = min(
            1.0,
            (current_time - fist_start_time) / fist_hold_duration
        )

        # Draw loading bar
        # choose loading bar color
        # green = restart
        # red = pause/play
        bar_color = (0, 255, 0) if game_over or game_won else (0, 0, 255)

        cv2.rectangle(
            frame,
            (50, 50),
            (50 + int(200 * progress), 70),
            bar_color,
            -1
        )

        # Show helper text
        cv2.putText(
            frame,
            "FIST DETECTED",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )


    # =====================================================
    # SNAKE GAME LOGIC
    # =====================================================

    # Only move snake if:
    #   a hand exists
    #   AND game is not paused
    #   AND game is not over
    if (
        center is not None
        and not paused
        and not game_over
        and not game_won
    ):

        # check wall collision
        margin = 20

        if (
            center[0] <= margin or
            center[0] >= w - margin or
            center[1] <= margin or
            center[1] >= h - margin
        ):
            game_over = True

        # Add new snake point if movement is large enough
        #
        # Prevents too many points being added
        if prev_c and dist(prev_c, center) > 3:
            snake.append(center)

        # Remove oldest snake point if snake is too long
        if len(snake) > snake_limit:
            snake.pop(0)

        # only check collision if apple exists
        if apple_x is not None and apple_y is not None:

            if dist(center, (apple_x, apple_y)) < 20:

                score += 1
                snake_limit += 1

                apple_x = None
                apple_y = None

                if score >= max_score:
                    game_won = True

        # Save current position for next frame
        prev_c = center


    # =====================================================
    # DRAW SNAKE
    # =====================================================

    # Draw lines between all snake points
    for i in range(1, len(snake)):

        # Snake thickness grows slightly with size
        thickness = int(len(snake) / 10 + 2)

        # Draw snake segment
        cv2.line(
            frame,
            snake[i - 1],
            snake[i],
            (0, 255, 0),
            thickness
        )


    # =====================================================
    # USER INTERFACE
    # =====================================================

    # Draw score text
    cv2.putText(
        frame,
        f"Score: {score}",
        (400, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 200),
        2
    )

    # Show paused text
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

    # show START text for 1 second
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
        if current_time - start_text_time > 1:
            show_start_text = False

    # Show win message
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


    # =====================================================
    # SHOW FINAL FRAME
    # =====================================================

    # Display the final game window
    cv2.imshow("Snake Game (MediaPipe)", frame)


    # =====================================================
    # EXIT KEY
    # =====================================================

    # If ESC key is pressed, stop program
    if cv2.waitKey(1) & 0xFF == 27:
        break


# =========================================================
# CLEANUP
# =========================================================

# Release webcam
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
