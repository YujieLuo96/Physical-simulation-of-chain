import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 参数设置
n_segments = 30  # 锁链段数
length = 2.4  # 每段长度（总长 = length * n_segments）
dt = 0.01  # 时间步长
g = np.array([0, -9.81])  # 重力加速度
initial_angle = np.radians(50)  # 初始角度（弧度）
iterations = 5  # 约束投影迭代次数

# 初始化质点的位置和速度
positions = np.zeros((n_segments + 1, 2))
for i in range(n_segments + 1):
    positions[i] = [i * (length / n_segments) * np.sin(initial_angle),
                    -i * (length / n_segments) * np.cos(initial_angle)]
velocities = np.zeros_like(positions)

# 固定第一个质点
positions[0] = [0, 0]
velocities[0] = [0, 0]

# 创建图形
fig, ax = plt.subplots()
ax.set_xlim(-2, 2)
ax.set_ylim(-3, 1)
line, = ax.plot([], [], 'o-', lw=1)
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)


# 初始化动画
def init():
    line.set_data([], [])
    time_text.set_text('')
    return line, time_text


# 更新函数
def animate(frame):
    global positions, velocities

    # 应用重力
    velocities[1:] += g * dt

    # 临时更新位置
    new_positions = positions + velocities * dt

    # 约束投影
    for _ in range(iterations):
        for i in range(1, n_segments + 1):
            delta = new_positions[i] - new_positions[i - 1]
            dist = np.linalg.norm(delta)
            if dist == 0:
                continue
            correction = delta * (dist - (length / n_segments)) / dist * 0.5
            new_positions[i] -= correction
            new_positions[i - 1] += correction

        # 固定第一个质点
        new_positions[0] = positions[0]

    # 更新速度并确保第一个质点静止
    velocities = (new_positions - positions) / dt
    positions = new_positions.copy()
    velocities[0] = [0, 0]

    # 更新绘图数据
    line.set_data(positions[:, 0], positions[:, 1])
    time_text.set_text(f'Time: {frame * dt:.2f}s')
    return line, time_text


# 生成动画
ani = animation.FuncAnimation(fig, animate, frames=300,
                              init_func=init, blit=True, interval=10)

plt.show()