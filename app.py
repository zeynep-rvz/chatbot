import streamlit as st
from google import genai
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="MEB Ders Planı Asistanı", page_icon="📚")

st.title("📚 MEB Uyumlu Ders Planı ve Etkinlik Botu")
st.markdown("Öğretmenler için zaman kazandıran asistan! Haftanın kazanımını girin, içerik hazır olsun ve otomatik olarak Google E-Tablolar'a kaydedilsin.")

# Yan çubukta (sidebar) API Anahtarı
st.sidebar.header("Ayarlar")
api_key = st.sidebar.text_input("Gemini API Anahtarınızı Girin:", type="password")

# Kullanıcıdan kazanım alma
kazanim = st.text_input("Bu Haftanın Kazanımı Nedir?", placeholder="Örn: Dijital Etik, İklim Değişikliği...")

if st.button("Ders İçeriğini Hazırla", type="primary"):
    if not api_key:
        st.warning("Lütfen sol menüden Gemini API anahtarınızı girin.")
    elif not kazanim:
        st.warning("Lütfen bir ders kazanımı girin.")
    else:
        client = genai.Client(api_key=api_key)
        prompt = f"Sen MEB müfredatına tam hakim bir öğretmensin. Şu kazanım için içerik hazırla: '{kazanim}'. Lütfen yanıtını 1. 5 Soruluk Kahoot, 2. Kısa Hikaye, 3. Çalışma Kağıdı Taslağı olarak bölümlere ayır."
        
        with st.spinner("İçerik hazırlanıyor ve tablonuza kaydediliyor..."):
            try:
                # 1. Gemini'dan içeriği al
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                icerik = response.text
                
                # Ekrana yazdır
                st.success("İçerik başarıyla oluşturuldu!")
                st.markdown("---")
                st.markdown(icerik)
                
                # 2. Google Sheets'e Kaydetme İşlemi
                try:
                    # Streamlit Secrets'tan (O kilitli kasadan) anahtarı alıyoruz
                    krediler_dict = json.loads(st.secrets["google_credentials"])
                    
                    # Google'a giriş yapıyoruz
                    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                    credentials = Credentials.from_service_account_info(krediler_dict, scopes=scopes)
                    gc = gspread.authorize(credentials)
                    
                    # Tabloyu bul ve aç (Adının tam olarak "Ders Planları" olduğundan emin olun)
                    sh = gc.open("Ders Planları")
                    worksheet = sh.sheet1
                    
                    # Verileri tabloya alt alta ekle
                    su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    worksheet.append_row([su_an, kazanim, icerik])
                    
                    # Sağ altta şık bir bildirim göster
                    st.toast("✅ İçerik başarıyla Google E-Tablolar'a kaydedildi!", icon="📊")
                    
                except Exception as sheet_hata:
                    st.error("İçerik üretildi ama tabloya bağlanırken bir sorun çıktı. Ayarları kontrol edelim.")
                    st.code(f"Hata Detayı: {sheet_hata}")

            except Exception as e:
                st.error(f"Yapay zeka bir hata verdi: {e}")
