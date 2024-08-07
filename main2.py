import cv2 as cv
import numpy as np
import kociemba
from collections import Counter
import colorama

# Define the colors for better visualization
colorama.init(autoreset=True)
ERROR = "{ERROR}   : " + colorama.Fore.RED
SUCCESS = "{SUCCESS} : " + colorama.Fore.GREEN
INFO = "{INFO}    : " + colorama.Fore.CYAN
DEBUG = "{DEBUG}   : " + colorama.Fore.YELLOW

# If you want to use the default camera, use 1, if you want to use a video file, use the file name
# Comment out the one you don't want to use
# video = cv.VideoCapture("test.mp4")
video = cv.VideoCapture(1)

# Minimum number of occurrences of a color mapped face to be considered
min_occurrences = 100

# Dictionary to store the faces of the cube
faces = {
    'Red': "",
    'Yellow': "",
    'Green': "",
    'Blue': "",
    'White': "",
    'Orange': ""
}

# Dictionary to store the mapping of the colors to the corresponding letter of the face
color_name_to_face_letter = {
    'Yellow': 'U',
    'Red': 'R',
    'Blue': 'F',
    'White': 'D',
    'Orange': 'L',
    'Green': 'B'
}

# Dictionary to store the mapping of the letter of the face to the corresponding color
face_letter_to_color_name = {
    'R': 'Red',
    'U': 'Yellow',
    'B': 'Green',
    'F': 'Blue',
    'D': 'White',
    'L': 'Orange'
}

# Mappa lettere a colori
color_map = {
    'R': (0, 0, 255),  # Rosso
    'U': (0, 255, 255),  # Giallo
    'B': (0, 255, 0),  # Verde
    'F': (255, 0, 0),  # Blu
    'D': (255, 255, 255),  # Bianco
    'L': (0, 165, 255),  # Arancione
    '': (255, 255, 255)  # Colore di default (bianco) per celle vuote
}

# We draw the face with the colors that are being mapped in real-time
def draw_face(image, start_x, start_y, face_str):
    # The size of each cell is 50x50 pixels
    cell_size = 50
    for i in range(3):
        for j in range(3):
            # Get the color of the cell
            color = color_map[face_str[i*3 + j] if face_str else '']
            top_left = (start_x + j * cell_size, start_y + i * cell_size)
            bottom_right = (start_x + (j + 1) * cell_size, start_y + (i + 1) * cell_size)
            # Fill the cell with the color (-1 at the end means fill the rectangle)
            cv.rectangle(image, top_left, bottom_right, color, -1)
            # Black border around the cell
            cv.rectangle(image, top_left, bottom_right, (0, 0, 0), 1)

# Function to draw the cube with the faces that are being mapped in real-time
def draw_cube(faces):
    # Each face is 150x150 pixels
    image_size = 150
    # The window is 600x450 pixels cause we have 4 faces in a row and 3 faces in a column
    full_width = image_size * 4
    full_height = image_size * 3
    # Create a white image
    image = np.ones((full_height, full_width, 3), dtype=np.uint8) * 255

    # We draw the 4 faces in row
    # Orange, Blue, Red, Green
    draw_face(image, 0, image_size, faces['Orange'])
    draw_face(image, image_size, image_size, faces['Blue'])
    draw_face(image, image_size * 2, image_size, faces['Red'])
    draw_face(image, image_size * 3, image_size, faces['Green'])

    # We draw the 2 faces in column
    # Yellow
    # Blue (in my case, it's the front face)
    # White
    draw_face(image, image_size, 0, faces['Yellow'])
    draw_face(image, image_size, image_size * 2, faces['White'])

    # Result:
    #         Yellow
    # Orange, Blue, Red, Green
    #         White
    return image

