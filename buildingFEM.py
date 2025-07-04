import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

# Define the problem: 2D linear elastic square domain
# Domain: 1x1 square, meshed with triangular elements
# Material: Young's modulus E = 1e6, Poisson's ratio nu = 0.3
# Boundary conditions: Left edge fixed (x=0), right edge with traction (x=1)

def generate_mesh(nx, ny, Lx=1.0, Ly=1.0):
    """Generate a 2D triangular mesh for a rectangular domain."""
    nodes = []
    elements = []
    dx, dy = Lx / nx, Ly / ny
    
    # Create nodes
    for j in range(ny + 1):
        for i in range(nx + 1):
            nodes.append([i * dx, j * dy])
    
    # Create triangular elements (two triangles per quad)
    for j in range(ny):
        for i in range(nx):
            n0 = i + j * (nx + 1)
            n1 = n0 + 1
            n2 = n0 + (nx + 1)
            n3 = n2 + 1
            # Lower triangle
            elements.append([n0, n1, n2])
            # Upper triangle
            elements.append([n1, n3, n2])
    
    return np.array(nodes), np.array(elements)

def compute_element_stiffness(nodes, element, E, nu):
    """Compute the stiffness matrix for a single triangular element."""
    # Nodal coordinates
    x = nodes[element, 0]
    y = nodes[element, 1]
    
    # Area of triangle
    A = 0.5 * abs(x[0] * (y[1] - y[2]) + x[1] * (y[2] - y[0]) + x[2] * (y[0] - y[1]))
    
    # Shape function derivatives (B matrix)
    B = np.zeros((3, 6))  # Strain-displacement matrix
    B[0, 0] = y[1] - y[2]
    B[0, 2] = y[2] - y[0]
    B[0, 4] = y[0] - y[1]
    B[1, 1] = x[2] - x[1]
    B[1, 3] = x[0] - x[2]
    B[1, 5] = x[1] - x[0]
    B[2, 0] = B[1, 1]
    B[2, 1] = B[0, 0]
    B[2, 2] = B[1, 3]
    B[2, 3] = B[0, 2]
    B[2, 4] = B[1, 5]
    B[2, 5] = B[0, 4]
    B /= (2 * A)
    
    # Material matrix (plane stress)
    C = (E / (1 - nu**2)) * np.array([
        [1, nu, 0],
        [nu, 1, 0],
        [0, 0, (1 - nu) / 2]
    ])
    
    # Element stiffness matrix
    K_e = A * B.T @ C @ B
    return K_e

def assemble_global_stiffness(nodes, elements, E, nu):
    """Assemble the global stiffness matrix."""
    n_nodes = len(nodes)
    n_dofs = n_nodes * 2  # 2 DOFs per node (ux, uy)
    data, row, col = [], [], []
    
    for element in elements:
        K_e = compute_element_stiffness(nodes, element, E, nu)
        dofs = np.array([2 * element[0], 2 * element[0] + 1,
                         2 * element[1], 2 * element[1] + 1,
                         2 * element[2], 2 * element[2] + 1])
        
        for i in range(6):
            for j in range(6):
                data.append(K_e[i, j])
                row.append(dofs[i])
                col.append(dofs[j])
    
    K = coo_matrix((data, (row, col)), shape=(n_dofs, n_dofs)).tocsr()
    return K

def apply_boundary_conditions(K, nodes, nx, ny, traction=1000.0):
    """Apply Dirichlet (fixed left edge) and Neumann (traction on right edge) conditions."""
    n_nodes = len(nodes)
    n_dofs = n_nodes * 2
    f = np.zeros(n_dofs)
    
    # Fixed left edge (x = 0)
    fixed_dofs = []
    for i in range(ny + 1):
        node = i * (nx + 1)
        fixed_dofs.extend([2 * node, 2 * node + 1])
    
    # Apply traction on right edge (x = 1) in x-direction
    for i in range(ny + 1):
        node = i * (nx + 1) + nx
        f[2 * node] = traction / ny  # Uniform traction in x-direction
    
    # Modify stiffness matrix for Dirichlet BCs
    for dof in fixed_dofs:
        K[dof, :] = 0
        K[:, dof] = 0
        K[dof, dof] = 1
        f[dof] = 0
    
    return K, f

def solve_fem(nodes, elements, E, nu, nx, ny, traction):
    """Solve the FEM problem."""
    K = assemble_global_stiffness(nodes, elements, E, nu)
    K, f = apply_boundary_conditions(K, nodes, nx, ny, traction)
    u = spsolve(K, f)
    return u

def plot_results(nodes, elements, u, scale_factor=100):
    """Plot the deformed mesh."""
    deformed_nodes = nodes.copy()
    deformed_nodes[:, 0] += u[::2] * scale_factor  # Scale displacements for visibility
    deformed_nodes[:, 1] += u[1::2] * scale_factor
    
    plt.figure()
    for element in elements:
        x = np.append(nodes[element, 0], nodes[element[0], 0])
        y = np.append(nodes[element, 1], nodes[element[0], 1])
        plt.plot(x, y, 'b-', alpha=0.3, label='Original' if element[0] == 0 else "")
        x_def = np.append(deformed_nodes[element, 0], deformed_nodes[element[0], 0])
        y_def = np.append(deformed_nodes[element, 1], deformed_nodes[element[0], 1])
        plt.plot(x_def, y_def, 'r-', label='Deformed' if element[0] == 0 else "")
    plt.title('Original (blue) vs Deformed (red) Mesh')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.axis('equal')
    plt.show()

# Main script
if __name__ == "__main__":
    # Parameters
    nx, ny = 2, 2  # Small mesh for testing
    E, nu = 1e6, 0.3  # Material properties
    traction = 10000.0  # Increased traction for visible deformation
    
    # Generate mesh
    nodes, elements = generate_mesh(nx, ny)
    
    # Solve FEM
    u = solve_fem(nodes, elements, E, nu, nx, ny, traction)
    
    # Plot results
    plot_results(nodes, elements, u)