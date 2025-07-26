
import streamlit as st
import pandas as pd
import unicodedata
import re

def normalize_name(name):
    name = str(name).lower()
    name = unicodedata.normalize('NFD', name)
    name = name.encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

st.title("📊 İsim Karşılaştırma Uygulaması")

file1 = st.file_uploader("1. Dosya (Kaynak)", type=["xlsx"], key="file1")
file2 = st.file_uploader("2. Dosya (Kontrol)", type=["xlsx"], key="file2")

if file1 and file2:
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    name_col1 = df1.columns[0]
    name_col2 = df2.columns[0]

    df1["normalized"] = df1[name_col1].apply(normalize_name)
    df2["normalized"] = df2[name_col2].apply(normalize_name)

    df1_counts = df1["normalized"].value_counts()
    df2_counts = df2["normalized"].value_counts()

    farkli_isimler = []

    for name, count1 in df1_counts.items():
        count2 = df2_counts.get(name, 0)
        if count1 > count2:
            orijinal_isim = df1[df1["normalized"] == name][name_col1].iloc[0]
            farkli_isimler.append({
                "İsim": orijinal_isim,
                "1. Dosyada": count1,
                "2. Dosyada": count2,
                "Fark": count1 - count2
            })

    result_df = pd.DataFrame(farkli_isimler)

    if not result_df.empty:
        st.subheader("🔍 Farklılıklar:")
        st.dataframe(result_df)
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Sonuçları İndir", csv, "isim_farklari.csv", "text/csv")
    else:
        st.success("🎉 Tüm isimler eşleşiyor!")
