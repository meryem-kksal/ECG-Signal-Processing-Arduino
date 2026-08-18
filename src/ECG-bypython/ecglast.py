import sys
import serial
import threading
import collections
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from scipy.signal import butter, lfilter, filtfilt

# === KULLANICI AYARLARI ===
PORT = 'COM9'         # Arduino'nun bağlı olduğu port
BAUD_RATE = 9600      # Arduino kodundaki Serial.begin hızı
FS = 100.0            # Örnekleme frekansı (delay(10) -> ~100 Hz)
PENCERE_SURESI = 5.0  # Ekranda kaç saniyelik veri gösterilsin?
# ==========================

# Ekranda tutulacak toplam örnek sayısı
WINDOW_SIZE = int(FS * PENCERE_SURESI)

# Verileri tutacağımız global hafıza (Thread-safe dairesel tampon)
# maxlen sayesinde dolduğunda otomatik olarak en eskileri siler
veri_tamponu = collections.deque(maxlen=WINDOW_SIZE)

def seri_port_oku():
    """Arka planda Arduino'dan sürekli veri okuyan fonksiyon (Arayüzü dondurmamak için)"""
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        print(f"{PORT} portuna bağlanıldı. Veriler alınıyor...")
        
        while True:
            satir = ser.readline().decode('utf-8', errors='ignore').strip()
            if satir:
                try:
                    # Arduino'dan "ham,ema" gibi virgüllü gelebilir, 
                    # biz ilk kısmı (ham değeri) alıyoruz
                    parcalar = satir.split(',')
                    ham_deger = float(parcalar[0])
                    veri_tamponu.append(ham_deger)
                except ValueError:
                    pass
    except Exception as e:
        print(f"Seri port hatası: {e}")
        print("Lütfen Arduino IDE'deki Seri Port Ekranı/Çizicisinin KAPALI olduğundan emin olun!")

app = QtWidgets.QApplication(sys.argv)

# Ana pencereyi oluştur
win = pg.GraphicsLayoutWidget(show=True, title="Canlı EKG Monitörü")
win.resize(1200, 800)
win.setBackground('w') # Beyaz arka plan

# 1. Ham Sinyal Grafiği
p1 = win.addPlot(title="1. Ham Sinyal (Zaman Alanı)")
p1.showGrid(x=True, y=True)
p1.setLabel('left', 'Voltaj', units='0-1023')
curve_raw = p1.plot(pen=pg.mkPen(color='#aaaaaa', width=1.5)) # Gri renk

win.nextRow() # Alt satıra geç

# 2. EMA Filtreli Sinyal
p2 = win.addPlot(title="2. EMA Filtresi (Yumuşatılmış)")
p2.showGrid(x=True, y=True)
curve_ema = p2.plot(pen=pg.mkPen(color='#ffa500', width=1.5)) # Turuncu

win.nextRow()

# 3. Band-Pass Filtreli (0.5 - 15Hz)
p3 = win.addPlot(title="3. Band-Pass Filtresi (0.5 Hz - 15 Hz) -> ASIL EKG!")
p3.showGrid(x=True, y=True)
curve_bp = p3.plot(pen=pg.mkPen(color='#ff0000', width=2.0)) # Kırmızı

win.nextRow()

# 4. FFT Frekans Spektrumu
p4 = win.addPlot(title="4. FFT Frekans Analizi")
p4.showGrid(x=True, y=True)
p4.setLabel('bottom', 'Frekans', units='Hz')
p4.setXRange(0, 50) # Sadece 0-50 Hz arasını göster
curve_fft_raw = p4.plot(pen=pg.mkPen(color='#dddddd', width=1)) # Orijinal (Gri)
curve_fft_bp = p4.plot(pen=pg.mkPen(color='#0000ff', width=1.5))  # Filtreli (Mavi)

def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    # Canlı sistemlerde filtfilt yerine lfilter veya sinyalin boyutuna göre korumalı filtfilt
    try:
        y = filtfilt(b, a, data)
    except:
        y = np.zeros_like(data)
    return y

def guncelle():
    # Yeterli veri birikene kadar (5 saniye) bekle
    if len(veri_tamponu) < WINDOW_SIZE:
        return
        
    # Thread-safe kopyalama
    raw_data = np.array(veri_tamponu)
    zaman_ekseni = np.linspace(0, PENCERE_SURESI, len(raw_data))
    
    # --- 1. EMA Filtresi ---
    alpha = 0.15
    # Scipy lfilter kullanarak EMA'yı tüm diziye anında uygularız
    ema_data = lfilter([alpha], [1, -(1-alpha)], raw_data)
    
    # --- 2. Band-Pass Filtresi ---
    bp_data = butter_bandpass_filter(raw_data, 0.5, 15.0, FS, order=3)
    
    # --- 3. FFT Hesaplama ---
    # DC ofsetini sıfırlamak için ortalamayı çıkarıyoruz
    fft_raw = np.abs(np.fft.rfft(raw_data - np.mean(raw_data)))
    fft_bp = np.abs(np.fft.rfft(bp_data - np.mean(bp_data)))
    frekanslar = np.fft.rfftfreq(len(raw_data), 1/FS)
    
    # --- GRAFİKLERİ GÜNCELLE ---
    curve_raw.setData(zaman_ekseni, raw_data)
    curve_ema.setData(zaman_ekseni, ema_data)
    curve_bp.setData(zaman_ekseni, bp_data)
    curve_fft_raw.setData(frekanslar, fft_raw)
    curve_fft_bp.setData(frekanslar, fft_bp)

timer = QtCore.QTimer()
timer.timeout.connect(guncelle)
timer.start(50) # Her 50 milisaniyede bir ekranı yenile (20 FPS)

if __name__ == '__main__':
    # Seri port okumayı arka planda başlat
    thread = threading.Thread(target=seri_port_oku, daemon=True)
    thread.start()
    
    # Arayüzü çalıştır
    sys.exit(app.exec_())