# Function to detect the color of the region of interest (ROI)
def detect_color(hsv_roi):
    # Define color ranges in HSV
    # The ranges are defined as a tuple of two lists: the lower and upper bounds of the color range
    # The color ranges are defined for the following colors: Red, Yellow, Green, Blue, White, Orange
    # The ranges are defined in the following format: ([H_min, S_min, V_min], [H_max, S_max, V_max])
    # Red color is a special case because it wraps around the 0-180 range in HSV
    # White color is also a special case because it has a low saturation and high value
    # Orange is missing because it was mistakenly detected as Red, so it is treated by exclusion as the last case
    color_ranges = {
        'Red': ([0, 50, 50], [5, 255, 255]),
        'Red2': ([175, 50, 50], [180, 255, 255]),
        'Yellow': ([20, 70, 120], [35, 255, 255]),
        'Green': ([35, 70, 70], [85, 255, 255]),
        'Blue': ([85, 150, 50], [130, 255, 255]),
        'White': ([0, 0, 200], [180, 30, 255]),
        'White2': ([0, 0, 100], [180, 30, 200])
    }

    # Calculate the median color of the ROI
    # The median color is used to determine the color of the ROI
    median_color = np.median(hsv_roi, axis=(0, 1)).astype(int)

    # Check the median color against the color ranges
    for color_name, (lower, upper) in color_ranges.items():
        lower = np.array(lower)
        upper = np.array(upper)
        # Check if the median color is within the color range
        if cv.inRange(np.array([[median_color]]), lower, upper):
            # Return the color name
            # If the color is Red2 or White2, return Red or White respectively
            if color_name == 'Red2':
                return 'Red'
            elif color_name == 'White2':
                return 'White'
            return color_name
    # If the color is not Red, Yellow, Green, Blue, White, return Orange
    return 'Orange'

