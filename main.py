import pandas as pd
import matplotlib.pyplot as plt

# 1. Rule Engine Matriks PWS-KIA
def tentukan_status(kumulatif, target, bln_lalu, bln_ini):
    if bln_ini > bln_lalu:
        tren = "Naik"
    elif bln_ini < bln_lalu:
        tren = "Turun"
    else:
        tren = "Tetap"
    
    is_diatas_target = kumulatif >= target
    
    if is_diatas_target and (tren == "Naik" or tren == "Tetap"):
        return tren, "BAIK"
    elif is_diatas_target and tren == "Turun":
        return tren, "KURANG"
    elif not is_diatas_target and tren == "Naik":
        return tren, "CUKUP"
    else:
        return tren, "JELEK"

def main():
    print("Memproses Visualisasi Dashboard PWS-KIA (V2 - Robust)...")
    file_path = 'PECANGAAN_04_2026_Laporan_Ibu.xlsx'
    
    try:
        df_raw = pd.read_excel(file_path, sheet_name='2.PWS', header=None)
    except Exception as e:
        print(f"Error membaca file: {e}")
        return

    # Ambil baris data desa (7-18)
    df_data = df_raw.iloc[7:19].copy()
    
    # 2. Pembersihan Data Desa (Sumbu X)
    # Kita pastikan kolom Desa bersih dari nilai non-string
    df_clean = pd.DataFrame()
    df_clean['Desa'] = df_data.iloc[:, 1].apply(lambda x: str(x).strip() if pd.notnull(x) else "NAN")
    
    # Buang baris yang bukan nama desa asli (NAN, 0, dsb)
    df_clean = df_clean[~df_clean['Desa'].isin(['NAN', 'nan', 'NaN', '0', 'None', '', '0.0'])]

    # 3. Ekstraksi Nilai Numerik
    # Indeks kolom: 2=Sasaran, 5=Lalu, 6=Ini, 7=Kum
    cols = {'Sasaran': 2, 'Lalu': 5, 'Ini': 6, 'Kum': 7}
    for name, idx in cols.items():
        # Align data berdasarkan index yang sudah difilter di df_clean
        df_clean[name] = pd.to_numeric(df_data.iloc[:, idx], errors='coerce').fillna(0)

    # 4. Kalkulasi Persentase & Status
    target_januari = 8.33
    df_clean['Kum_%'] = round((df_clean['Kum'] / df_clean['Sasaran']) * 100, 2)
    df_clean['Ini_%'] = round((df_clean['Ini'] / df_clean['Sasaran']) * 100, 2)
    df_clean['Lalu_%'] = round((df_clean['Lalu'] / df_clean['Sasaran']) * 100, 2)
    
    status_results = []
    for _, row in df_clean.iterrows():
        tren, stat = tentukan_status(row['Kum_%'], target_januari, row['Lalu_%'], row['Ini_%'])
        status_results.append((tren, stat))
    
    df_clean['Tren'], df_clean['Status'] = zip(*status_results)

    # 5. Visualisasi Dashboard
    print("Menghasilkan Grafik...")
    plt.figure(figsize=(12, 7))
    
    # Pastikan label sumbu X adalah list of strings yang murni
    x_labels = df_clean['Desa'].tolist()
    y_values = df_clean['Kum_%'].tolist()
    
    bars = plt.bar(x_labels, y_values, color='skyblue', edgecolor='navy', label='Capaian Kumulatif (%)')
    plt.axhline(y=target_januari, color='red', linestyle='--', linewidth=2, label=f'Target ({target_januari}%)')

    # Tambahkan angka di atas batang
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{height}%', ha='center', va='bottom', fontweight='bold')

    plt.title('PWS-KIA K1: Capaian Kumulatif per Desa\nPuskesmas Pecangaan - Januari 2026', fontsize=14, pad=20)
    plt.ylabel('Persentase (%)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    # Output file
    plt.savefig('Dashboard_PWS_KIA_K1.png', dpi=300)
    df_clean.to_excel('Laporan_Final_PWS_KIA.xlsx', index=False)
    
    print("\nBERHASIL!")
    print(f"File Dashboard_PWS_KIA_K1.png telah dibuat.")
    print(df_clean[['Desa', 'Kum_%', 'Status']].sort_values(by='Kum_%', ascending=False))

if __name__ == "__main__":
    main()