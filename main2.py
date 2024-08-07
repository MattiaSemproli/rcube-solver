import cv2 as cv
import numpy as np

# If you want to use the default camera, use 1, if you want to use a video file, use the file name
# Comment out the one you don't want to use
# video = cv.VideoCapture("test.mp4")
video = cv.VideoCapture(1)

faces = {
    'Red': "",
    'Yellow': "",
    'Green': "",
    'Blue': "",
    'White': "",
    'Orange': ""
}

color_name_to_face_letter = {
    'Red': 'R',
    'Yellow': 'U',
    'Green': 'B',
    'Blue': 'F',
    'White': 'D',
    'Orange': 'L'
}

def detect_color(hsv_roi):
    # Define color ranges in HSV
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
    median_color = np.median(hsv_roi, axis=(0, 1)).astype(int)

    for color_name, (lower, upper) in color_ranges.items():
        lower = np.array(lower)
        upper = np.array(upper)
        if cv.inRange(np.array([[median_color]]), lower, upper):
            if color_name == 'Red2':
                return 'Red'
            elif color_name == 'White2':
                return 'White'
            return color_name
    return 'Orange'

def run():
    while True:
        ret, frame = video.read()
        if not ret:
            break

        copy = frame.copy()

        # Convert the frame to HSV color space
        hsv_frame = cv.cvtColor(copy, cv.COLOR_BGR2HSV)

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
                
                # Extract the region of interest (ROI) from the original frame
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

        # Print detected colors as Red, Red, Red
        #                          Red, Red, Red
        #                          Red, Red, Red
        # for i in range(3):
        #     print(detected_colors[i*3:i*3+3])
        # print()

        # Print detected colors as R U F
        #                          U F R
        #                          R F U
        for i in range(3):
            for j in range(3):
                color = detected_colors[i*3 + j]
                face_letter = color_name_to_face_letter[color]
                print(face_letter, end=' ')
            print()
        print()
        
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("s"):
            cv.imwrite("screenshot.png", grid_view)
            break
        
    video.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    run()
