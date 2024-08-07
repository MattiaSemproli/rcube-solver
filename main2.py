import cv2 as cv
import numpy as np

# if you want to use the default camera, use 1, if you want to use a video file, use the file name
# comment out the one you don't want to use
# video = cv.VideoCapture("test.mp4")
video = cv.VideoCapture(1)

def run():
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        copy = frame.copy()

        # Get the dimensions of the frame
        height, width, _ = frame.shape
        
        # Define the size of the square that would have contained the 3x3 grid (e.g., 300x300 pixels)
        square_size = 300
        
        # Calculate the size of each cell in the 3x3 grid
        cell_size = square_size // 3
        
        # Create an empty image for the 3x3 grid view
        grid_view = np.zeros((square_size, square_size, 3), dtype=np.uint8)
        
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
                
                # Resize the ROI to fit the grid cell size
                resized_roi = cv.resize(roi, (cell_size, cell_size))
                
                # Place the resized ROI into the correct position in the grid view
                grid_view[i*cell_size:(i+1)*cell_size, j*cell_size:(j+1)*cell_size] = resized_roi
        
        # Display the original frame with the smaller squares
        cv.imshow("frame", frame)
        
        # Display the 3x3 grid view in a new window
        cv.imshow("3x3 Grid View", grid_view)
        
        
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
