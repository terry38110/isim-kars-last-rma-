import streamlit as st
import pandas as pd
import unicodedata
import re

# Gelişmiş isim temizleme ve normalize etme fonksiyonu
def normalize_advanced(name):
    if not isinstance(name, str):
        return ""
    name = name.lower()
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"bireysel\s*odeme", "", name)  # 'bireysel ödeme' ifadesini sil
    name = re.sub(r"[^\w\s]", "", name)  # Noktalama işaretlerini sil
    name = re.sub(r"\s+", "", name)  # Tüm boşlukları sil
    return name.strip()

st.title("Gelişmiş İsim Karşılaştırma Uygulaması")

file1 = st.file_uploader("1. Dosya (Referans)", type=["xlsx"])
file2 = st.file_uploader("2. Dosya (Kontrol)", type=["xlsx"])

if file1 and file2:
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # Kolonları küçük harfe çevir
    df1.columns = [c.lower() for c in df1.columns]
    df2.columns = [c.lower() for c in df2.columns]

    # İsim kolonlarını bul
    name_col1 = [c for c in df1.columns if "isim" in c][0]
    name_col2 = [c for c in df2.columns if "isim" in c][0]

    # Normalize edilmiş isim kolonlarını ekle
    df1["normalized"] = df1[name_col1].apply(normalize_advanced)
    df2["normalized"] = df2[name_col2].apply(normalize_advanced)

    # Her dosyada isim sayısını hesapla
    count1 = df1["normalized"].value_counts()
    count2 = df2["normalized"].value_counts()

    # Eksik olanları listele
    results = []
    for name in count1.index:
        c1 = count1[name]
        c2 = count2.get(name, 0)
        if c1 > c2:
            orijinal = df1[df1["normalized"] == name][name_col1].iloc[0]
            results.append({
                "İsim": orijinal,
                "1. Dosya Adet": c1,
                "2. Dosya Adet": c2,
                "Eksik Sayı": c1 - c2
            })

    if results:
        df_result = pd.DataFrame(results)
        st.subheader("Eksik Olan İsimler")
        st.dataframe(df_result)
        csv = df_result.to_csv(index=False).encode("utf-8")
        st.download_button("CSV Olarak İndir", csv, "eksik_isimler.csv", "text/csv")
    else:
        st.success("Her iki dosyada da tüm isimler eşleşiyor!")