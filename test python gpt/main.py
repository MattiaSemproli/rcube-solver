import cv2
import numpy as np
import kociemba

# Definizione dei colori standard del cubo di Rubik in formato HSV
color_ranges = {
    'white': ((0, 0, 200), (180, 20, 255)),
    'red': ((0, 100, 100), (10, 255, 255)),
    'orange': ((10, 100, 100), (25, 255, 255)),
    'yellow': ((20, 100, 100), (30, 255, 255)),
    'green': ((50, 100, 100), (70, 255, 255)),
    'blue': ((100, 100, 100), (130, 255, 255)),
}

# Mappatura dei colori sui lati del cubo di Rubik
color_map = {
    'white': 'U', 'red': 'R', 'orange': 'L',
    'yellow': 'D', 'green': 'F', 'blue': 'B'
}

# Funzione per trovare il colore in base ai range HSV
def detect_color(hsv_pixel):
    for color, (lower, upper) in color_ranges.items():
        lower = np.array(lower)
        upper = np.array(upper)
        if cv2.inRange(hsv_pixel, lower, upper):
            return color
    return None

# Funzione per rilevare i colori della faccia del cubo
def detect_face(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    face_colors = []

    # Definire le posizioni delle 9 caselle sul cubo di Rubik
    positions = [(x, y) for y in range(1, 4) for x in range(1, 4)]
    
    for pos in positions:
        x, y = pos
        # Adatta queste coordinate in base alla dimensione del frame e della regione
        region = hsv_frame[(y-1)*100:y*100, (x-1)*100:x*100]
        avg_color = np.mean(region, axis=(0, 1))
        color_name = detect_color(np.uint8([[avg_color]]))
        if color_name:
            face_colors.append(color_map[color_name])
            # Disegna un rettangolo attorno alla casella con il colore rilevato
            cv2.rectangle(frame, ((x-1)*100, (y-1)*100), (x*100, y*100), (255, 255, 255), 2)
            cv2.putText(frame, color_name, ((x-1)*100 + 20, (y-1)*100 + 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    # Stampa i colori rilevati per debug
    print(f'Colors detected: {face_colors}')
    
    return face_colors

# Acquisizione video e rilevamento
cap = cv2.VideoCapture(1)
faces = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('Rubik\'s Cube Detector', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key in [ord('u'), ord('d'), ord('f'), ord('b'), ord('l'), ord('r')]:
        face_key = chr(key).upper()
        face_colors = detect_face(frame)
        if len(face_colors) == 9:
            faces[face_key] = ''.join(face_colors)
            print(f'{face_key} face detected: {faces[face_key]}')

        # Visualizzazione dei rettangoli con i colori rilevati
        cv2.imshow('Detected Colors', frame)

cap.release()
cv2.destroyAllWindows()

# Costruzione della stringa per il solver
if len(faces) == 6:
    cube_state = ''.join([faces[face] for face in 'URFDLB'])
    solution = kociemba.solve(cube_state)
    print(f'Solution: {solution}')
else:
    print('Please scan all faces of the cube.')
