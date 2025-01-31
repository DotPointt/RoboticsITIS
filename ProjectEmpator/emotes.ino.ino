#include <Servo.h>

Servo myServo;  // Создаем объект для управления сервоприводом

const int servoPin = 3;  // Пин для подключения сервопривода
const int speakerPin = 5;  // Пин для подключения динамика

// Определение нот
#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523

// Веселая мелодия ("Crazy Frog")
int happyMelody[] = {
  NOTE_D4, NOTE_F4, NOTE_A4, NOTE_D4, NOTE_D4, 
  NOTE_G4, NOTE_A4, NOTE_D4, NOTE_A4, NOTE_D4,
  NOTE_D4, NOTE_F4, NOTE_A4, NOTE_D4, NOTE_D4, 
  NOTE_C5, NOTE_A4, NOTE_D4
};

int happyNoteDurations[] = {
  8, 8, 8, 8, 8, 
  8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 
  8, 8, 4
};

// Грустная мелодия ("Грустный вальс" Сибелиуса)
int sadMelody[] = {
  NOTE_G4, NOTE_C5, NOTE_C5, NOTE_AS4, NOTE_C5, NOTE_G4,
  NOTE_DS4, NOTE_F4, NOTE_G4, NOTE_C4, NOTE_DS4, NOTE_F4,
  NOTE_D4, NOTE_F4, NOTE_AS4, NOTE_GS4, NOTE_G4, NOTE_F4
};

int sadNoteDurations[] = {
  2, 4, 4, 4, 4, 2,
  2, 4, 4, 4, 4, 2,
  2, 4, 4, 4, 4, 2
};

void setup() {
  Serial.begin(9600);  // Инициализация Serial порта
  myServo.attach(servoPin);  // Подключаем сервопривод к пину
}

void loop() {
  if (Serial.available() > 0) {  // Если есть данные в Serial порте
    int command = Serial.parseInt();  // Читаем команду

    if (command == 1) {
      myServo.write(0);  // Устанавливаем сервопривод в 0 градусов
      playMelody(sadMelody, sadNoteDurations, 8);  // Проигрываем грустную мелодию
      Serial.println("Command executed: 1");
    } else if (command == 2) {
      myServo.write(180);  // Устанавливаем сервопривод в 180 градусов
      playMelody(happyMelody, happyNoteDurations, 8);  // Проигрываем веселую мелодию
      Serial.println("Command executed: 2");  // Отправляем подтверждение выполнения команды
    } else {
    Serial.println("Unknown command");
    }
  }
}

void playMelody(int melody[], int noteDurations[], int length) {
  for (int i = 0; i < length; i++) {
    int noteDuration = 1000 / noteDurations[i];
    tone(speakerPin, melody[i], noteDuration);
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(speakerPin);
  }
}
