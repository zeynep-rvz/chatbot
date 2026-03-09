import streamlit as st
from google import genai
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="MEB Ders Planı Asistanı", page_icon="📚")

st.title("📚 MEB Uyumlu Ders Planı ve Etkinlik Botu")
st.markdown("""
Öğretmenler için zaman kazandıran asistan! Haftanın kazanımını girin; 
içerik hazır olsun ve otomatik olarak Google E-Tablolar'a kaydedilsin.
""")

# --- API VE KİMLİK AYARLARI (SECRETS) ---
# Streamlit Secrets'tan anahtarları güvenli bir şekilde çekiyoruz
try:
    # Gemini API Anahtarı
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    # Google Sheets Kimlik Bilgileri (JSON formatında sakladığımız)
    google_secrets = json.loads(st.secrets["google_credentials"])
    
    st.sidebar.success("✅ Sistem Bağlantıları Hazır")
except Exception as e:
    st.sidebar.error("⚠️ Ayarlar eksik! Secrets kısmını kontrol edin.")
    st.stop() # Ayarlar eksikse uygulamayı durdur

# --- KULLANICI GİRİŞİ ---
kazanim = st.text_input("Bu Haftanın Kazanımı Nedir?", placeholder="Örn: Dijital Etik, Fotosentez, Madde ve Isı...")

if st.button("Ders İçeriğini Hazırla", type="primary"):
    if not kazanim:
        st.warning("Lütfen bir ders kazanımı girin.")
    else:
        # Gemini İstemcisi
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Yapay Zeka Komutu (Prompt)
        prompt = f"""
        Sen MEB müfredatına tam hakim, uzman bir öğretmensin. 
        Lütfen şu kazanım için bir içerik hazırla: '{kazanim}'
        
        Yanıtını şu 3 başlık altında düzenle:
        1. 5 Soruluk Kahoot Bilgi Yarışması (Şıklar ve cevap anahtarı dahil)
        2. Derste anlatılacak kısa bir hikaye veya vaka analizi
        3. Öğrenciler için bir çalışma kağıdı taslağı
        """
        
        with st.spinner("Yapay zeka içeriği hazırlıyor ve tabloya kaydediyor..."):
            try:
                # 1. Gemini'dan içerik üretimi
                response = client.models.generate_content(
                    model='gemini-2.0-flash', # En güncel ve hızlı model
                    contents=prompt,
                )
                icerik_metni = response.text
                
                # Ekranda Göster
                st.success("İçerik Başarıyla Oluşturuldu!")
                st.markdown("---")
                st.markdown(icerik_metni)
                
                # 2. Google Sheets'e Kaydetme
                try:
                    # Google Yetkilendirme
                    scopes = [
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                    creds = Credentials.from_service_account_info(google_secrets, scopes=scopes)
                    gc = gspread.authorize(creds)
                    
                    # Tabloyu aç (İsminin tam olarak "Ders Planları" olduğundan emin olun)
                    sh = gc.open("Ders Planları")
                    worksheet = sh.sheet1
                    
                    # Kayıt bilgilerini hazırla
                    tarih = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    
                    # Tabloya yeni satır ekle
                    worksheet.append_row([tarih, kazanim, icerik_metni])
                    
                    st.toast("✅ Veriler Google E-Tablo'ya kaydedildi!", icon="📊")
                    
                except Exception as sheet_err:
                    st.error(f"Tabloya kaydedilirken bir hata oluştu: {sheet_err}")
                    
            except Exception as gen_err:
                st.error(f"İçerik üretilirken bir hata oluştu: {gen_err}")

# --- ALT BİLGİ ---
st.markdown("---")
st.caption("Bu araç Gemini AI kullanılarak öğretmenler için geliştirilmiştir.")
