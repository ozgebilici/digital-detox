# 🌿 Dijital Arınma (Digital Detox)

**Gmail hesabınıza kayıtlı olduğunuz dijital platformları keşfedin, kişisel verilerinizin silinmesini talep edin ve başvurularınızı tek bir yerden takip edin.**

Dijital Arınma, Gmail hesabındaki kayıt ve üyelik e-postalarını analiz ederek kullanıcının üye olduğu dijital platformları tespit etmeyi ve bu platformlara KVKK/GDPR kapsamında kişisel veri silme talepleri oluşturmayı amaçlayan web tabanlı bir uygulamadır.

Proje, unutulmuş dijital hesapların keşfedilmesini ve kişisel veriler üzerindeki kontrolün artırılmasını hedefler.

---

## 📌 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Özellikler](#-özellikler)
- [Nasıl Çalışır?](#-nasıl-çalışır)
- [Kullanılan Teknolojiler](#️-kullanılan-teknolojiler)
- [Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
- [Google OAuth ve Gmail API Ayarları](#-google-oauth-ve-gmail-api-ayarları)
- [Kullanım Kılavuzu](#-kullanım-kılavuzu)
- [Güvenlik ve Gizlilik](#-güvenlik-ve-gizlilik)
- [Sorun Giderme](#-sorun-giderme)
- [Geliştirici](#-geliştirici)

## 🎯 Proje Hakkında

Dijital platformlara üyelikler zamanla artabilir ve kullanıcılar artık kullanmadıkları hesapları unutabilir. Bu durum, kişisel verilerin farklı platformlarda tutulmaya devam etmesine neden olabilir.

**Dijital Arınma**, Gmail hesabındaki ilgili e-postaları inceleyerek kayıtlı olunan platformları belirlemeye yardımcı olur. Ardından kullanıcıların ilgili platformlara kişisel verilerinin silinmesi için talep hazırlamasını ve bu taleplerin durumunu takip etmesini sağlar.

Uygulama, kullanıcıların dijital ayak izlerini daha bilinçli yönetmelerine yardımcı olmak üzere tasarlanmıştır.

## ✨ Özellikler

- **📧 Gmail entegrasyonu:** Google OAuth 2.0 üzerinden kullanıcı girişi.
- **🔎 Dijital hesap tespiti:** Gmail'deki kayıt ve üyelik e-postalarından platformların belirlenmesi.
- **🌐 Geniş platform desteği:** 300'den fazla platform için tanıma desteği hedefi.
- **🗑️ Veri silme talebi oluşturma:** KVKK ve GDPR kapsamında kullanılabilecek talep metinlerinin hazırlanması.
- **📋 Talep takibi:** Oluşturulan taleplerin tek bir panel üzerinden yönetilmesi.
- **⏳ Son tarih takibi:** Talepler için 30 günlük süreye ilişkin hatırlatıcı bilgiler.
- **📨 E-posta seçenekleri:** Talep metnini kopyalama veya desteklenen e-posta istemcilerinde açma.
- **☑️ Toplu işlem:** Birden fazla platform için talep hazırlama.
- **🔐 Token tabanlı erişim:** Kimlik doğrulama ve korunan işlemler için JWT kullanımı.

> **Önemli:** Bir platformun tespit edilmesi, hesabın hâlen aktif olduğunu veya talebin kabul edildiğini göstermez. Veri silme işleminin sonucu ilgili platformun yanıtına bağlıdır.

## ⚙️ Nasıl Çalışır?

1. Kullanıcı, Google hesabıyla oturum açar.
2. Gmail API üzerinden gerekli e-posta üst bilgileri incelenir.
3. E-posta göndereni, konusu ve tarihi gibi bilgiler kullanılarak bilinen platformlar tespit edilir.
4. Tespit edilen platformlar kontrol panelinde listelenir.
5. Kullanıcı, seçtiği platform için veri silme talebi metni oluşturur.
6. Talep metnini kopyalayarak veya desteklenen e-posta seçeneklerini kullanarak ilgili platforma iletir.
7. Başvuruyu sisteme kaydeder ve durumunu takip eder.

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Kullanım amacı |
|---|---|
| Python | Backend geliştirme |
| FastAPI | REST API ve backend servisleri |
| Uvicorn | Backend uygulamasını çalıştırma |
| SQLAlchemy | Veritabanı işlemleri |
| Alembic | Veritabanı şema ve migration yönetimi |
| PostgreSQL | İlişkisel veritabanı |
| Psycopg | PostgreSQL bağlantısı |
| Google OAuth 2.0 | Google ile kimlik doğrulama |
| Gmail API | İlgili e-posta bilgilerine erişim |
| JWT | Token tabanlı kimlik doğrulama |
| HTML, CSS, JavaScript | Web arayüzü |

*Not: Dosya ağacı, raporda belirtilen temel dosyalara göre hazırlanmıştır. Alt klasör ve dosya adlarını güncel GitHub deposundaki gerçek yapıyla eşleştirmen gerekir.*

## 🚀 Kurulum ve Çalıştırma

Aşağıdaki adımlar Windows ve PowerShell ortamı içindir.

### Gereksinimler

Kurulumdan önce aşağıdaki araçların bilgisayarınızda bulunması gerekir:

- Python
- PostgreSQL
- Git
- Google Cloud hesabı
- Gmail hesabı

### 1. Projeyi bilgisayarınıza indirin

```powershell
git clone https://github.com/ozgebilici/digital-detox.git
cd digital-detox
```

### 2. Python sanal ortamını oluşturun

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Sanal ortam etkinleştirildiğinde terminal satırının başında `(.venv)` görünür.

PowerShell betik çalıştırma politikası nedeniyle etkinleştirme engellenirse yalnızca mevcut oturum için şu komut kullanılabilir:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Python bağımlılıklarını yükleyin

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

SQLAlchemy'nin asenkron özellikleri için `greenlet` eksikliği hatası alınırsa:

```powershell
python -m pip install greenlet
```

Kalıcı ve tekrarlanabilir kurulum için gerekli bağımlılıkların `requirements.txt` dosyasında tanımlı olduğundan emin olun.

### 4. Güvenlik anahtarlarını oluşturun

Projenin ana dizinine dönün ve anahtar üretme betiğini çalıştırın:

```powershell
cd ..
python scripts\generate_keys.py
```

Betik tarafından üretilen değerleri güvenli bir yerde saklayın. Hangi anahtarın hangi `.env` değişkenine karşılık geldiğini betiğin çıktısına ve yapılandırma dosyasına göre belirleyin.

### 5. Ortam değişkenlerini yapılandırın

`backend` klasöründeki `.env.example` dosyasını `.env` adıyla kopyalayın. Örnek:

```powershell
Copy-Item backend\.env.example backend\.env
```

`.env` dosyasını açarak Google OAuth bilgilerini, güvenlik anahtarlarını ve PostgreSQL bağlantı ayarlarını doldurun.

> `.env` dosyasını, gerçek erişim anahtarlarını veya veritabanı şifrelerini GitHub'a yüklemeyin.

### 6. PostgreSQL veritabanını hazırlayın

PostgreSQL servisinin çalıştığını ve `.env` içindeki bağlantı bilgilerinin doğru olduğunu kontrol edin.

Proje yapılandırmasına uygun veritabanını hazırlamak için ana dizinde:

```powershell
python scripts\setup_db.py
```

Bu adımın başarılı olması için PostgreSQL kullanıcı adı, parola, sunucu ve veritabanı bilgilerinin doğru ayarlanmış olması gerekir.

### 7. Veritabanı tablolarını oluşturun

Backend klasörüne geçin:

```powershell
cd backend
alembic upgrade head
```

Bu komut, tanımlanmış Alembic migration'larını veritabanına uygular.

### 8. Backend sunucusunu başlatın

Aynı `backend` klasöründe ve sanal ortam etkinken:

```powershell
uvicorn app.main:app --reload
```

Backend varsayılan olarak şu adreste çalışır:

- API: http://localhost:8000
- Swagger API dokümantasyonu: http://localhost:8000/docs

Sunucunun başarıyla başladığını terminal çıktısından kontrol edin.

### 9. Frontend arayüzünü başlatın

Backend çalışırken **ikinci bir PowerShell terminali** açın. Projenin ana dizinine gidin:

```powershell
cd "C:\digital-detox"
```

Bu yolu kendi bilgisayarınızdaki proje klasörünün gerçek yolu ile değiştirin. Ardından:

```powershell
cd frontend
python -m http.server 5500
```

Tarayıcıda şu adresi açın:

http://localhost:5500

Bu yöntem, statik HTML/CSS/JavaScript dosyalarını sunar. Frontend farklı bir çalıştırma yöntemi kullanıyorsa ilgili komutlar güncellenmelidir.

## 🔑 Google OAuth ve Gmail API Ayarları

Google ile giriş ve Gmail entegrasyonu için Google Cloud Console üzerinden gerekli yapılandırmalar yapılmalıdır.

1. Google Cloud Console'da bir proje oluşturun veya mevcut projenizi seçin.
2. Gmail API'yi etkinleştirin.
3. OAuth izin ekranını yapılandırın.
4. Web uygulaması türünde bir OAuth istemci kimliği oluşturun.
5. Geliştirme ortamında kullanılan yönlendirme adresini şu şekilde tanımlayın:

   `http://localhost:8000/api/auth/callback`

6. Google OAuth istemci bilgilerini backend'in `.env` dosyasına, uygulamanın beklediği değişken adlarıyla ekleyin.
7. Gmail erişim izinlerini yalnızca uygulamanın ihtiyaç duyduğu kapsamlarla sınırlandırın.

Google OAuth izin ekranı test modundaysa, hesabınızın test kullanıcıları arasında tanımlanması gerekebilir. Kullanılan OAuth yapılandırması ve Gmail kapsamları Google tarafından belirlenen kurallara uygun olmalıdır.

## 🧭 Kullanım Kılavuzu

### 1. Google ile giriş yapın

Frontend adresini açın ve **Google ile Giriş Yap** butonunu kullanın. İstenen izinleri inceleyip onayladıktan sonra uygulamanın yönlendirmesini bekleyin.

### 2. Dijital hesaplarınızı tarayın

Kontrol panelindeki **Hesaplarımı Tara** butonuna tıklayın. Tespit edilen platformlar listelenir.

### 3. Veri silme talebi hazırlayın

İlgili platformun kartındaki **Veri Sil** seçeneğini kullanın. Oluşturulan talep metnini inceleyin ve gerekli bilgilerin doğru olduğundan emin olun.

### 4. Talebi ilgili platforma iletin

Metni kopyalayabilir veya arayüzde sunulan desteklenen e-posta seçeneklerini kullanabilirsiniz. Talebin gerçekten gönderildiğini kontrol edin.

### 5. Talebi kaydedin ve takip edin

**Talebi Kaydettim** seçeneğiyle başvuruyu takip listesine ekleyin. İlgili sayfadan durumunu güncelleyin ve son tarih bilgilerini izleyin.

### 6. Birden fazla hesabı yönetin

Desteklenen arayüzde birden fazla platformu seçerek toplu talep hazırlama özelliğini kullanabilirsiniz.

## 🔐 Güvenlik ve Gizlilik

Dijital Arınma, kişisel verilerin korunmasını temel alan bir yaklaşımla tasarlanmıştır.

- Google hesabı parolası uygulama tarafından istenmez veya saklanmaz.
- Gmail erişimi Google OAuth 2.0 üzerinden gerçekleştirilir.
- Tasarım gereği e-posta içeriği yerine gönderen, konu ve tarih gibi üst bilgilerin kullanılması hedeflenir.
- Korunan API işlemlerinde JWT tabanlı kimlik doğrulama kullanılır.
- Gizli anahtarlar ve veritabanı kimlik bilgileri `.env` dosyasında tutulmalıdır.
- Gerçek kullanım öncesinde OAuth kapsamları, token saklama yöntemi, erişim kontrolleri, hata kayıtları ve veritabanı güvenliği ayrıca denetlenmelidir.

**Gizlilik notu:** Yukarıdaki maddeler projenin tasarım hedeflerini açıklar; uygulamanın tüm güvenlik koşullarını sağladığı anlamına gelmez. Gerçek davranış, kaynak kodu ve yapılandırma üzerinden doğrulanmalıdır.

## 🧰 Sorun Giderme

| Hata | Kontrol edilecekler |
|---|---|
| `ModuleNotFoundError` | Sanal ortamın etkin olduğunu ve `pip install -r requirements.txt` komutunun tamamlandığını kontrol edin. |
| `greenlet` hatası | `python -m pip install greenlet` komutunu çalıştırın ve SQLAlchemy bağımlılıklarını kontrol edin. |
| PostgreSQL bağlantı hatası | PostgreSQL servisinin çalıştığını ve `.env` bağlantı bilgilerinin doğru olduğunu kontrol edin. |
| Alembic migration hatası | Backend klasöründe olduğunuzdan emin olun ve `alembic upgrade head` komutunu tekrar kontrol edin. |
| `401 Unauthorized` | Oturumun ve JWT token'ının geçerli olup olmadığını kontrol edin; gerekirse yeniden giriş yapın. |
| Google OAuth yönlendirme hatası | Google Cloud Console'daki yönlendirme adresi ile uygulama yapılandırmasının aynı olduğunu kontrol edin. |
| Frontend açılamıyor | `frontend` klasöründe `python -m http.server 5500` komutunun çalıştığını ve dosyaların mevcut olduğunu doğrulayın. |
| `npm` ile ilgili hata | Frontend'in Node.js tabanlı bir proje olup olmadığını kontrol edin. Statik dosyalar için yukarıdaki Python HTTP sunucusu yeterlidir. |

## 👩‍💻 Geliştirici

**Özge Bilici**

Aksaray Üniversitesi  
Mühendislik Fakültesi — Yazılım Mühendisliği Bölümü

**Proje:** Dijital Arınma  

---

*Bu proje, dijital üyeliklerin fark edilmesini ve kişisel verilerin korunmasına yönelik taleplerin yönetilmesini kolaylaştırmak amacıyla geliştirilmiştir.*
