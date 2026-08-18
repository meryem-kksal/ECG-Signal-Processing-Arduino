// --- SİSTEM MİMARİSİ AYARLARI ---
const int pencereboyutu = 10;
int datas[pencereboyutu];
int index = 0;
long toplam = 0;

unsigned long sonateszamani = 0;

// EMA (Exponential Moving Average) Filtre Katsayısı (0 ile 1 arasında)
// 1'e yakın: Gürültülü ama çok hızlı tepki (tepeleri kesmez)
// 0'a yakın: Çok pürüzsüz ama gecikmeli (tepeleri ezer)
const float EMA_ALPHA = 0.4; 
float ema_clean = 0; // EMA filtremizin tutulduğu değişken

void setup() {
  pinMode(13, INPUT);
  pinMode(12, INPUT);
  
  // Python'daki BAUD_RATE ile aynı olmalı
  Serial.begin(115200); // 9600 biyomedikal veri (saniyede yüzlerce veri) için çok yavaştır, 115200'e çıkardık.
  
  // Buffer'ı sıfırlarla doldur
  for(int i=0; i<pencereboyutu; i++){
    datas[i] = 0;
  }
}

void loop() {
  // 1. GÜVENLİK KONTROLÜ
  if(digitalRead(13) == HIGH || digitalRead(12) == HIGH) {
    // Pedler koptuğunda Python'a metin gönderme, veri akışını bozmamak için 0 gönder
    Serial.println("0,0");
    delay(10);
    return;
  } 

  // 2. SENSÖRDEN HAM VERİ OKUMA
  int rawsignal = analogRead(A1);

  // 3. YÖNTEM B: PROFESYONEL YÖNTEM (EMA FİLTRESİ)
  // Formül: Yeni Temiz = (Alpha * Ham_Veri) + ((1 - Alpha) * Eski_Temiz)
  // Bu yöntem tepe noktalarını senin Circular Buffer'ın gibi kesmez, daha sivri tutar.
  if (ema_clean == 0) {
    ema_clean = rawsignal; // İlk veriyi baz al
  } else {
    ema_clean = (EMA_ALPHA * rawsignal) + ((1.0 - EMA_ALPHA) * ema_clean);
  }

  // BPM HESAPLAMA (Mantığın harika, bunu koruyoruz ama seri porta yazdırmıyoruz)
  int esikDegeri = 600;
  if(rawsignal > esikDegeri) {
    if(millis() - sonateszamani > 300) {
      unsigned long suankizaman = millis();
      unsigned long gecensure = suankizaman - sonateszamani;
      int bpm = 60000 / gecensure;
      sonateszamani = suankizaman;
      
      // Mimar Notu: BPM bilgisini Python'a atmıyoruz çünkü Python frekans (Hz) analizinden
      // kendi BPM'ini Fourier ile (çok daha hassas bir şekilde) zaten bulacak!
    }
  }

  // 4. PYTHON'A VERİ GÖNDERİMİ (SADECE SAF VERİ!)
  // Format: "Ham_Veri,Temiz_Veri"
  Serial.print(rawsignal);
  Serial.print(",");
  Serial.println(ema_clean); // Şimdilik Circular Buffer yerine EMA filtresini yolluyoruz.
  
  // Örnekleme hızı ~100Hz
  delay(10);
}