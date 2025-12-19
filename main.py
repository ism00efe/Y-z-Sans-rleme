import cv2
import numpy as np
import os
import time  # <--- YENİ: Zaman modülü eklendi

# --- KULLANICI AYARLARI ---
KAMERA_INDEX = 1
VIDEO_DOSYA_ADI = 'proje_kayit.mp4'

# --- Modeller ve Dosyalar ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

overlay_image_path = "mask_overlay.png"
overlay_img_orig = None

if os.path.exists(overlay_image_path):
    overlay_img_orig = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)
else:
    overlay_img_orig = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(overlay_img_orig, (50, 50), 45, (0, 255, 255), -1)
    cv2.circle(overlay_img_orig, (35, 35), 8, (0, 0, 0), -1)
    cv2.circle(overlay_img_orig, (65, 35), 8, (0, 0, 0), -1)
    cv2.ellipse(overlay_img_orig, (50, 60), (25, 12), 0, 0, 180, (0, 0, 0), 4)

# --- Kamera Başlatma ---
cap = cv2.VideoCapture(KAMERA_INDEX)
if not cap.isOpened():
    print(f"HATA: {KAMERA_INDEX} numaralı kamera açılamadı! Lütfen 0 veya 2 deneyin.")
    exit()

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
# 'mp4v' hata verirse site üzerinden dönüştürme taktiğini kullanıyoruz
out = cv2.VideoWriter(VIDEO_DOSYA_ADI, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (frame_width, frame_height))

# --- Değişkenler ---
is_recording = False
start_time = 0  # <--- YENİ: Başlangıç zamanını tutacak değişken

privacy_mode = False
shapes = ["Kare", "Daire", "Ucgen"]
current_shape_index = 0
mask_types = ["Blur", "Renk", "Resim"]
current_mask_index = 0
colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255)]
current_color_index = 0


def draw_features(img, x, y, w, h, text):
    shape_mode = shapes[current_shape_index]
    mask_type = mask_types[current_mask_index]
    color = colors[current_color_index]
    center_x, center_y = x + w // 2, y + h // 2
    radius = int(h / 1.8)
    tri_pt1, tri_pt2, tri_pt3 = (x + w // 2, y), (x, y + h), (x + w, y + h)

    if privacy_mode:
        if mask_type == "Resim":
            try:
                resized_overlay = cv2.resize(overlay_img_orig, (w, h))
                if resized_overlay.shape[2] == 4:
                    resized_overlay = cv2.cvtColor(resized_overlay, cv2.COLOR_BGRA2BGR)
                img[y:y + h, x:x + w] = resized_overlay
            except:
                pass
        elif mask_type == "Blur":
            mask = np.zeros_like(img)
            if shape_mode == "Kare":
                cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
            elif shape_mode == "Daire":
                cv2.circle(mask, (center_x, center_y), radius, (255, 255, 255), -1)
            elif shape_mode == "Ucgen":
                cv2.drawContours(mask, [np.array([tri_pt1, tri_pt2, tri_pt3])], 0, (255, 255, 255), -1)
            blurred_img = cv2.GaussianBlur(img, (51, 51), 30)
            img[:] = np.where(mask == (255, 255, 255), blurred_img, img)
        elif mask_type == "Renk":
            if shape_mode == "Kare":
                cv2.rectangle(img, (x, y), (x + w, y + h), color, -1)
            elif shape_mode == "Daire":
                cv2.circle(img, (center_x, center_y), radius, color, -1)
            elif shape_mode == "Ucgen":
                cv2.drawContours(img, [np.array([tri_pt1, tri_pt2, tri_pt3])], 0, color, -1)

    should_draw_outline = not (privacy_mode and (mask_type == "Renk" or mask_type == "Resim"))
    if should_draw_outline:
        thickness = 2
        if shape_mode == "Kare":
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
        elif shape_mode == "Daire":
            cv2.circle(img, (center_x, center_y), radius, color, thickness)
        elif shape_mode == "Ucgen":
            cv2.drawContours(img, [np.array([tri_pt1, tri_pt2, tri_pt3])], 0, color, thickness)

    if not (privacy_mode and mask_type != "Blur"):
        cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def is_overlapping(new_rect, existing_rects):
    nx, ny, nw, nh = new_rect
    for (ex, ey, ew, eh) in existing_rects:
        dist = ((nx - ex) ** 2 + (ny - ey) ** 2) ** 0.5
        if dist < 50: return True
    return False


while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    detected_rects = []

    # Yüz Tarama İşlemleri
    faces_front = face_cascade.detectMultiScale(gray, 1.3, 8)
    for (x, y, w, h) in faces_front:
        detected_rects.append((x, y, w, h))
        draw_features(frame, x, y, w, h, "On")

    faces_profile = profile_cascade.detectMultiScale(gray, 1.3, 6)
    for (x, y, w, h) in faces_profile:
        if not is_overlapping((x, y, w, h), detected_rects):
            detected_rects.append((x, y, w, h))
            draw_features(frame, x, y, w, h, "Yan")

    flipped_gray = cv2.flip(gray, 1)
    faces_flipped = profile_cascade.detectMultiScale(flipped_gray, 1.3, 6)
    for (x, y, w, h) in faces_flipped:
        x_orig = width - x - w
        if not is_overlapping((x_orig, y, w, h), detected_rects):
            detected_rects.append((x_orig, y, w, h))
            draw_features(frame, x_orig, y, w, h, "Yan")

    # --- KAYIT VE SAYAÇ BÖLÜMÜ (GÜNCELLENDİ) ---
    if is_recording:
        # 1. Kayıt Süresini Hesapla
        gecen_sure = int(time.time() - start_time)

        # 2. Kırmızı Nokta
        cv2.circle(frame, (frame_width - 30, 30), 10, (0, 0, 255), -1)

        # 3. Süreyi Ekrana Yaz (Örn: REC 14sn)
        timer_text = f"REC {gecen_sure}sn"
        cv2.putText(frame, timer_text, (frame_width - 150, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        out.write(frame)

    # --- ARAYÜZ ---
    info = f"MOD: {'GIZLI' if privacy_mode else 'ACIK'} | SEKIL: {shapes[current_shape_index]} | TIP: {mask_types[current_mask_index]}"
    cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 0), 4)
    cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)

    help_text = "'r':KAYIT | 'b':Gizle | 's':Sekil | 'm':Tip | 'c':Renk | 'q':Cikis"
    cv2.putText(frame, help_text, (10, 55), cv2.FONT_HERSHEY_PLAIN, 1, (50, 50, 50), 2)
    cv2.putText(frame, help_text, (10, 55), cv2.FONT_HERSHEY_PLAIN, 1, (200, 200, 200), 1)

    cv2.imshow('Sayacli Uygulama', frame)

    # --- TUŞ KONTROLLERİ ---
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('b'):
        privacy_mode = not privacy_mode
    elif key == ord('s'):
        current_shape_index = (current_shape_index + 1) % len(shapes)
    elif key == ord('m'):
        current_mask_index = (current_mask_index + 1) % len(mask_types)
    elif key == ord('c'):
        current_color_index = (current_color_index + 1) % len(colors)
    elif key == ord('r'):
        if not is_recording:
            # Kayıt YENİ başlıyorsa, başlangıç zamanını tut
            start_time = time.time()
            is_recording = True
            print("Kayıt Başladı...")
        else:
            # Kayıt zaten varsa durdur
            is_recording = False
            print("Kayıt Durdu.")

cap.release()
out.release()
cv2.destroyAllWindows()
