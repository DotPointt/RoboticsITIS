import cv2
import numpy as np

def process_frame(frame, color_lower, color_upper):
    # Преобразование кадра в цветовое пространство HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Создание маски для заданного диапазона цветов
    mask = cv2.inRange(hsv, color_lower, color_upper)

    # Улучшение маски (фильтрация шумов)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Поиск контуров
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Обработка контуров
    if contours:
        # Нахождение наибольшего контура (предполагаем, что это мяч)
        largest_contour = max(contours, key=cv2.contourArea)

        # Вычисление центра масс
        moments = cv2.moments(largest_contour)
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])

            # Отображение центра масс и координат
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"{cx}, {cy}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Отображение контура
        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Object not found", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return frame

# Настройка диапазона цветов для мяча (например, оранжевый)
ball_color_lower = np.array([20, 100, 100])  # Нижняя граница HSV
ball_color_upper = np.array([40, 255, 255])  # Верхняя граница HSV

# Обработка видеофайла "catball.mp4"
video_path = "catball.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Ошибка открытия видеофайла")
    exit()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Обработка кадра
    processed_frame = process_frame(frame, ball_color_lower, ball_color_upper)

    # Отображение результата
    cv2.imshow("Processed Video", processed_frame)

    # Выход по клавише 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()