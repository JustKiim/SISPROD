import streamlit as st
from ortools.sat.python import cp_model
import collections
import matplotlib.pyplot as plt
import numpy as np

# Konfigurasi halaman agar grafik terlihat bagus
st.set_page_config(layout="wide")

st.title("Penyelesaian Job Shop Scheduling dengan Visualisasi yang Ditingkatkan")

# Bagian Input (Sudah dioptimalkan untuk Streamlit)
st.sidebar.header("Konfigurasi Masalah")
try:
    num_jobs = st.sidebar.number_input("Jumlah Job", min_value=1, value=2, step=1)
    num_machines = st.sidebar.number_input("Jumlah Mesin", min_value=1, value=2, step=1)
except Exception:
    st.sidebar.error("Input harus berupa angka bulat positif!")
    st.stop()

machine_names = []
for i in range(num_machines):
    machine_names.append(st.sidebar.text_input(f"Nama Mesin {i+1}", value=f"M{i+1}", key=f"m_name_{i}"))

jobs_data = []
for i in range(num_jobs):
    st.subheader(f"Data Job ke-{i+1}")
    # Menggunakan alphabet seperti pada gambar contoh (B, D, A, C)
    import string
    alphabet = string.ascii_uppercase
    default_name = alphabet[i] if i < len(alphabet) else f"Job {i+1}"
    
    job_name = st.text_input(f"Nama Job ke-{i+1}", value=default_name, key=f"job_name_{i}")
    tasks = []
    
    # Gunakan baris input untuk setiap mesin agar lebih rapi
    cols = st.columns(num_machines)
    for j in range(num_machines):
        with cols[j]:
            time = st.number_input(f"Waktu {job_name} di {machine_names[j]}", min_value=1, value=5, key=f"time_{i}_{j}")
            tasks.append((j, int(time)))
    
    jobs_data.append({'name': job_name, 'tasks': tasks})

# Pemecah Masalah (Solver) - Logika tidak berubah
if st.button("Selesaikan dan Visualisasikan"):
    model = cp_model.CpModel()
    horizon = sum(task[1] for job in jobs_data for task in job['tasks'])
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)
    
    for job_id, job in enumerate(jobs_data):
        for task_id, (machine, duration) in enumerate(job['tasks']):
            start = model.new_int_var(0, horizon, f"s_{job_id}_{task_id}")
            end = model.new_int_var(0, horizon, f"e_{job_id}_{task_id}")
            interval = model.new_interval_var(start, duration, end, f"i_{job_id}_{task_id}")
            all_tasks[job_id, task_id] = {'start': start, 'end': end, 'dur': duration, 'name': job['name']}
            machine_to_intervals[machine].append(interval)

    # Batasan: Mesin tidak boleh memproses dua tugas secara bersamaan
    for m_idx in range(num_machines):
        model.add_no_overlap(machine_to_intervals[m_idx])

    # Batasan: Tugas dalam satu job harus berurutan
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job['tasks']) - 1):
            model.add(all_tasks[job_id, task_id + 1]['start'] >= all_tasks[job_id, task_id]['end'])

    # Batasan & Tujuan: Meminimalkan waktu penyelesaian total (Makespan)
    obj_var = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(obj_var, [all_tasks[job_id, len(job['tasks'])-1]['end'] for job_id, job in enumerate(jobs_data)])
    model.minimize(obj_var)
    
    solver = cp_model.CpSolver()
    if solver.solve(model) == cp_model.OPTIMAL:
        st.success(f"Makespan Optimal ditemukan: {solver.objective_value}")
        
        # --- Visualisasi Gantt Chart yang Ditingkatkan ---
        fig, ax = plt.subplots(figsize=(12, 6))
        all_event_times = {0, solver.objective_value} # Untuk label sumbu X
        
        # Daftar warna unik untuk setiap job
        colors = plt.cm.get_cmap('tab10', num_jobs)
        
        # Iterasi melalui setiap mesin
        for m_idx, m_name in enumerate(machine_names):
            tasks_on_m = []
            
            # Kumpulkan semua tugas yang dijadwalkan pada mesin ini
            for j_id in range(num_jobs):
                for t_id, (machine, dur) in enumerate(jobs_data[j_id]['tasks']):
                    if machine == m_idx:
                        s = solver.value(all_tasks[j_id, t_id]['start'])
                        e = solver.value(all_tasks[j_id, t_id]['end'])
                        tasks_on_m.append({
                            'start': s, 
                            'end': e, 
                            'name': jobs_data[j_id]['name'], 
                            'color_idx': j_id
                        })
                        all_event_times.update([s, e])
            
            # Urutkan tugas berdasarkan waktu mulai untuk penanganan idle
            tasks_on_m.sort(key=lambda x: x['start'])
            
            curr_m_time = 0
            
            # Plot setiap tugas pada mesin
            for t in tasks_on_m:
                duration = t['end'] - t['start']
                
                # Tambahkan area "Idle" jika ada kekosongan
                if t['start'] > curr_
