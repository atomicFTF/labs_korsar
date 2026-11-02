import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

script_dir = Path(__file__).parent
file_path = script_dir / "result" / "out" / "_sensor_1.dat"

if not file_path.exists():
    file_path = script_dir / "result" / "_sensor_1.dat"

try:
    data = pd.read_csv(file_path, sep=r"\s+", encoding="utf-8-sig")
    kgs_list = np.sort(data['d3'].unique())
    
    # =========================================================
    # ГРАФИК 1: Сравнение реальной и идеальной (для КГС=140)
    # =========================================================
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    
    nominal_kgs = 140.0
    if nominal_kgs not in kgs_list:
        nominal_kgs = kgs_list[len(kgs_list)//2]
        
    df_nom = data[data['d3'] == nominal_kgs]
        
    s_raw = df_nom['d1'].values
    q_raw = df_nom['d2'].values
    
    # Очистка от переходных процессов
    unique_s = np.unique(s_raw)
    steady_s, steady_q = [], []
    for val_s in unique_s:
        if val_s == 0.0:
            steady_s.append(0.0)
            steady_q.append(0.0) # В начале расход всегда 0
            continue
            
        mask = (s_raw == val_s)
        q_step = q_raw[mask]
        if len(q_step) > 5:
            steady_q.append(np.mean(q_step[-int(len(q_step)*0.2):]))
        else:
            steady_q.append(q_step[-1])
        steady_s.append(val_s)
        
    steady_s = np.array(steady_s)
    steady_q = np.array(steady_q)
    
    # Сглаживание полиномом 4-й степени (как в самом первом успешном варианте)
    z = np.polyfit(steady_s, steady_q, 4)
    p = np.poly1d(z)
    
    # Строим только по реальному диапазону s
    s_smooth = np.linspace(steady_s.min(), steady_s.max(), 300)
    q_smooth = p(s_smooth)
    q_smooth = np.maximum(q_smooth, 0)
    
    q_max = steady_q.max()
    q_rel = q_smooth / q_max
    
    ax1.plot(s_smooth, q_rel, color='tab:blue', linewidth=3, label='Расходная (реальная)')
    ax1.plot(s_smooth, s_smooth, color='tab:red', linestyle='--', linewidth=2.5, label='Пропускная (идеальная)')
    
    ax1.set_title(f'Сравнение характеристик РК (в относительных единицах, КГС={nominal_kgs:g})', fontsize=14)
    ax1.set_xlabel('Относительное положение клапана (s)', fontsize=12)
    ax1.set_ylabel('Относительный расход (q/q_max)', fontsize=12)
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.5)
    
    fig1.tight_layout()
    fig1.savefig(script_dir / "graph1_compare.png", dpi=200)
    print(f"График 1 сохранен: graph1_compare.png")

    # =========================================================
    # ГРАФИК 2: Влияние КГС (веер кривых)
    # =========================================================
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    colors = plt.cm.plasma(np.linspace(0, 1, len(kgs_list)))
    
    for kgs_val, color in zip(kgs_list, colors):
        df_kgs = data[data['d3'] == kgs_val]
        s_raw = df_kgs['d1'].values
        q_raw = df_kgs['d2'].values
        
        unique_s = np.unique(s_raw)
        steady_s, steady_q = [], []
        for val_s in unique_s:
            if val_s == 0.0:
                steady_s.append(0.0)
                steady_q.append(0.0)
                continue
                
            mask = (s_raw == val_s)
            q_step = q_raw[mask]
            if len(q_step) > 5:
                steady_q.append(np.mean(q_step[-int(len(q_step)*0.2):]))
            else:
                steady_q.append(q_step[-1])
            steady_s.append(val_s)
            
        steady_s = np.array(steady_s)
        steady_q = np.array(steady_q)
        
        z = np.polyfit(steady_s, steady_q, 4)
        p = np.poly1d(z)
        s_smooth = np.linspace(steady_s.min(), steady_s.max(), 300)
        q_smooth = p(s_smooth)
        q_smooth = np.maximum(q_smooth, 0)
        
        ax2.plot(s_smooth, q_smooth, color=color, linewidth=2.5, label=f'КГС = {kgs_val:g}')

    ax2.set_title('Влияние сопротивления сети (КГС) на характеристику РК', fontsize=14)
    ax2.set_xlabel('Относительное положение клапана (s)', fontsize=12)
    ax2.set_ylabel('Расход, кг/с', fontsize=12)
    ax2.legend(fontsize=12, title="Модуль системы", title_fontsize=12)
    ax2.grid(True, alpha=0.5)

    fig2.tight_layout()
    fig2.savefig(script_dir / "graph2_kgs.png", dpi=200)
    print(f"График 2 сохранен: graph2_kgs.png")
    
    plt.show()

except Exception as e:
    print(f"Ошибка: {e}")