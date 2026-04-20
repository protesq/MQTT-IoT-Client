# MQTT IoT Client

Python + Mosquitto tabanlı IoT cihaz yönetim sistemi.

## Yapı

```
mqttClient/
├── core/
│   ├── connect.py       # Broker config ve client factory
│   └── manager.py       # Cihaz listesi ve komut gönderme
├── device/
│   └── simulator.py     # IoT cihaz simülasyonu
├── ui/
│   ├── dashboard.py     # Ana yönetim paneli
│   └── tester.py        # Test paneli
├── mosquitto/
│   └── config/
│       └── mosquitto.conf
├── docker-compose.yml
├── run_dashboard.py
├── run_device.py
└── run_test.py
```

## Kurulum

### 1. Broker'ı başlat

```bash
docker-compose up -d
```

Mosquitto `localhost:1883` (MQTT) ve `localhost:9001` (WebSocket) üzerinde çalışır.

### 2. Bağımlılıkları yükle

```bash
pip install paho-mqtt
```

## Kullanım

### Ana panel

```bash
python run_dashboard.py
```

- Bağlan → cihazları listeler
- Cihaz seç → komut yaz → Gönder
- ACK gelince logda `[ACK]` görünür

### Cihaz simülasyonu

```bash
python run_device.py
```

Her çalıştırmada yeni UUID ile bağlanır, panelde otomatik görünür.

### Test paneli

```bash
python run_test.py
```

- Cihaz seç → mesaj sayısı gir → Test Gönder
- Gönderilen / ACK alınan karşılaştırması yapar

## MQTT Topic Yapısı

| Topic | Yön | Açıklama |
|---|---|---|
| `iot/discovery` | Cihaz → Broker | Cihaz online/offline durumu (retain) |
| `iot/{id}/cmd` | Panel → Cihaz | Komut gönderme |
| `iot/{id}/data` | Cihaz → Panel | ACK ve veri |
| `iot/{id}/status` | Broker → Panel | Will mesajı (cihaz düşünce offline) |

## QoS

Tüm mesajlar **QoS 1** ile gönderilir — broker teslimi garanti eder. Cihaz geçici offline olsa bile broker komutu tutar, cihaz bağlanınca iletir.
