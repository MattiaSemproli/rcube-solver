
# rcube-solver

`rcube-solver` is an auto-solver application for a Rubik's cube. It maps the starting pattern from the camera and provides a solution.

## Installation

To install the necessary dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Camera Initialization:**
   The application initializes the video capture from the default camera. Ensure your camera is working correctly.

3. **Color Detection:**
   The application detects the colors on the Rubik's cube faces and maps them to the corresponding positions.

4. **Solving the Cube:**
   The detected pattern is fed to the solver, which provides the sequence of moves to solve the Rubik's cube.

## Project Structure

- `main.py`: Contains the main logic for capturing the video feed, detecting colors, and interfacing with the solver.
- `solver.py`: Contains the logic for solving the Rubik's cube using the Kociemba algorithm and the Ursina game engine for visualization.

## Key Components

### main.py

- **Color Detection:**
  Uses OpenCV to capture the video feed and detect the colors on the Rubik's cube faces. It uses HSV color space for more accurate detection under different lighting conditions.

- **Face Mapping:**
  Maps the detected colors to their respective positions on the cube.

- **Kociemba Solver:**
  Uses the Kociemba algorithm to determine the optimal sequence of moves to solve the cube.

### solver.py

- **Visualization:**
  Uses the Ursina engine to visualize the cube.

- **Ursina Integration:**
  Integrates with the Ursina engine to provide a visual representation of the cube and its solution process.

## How It Works

1. **Initialization:**
   The application initializes the camera and prepares for color detection.

2. **Color Detection:**
   Detects the colors on the cube faces using predefined HSV color ranges.

3. **Pattern Mapping:**
   Maps the detected colors to their respective faces and positions.

4. **Solving:**
   Uses the Kociemba algorithm to find the solution and visualizes the moves using Ursina.

## Troubleshooting

- **Camera Issues:**
  Ensure your camera is connected and working properly. You may need to adjust the camera index in the `cv.VideoCapture` call if you have multiple cameras.

- **Color Detection:**
  Lighting conditions can affect color detection. Ensure you have consistent lighting for better accuracy.

- **Dependencies:**
  Ensure all dependencies are installed correctly. Refer to the `requirements.txt` for the necessary packages.

## Contributing

Contributions are welcome! Please create an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.