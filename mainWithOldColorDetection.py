from ursina import *
import numpy as np
import cv2 as cv
import kociemba

video = cv.VideoCapture("test.mp4") # 0 is the default camera, "video.mp4" is the video file


cube_color_faces_map = []
cube_string_faces_map = []

class MainPage(Entity):
    def __init__(self):
        super().__init__()

        # Funzione per calcolare la distanza tra due colori RGB
        def distanza_rgb(color1, color2):
            r1, g1, b1 = color1
            r2, g2, b2 = color2
            return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

        def get_dom_color(m):
            # Lista dei colori con le loro medie RGB
            colors = {
                'rosso': (219, 22, 29),
                'verde': (0, 171, 50),
                'blu': (0, 33, 113),
                'giallo': (220, 232, 34),
                'bianco': (187, 187, 187),
                'arancione': (238, 100, 24)
            }

            # Inizializza la distanza minima e il colore corrispondente
            distanza_minima = float('inf')
            colore_corrispondente = None

            # Trova il colore più simile
            for nome_colore, colore in colors.items():
                distanza = distanza_rgb(m, colore)
                if distanza < distanza_minima:
                    distanza_minima = distanza
                    colore_corrispondente = nome_colore
            return colore_corrispondente

        def draw_framing_roi(copy):
            rectangle_width = 200
            rectangle_height = rectangle_width
            costant = 50
            rectangle_color = (0, 255, 0)
            fwidth, fheight = int(video.get(3)/2), int(video.get(4)/2)

            top_left = int(fwidth/2 - rectangle_width/2), int(fheight/2 - rectangle_height/2) + 15
            top_right = int(fwidth/2 + rectangle_width/2), int(fheight/2 - rectangle_height/2) + 15
            bottom_left = int(fwidth/2 - rectangle_width/2), int(fheight/2 + rectangle_height/2) + 15
            bottom_right = int(fwidth/2 + rectangle_width/2), int(fheight/2 + rectangle_height/2) + 15

            # TOP LEFT CORNER
            cv.line(copy, (top_left), (top_left[0] + costant, top_left[1]), rectangle_color, 2)
            cv.line(copy, (top_left), (top_left[0], top_left[1] + costant), rectangle_color, 2)

            # TOP RIGHT CORNER
            cv.line(copy, (top_right[0] - costant, top_right[1]), (top_right), rectangle_color, 2)
            cv.line(copy, (top_right[0], top_right[1] + costant), (top_right), rectangle_color, 2)
            
            # BOTTOM LEFT CORNER
            cv.line(copy, (bottom_left), (bottom_left[0] + costant, bottom_left[1]), rectangle_color, 2)
            cv.line(copy, (bottom_left), (bottom_left[0], bottom_left[1] - costant), rectangle_color, 2)
            
            # BOTTOM RIGHT CORNER
            cv.line(copy, (bottom_right[0] - costant, bottom_right[1]), (bottom_right), rectangle_color, 2)
            cv.line(copy, (bottom_right[0], bottom_right[1] - costant), (bottom_right), rectangle_color, 2)

            # cv.rectangle(copy, (top_left[0] - 10, top_left[1] - 10), (bottom_right[0] + 10, bottom_right[1] + 10), (255, 0 ,0), 2)

            return top_left, bottom_right
                
        def draw_mask_on_roi(copy2, top_left, bottom_right):
            mask = cv.imread('mask.png', cv.IMREAD_UNCHANGED)  # IMREAD_UNCHANGED => open image with the alpha channel

            # separate the alpha channel from the color channels
            alpha_channel = mask[:, :, 3] / 255 # convert from 0-255 to 0.0-1.0

            alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

            background_subsection = copy2[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

            # combine the background with the overlay image weighted by alpha
            composite = background_subsection * (1 - alpha_mask)

            # overwrite the section of the background image that has been updated
            copy2[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = composite
            
            return background_subsection

        def draw_roi_cells(roi):
            cells = {}
            gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
            contours, _ = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
            for (i, c) in enumerate(contours):
                if len(contours) == 9:
                    area = cv.contourArea(c)
                    if area > 1500:
                        peri = cv.arcLength(c, True)
                        approx = cv.approxPolyDP(c, 0.02 * peri, True)
                        if len(approx) == 4:
                            cv.drawContours(roi, c, -1, (255, 255, 255), 2)
                            x, y, w, h = cv.boundingRect(approx)
                            cells[f"X{len(contours) - i}"] = (x, y, w, h)
            
            cls = ""
            arr = []
            for k, v in cells.items():
                x, y, w, h = v
                cv.putText(roi, k, (int(x+w/2-20), int(y+h/2+10)), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
                rois = cv.cvtColor(roi.copy(), cv.COLOR_BGR2RGB)[y:y+h, x:x+w]

                cd = get_dom_color(np.mean(rois, axis=(0, 1)).astype(int))
                
                cls += cd
                arr.append(cd)

                print(f"{k}: {cd}")
                if k == "X1":
                    print("\n")
            if cube_string_faces_map.count(cls) < 5:
                cube_string_faces_map.append(cls)
                cube_color_faces_map.append(arr)
            
        def mapp_cube():
            is_mapped = False
            scramble = ""
            while True:
                ret, frame = video.read()
                if not ret:
                    break
                
                frame = cv.resize(frame, (int(video.get(3)/2), int(video.get(4)/2)))
                copy = frame.copy()

                TL, BR = draw_framing_roi(copy)
                copy2 = copy.copy()

                roi = draw_mask_on_roi(copy2, TL, BR)

                draw_roi_cells(roi)

                print(cube_string_faces_map)
                temp = list(set([i for i in cube_string_faces_map if cube_string_faces_map.count(i) > 3]))
                print(temp)
                print("\n\n\n\n")
                if len(temp) == 6:
                    is_mapped = True
                    tmp = {
                        "U": "",
                        "R": "",
                        "F": "",
                        "D": "",
                        "L": "",
                        "B": ""
                    }
                    for face in temp:
                        face = face.replace("giallo", "U").replace("rosso", "R").replace("blu", "F").replace("bianco", "D").replace("arancione", "L").replace("verde", "B")
                        faceTMP = [f for f in face]
                        tmp[faceTMP[4]] = face
                    
                    scramble = tmp["U"] + tmp["R"] + tmp["F"] + tmp["D"] + tmp["L"] + tmp["B"]


                cv.imshow("Video", np.hstack([frame, copy, copy2]))

                if cv.waitKey(1) & 0xFF == ord("q") or is_mapped:
                    break
            
            video.release()
            cv.destroyAllWindows()

            print(scramble)
            print(list(set([c for c in scramble if scramble.count(c) == 9])))
            print(cube_color_faces_map)
            if len(list(set([c for c in scramble if scramble.count(c) == 9]))) == 6:
                return scramble
            else:
                return None       

        def solve_rubiks_cube(scrambled_cube):
            
            # Scramble the Rubik's Cube
            # The following string represents the state of the Rubik's Cube after it has been scrambled
            # The string is a sequence of 54 characters, each representing the color of a facelet on the Rubik's Cube
            # The 54 characters are arranged in the following order:
            # - The first 9 characters represent the facelets on the upper face (U) of the Rubik's Cube
            # - The next 9 characters represent the facelets on the right face (R) of the Rubik's Cube
            # - The next 9 characters represent the facelets on the front face (F) of the Rubik's Cube
            # - The next 9 characters represent the facelets on the down face (D) of the Rubik's Cube
            # - The next 9 characters represent the facelets on the left face (L) of the Rubik's Cube
            # - The last 9 characters represent the facelets on the back face (B) of the Rubik's Cube
            # From top left to bottom right
            # For example the string: UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB represent a solved Rubik's Cube
            #
            #       | UUU |
            #       | UUU |
            #       | UUU |
            # | LLL | FFF | RRR | BBB |
            # | LLL | FFF | RRR | BBB |
            # | LLL | FFF | RRR | BBB |
            #       | DDD |
            #       | DDD |
            #       | DDD |
            # 
            
            # Solve the Rubik's Cube
            solution = kociemba.solve(scrambled_cube)
            print(solution)
            return solution

        def test(s):
            scramble = "LURRUFFUBURFDRDRBDDLLDFLLFBDLUFDUFLBUBLFLRRUBDRFBBDRBU"
            if s == scramble:
                print("Scramble is correct")
                return True
            else:
                print("Scramble is NOT correct")
                return True
            
        s = mapp_cube()
        if s is not None and test(s): solution = solve_rubiks_cube(s) 
        # if test(s): solution = solve_rubiks_cube(s)
        self.go_to_second_page(solution)
    
    def go_to_second_page(self, solution: str):
        destroy(self)
        from solver import SecondPage
        SecondPage(solution)

if __name__ == "__main__":
    app = Ursina()
    MainPage()
    app.run()
