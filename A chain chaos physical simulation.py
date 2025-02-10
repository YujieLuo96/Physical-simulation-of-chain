import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants
g = 9.8  # Gravity (m/s^2)
L = 1.0   # Length of each stick (m)
F = 0   # Applied force (N)
dt = 0.01 # Time step (s)
t_max = 20.0  # Total simulation time (s)

# Masses of the sticks (from top to bottom: 15 kg to 1 kg)
masses = np.linspace(15, 1, 15)  # [15, 14, 13, ..., 1] kg

# Moments of inertia for each stick (I = (1/12) * m * L^2 for a stick rotating about its center)
I = (1 / 12) * masses * L**2

# Initial conditions
theta = np.array([np.pi / 4] * 15)  # Angles of the sticks (rad)
omega = np.array([0.0] * 15)        # Angular velocities of the sticks (rad/s)

# Arrays to store results
time = np.arange(0, t_max, dt)
theta_arr = np.zeros((len(time), 15))  # Angles for all sticks over time

# Function to compute derivatives (angular velocities and accelerations)
def derivatives(theta, omega, t):
    alpha = np.zeros_like(theta)  # Angular accelerations

    # Equations of motion for the 15-stick system
    # Using Lagrangian mechanics (simplified for small angles)
    for i in range(15):
        # Torque due to gravity on the current stick and all sticks below it
        torque_gravity = -masses[i] * g * (L / 2) * np.sin(theta[i])
        for j in range(i + 1, 15):
            torque_gravity += -masses[j] * g * L * np.sin(theta[j])

        # Torque due to applied force on the last stick (only for t < 1 second)
        if i == 14 and t < 1.0:
            torque_gravity += F * L * np.cos(theta[i])

        # Angular acceleration
        alpha[i] = torque_gravity / I[i]

    return omega, alpha

# Simulation loop
for i, t in enumerate(time):
    # Store current angles
    theta_arr[i] = theta

    # Compute derivatives
    omega, alpha = derivatives(theta, omega, t)

    # Update angles and angular velocities using Euler's method
    theta += omega * dt
    omega += alpha * dt

# Animation function
def animate(i):
    ax.clear()
    ax.set_xlim(-15 * L, 15 * L)
    ax.set_ylim(-15 * L, 15 * L)

    # Compute stick positions
    x = [0]  # Fixed point
    y = [0]
    for j in range(15):
        x.append(x[j] + L * np.sin(theta_arr[i, j]))
        y.append(y[j] - L * np.cos(theta_arr[i, j]))

    # Plot sticks
    colors = plt.cm.viridis(np.linspace(0, 1, 15))  # Use a colormap for stick colors
    for j in range(15):
        ax.plot([x[j], x[j + 1]], [y[j], y[j + 1]], color=colors[j], linestyle='-', lw=2, label=f"Stick {j + 1} (m={masses[j]:.1f} kg)")

    # Plot fixed point
    ax.plot(x[0], y[0], 'ko')  # Fixed point

    # Add force arrow (only for t < 1 second)
    if time[i] < 1.0:
        ax.arrow(x[15], y[15], 0.2 * F, 0, color='orange', width=0.05, label="Applied Force")

    # Add title and legend
    ax.set_title(f"Time: {time[i]:.2f} s")
    ax.legend()

# Create animation
fig, ax = plt.subplots()
ani = FuncAnimation(fig, animate, frames=len(time), interval=dt * 1000, repeat=False)

# Show animation
plt.show()