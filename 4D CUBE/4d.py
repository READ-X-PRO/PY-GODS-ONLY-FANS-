import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Define a 4D hypercube
def hypercube_vertices(size=1):
    vertices = np.array([
        [x, y, z, w]
        for x in [-size, size]
        for y in [-size, size]
        for z in [-size, size]
        for w in [-size, size]
    ])
    return vertices

# Define rotation matrices (example: rotation around xy plane)
def rotation_xy(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

# Projection (simple orthographic)
def project(vertices):
    return vertices[:, :3]  # Drop the 4th dimension

# Set up plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([-2, 2])
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("4D Hypercube Projection")

# Initialize hypercube and plot
vertices = hypercube_vertices()
lines = []
for i in range(vertices.shape[0]):
    for j in range(i + 1, vertices.shape[0]):
        # Check if vertices are connected (share 3 coordinates)
        if np.sum(vertices[i, :-1] == vertices[j, :-1]) == 3 or \
           np.sum(vertices[i, 1:] == vertices[j, 1:]) == 3 or \
           np.sum(vertices[i, [0,1,3]] == vertices[j, [0,1,3]]) == 3 or \
           np.sum(vertices[i, [0,2,3]] == vertices[j, [0,2,3]]) == 3 or \
           np.sum(vertices[i, [1,2,3]] == vertices[j, [1,2,3]]) == 3:
            line, = ax.plot([], [], [], 'b-')
            lines.append((line, i, j))

# Animation function
def animate(frame):
    angle = frame * 0.02
    rotation_matrix = rotation_xy(angle)
    rotated_vertices = np.dot(vertices, rotation_matrix)
    projected_vertices = project(rotated_vertices)
    
    for line, i, j in lines:
        line.set_data_3d(projected_vertices[[i, j], 0],
                         projected_vertices[[i, j], 1],
                         projected_vertices[[i, j], 2])
    return [line for line, _, _ in lines]

# Create animation
ani = FuncAnimation(fig, animate, frames=200, blit=False, repeat=True)
plt.show()