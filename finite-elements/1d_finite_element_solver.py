# =============================================================================
# 1 dimensional finite element solver for computing the temperature of a sytem
# given a force vector F(x).
#
# The local stiffness matrix is defined as following:
# k_ab = ((-1) ** (a+b)) / x_A+1 - x_A
# x_A+1 and x_A are the global node positions
#
# =============================================================================

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.size'] = 16
rcParams['figure.figsize'] = (12, 6)


# =============================================================================
# Functions
# =============================================================================

def f_function(x):
    """
    The function used when computing the local force matrix.

    Parameters
    ----------
    x: float.
        The coordinate location of a node.
    """
    return x * x


def local_stiffness(local_nodes):
    """
    Compute the local stiffness matrix for an element with nodes local_nodes.

    Parameters
    ----------
    local_nodes: 1 x 2 array of floats.
        The coordinate locations of the nodes which define an element.

    Returns
    -------
    k: 2 x 2 array of floats.
        The stiffness coefficents of an element.
    """

    N = len(local_nodes)
    k = np.zeros((N, N))

    for a in range(N):
        for b in range(N):
            k[a, b] = ((-1) ** (a + b)) / (local_nodes[1] - local_nodes[0])

    return k


def local_force(local_nodes):
    """
    Compute the local force vector for an element.

    Parameters
    ----------
    local_nodes: 1 x 2 array of floats.
        The coordinate locations of the nodes which define an element.

    Returns
    -------
    f: 2 x 2 array of floats.
        The force vector of an element.
    """

    f = ((local_nodes[1] - local_nodes[0])/6) * \
        np.array([2 * f_function(local_nodes[0]) + f_function(local_nodes[1]),
                  f_function(local_nodes[0]) + 2 * f_function(local_nodes[1])])

    return f


def finite_element(interval, N_Elements):
    """
    Compute the temperatre of a 1D mesh using finite elements. This algorithm
    first creates a grid and then creates the location matrix to link the nodes
    to elements.

    The local force and stiffness matrices are then computed and added to the
    global force and stifness matrices. To solve for temperature, the linear
    system k * T = F is solved.

    Parameters
    ----------
    interval: list of 2 floats.
        The start and end point of the finite element mesh.
    N_Elements: float.
        The number of elements in the finite element mesh.

    Returns
    -------
    x: 1 x N_Elements array of floats.
        The coordinate locations of the elements in the mesh.
    T: 1 x N_Elements array of floats.
        The temperature of each element.
    """

    # x are the global node locations
    x = np.linspace(interval[0], interval[1], N_Elements + 1)

    # set up location matrix
    LM = np.zeros((2, N_Elements), dtype=np.int)
    for e in range(N_Elements):
        LM[0, e] = e      # left hand node
        LM[1, e] = e+1    # right hand node
        # the columns correspond to each individual elements
        # the rows are the values for the nodes which relate to the element

    LM[1, -1] = -1  # right hand node of the final element is not considered
    # due to the boundary conditions

    # create arrays for the global stiffness matrix and force vector
    K_global = np.zeros((N_Elements, N_Elements))
    F_global = np.zeros(N_Elements)

    # compute the global matrices
    for element in range(N_Elements):
        # for each element, look at the left and right node..?
        kab = local_stiffness(x[element:element + 2])
        fab = local_force(x[element:element + 2])
        for a in range(2):
            A = LM[a, element]
            for b in range(2):
                B = LM[b, element]
                if (A >= 0) and (B >= 0):
                    K_global[A, B] += kab[a, b]
            if (A >= 0):
                F_global[A] += fab[a]

    # use numpy.linalg.solve to solve the linear equation and find T_A, i.e.
    # the temperature at each node
    T_A = np.linalg.solve(K_global, F_global)

    T = np.hstack((T_A, [0]))

    return x, T


# =============================================================================
# Plot the results
# =============================================================================

nodes, T = finite_element([0, 1], 100)

# find the exact solution
x_exact = np.linspace(0, 1)
T_exact = (1 - x_exact ** 4)/12

# plot the exact solution against the finite element solution
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(nodes, T, label='Finite element solution')
ax1.plot(x_exact, T_exact, '--', label='Exact solution')
ax1.set_xlim(0, 1)
ax1.set_ylim(0)
ax1.set_xlabel('$x$')
ax1.set_ylabel('Temperature, $T$')
ax1.legend()
plt.show()
