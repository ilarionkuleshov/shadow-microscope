// Скетч для модуля ESP32-CAM

#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>


// Название WiFi сети и её пароль
const char *WIFI_SSID = "example-ssid";
const char *WIFI_PASS = "example-pass";

WebServer server(80);

static auto cam_res = esp32cam::Resolution::find(800, 600);


// Функция для захвата видеопотока mjpeg с камеры
void handle_mjpeg(){
	Serial.println("Stream begin");

	WiFiClient client = server.client();
	int result = esp32cam::Camera.streamMjpeg(client);

	if(result <= 0){
		Serial.println("Stream error");
		return;
	}

	Serial.println("Stream end");
}


// Функция для захвата кадра с камеры
void handle_jpg(){
	auto frame = esp32cam::capture();

	if(frame == nullptr){
		Serial.println("Capture error");
		server.send(503, "", "");
		return;
	}

	server.setContentLength(frame->size());
	server.send(200, "image/jpeg");

	WiFiClient client = server.client();
	frame->writeTo(client);

	Serial.println("Capture ok");
}


void setup(){
	Serial.begin(115200);
	Serial.println();

	{
		using namespace esp32cam;

		Config config;

		config.setPins(pins::AiThinker);
		config.setResolution(cam_res);
		config.setBufferCount(2);
		config.setJpeg(80);

		bool is_camera_ok = Camera.begin(config);

		if(is_camera_ok) Serial.println("Camera ok");
		else Serial.println("Camera error");
	}

	WiFi.persistent(false);
	WiFi.mode(WIFI_STA);
	WiFi.begin(WIFI_SSID, WIFI_PASS);

	while(WiFi.status() != WL_CONNECTED) delay(400);

	server.on("/cam.jpg", handle_jpg);
	server.on("/cam.mjpeg", handle_mjpeg);

	server.begin();

	Serial.print("http://");
	Serial.print(WiFi.localIP());
	Serial.println("/cam.mjpeg");

	Serial.print("http://");
	Serial.print(WiFi.localIP());
	Serial.println("/cam.jpg");
}


void loop(){
	server.handleClient();
}
