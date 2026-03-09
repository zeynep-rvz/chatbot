import streamlit as st
from google import genai

# Sayfa Ayarları
st.set_page_config(page_title="MEB Ders Planı Asistanı", page_icon="📚")

st.title("📚 MEB Uyumlu Ders Planı ve Etkinlik Botu")
st.markdown("""
Öğretmenler için zaman kazandıran asistan! Haftanın kazanımını girin; bilgi yarışması, vaka analizi ve çalışma kağıdınız saniyeler içinde hazır olsun.
""")

# Yan çubukta (sidebar) API Anahtarı girişi
st.sidebar.header("Ayarlar")
api_key = st.sidebar.text_input("Gemini API Anahtarınızı Girin:", type="password")

# Ana ekranda kullanıcıdan kazanım alma
kazanim = st.text_input("Bu Haftanın Kazanımı Nedir?", placeholder="Örn: Dijital Etik, İklim Değişikliği, Hücrenin Yapısı...")

# Butona tıklandığında çalışacak işlemler
if st.button("Ders İçeriğini Hazırla", type="primary"):
    if not api_key:
        st.warning("Lütfen sol menüden Gemini API anahtarınızı girin.")
    elif not kazanim:
        st.warning("Lütfen bir ders kazanımı girin.")
    else:
        # Gemini İstemcisi oluşturuluyor
        client = genai.Client(api_key=api_key)
        
        # Yapay zekaya vereceğimiz detaylı talimat (Prompt Engineering)
        prompt = f"""
        Sen MEB müfredatına tam hakim, yaratıcı ve uzman bir öğretmensin.
        Bana şu kazanım ile ilgili bir ders planı içeriği hazırla: '{kazanim}'
        
        Lütfen yanıtını aşağıdaki 3 ana başlık altında, açık ve anlaşılır bir dille oluştur:
        
        1. 5 Soruluk Kahoot Bilgi Yarışması
        (Her soru için 4 şık (A, B, C, D) ve doğru cevabı net bir şekilde belirt.)
        
        2. Kısa Hikaye veya Vaka Analizi
        (Öğrencilerin ilgisini çekecek, derse giriş veya pekiştirme amaçlı kullanılabilecek, yaş grubuna uygun kısa bir hikaye veya olay kurgusu.)
        
        3. Çalışma Kağıdı Taslağı
        (Öğrencilerin ders sonunda doldurabileceği, boşluk doldurma, açık uçlu sorular veya eşleştirme gibi bölümler içeren, PDF'e dönüştürülmeye hazır bir çalışma kağıdı metni.)
        """
        
        with st.spinner("Ders içeriğiniz özenle hazırlanıyor... Lütfen bekleyin."):
            try:
                # Gemini 2.5 Flash modelini kullanarak içerik üretimi
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                # Sonucu ekrana yazdırma
                st.success("İçerik başarıyla oluşturuldu!")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")