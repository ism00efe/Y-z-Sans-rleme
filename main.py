import cv2

# 1. Yüz tanıma modelini yükle (OpenCV ile hazır gelir)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Kamerayı aç
cap = cv2.VideoCapture(0)

while True:
    # Kameradan görüntü oku
    ret, frame = cap.read()
    if not ret:
        print("Kamera açılmadı!")
        break

    # Yapay zeka siyah-beyaz fotoğrafta daha hızlı çalışır
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- SİHİR BURADA: Yüzleri Bul ---
    # 1.1: Ölçek faktörü (yüzü ne kadar küçülterek arayayım?)
    # 4: Hassasiyet (sayı artarsa daha az hata yapar ama bazı yüzleri kaçırabilir)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Bulunan her yüz için:
    for (x, y, w, h) in faces:
        # Yüzün etrafına Mavi kutu çiz (BGR: Blue, Green, Red)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Sadece yüzün olduğu bölgede gözleri ara (Performans için)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(roi_gray)
        # Bulunan her yüz için:
        for (x, y, w, h) in faces:
            # 1. Yüzün olduğu bölgeyi (ROI - Region of Interest) kesip al
            roi = frame[y:y + h, x:x + w]

            # 2. Bu bölgeye çok güçlü bir "Gaussian Blur" (Bulanıklaştırma) uygula
            # (99, 99) bulanıklık şiddetidir, artırabilirsin. Sayılar tek olmalı.
            blurred_roi = cv2.GaussianBlur(roi, (99, 99), 30)

            # 3. Bulanıklaşmış parçayı ana resimdeki yerine geri yapıştır
            frame[y:y + h, x:x + w] = blurred_roi

            # İstersen etrafına yine kutu çizebilirsin (opsiyonel)
            # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Ekrana yansıt
    cv2.imshow('Yuz Tanima (Cikmak icin "q" bas)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()