import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import string

st.title("2-Machine Flowshop Scheduler")

# 1. Pengaturan Mesin
col1, col2 = st.columns(2)
with col1:
    m1_name = st.text_input("Nama Mesin 1", value="Mesin 1")
with col2:
    m2_name = st.text_input("Nama Mesin 2", value="Mesin 2")

# 2. Input Jumlah Job
n = st.number_input("Masukkan jumlah job", min_value=1, max_value=26, value=3)

# Input Waktu Proses per Job
jobs = {}
alphabet = string.ascii_uppercase

st.subheader("Input Waktu Proses")
for i in range(n):
    job_name = alphabet[i]
    c1, c2 = st.columns(2)
    with c1:
        t1 = st.number_input(f"Waktu '{job_name}' di {m1_name}", min_value=1, value=5, key=f"t1_{i}")
    with c2:
        t2 = st.number_input(f"Waktu '{job_name}' di {m2_name}", min_value=1, value=5, key=f"t2_{i}")
    jobs[job_name] = [t1, t2]

# 3. Logika (Tombol Proses)
if st.button("Hitung Jadwal"):
    # Urutan sederhana berdasarkan waktu M1 (bisa diubah ke algoritma Johnson's)
    sequence = sorted(jobs.keys(), key=lambda x: jobs[x][0])
    
    table_data = []
    w1_time, w2_time = 0, 0
    all_times = {0}
    
    for job in sequence:
        start_w1 = w1_time
        end_w1 = start_w1 + jobs[job][0]
        
        start_w2 = max(end_w1, w2_time)
        end_w2 = start_w2 + jobs[job][1]
        
        table_data.append({'Job': job, 'M1 Start': start_w1, 'M1 End': end_w1, 
                           'M2 Start': start_w2, 'M2 End': end_w2})
        
        all_times.update([start_w1, end_w1, start_w2, end_w2])
        w1_time, w2_time = end_w1, end_w2

    df = pd.DataFrame(table_data)
    
    st.write("### Tabel Sequential Times")
    st.table(df)
    st.metric("Makespan Total", w2_time)

    # 6. Plotting
    fig, ax = plt.subplots(figsize=(10, 4))
    
    for _, row in df.iterrows():
        # Plot Mesin 1
        ax.barh(m1_name, row['M1 End'] - row['M1 Start'], left=row['M1 Start'], color='skyblue', edgecolor='black')
        ax.text((row['M1 Start'] + row['M1 End'])/2, m1_name, row['Job'], ha='center', va='center')
        
        # Idle di Mesin 2
        if row['M2 Start'] > row['M1 End']:
            ax.barh(m2_name, row['M2 Start'] - row['M1 End'], left=row['M1 End'], color='lightgrey', hatch='//', edgecolor='grey')
        
        # Plot Mesin 2
        ax.barh(m2_name, row['M2 End'] - row['M2 Start'], left=row['M2 Start'], color='salmon', edgecolor='black')
        ax.text((row['M2 Start'] + row['M2 End'])/2, m2_name, row['Job'], ha='center', va='center')

    ax.set_title(f"Gantt Chart (Makespan: {w2_time})")
    ax.set_xlabel("Waktu")
    st.pyplot(fig)
