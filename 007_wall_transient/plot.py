import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# 1. ЧТЕНИЕ ДАННЫХ
# =========================================================
print("Чтение файла result...")
try:
    with open('result', 'r') as f:
        numbers = []
        for line in f:
            if line.strip():
                numbers.extend([float(x) for x in line.split()])
except FileNotFoundError:
    print("ОШИБКА: Файл result не найден!")
    exit()

data = np.array(numbers)
num_steps = len(data) // 12
data = data[:num_steps * 12].reshape((num_steps, 12))

tau = data[:, 0]
T_num = data[:, 1:]

L = 0.020
x_coords = np.linspace(0, L, 11)
X = x_coords / L
x_mm = x_coords * 1000

lam = 16.0
a = lam / (7800.0 * 500.0)
T0 = 293.15
Tb = 393.15
dT_max = Tb - T0
A_s = 1.0

# =========================================================
# 2. ОПРЕДЕЛЕНИЕ ВАРИАНТА (А или В)
# =========================================================
T_right_end = T_num[-1, -1]
if abs(T_right_end - T0) < 10.0:
    variant = 'A'
    print("--- ОПРЕДЕЛЕН ВАРИАНТ А (правая стенка = T0) ---")
else:
    variant = 'B'
    print("--- ОПРЕДЕЛЕН ВАРИАНТ В (адиабата) ---")

# =========================================================
# 3. АНАЛИТИКА
# =========================================================
def theta_A(X, Fo):
    theta = 1.0 - X
    for n in range(1, 100):
        term = (2.0 / (n * np.pi)) * np.sin(n * np.pi * X) * np.exp(-(n**2) * (np.pi**2) * Fo)
        theta -= term
    return theta

def theta_B(X, Fo):
    theta = 1.0
    for n in range(1, 100):
        mu_n = (n - 0.5) * np.pi
        term = (2.0 / mu_n) * np.sin(mu_n * X) * np.exp(-(mu_n**2) * Fo)
        theta -= term
    return theta

if variant == 'A':
    theta_func = theta_A
    def q_analyt_A(Fo):
        dtheta_dX = -1.0
        for n in range(1, 100):
            dtheta_dX -= 2.0 * np.exp(-(n**2) * (np.pi**2) * Fo)
        return - (lam / L) * dT_max * dtheta_dX
    q_analyt_func = q_analyt_A
    q_stat = 80000
else:
    theta_func = theta_B
    def q_analyt_B(Fo):
        dtheta_dX = 0.0
        for n in range(1, 100):
            mu_n = (n - 0.5) * np.pi
            dtheta_dX -= 2.0 * np.exp(-(mu_n**2) * Fo)
        return - (lam / L) * dT_max * dtheta_dX
    q_analyt_func = q_analyt_B
    q_stat = 0

# =========================================================
# 4. ТАБЛИЦА 1: ОБЩАЯ ПОГРЕШНОСТЬ
# =========================================================
print("\n" + "="*70)
print(f"ТАБЛИЦА 1: ОБЩАЯ ПОГРЕШНОСТЬ (для k=11, Вариант {variant})")
print("="*70)
print(f"{'Время, с':<10} | {'Макс. абс. погр., К':<20} | {'Отн. погрешность, %':<20}")
print("-" * 70)

times_to_check = [1.0, 5.0, 20.0, 100.0]
for t_target in times_to_check:
    idx = np.argmin(np.abs(tau - t_target))
    t_actual = tau[idx]
    T_n = T_num[idx, :]
    Fo = a * t_actual / (L**2)
    T_a = T0 + theta_func(X, Fo) * dT_max
    abs_diff = np.abs(T_n - T_a)
    max_abs_err = np.max(abs_diff)
    max_rel_err = (max_abs_err / dT_max) * 100
    print(f"{t_actual:<10.1f} | {max_abs_err:<20.4f} | {max_rel_err:<20.4f}")
print("="*70 + "\n")

# =========================================================
# 5. ТАБЛИЦА 2: СХОДИМОСТЬ (t=20 с, x=10 мм)
# =========================================================
t_check = 20.0
center_idx = 5
idx = np.argmin(np.abs(tau - t_check))
t_actual = tau[idx]
T_center_num = T_num[idx, center_idx]
Fo = a * t_actual / (L**2)
T_center_analyt = T0 + theta_func(0.5, Fo) * dT_max
error = np.abs(T_center_num - T_center_analyt) / dT_max * 100

print("="*70)
print(f"ТАБЛИЦА 2: СХОДИМОСТЬ (Время t = {t_actual:.1f} с, x = 10 мм, Вариант {variant})")
print("="*70)
print(f"Температура в центре (Числ. КОРСАР): {T_center_num:.2f} К")
print(f"Температура в центре (Аналитика):    {T_center_analyt:.2f} К")
print(f"Относительная погрешность:           {error:.2f} %")
print("="*70 + "\n")

# =========================================================
# 6. ТЕПЛОВОЙ ПОТОК
# =========================================================
dx = L / 10.0
q_left_num = -lam * (T_num[:, 1] - T_num[:, 0]) / dx
q_right_num = -lam * (T_num[:, -1] - T_num[:, -2]) / dx
q_left_analyt = np.array([q_analyt_func(a * t / (L**2)) for t in tau])
q_right_analyt = -q_left_analyt

