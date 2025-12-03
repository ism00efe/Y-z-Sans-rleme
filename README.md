# Face Blur & Privacy Tool (Yüz Sansürleme Aracı)

Bu proje, Python ve OpenCV kullanarak gerçek zamanlı görüntüdeki insan yüzlerini algılar ve otomatik olarak sansürler (bulanıklaştırır).

## 🎯 Projenin Amacı
Video içeriklerinde veya canlı yayınlarda, arka plandaki kişilerin yüzlerini otomatik gizleyerek **kişisel veri mahremiyetini (Privacy Protection)** sağlamak için geliştirilmiş bir prototiptir.

## 🚀 Özellikler
* **Gerçek Zamanlı Tespit:** Webcam görüntüsü üzerinden anlık yüz takibi yapar.
* **Otomatik Sansür:** Algılanan yüz bölgesine dinamik `Gaussian Blur` (Gauss Bulanıklığı) uygular.
* **Optimize Performans:** Haar Cascade sınıflandırıcısı kullanılarak düşük donanımlı bilgisayarlarda bile yüksek FPS ile çalışır.

## 🛠 Kullanılan Teknolojiler
* **Python 3.13**
* **OpenCV:** Görüntü işleme, yüz algılama ve matris manipülasyonu için.

## ⚠️ Eğitim Notu (Learning Process)
Bu proje benim **Görüntü İşleme (Computer Vision)** alanındaki öğrenme sürecimin bir parçasıdır. 
* Projede **"Haar Cascades"** algoritmasının çalışma mantığı ve limitleri (ışık/açı hassasiyeti) test edilmiştir.
* Görüntü matrisleri üzerinde bölge kesme (ROI) ve bulanıklaştırma işlemleri deneyimlenmiştir.