# Function to run the color detection and face mapping
def run():
    # Dictionary to store the mapping
    # The key is the mapped face, and the value is the number of occurrences
    # number_of_face_mapped is the number of faces that have been mapped so far
    mapping = {}
    number_of_face_mapped = 0

    # Loop through the video frames
    while True:
        # Read the next frame
        ret, frame = video.read()
        # If the frame is empty, break the loop
        if not ret:
            break

        # Make a copy of the frame
        copy = frame.copy()

        # Get the dimensions of the frame
        height, width, _ = frame.shape
        
        # Define the size of the square that would have contained the 3x3 grid (e.g., 300x300 pixels)
        square_size = 300
        
        # Calculate the size of each cell in the 3x3 grid
        cell_size = square_size // 3
        
        # Create an empty image for the 3x3 grid view
        grid_view = np.zeros((square_size, square_size, 3), dtype=np.uint8)

        # To store the detected colors
        detected_colors = []

        # Process each of the 9 cells in the 3x3 grid
        for i in range(3):
            for j in range(3):
                # Calculate the top-left corner of the smaller square in the original frame
                small_square_size = cell_size // 2
                small_top_left = (width // 2 - square_size // 2 + j * cell_size + (cell_size - small_square_size) // 2,
                                  height // 2 - square_size // 2 + i * cell_size + (cell_size - small_square_size) // 2)
                
                # Calculate the bottom-right corner
                small_bottom_right = (small_top_left[0] + small_square_size, small_top_left[1] + small_square_size)
                
                # Draw the smaller square in the original frame
                cv.rectangle(frame, small_top_left, small_bottom_right, (0, 255, 0), 1)
                
                # Extract the region of interest (ROI) from the copy of the frame
                # so we don't see the rectangles from the grid view in the original frame
                roi = copy[small_top_left[1]:small_bottom_right[1], small_top_left[0]:small_bottom_right[0]]
                
                # Convert the ROI to HSV
                hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)
                
                # Detect the color of the ROI
                color = detect_color(hsv_roi)
                detected_colors.append(color)
                
                # Annotate the detected color on the frame
                cv.putText(frame, color, (small_top_left[0], small_top_left[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
                
                # Resize the ROI to fit the grid cell size
                resized_roi = cv.resize(roi, (cell_size, cell_size))
                
                # Place the resized ROI into the correct position in the grid view
                grid_view[i*cell_size:(i+1)*cell_size, j*cell_size:(j+1)*cell_size] = resized_roi

        # Display the original frame with the smaller squares
        cv.imshow("frame", frame)
        
        # Display the 3x3 grid view in a new window
        cv.imshow("3x3 Grid View", grid_view)

        # Display the cube with the faces that are being mapped in real-time
        cube_image = draw_cube(faces)
        cv.imshow("Cube", cube_image)

        # Print detected colors as Red, Red, Red
        #                          Red, Red, Red
        #                          Red, Red, Red
        # for i in range(3):
        #     print(detected_colors[i*3:i*3+3])
        # print()

        # Initialize the mapped face in this frame
        mapped_face = ""

        # Print detected colors as R U F
        #                          U F R
        #                          R F U
        # Iterate through the detected colors of the map (3x3 grid of cells)
        for i in range(3):
            for j in range(3):
                # get the color of a single cell
                color = detected_colors[i*3 + j]
                # get the corresponding face letter
                face_letter = color_name_to_face_letter[color]
                # append the face letter to the mapped face
                mapped_face += face_letter
                # print the face letter
                # NOTE: uncomment the following lines to see the face letters
        #         print(face_letter, end=' ')
        #     print()
        # print()

        # Check if the mapped face is in the mapping
        if mapped_face in mapping:
            # Increment the occurrence
            mapping[mapped_face] += 1
        else:
            # Add the mapped face to the mapping with an occurrence of 1
            mapping[mapped_face] = 1

        # Check if the number of occurrences of the mapped face is greater than or equal to the minimum occurrences required
        for face, occurrences in mapping.items():
            if occurrences >= min_occurrences:
                # Get the color name of the central cell of the face to identify which face it is
                # For example:
                #
                #     R U F
                #     U F R
                #     R F U
                #
                # The central cell of the face is F which corresponds to the color Blue
                # So we know that we are mapping the Blue face
                c_name = face_letter_to_color_name[face[4]]
                # Check if the face is not already mapped
                if faces[c_name] == "" and c_name in faces:
                    # Map the colors to the face corresponding to the color name
                    faces[c_name] = face
                    # Empty the mapping and increment the number of faces mapped
                    mapping = {}
                    number_of_face_mapped += 1
        
        # Check for key presses
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            # If the 'q' key is pressed, print the mapping and the faces and exit the loop
            print(mapping)
            print(faces)
            print("Exiting...")
            break
        elif key == ord("s"):
            # If the 's' key is pressed, save the screenshot of the grid view and exit the loop
            cv.imwrite("screenshot.png", grid_view)
            print("Screenshot saved! Now exiting...")
            break
        elif key in [ord("l"), ord("f"), ord("r"), ord("b"), ord("u"), ord("d")]:
            # If the letter of the face is pressed, reset the face to be remapped
            color_face = face_letter_to_color_name[chr(key).upper()]
            faces[color_face] = ""
            print(f"{INFO}Resetting {color_face} face...")
        elif number_of_face_mapped == 6:
            # If the number of faces mapped is 6, the cube is mapped
            print(faces)
            print("Mapped!")

            # Get the string representing the cube state by joining the faces values
            string_to_solve = "".join(faces.values())

            # Get the letter counts of the string
            tmp_letter_counts = Counter(string_to_solve)
            # Check if the letter counts is exactly 6
            if len(tmp_letter_counts) == 6:
                # Check if each letter has exactly 9 occurrences
                if all(count == 9 for count in tmp_letter_counts.values()):
                    # The cube state mapping is valid, so solve the cube using the Kociemba algorithm
                    print("Solution: ", kociemba.solve(string_to_solve))
                else:
                    print("Invalid cube state: less or more than 9 occurrences of some colors are found")
            else:
                print("Invalid cube state: less or more than 6 colors are found")
            break

    # Release the video capture and close all windows       
    video.release()
    cv.destroyAllWindows()

# Run the application
if __name__ == "__main__":
    # Run method
    run()
