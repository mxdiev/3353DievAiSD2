import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline  # Для сглаживания

x_values = np.arange(0, 101, 5)
y_values = [18, 39, 70, 90, 102, 112, 119, 125, 131, 136, 141, 145, 151, 158, 166, 176, 190, 209, 240, 300, 457]
y_interval = 150

# Интерполяция: создаём сглаженную кривую
x_smooth = np.linspace(x_values.min(), x_values.max(), 300)
spline = make_interp_spline(x_values, y_values, k=3)
y_smooth = spline(x_smooth)

plt.figure(figsize=(10, 6))

# Плавная линия
plt.plot(x_smooth, y_smooth, color='blue')

# Оригинальные точки
plt.plot(x_values, y_values, 'o', color='red')

# Подписи к точкам
for x, y in zip(x_values, y_values):
    plt.text(x, y + y_interval * 0.05, f"{y} кБ", ha='center', fontsize=9)

# Настройка осей
plt.xticks(np.arange(0, 101, 5))
# plt.yticks(np.arange(0, max(y_values) + y_interval, y_interval))
plt.xlabel("Качество")
plt.ylabel("Размер файла (кБ)")
plt.title("Зависимость размера файла от качества JPEG")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()