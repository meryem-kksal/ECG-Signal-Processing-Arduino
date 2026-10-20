import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, ifft
import time

# --- MİMARİ AYARLARI ---
PORT = 'COM9'
BAUD_RATE = 115200
ORNEKLEME_SAYISI = 500

def veri_topla(port, baud, max_veri):
    raw_veriler = []
    clean_veriler = []
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"{port} dinleniyor... Lütfen hareket etmeyin.")
        time.sleep(2)
        
        start_time = time.time()
        while len(raw_veriler) < max_veri:
            if ser.in_waiting > 0:
                satir = ser.readline().decode('utf-8', errors='ignore').strip()
                try:
                    degerler = satir.split(',')
                    if len(degerler) == 2:
                        raw_veriler.append(float(degerler[0]))
                        clean_veriler.append(float(degerler[1]))
                except ValueError:
                    pass
                    
        end_time = time.time()
        ser.close()
        
        gercek_fs = max_veri / (end_time - start_time)
        print(f"Gerçek Örnekleme Frekansınız (fs): {gercek_fs:.2f} Hz")
        print(f"Nyquist Sınırınız (Maksimum Görebileceğiniz Frekans): {gercek_fs/2:.2f} Hz")
        return np.array(raw_veriler), np.array(clean_veriler), gercek_fs
    except Exception as e:
        print(f"Hata: {e}")
        return None, None, None

def gelismis_fourier_analizi(raw_sinyal, ema_sinyal, fs):
    N = len(raw_sinyal)
    T = 1.0 / fs
    zaman = np.linspace(0.0, N*T, N, endpoint=False)
    
    # 1. HAM VERİNİN FOURIER'İ
    raw_fft = fft(raw_sinyal)
    frekanslar = fftfreq(N, T)
    
    # --- DİJİTAL BÜYÜ BURADA BAŞLIYOR (FREQUENCY DOMAIN FILTERING) ---
    # raw_fft'nin bir kopyasını alıyoruz ve istemediğimiz frekansları SIFIRLIYORUZ!
    temizlenmis_fft = raw_fft.copy()
    
    # 0 Hz'i (DC Offset) sıfırla ki grafiği bozmasın
    temizlenmis_fft[0] = 0
    raw_fft[0] = 0
    
    # KESKİN NİŞANCI FİLTRESİ: 40 Hz'den yüksek olan tüm frekansları ve 
    # 0.5 Hz'den küçük olan dalgalanmaları (nefes alma) acımasızca sıfırla!
    for i, freq in enumerate(frekanslar):
        if abs(freq) > 40.0 or abs(freq) < 0.5:
            temizlenmis_fft[i] = 0 
            
    # 2. TERS FOURIER (IFFT) İLE ZAMANA GERİ DÖNÜŞ
    # Temizlenmiş frekansları tekrar normal sinyale çeviriyoruz
    ifft_sinyal = np.real(ifft(temizlenmis_fft))
    
    # Görselleştirme için sadece pozitif frekansları alalım
    pozitif_frekanslar = frekanslar[:N//2]
    raw_genlikler = 2.0/N * np.abs(raw_fft[0:N//2])
    temiz_genlikler = 2.0/N * np.abs(temizlenmis_fft[0:N//2])

    # --- SİNYAL MİMARİSİNİ GÖRSELLEŞTİRME ---
    fig, axs = plt.subplots(3, 1, figsize=(12, 10))
    fig.canvas.manager.set_window_title('AD8232 Gelişmiş DSP Analizi')
    
    # Üst Grafik: Ham Sinyal
    axs[0].plot(zaman, raw_sinyal, color='red', label='Arduino Ham Veri')
    axs[0].set_title('1. Aşama: Zaman Düzlemindeki Ham Sinyal')
    axs[0].legend()
    axs[0].grid(True)
    
    # Orta Grafik: Frekans Düzleminde Filtreleme (Senin Tahmin Ettiğin İşlem!)
    axs[1].plot(pozitif_frekanslar, raw_genlikler, color='lightcoral', label='Ham Spektrum (Gürültülü)')
    axs[1].plot(pozitif_frekanslar, temiz_genlikler, color='darkblue', label='Filtrelenmiş Spektrum (<40Hz)')
    axs[1].set_title('2. Aşama: Frekans Düzleminde Fourier Kesimi (Nyquist Limitine Kadar)')
    axs[1].legend()
    axs[1].grid(True)
    
    # Alt Grafik: Ters Fourier (IFFT) ile Elde Edilen Kusursuz Sinyal
    # Arduino'daki EMA'yı ve IFFT sonucunu kıyaslayalım
    axs[2].plot(zaman, ema_sinyal - np.mean(ema_sinyal), color='gray', alpha=0.5, label='Arduino EMA Filtresi')
    axs[2].plot(zaman, ifft_sinyal, color='green', linewidth=2, label='Python IFFT (Ters Fourier) Filtresi')
    axs[2].set_title('3. Aşama: IFFT ile Zamana Geri Döndürülmüş Pürüzsüz Kalp Ritmi')
    axs[2].set_xlabel('Zaman (saniye)')
    axs[2].legend()
    axs[2].grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    r_data, c_data, fs = veri_topla(PORT, BAUD_RATE, ORNEKLEME_SAYISI)
    if r_data is not None:
        gelismis_fourier_analizi(r_data, c_data, fs)