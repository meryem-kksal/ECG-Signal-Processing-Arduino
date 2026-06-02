# ECG-Signal-Processing-Arduino
# Gerçek Zamanlı EKG Sinyal İşleme ve Nabız (BPM) Ölçüm Sistemi

Bu proje, AD8232 Biyopotansiyel Sensörü ve Arduino kullanılarak insan vücudundan alınan analog EKG (Elektrokardiyografi) sinyallerinin donanımsal ve yazılımsal olarak filtrelenmesi, gürültüden arındırılması ve gerçek zamanlı nabız (BPM) hesabı yapılması amacıyla geliştirilmiş bir gömülü sistem uygulamasıdır.

## 🚀 Proje Özeti ve Mühendislik Yaklaşımı

Biyolojik sinyaller (mV seviyesinde) yüksek oranda şebeke gürültüsü (50Hz) ve kas (EMG) paraziti içerir. Bu projede:
1. **Donanımsal Filtreleme:** AD8232 içindeki enstrümantasyon amplifikatörü (Op-Amp) ile sinyal yükseltilmiş ve CMRR (Ortak Mod Reddetme Oranı) ile ana gürültüler bastırılmıştır.
2. **Yazılımsal Filtreleme (DSP):** ADC (Analog-Digital Converter) üzerinden okunan ham sinyal, **Dairesel Tampon (Circular Buffer)** algoritması kullanılarak "Hareketli Ortalama (Moving Average)" filtresinden geçirilmiş, anlık mikro sıçramalar ve ADC kararsızlıkları dijital olarak sönümlenmiştir.
3. **BPM Algoritması:** Filtrelenmiş sinyal üzerinden R-Tepesi (R-Peak) tespiti yapılmış, ardışık iki tepe arasındaki süre (RR Interval) `millis()` fonksiyonu ile ölçülerek dakikadaki kalp atış hızı hesaplanmıştır. Çift tetiklemeyi (Double-triggering) önlemek için yazılımsal "Debounce" (refrakter periyot) süresi eklenmiştir.

## 📂 Klasör Yapısı (Repository Structure)

Bu repo, gelişmişlik düzeyine göre iki farklı kod dosyası içerir:

* **`src/01_Basic_ECG_Filter/`** : Sensörden gelen ham analog veriyi okuyan, pedlerin koptuğunu (Leads-off) denetleyen ve hareketli ortalama filtresi ile sinyali pürüzsüzleştiren temel kod. (Serial Plotter ile dalga izlemek için idealdir).
* **`src/02_ECG_BPM_Calculator/`** : Filtrelenmiş sinyal üzerinden tepe noktalarını yakalayarak gerçek zamanlı BPM hesaplayan gelişmiş kod.

## ⚙️ Donanım Kurulumu (Pinout)

Sistemin donanım bağlantıları aşağıdaki gibidir:

| AD8232 Pini | Arduino Pini | İşlev |
| :--- | :--- | :--- |
| **GND** | GND | Toprak (Referans) |
| **3.3V** | 3.3V | Güç Beslemesi *(DİKKAT: 5V KULLANILMAMALIDIR)* |
| **OUTPUT** | A0 | Analog EKG Sinyal Çıkışı |
| **LO-** | D12 | Ped Kopma Sensörü (Negatif) |
| **LO+** | D13 | Ped Kopma Sensörü (Pozitif) |
| **SDN** | Boş (veya 3.3V) | Uyku Modu (Aktif Düşük) |

> **⚠️ Güvenlik Uyarısı:** Biyolojik sinyal okumaları sırasında bilgisayarınızın şarj adaptörünün prize takılı olmamasına (sadece batarya ile çalışmasına) özen gösterin. Bu hem şebeke gürültüsünü engeller hem de elektriksel güvenliği (Galvanik izolasyon) sağlar.

## 📊 Örnek Çıktı
`![EKG Dalgaları](docs/serial_plotter_result.png/ECG.21)