times_to_plot = [1.0, 5.0, 20.0, 100.0]
colors = ['blue', 'orange', 'green', 'red']

# =========================================================
# 7. ГРАФИК 1: РАЗМЕРНЫЙ ПРОФИЛЬ T(x)
# =========================================================
print(f"Построение графика 1 (Вариант {variant})...")
plt.figure(figsize=(10, 6))
for i, t_target in enumerate(times_to_plot):
    idx_plot = np.argmin(np.abs(tau - t_target))
    t_plot = tau[idx_plot]
    plt.plot(x_mm, T_num[idx_plot, :], marker='o', color=colors[i], label=f'Числ. t={t_plot:.1f} с')
    Fo = a * t_plot / (L**2)
    T_analyt = T0 + theta_func(X, Fo) * dT_max
    plt.plot(x_mm, T_analyt, '--', color=colors[i], label=f'Аналит. t={t_plot:.1f} с')
plt.xlabel('Координата x, мм')
plt.ylabel('Температура T, K')
plt.title(f'Размерные профили температуры (Вариант {variant})')
plt.legend()
plt.grid(True)
plt.savefig(f'plot_{variant}_1.PNG', dpi=300)

# =========================================================
# 8. ГРАФИК 2: БЕЗРАЗМЕРНЫЙ ПРОФИЛЬ θ(X)
# =========================================================
print(f"Построение графика 2 (Вариант {variant})...")
plt.figure(figsize=(10, 6))
for i, t_target in enumerate(times_to_plot):
    idx_plot = np.argmin(np.abs(tau - t_target))
    t_plot = tau[idx_plot]
    theta_num = (T_num[idx_plot, :] - T0) / dT_max
    plt.plot(X, theta_num, marker='o', color=colors[i], label=f'Числ. t={t_plot:.1f} с')
    Fo = a * t_plot / (L**2)
    theta_analyt = theta_func(X, Fo)
    plt.plot(X, theta_analyt, '--', color=colors[i], label=f'Аналит. t={t_plot:.1f} с')
plt.xlabel('Безразмерная координата X = x/L')
plt.ylabel('Безразмерная температура θ')
plt.title(f'Безразмерные профили температуры (Вариант {variant})')
plt.legend()
plt.grid(True)
plt.savefig(f'plot_{variant}_2.PNG', dpi=300)

# =========================================================
# 9. ГРАФИК 3: ВРЕМЕННАЯ ЗАВИСИМОСТЬ θ(t)
# =========================================================
print(f"Построение графика 3 (Вариант {variant})...")
plt.figure(figsize=(10, 6))
theta_center_num = (T_num[:, center_idx] - T0) / dT_max
plt.plot(tau, theta_center_num, 'o', label='Численное (КОРСАР)', markersize=3)
Fo_array = a * tau / (L**2)
theta_center_analyt = np.array([theta_func(0.5, fo) for fo in Fo_array])
plt.plot(tau, theta_center_analyt, '-', label='Аналитическое', linewidth=2)
plt.xlabel('Время t, с')
plt.ylabel('Безразмерная температура θ в центре')
plt.title(f'Временная зависимость температуры в центре стенки (Вариант {variant})')
plt.legend()
plt.grid(True)
plt.savefig(f'plot_{variant}_3.PNG', dpi=300)

# =========================================================
# 10. ГРАФИК 4: ТЕПЛОВОЙ ПОТОК НА ОБЕИХ СТЕНКАХ
# =========================================================
print(f"Построение графика 4 (Вариант {variant})...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

start_idx = 10 if variant == 'A' else 100
tau_plot = tau[start_idx:]

ax1.plot(tau_plot, q_left_num[start_idx:], 'o', label='Числ. левая стенка', markersize=3)
ax1.plot(tau_plot, q_left_analyt[start_idx:], '-', label='Аналит. левая стенка', linewidth=2)
ax1.plot(tau_plot, q_right_num[start_idx:], 's', label='Числ. правая стенка', markersize=3, alpha=0.5)
ax1.plot(tau_plot, q_right_analyt[start_idx:], '--', label='Аналит. правая стенка', linewidth=2, alpha=0.5)
ax1.axhline(y=q_stat, color='r', linestyle=':', label=f'Стационар ({q_stat:.0f})')
ax1.set_ylabel('Плотность теплового потока q, Вт/м²')
ax1.set_title(f'Тепловой поток на обеих стенках (Вариант {variant})')
ax1.legend()
ax1.grid(True)

ax2.plot(tau_plot, q_left_num[start_idx:] * A_s, 'o', label='Числ. левая (Q)', markersize=3)
ax2.plot(tau_plot, q_right_num[start_idx:] * A_s, 's', label='Числ. правая (Q)', markersize=3, alpha=0.5)
ax2.axhline(y=q_stat * A_s, color='r', linestyle=':', label=f'Стационар ({q_stat:.0f})')
ax2.set_xlabel('Время t, с')
ax2.set_ylabel('Мощность Q, Вт')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig(f'plot_{variant}_4.PNG', dpi=300)

print(f"\nВсе графики сохранены в файлы plot_{variant}_1.PNG ... plot_{variant}_4.PNG")
plt.show()