import numpy as np
import cv2
import serial
import serial.tools.list_ports
import time
import threading
from queue import Queue


# Функция для вычисления расстояния между двумя точками
def euclidean_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


smile_detected = False

# Функция для определения улыбки
def is_smiling(mouth_points):
    left_mouth_point = mouth_points[0]
    right_mouth_point = mouth_points[6]
    top_lip_center = mouth_points[3]
    bottom_lip_center = mouth_points[9]
    # Расчет соотношения высоты и ширины рта
    mouth_width = euclidean_distance(left_mouth_point, right_mouth_point)
    mouth_height = euclidean_distance(top_lip_center, bottom_lip_center)
    if mouth_width == 0:
        return False
    ratio = mouth_height / mouth_width
    # Если отношение больше определенного порога, считаем, что человек улыбается
    return ratio > 0.2


# Функция для выбора порта
def select_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("Нет доступных портов.")
        exit(1)
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")
    choice = int(input("Выберите номер порта: "))
    if 0 <= choice < len(ports):
        return ports[choice].device
    else:
        print("Неверный выбор.")
        exit(1)


# Функция для ожидания ответа от устройства
def wait_for_response(serial_device):
    response_buffer = ""
    while True:
        # Проверяем наличие данных в буфере
        if serial_device.in_waiting > 0:
            # Читаем данные из порта
            response_part = serial_device.read(serial_device.in_waiting).decode('utf-8')
            response_buffer += response_part
            print(
                f"Received raw: {repr(response_part)}")  # Отладочный вывод с использованием repr для видимости всех символов

            # Проверяем, есть ли в буфере завершающий символ новой строки
            if "\n" in response_buffer:
                # Разделяем буфер на полные сообщения и оставшийся буфер
                parts = response_buffer.split("\n")
                complete_response = parts[0]
                response_buffer = "\n".join(parts[1:])

                # Возвращаем первое полное сообщение
                return complete_response.strip()
        else:
            # Если нет данных, ждем немного перед следующей проверкой
            time.sleep(0.1)

# Функция для работы с последовательным портом в отдельном потоке
def serial_worker(command_queue, serial_device):
    while True:
        if smile_detected:
            command = "2\n"
        else:
            command = "1\n"
        try:
            serial_device.write(command.encode('utf-8'))
            print(f"Sent to Arduino: {command.strip()}")
            flag = False
            while not flag:
                response = wait_for_response(serial_device)
                if response in ["Command executed: 1", "Command executed: 2"]:
                    print(f"Response from Arduino: {response}")
                    flag = True
                elif response == "":
                    time.sleep(0.1)
                else:
                    print("Ошибка: Некорректный ответ от устройства")
                    print(response)
                    time.sleep(0.1)
            time.sleep(3)
        except serial.SerialException as e:
            print(f"Ошибка отправки данных: {e}")


# Выбор порта и установка соединения
port = select_serial_port()
baudrate = 9600
try:
    serialDevice = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Дайте время устройству на инициализацию
except serial.SerialException as e:
    print(f"Ошибка подключения к порту {port}: {e}")
    exit(1)

# Загрузка модели Haar Cascade для обнаружения лиц
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# Загрузка модели Haar Cascade для обнаружения улыбок
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

# Очередь для передачи команд в поток работы с последовательным портом
command_queue = Queue()

# Создание и запуск потока для работы с последовательным портом
serial_thread = threading.Thread(target=serial_worker, args=(command_queue, serialDevice), daemon=True)
serial_thread.start()


# Инициализация видеопотока с камеры
cap = cv2.VideoCapture(0)
# Переменные для расчета FPS
prev_time = 0
fps = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Преобразование кадра в градации серого
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Детекция лиц
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    # Переменные для проверки улыбки
    smile_detected = False
    for (x, y, w, h) in faces:
        # Рисуем прямоугольник вокруг лица
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # Область интереса (ROI) для глаз и улыбки
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        # Детекция улыбки
        smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.5, minNeighbors=20, minSize=(20, 20))
        if len(smiles) > 0:  # Если найдена улыбка
            smile_detected = True
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)
        else:
            smile_detected = False

    # Вывод сообщений в зависимости от переменной smile_detected
    if smile_detected:
        smile_text = "Smile)"
        color = (0, 255, 0)
        command = "2\n"
    else:
        smile_text = "no smile("
        color = (0, 0, 255)
        command = "1\n"

    # Добавляем команду в очередь для отправки через последовательный порт
    #command_queue.put(command)
    # Добавляем текст о наличии улыбки
    cv2.putText(frame, smile_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Расчет FPS
    current_time = time.time()
    time_diff = current_time - prev_time
    fps = 1 / time_diff if time_diff > 0 else 0
    prev_time = current_time
    # Отображение FPS
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Отображение кадра
    cv2.imshow('Face Detection', frame)
    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()
serialDevice.close()