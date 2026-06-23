import matplotlib.pyplot as plt
import pandas as pd
import string

def solve_2_machine_flowshop():
    # 1. Pengaturan Mesin
    print("--- Pengaturan Mesin ---")
    m1_name = input("Masukkan nama Mesin 1: ")
    m2_name = input("Masukkan nama Mesin 2: ")
    
    # 2. Input Data
    try:
        n = int(input("\nMasukkan jumlah job: "))
    except ValueError:
        print("Input harus angka!")
        return

    jobs = {}
    # Membuat list abjad A-Z secara otomatis
    alphabet = string.ascii_uppercase
    
    for i in range(n):
        job_name = alphabet[i]
        print(f"\n--- Data Job {job_name} ---")
        t1 = int(input(f"Waktu proses '{job_name}' di {m1_name}: "))
        t2 = int(input(f"Waktu proses '{job_name}' di {m2_name}: "))
        jobs[job_name] = [t1, t2]

    # 3. Logika Urutan (Greedy/Johnson's Rule)
    # Untuk tujuan penjadwalan 2 mesin, kita gunakan pendekatan urutan
    # agar mesin 2 tidak terlalu lama idle.
    sequence = sorted(jobs.keys(), key=lambda x: jobs[x][0]) # Sederhana berdasarkan M1
    
    # 4. Hitung Waktu Sequential
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

    # 5. Output Tabel
    df = pd.DataFrame(table_data)
    print("\n--- Tabel Sequential Times ---")
    print(df.to_string(index=False))
    print(f"\nMakespan Total: {w2_time}")

    # 6. Plotting
    fig, ax = plt.subplots(figsize=(12, 5))
    
    for _, row in df.iterrows():
        # Plot Mesin 1
        ax.barh(m1_name, row['M1 End'] - row['M1 Start'], left=row['M1 Start'], 
                color='skyblue', edgecolor='black')
        ax.text((row['M1 Start'] + row['M1 End'])/2, m1_name, row['Job'], ha='center', va='center')
        
        # Idle di Mesin 2
        if row['M2 Start'] > row['M1 End']:
            ax.barh(m2_name, row['M2 Start'] - row['M1 End'], left=row['M1 End'], 
                    color='lightgrey', hatch='//', edgecolor='grey')
        
        # Plot Mesin 2
        ax.barh(m2_name, row['M2 End'] - row['M2 Start'], left=row['M2 Start'], 
                color='salmon', edgecolor='black')
        ax.text((row['M2 Start'] + row['M2 End'])/2, m2_name, row['Job'], ha='center', va='center')

    ax.set_xticks(sorted(list(all_times)))
    ax.set_title(f"Gantt Chart (Makespan: {w2_time})")
    ax.set_xlabel("Waktu")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    solve_2_machine_flowshop()
