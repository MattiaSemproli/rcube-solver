import cv2
import mediapipe as mp

# Inizializza Mediapipe Hands e Drawing
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Apri la videocamera
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=2,  # Numero massimo di mani da rilevare
    min_detection_confidence=0.7,  # Confidenza minima per la rilevazione
    min_tracking_confidence=0.7  # Confidenza minima per il tracciamento
) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Non riesco a leggere il flusso video")
            continue

        # Capovolgi l'immagine orizzontalmente per una visualizzazione in stile selfie
        image = cv2.flip(image, 1)
        
        # Converti l'immagine in RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Processa l'immagine per trovare le mani
        results = hands.process(image_rgb)
        
        # Disegna i risultati delle mani
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Mostra l'immagine con i risultati
        cv2.imshow('Hand Tracking', image)

        if cv2.waitKey(5) & 0xFF == 27:  # Premi ESC per uscire
            break

cap.release()
cv2.destroyAllWindows()
