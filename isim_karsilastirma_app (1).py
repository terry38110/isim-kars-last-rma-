import streamlit as st
import pandas as pd
import unicodedata
import re

# İsimleri normalize eden fonksiyon (Türkçe karakter sadeleştirme, boşluk temizleme, küçük harf)
def normalize_name(name):
    if not isinstance(name, str):
        return ""
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("utf-8")
    name = name.lower()
    name = re.sub(r"bireysel\s+odeme", "", name)  # Bireysel Ödeme ifadesini sil
    name = re.sub(r"[^a-z0-9]", "", name)  # Harf ve rakam dışındaki her şeyi sil
    return name

st.title("İsim ve Miktar Karşılaştırma Uygulaması")

file1 = st.file_uploader("1. Dosya (Referans)", type=["xlsx"])
file2 = st.file_uploader("2. Dosya (Kontrol Edilecek)", type=["xlsx"])

if file1 and file2:
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # İlk dosyada isim ve miktar olduğunu varsayalım
    df1.columns = [col.lower() for col in df1.columns]
    df2.columns = [col.lower() for col in df2.columns]

    # İsim sütunu bulma
    col_name1 = [c for c in df1.columns if "isim" in c][0]
    col_name2 = [c for c in df2.columns if "isim" in c][0]

    # Normalize edilmiş isimlerle çalışalım
    df1["normalized_name"] = df1[col_name1].apply(normalize_name)
    df2["normalized_name"] = df2[col_name2].apply(normalize_name)

    # Sayı sütununu alalım (opsiyonel)
    col_amount1 = next((c for c in df1.columns if "miktar" in c or "tutar" in c), None)
    col_amount2 = next((c for c in df2.columns if "miktar" in c or "tutar" in c), None)

    # Normalleştirilmiş isme göre sayım yap
    count1 = df1["normalized_name"].value_counts()
    count2 = df2["normalized_name"].value_counts()

    # Farklı olanları tespit et
    mismatch = []
    for name in count1.index:
        n1 = count1[name]
        n2 = count2.get(name, 0)
        if n1 > n2:
            orijinal_adi = df1[df1["normalized_name"] == name][col_name1].iloc[0]
            mismatch.append({
                "İsim": orijinal_adi,
                "1. Dosya Adet": n1,
                "2. Dosya Adet": n2,
                "Eksik Sayı": n1 - n2
            })

    if mismatch:
        result_df = pd.DataFrame(mismatch)
        st.subheader("2. dosyada eksik olan isimler:")
        st.dataframe(result_df)
        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("Sonucu İndir (CSV)", csv, "eksik_olanlar.csv", "text/csv")
    else:
        st.success("Tüm isimler her iki dosyada eşleşiyor. Eksik yok.")