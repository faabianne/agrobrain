#include <DHT.h>

#define DHTPIN 2      
#define DHTTYPE DHT22   
DHT dht(DHTPIN, DHTTYPE);

const int sueloPin = A0;      // Analógico A0: Humedad de suelo
const int ldrPin = 4;         // Digital D4: Módulo LDR (Salida DO)
const int boyaPin = 6;        // Digital D7: Simulador manual de nivel de agua (Jumper)

const int ledVerdePin = 8;    // Digital D8: LED Verde (Tanque Suficiente)
const int ledRojoPin = 9;     // Digital D9: LED Rojo (Alerta / Tanque Bajo)

// Calibración del sensor de suelo
const int valorAire = 1023;  
const int valorAgua = 400;   

float ultimaHumedadAmb = 0.0;
float ultimaTemp = 0.0;

void setup() {
  Serial.begin(9600);
  delay(2000);
  
  dht.begin();
  pinMode(boyaPin, INPUT_PULLUP);
  pinMode(ldrPin, INPUT); // Configuramos D4 como entrada digital
  
  pinMode(ledVerdePin, OUTPUT);
  pinMode(ledRojoPin, OUTPUT);
  
  Serial.println(">>> AgroBrain MVP: LDR Digital en Pin D4 Activo <<<");
}

void loop() {
  delay(2000); 

  // 1. Lectura de Suelo (Oversampling)
  long sumaLecturasSuelo = 0;
  for(int i = 0; i < 10; i++) {
    sumaLecturasSuelo += analogRead(sueloPin);
    delay(5); 
  }
  int valorBrutoSuelo = sumaLecturasSuelo / 10; 
  int porcentajeSuelo = map(valorBrutoSuelo, valorAire, valorAgua, 0, 100);
  porcentajeSuelo = constrain(porcentajeSuelo, 0, 100);

  // 2. Lectura del DHT22
  float humedadAmbiente = dht.readHumidity();
  float temperatura = dht.readTemperature();
  if (!isnan(humedadAmbiente) && !isnan(temperatura)) {
    ultimaHumedadAmb = humedadAmbiente;
    ultimaTemp = temperatura;
  } 

  // 3. LECTURA DIGITAL DE LUZ (Pin D4)
  int estadoLuz = digitalRead(ldrPin); 
  // Si estadoLuz es HIGH (1) interpretamos oscuridad (20%), si es LOW (0) hay luz (80%)
  // (Nota: Si notas que el comportamiento es al revés, solo invierte los valores)
  int porcentajeLuz = (estadoLuz == HIGH) ? 20 : 80;

  // 4. Lectura de Boya y LEDs
  int estadoBoya = digitalRead(boyaPin);
  int nivelAguaValido = (estadoBoya == LOW) ? 1 : 0;  

  if (nivelAguaValido == 1) {
    digitalWrite(ledVerdePin, HIGH); 
    digitalWrite(ledRojoPin, LOW);   
  } else {
    digitalWrite(ledVerdePin, LOW);  
    digitalWrite(ledRojoPin, HIGH);   
  }

  // 5. Salida de Telemetría
  Serial.println("----------------------------------------");
  Serial.print("Ambiente -> Humedad: ");
  Serial.print(ultimaHumedadAmb, 1);
  Serial.print("%  |  Temperatura: ");
  Serial.print(ultimaTemp, 1);
  Serial.println("°C");
  
  Serial.print("Suelo    -> Humedad: ");
  Serial.print(porcentajeSuelo);
  Serial.println("%");

  Serial.print("Luz      -> Estado D4: ");
  Serial.print(estadoLuz);
  Serial.print(" | Intensidad: ");
  Serial.print(porcentajeLuz);
  Serial.println("%");

  Serial.print("Tanque   -> Estado: ");
  Serial.println(nivelAguaValido == 1 ? "SUFICIENTE (Verde)" : "BAJO / ALERTA (Rojo)");
  Serial.println("----------------------------------------");
}
