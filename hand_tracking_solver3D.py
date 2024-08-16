from ursina import *
import cv2
import mediapipe as mp
import threading

class MainPage(Entity):
    def __init__(self):
        super().__init__()
        
        cube_colors = [
            color.red,     # right
            color.orange,  # left
            color.yellow,  # top
            color.white,   # bottom
            color.green,   # back
            color.blue,    # front
        ]

        # make a model with a separate color on each face
        combine_parent = Entity(enabled=False)
        for i in range(3):
            dir = Vec3(0,0,0)
            dir[i] = 1
            
            e = Entity(parent=combine_parent, model='plane', origin_y=-.5, texture='white_cube', color=cube_colors[i*2])
            e.look_at(dir, 'up')

            e_flipped = Entity(parent=combine_parent, model='plane', origin_y=-.5, texture='white_cube', color=cube_colors[(i*2)+1])
            e_flipped.look_at(-dir, 'up')

        combine_parent.combine()

        # place 3x3x3 cubes
        self.cubes = []
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    e = Entity(model=copy(combine_parent.model), position=Vec3(x,y,z) - (Vec3(3,3,3)/3), texture='white_cube')
                    self.cubes.append(e)

        # rotate a side when we click on it
        self.collider = Entity(model='cube', scale=3, collider='box', visible=False)

    def rotate_U_face(self, direction=1):
        # Rotate the top face by 90 degrees
        for cube in self.cubes:
            if cube.y > 0:
                cube.rotation_y += 90 * direction

    def rotate_E_face(self, direction=1):
        # Rotate the middle horizontal face by 90 degrees
        for cube in self.cubes:
            if -0.5 < cube.y < 0.5:  # Middle layer
                cube.rotation_y += 90 * direction

    def rotate_D_face(self, direction=1):
        # Rotate the bottom face by 90 degrees
        for cube in self.cubes:
            if cube.y < 0:
                cube.rotation_y += 90 * direction


def hand_tracking_thread(main_page):
    # Hand Tracking setup
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    finger_states = {"index_right": False, "index_left": False,
                     "middle_right": False, "middle_left": False,
                     "ring_right": False, "ring_left": False}

    # Open the webcam
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Determine if the hand is right or left
                    is_right_hand = handedness.classification[0].label == "Right"

                    # Retrieve landmark positions
                    landmarks = hand_landmarks.landmark

                    # Check index finger (U face)
                    index_finger_closed = landmarks[8].y > landmarks[7].y
                    if is_right_hand and index_finger_closed and not finger_states["index_right"]:
                        main_page.rotate_U_face(direction=1)
                        finger_states["index_right"] = True
                    elif not is_right_hand and index_finger_closed and not finger_states["index_left"]:
                        main_page.rotate_U_face(direction=-1)
                        finger_states["index_left"] = True
                    if not index_finger_closed:
                        finger_states["index_right"] = False
                        finger_states["index_left"] = False

                    # Check middle finger (E face)
                    middle_finger_closed = landmarks[12].y > landmarks[11].y
                    if is_right_hand and middle_finger_closed and not finger_states["middle_right"]:
                        main_page.rotate_E_face(direction=1)
                        finger_states["middle_right"] = True
                    elif not is_right_hand and middle_finger_closed and not finger_states["middle_left"]:
                        main_page.rotate_E_face(direction=-1)
                        finger_states["middle_left"] = True
                    if not middle_finger_closed:
                        finger_states["middle_right"] = False
                        finger_states["middle_left"] = False

                    # Check ring finger (D face)
                    ring_finger_closed = landmarks[16].y > landmarks[15].y
                    if is_right_hand and ring_finger_closed and not finger_states["ring_right"]:
                        main_page.rotate_D_face(direction=1)
                        finger_states["ring_right"] = True
                    elif not is_right_hand and ring_finger_closed and not finger_states["ring_left"]:
                        main_page.rotate_D_face(direction=-1)
                        finger_states["ring_left"] = True
                    if not ring_finger_closed:
                        finger_states["ring_right"] = False
                        finger_states["ring_left"] = False

            cv2.imshow('Hand Tracking', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


# Initialize Ursina app
app = Ursina()
main_page = MainPage()

# Start the hand tracking in a separate thread
tracking_thread = threading.Thread(target=hand_tracking_thread, args=(main_page,))
tracking_thread.start()

# Run the Ursina app (in the main thread)
app.run()

# Ensure the tracking thread stops when the app closes
tracking_thread.join()
