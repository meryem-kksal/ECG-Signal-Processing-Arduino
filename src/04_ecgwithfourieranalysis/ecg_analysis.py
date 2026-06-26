import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import time

# --- MİMARİ AYARLARI (Sistem Mimarı Burayı Kendi Sistemine Göre Değiştirir) ---
PORT = 'COM9'      # Arduino'nun bağlı olduğu port (Aygıt Yöneticisinden veya IDE'den bakıp değiştir)
BAUD_RATE = 115200 # Arduino Serial.begin değeri ile aynı olmalı
ORNEKLEME_SAYISI = 500 # Kaç veri toplayıp analiz edeceğiz?

def veri_topla(port, baud, max_veri):
    raw_veriler = []
    clean_veriler = []
    
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"{port} portundan veri dinleniyor... {max_veri} adet veri toplanacak. Kalp atışını sabit tut.")
        time.sleep(2) # Sensörün ve Arduino'nun oturması için bekleme
        
        # --- FREKANS HESAPLAMA İÇİN KRONOMETREYİ BAŞLAT ---
        start_time = time.time() 
        
        while len(raw_veriler) < max_veri:
            if ser.in_waiting > 0:
                satir = ser.readline().decode('utf-8', errors='ignore').strip()
                # MİMARİ NOT: Arduino'dan "RawDeğer,CleanDeğer" şeklinde (virgülle ayrılmış) veri bekliyoruz
                try:
                    degerler = satir.split(',')
                    if len(degerler) == 2:
                        raw = float(degerler[0])
                        clean = float(degerler[1])
                        raw_veriler.append(raw)
                        clean_veriler.append(clean)
                except ValueError:
                    pass # Gürültülü/Bozuk karakter gelirse atla
                    
        # --- KRONOMETREYİ DURDUR VE FREKANSI HESAPLA ---
        end_time = time.time() 
        ser.close()
        
        gecen_sure = end_time - start_time
        gercek_fs = max_veri / gecen_sure # Frekans = Toplam Veri / Toplam Saniye
        
        print("-" * 50)
        print(f"SİSTEM MİMARI RAPORU:")
        print(f"Veri toplama {gecen_sure:.2f} saniye sürdü.")
        print(f"Gerçek Örnekleme Frekansınız (fs): {gercek_fs:.2f} Hz")
        print("-" * 50)
        
        print("Matematiğe (Fourier'e) geçiliyor...")
        return np.array(raw_veriler), np.array(clean_veriler), gercek_fs
        
    except Exception as e:
        print(f"Seri port hatası: {e}. Portun kapalı olduğuna ve IDE Serial Monitor'ün kapalı olduğuna emin ol.")
        return None, None, None

def fourier_analizi_ciz(raw_sinyal, clean_sinyal, fs):
    N = len(raw_sinyal)
    T = 1.0 / fs
    zaman = np.linspace(0.0, N*T, N, endpoint=False)
    
    # --- DİJİTAL SİNYAL İŞLEME (DSP) - FOURIER DÖNÜŞÜMLERİ ---
    
    # Raw sinyal için Fourier
    raw_fft = fft(raw_sinyal)
    raw_frekanslar = fftfreq(N, T)[:N//2]
    raw_genlikler = 2.0/N * np.abs(raw_fft[0:N//2])
    
    # Clean (Circular Buffer'lı) sinyal için Fourier
    clean_fft = fft(clean_sinyal)
    clean_frekanslar = fftfreq(N, T)[:N//2]
    clean_genlikler = 2.0/N * np.abs(clean_fft[0:N//2])
    
    # DC Bileşenini (0 Hz - Sürekli Akım) filtrele ki grafiğin boyutunu bozmasın
    raw_genlikler[0] = 0
    clean_genlikler[0] = 0

    # --- SİNYAL MİMARİSİNİ GÖRSELLEŞTİRME ---
    fig, axs = plt.subplots(2, 2, figsize=(14, 8))
    fig.canvas.manager.set_window_title('AD8232 Biyomedikal Sinyal ve Spektrum Analizi')
    
    # 1. Ham Sinyal (Zaman Düzlemi - Osiloskop Görünümü)
    axs[0, 0].plot(zaman, raw_sinyal, color='red')
    axs[0, 0].set_title('Ham (Raw) Sinyal - Zaman Düzlemi')
    axs[0, 0].set_ylabel('Genlik (ADC Değeri)')
    axs[0, 0].grid(True)
    
    # 2. Ham Sinyal (Frekans Düzlemi - Fourier Spektrumu)
    axs[0, 1].plot(raw_frekanslar, raw_genlikler, color='darkred')
    axs[0, 1].set_title('Ham Sinyal İçindeki Frekanslar (Spektrum)')
    axs[0, 1].set_xlim(0, 50) # İnsan vücudu için 0-50Hz arasına bakmak yeterlidir
    axs[0, 1].set_ylabel('Sinyal Gücü')
    axs[0, 1].grid(True)
    
    # 3. Temiz Sinyal (Zaman Düzlemi)
    axs[1, 0].plot(zaman, clean_sinyal, color='blue')
    axs[1, 0].set_title(f'Temizlenmiş (Clean) Sinyal - {N} Örneklem')
    axs[1, 0].set_xlabel('Zaman (saniye)')
    axs[1, 0].set_ylabel('Genlik (ADC Değeri)')
    axs[1, 0].grid(True)
    
    # 4. Temiz Sinyal (Frekans Düzlemi)
    axs[1, 1].plot(clean_frekanslar, clean_genlikler, color='darkblue')
    axs[1, 1].set_title('Circular Buffer Sonrası Kalan Frekanslar')
    axs[1, 1].set_xlim(0, 50)
    axs[1, 1].set_xlabel('Frekans (Hz)')
    axs[1, 1].set_ylabel('Sinyal Gücü')
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plt.show()

# --- SİSTEMİ ÇALIŞTIR ---
if __name__ == '__main__':
    print("Sistem Mimarı Modu: Başlatılıyor...")
    # 1. Veri Toplama Aşaması (Python hızı kendi ölçecek)
    r_data, c_data, hesaplanan_fs = veri_topla(PORT, BAUD_RATE, ORNEKLEME_SAYISI)
    
    # 2. Veri İşleme Aşaması
    if r_data is not None and hesaplanan_fs is not None:
        fourier_analizi_ciz(r_data, c_data, hesaplanan_fs)
