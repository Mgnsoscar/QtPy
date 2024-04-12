#include "HX711.h"

#define DT_1  3
#define SCK_1 2

#define DT_2  5
#define SCK_2 4

#define DT_3  6
#define SCK_3 7

#define DT_4  9
#define SCK_4 8

HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;

float calibration_factors[] = {-205.0, -205.0, -205.0, -205.0};
long zero_factors[4];

void setup() {
  Serial.begin(2000000); // Increase baud rate for faster communication
  // No need to set Serial timeout for continuous reading

  scale1.begin(DT_1, SCK_1);
  scale2.begin(DT_2, SCK_2);
  scale3.begin(DT_3, SCK_3);
  scale4.begin(DT_4, SCK_4);

  scale1.set_scale(calibration_factors[0]);
  scale2.set_scale(calibration_factors[1]);
  scale3.set_scale(calibration_factors[2]);
  scale4.set_scale(calibration_factors[3]);

  scale1.tare();
  scale2.tare();
  scale3.tare();
  scale4.tare();

  zero_factors[0] = scale1.read_average();
  zero_factors[1] = scale2.read_average();
  zero_factors[2] = scale3.read_average();
  zero_factors[3] = scale4.read_average();
}

void loop() {

  // Create a string to hold the concatenated output
  String output = String((-scale1.get_units() + scale2.get_units())/2) + "," + String((-scale3.get_units()+scale4.get_units())/2);
  // Print the output
  Serial.println(output);

}
