import os; os.environ["OMP_NUM_THREADS"] = "1"
import copy
import numpy as np
from firedrake import *
from firedrake.__future__ import interpolate


class Density(object):
    """Class which defines the cdf, qdf and pdf of a function Y(X)."""

    def __init__(self, ptp, y, cdf, qdf, pdf):
        """Initialise the Density object."""
        self.ptp = ptp
        self.y = y
        self.cdf = cdf
        self.qdf = qdf
        self.pdf = pdf

        return None

    def compose(self, f, g, quadrature_degree):
        """
        Return the function composition f o g(y) = f(g(y)).

        Parameters
        ----------
        f,g : firedrake Function
            Input functions to compose.

        Returns
        -------
        f(g(y)) : firedrake Function
            Composition evaluated at points y_q of a quadrature mesh.
        """
        mesh_g = g.function_space().mesh()
        mesh_f = f.function_space().mesh()

        self.V_fgE = FiniteElement(family="Quadrature", cell="interval", degree=quadrature_degree, quad_scheme='default')
        self.V_fg = FunctionSpace(mesh=mesh_g, family=self.V_fgE)
        fg = Function(self.V_fg)

        m = self.V_fg.mesh()
        w = VectorFunctionSpace(m, self.V_fg.ufl_element())
        y_vec = assemble(interpolate(m.coordinates, w))

        y_q = [[y_i,] for y_i in y_vec.dat.data[:]]
        vom = VertexOnlyMesh(mesh_g, y_q)
        P0DG = FunctionSpace(vom, "DG", 0)
        g_vec = assemble(interpolate(g, P0DG))

        g_q = [[g_i,] for g_i in g_vec.dat.data[:]]
        vom = VertexOnlyMesh(mesh_f, g_q)
        P0DG = FunctionSpace(vom, "DG", 0)
        f_vec = assemble(interpolate(f, P0DG))

        fg.dat.data[:] = f_vec.dat.data[:]

        return fg

    def plot(self, function='CDF'):
        """Visualise the CDF, QDF and PDF using inbuilt plotting routines."""
        import matplotlib.pyplot as plt
        from firedrake.pyplot import plot

        if function == 'CDF':
            try:
                plot(self.cdf, num_sample_points=50)
                plt.title(r'CDF', fontsize=20)
                plt.ylabel(r'$F_Y$', fontsize=20)
                plt.xlabel(r'$y$', fontsize=20)
                plt.tight_layout()
                plt.grid()
                plt.show()
            except Exception as e:
                warning("Cannot plot figure. Error msg: '%s'" % e)
        elif function == 'QDF':

            try:
                plot(self.qdf, num_sample_points=50)
                plt.title(r'QDF', fontsize=20)
                plt.ylabel(r'$Q_Y$', fontsize=20)
                plt.xlabel(r'$p$', fontsize=20)
                plt.tight_layout()
                plt.grid()
                plt.show()
            except Exception as e:
                warning("Cannot plot figure. Error msg: '%s'" % e)
        elif function == 'PDF':

            try:
                plot(self.pdf, num_sample_points=50)
                plt.title(r'PDF', fontsize=20)
                plt.ylabel(r'$f_Y$', fontsize=20)
                plt.xlabel(r'$y$', fontsize=20)
                plt.tight_layout()
                plt.show()
            except Exception as e:
                warning("Cannot plot figure. Error msg: '%s'" % e)
        return None

    def evaluate(self, y):
        """Return the CDF, QDF and PDF at the point(s) y."""
        cdf_at_y = np.asarray(self.cdf.at(y))
        qdf_at_y = np.asarray(self.qdf.at(y))
        pdf_at_y = np.asarray(self.pdf.at(y))

        y_i = np.asarray(y)

        return cdf_at_y, qdf_at_y, pdf_at_y, y_i


class Ptp(object):
    """
    Ptp class - physical to probability.

    Given a user provided "function" over a physical "domain"

    Y(X) where X in Ω_X

    this class uses the fit method to return the "CDF", "QDF" & "PDF"

    F_Y(y), Q_Y(p), f_Y(y)

    over their corresponding probability space Ω_Y. The method uses
    a finite element discretisation consisting of n elements "bins".

    Parameters
    ----------
    Omega_X : dictionary
        Physical domain of the function Y(X).
    Omega_Y : dictionary
        Range of the function Y(x).
    n_elements : int
        Number of finite elements.

    Returns
    -------
    density : Density object
        A density object containing the CDF, QDF and PDF of Y(X).
    Examples
    --------
    Specify the domain size(s) & number of finite elements/bins:
    >>> ptp = Ptp(Omega_X={'x1': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=5)
    >>> x1 = ptp.x_coords()
    Compute the density of a function on this domain:
    >>> density = ptp.fit(Y=x1**2, quadrature_degree=100)
    >>> density.plot('CDF')
    """

    def __init__(self, Omega_X={'x1': (-1, 1), 'x2': (-1, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=10):
        """Intialise the Ptp object."""
        # Physical space
        self.Omega_X = Omega_X
        self.Omega_Y = Omega_Y
        self.n_e = n_elements

        # Mesh & Coordinates
        if len(self.Omega_X) == 1:
            cell_type = "interval"
            mesh_x = IntervalMesh(ncells=1, length_or_left=self.Omega_X['x1'][0], right=self.Omega_X['x1'][1])
        elif len(self.Omega_X) == 2:
            cell_type = "quadrilateral"
            mesh_x = RectangleMesh(nx=1, ny=1, Lx=self.Omega_X['x1'][1], Ly=self.Omega_X['x2'][1], originX=self.Omega_X['x1'][0], originY=self.Omega_X['x2'][0], quadrilateral=True)
        else:
            raise ValueError('The domain Ω must be 1D or 2D \n')

        self.m_y = IntervalMesh(ncells=self.n_e, length_or_left=self.Omega_Y['Y'][0], right=self.Omega_Y['Y'][1])
        self.m_yx = ExtrudedMesh(mesh_x, layers=self.n_e, layer_height=1./self.n_e, extrusion_type='uniform')

        # Finite-Element
        self.R_FE = FiniteElement(family="DG", cell=cell_type, degree=0, variant="equispaced")
        self.V_FE = FiniteElement(family="DG", cell="interval", degree=1, variant="equispaced")
        self.V_QE = FiniteElement(family="CG", cell="interval", degree=1, variant="equispaced")
        self.V_fE = FiniteElement(family="CG", cell="interval", degree=1, variant="equispaced")
        # Function-space
        self.V_F = FunctionSpace(mesh=self.m_y, family=self.V_FE)
        T_element = TensorProductElement(self.R_FE, self.V_FE)
        self.V_F_hat = FunctionSpace(mesh=self.m_yx, family=T_element)
        self.V_f = FunctionSpace(mesh=self.m_y, family=self.V_fE)

    def y_coord(self):
        """Return the y coordinate on the interval mesh."""
        return SpatialCoordinate(self.m_y)[0]

    def xy_coords(self):
        """Return the X & Y co-ordinates of the extended mesh."""
        return SpatialCoordinate(self.m_yx)

    def x_coords(self):
        """Return the co-ordinates of X=(x1,x2)."""
        if len(self.Omega_X) == 1:
            x1, _ = self.xy_coords()
            return x1
        elif len(self.Omega_X) == 2:
            x1, x2, _ = self.xy_coords()
            return x1, x2

    def map(self, Y):
        """Map Y(x) in Ω_x to Y(X) in [0,1]."""
        return Y/(self.Omega_Y['Y'][1]-self.Omega_Y['Y'][0]) - self.Omega_Y['Y'][0]/(self.Omega_Y['Y'][1]-self.Omega_Y['Y'][0])

    def indicator(self, Y):
        """Apply the indicator function I(y,X) to the random function Y(X)."""
        if len(self.Omega_X) == 1:
            _, y = self.xy_coords()
        elif len(self.Omega_X) == 2:
            _, _, y = self.xy_coords()
        return conditional(Y < y, 1, 0)

    def cdf(self, Y, quadrature_degree):
        """Return the CDF F_Y(y) of the random function Y(X)."""
        # Define trial & test functions on V_F_hat
        u = TrialFunction(self.V_F_hat)
        v = TestFunction(self.V_F_hat)

        # Construct the linear & bilinear forms
        a = inner(u, v) * dx
        L = inner(self.indicator(Y), v) * dx(degree=quadrature_degree)

        # Solve for F_hat
        F_hat = Function(self.V_F_hat)
        solve(a == L, F_hat)
        
        # Recover F_Y(y) in V_F
        F = Function(self.V_F)

        # Sort a linear function in ascending order
        # this creates a DOF map which matches
        # the extended mesh which are in ascending order
        y = self.y_coord()
        ys = assemble(interpolate(y, self.V_F))
        indx = np.argsort(ys.dat.data)

        # Pass F_hat into F
        F.dat.data[indx] = F_hat.dat.data[:]

        # Apply a slope limiter to F
        F = self.slope_limiter(F)

        # Check CDF properties
        if abs(assemble(F*ds) - 1) > 1e-02:
            print("Calculated F(+∞) - F(-∞) should equal 1, got %e. Check the domain of Ω_Y and the quadrature_degree specified."%assemble(F*ds))
            #raise ValueError("Calculated F(+∞) - F(-∞) should equal 1, got %e. Check the domain of Ω_Y and the quadrature_degree specified."%Surf_int)

        return F

    def qdf(self, F):
        """Return the QDF Q_Y(p) of Y(x) by inverting F_Y(y) = p."""
        # (1) Construct the non-uniform domain Ω_p
        # Obtain dofs F_i = F(z_i) from the CDF
        F_i = F.dat.data[:]

        # We extend Ω_p to include the endpoints 0,1
        # As F(y=0) ≠ 0 & F(y=1) ≠ 1 due to numerical error  
        p = np.hstack(([0], F_i, [1]))

        # Make a 1D mesh whose vertices are given by the p values
        layers = len(p[1:] - p[:-1])
        m_p = UnitIntervalMesh(ncells=layers)
        m_p.coordinates.dat.data[:] = p[:]

        # (2) Create a function Q(p) on this mesh
        V_Q = FunctionSpace(mesh=m_p, family=self.V_QE)
        Q = Function(V_Q)

        # (3) Extract the mesh coordinates of the CDF
        m_y = self.V_F.mesh()
        w = VectorFunctionSpace(m_y, self.V_F.ufl_element())
        y_m = assemble(interpolate(m_y.coordinates, w)).dat.data

        # Append the coordinates of the boundaries
        y_l = m_y.coordinates.dat.data[0]  # left endpoint
        y_r = m_y.coordinates.dat.data[-1]  # right endpoint
        y_i = np.hstack(([y_l], y_m, [y_r]))

        # Assign Q(F_i) = y_i
        Q.dat.data[:] = y_i[:]

        return Q

    def pdf(self, F):
        """Return the PDF f_Y(y) of Y(x) by projecting f_Y(y) = ∂y F_Y(y)."""
        # Define trial & test functions on V_f
        u = TrialFunction(self.V_f)
        v = TestFunction(self.V_f)

        # Construct the linear & bilinear forms
        a = inner(u, v) * dx
        L = -inner(F, v.dx(0)) * dx + F*v*ds(2) - F*v*ds(1)

        # Solve for f
        f = Function(self.V_f)
        solve(a == L, f)

        # Check PDF properties
        if abs(assemble(f*dx) - 1) > 1e-02:
            print("Calculated ∫ f(y) dy should equal 1, but got %e. Check the quadrature_degree used. "%assemble(f*dx))
            #raise ValueError("Calculated ∫ f(y) dy should equal 1, but got %e. Check the quadrature_degree used. "%PDF_int)

        return f

    def fit(self, Y, quadrature_degree=100):
        """Return the Density object correspoding to Y(X)."""
        
        y = self.y_coord()
        F = self.cdf(self.map(Y), quadrature_degree)
        Q = self.qdf(F)
        f = self.pdf(F)

        return Density(self, y, F, Q, f)

    def slope_limiter(self, F):
        """Apply the slope limiter to the CDF F(y)."""
        def jump_condition(a_n_minus, a_n_plus, a_0_minus):
            if a_n_plus < a_n_minus:
                return a_n_plus-a_n_minus
            else:
                return min(a_n_plus, a_0_minus) - a_n_minus

        def jumps(F, F_0):

            celldata_0 = F_0.dat.data[:].reshape((-1, 2))

            celldata_n = F.dat.data[:].reshape((-1, 2))
            ne = celldata_n.shape[0]
            jumps = np.zeros(ne)

            # Go through the cells from left to right
            for e in range(ne):

                # (1) cell data
                # e - 1
                if e == 0:
                    cell_n_em1 = np.zeros(2)
                    cell_0_em1 = np.zeros(2)
                else:
                    cell_n_em1 = celldata_n[e-1, :]
                    cell_0_em1 = celldata_0[e-1, :]
                # e
                cell_n_e = celldata_n[e, :]
                cell_0_e = celldata_0[e, :]

                # e + 1
                if e == ne-1:
                    cell_n_ep1 = np.ones(2)
                else:
                    cell_n_ep1 = celldata_n[e+1, :]
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                # (2) jumps
                left = jump_condition(cell_n_em1[1], cell_n_e[0], cell_0_em1[1])
                right = jump_condition(cell_n_e[1], cell_n_ep1[0], cell_0_e[1])
                jumps[e] = min(left, right)
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            return jumps

        F_0 = copy.deepcopy(F)
        ne = F_0.dat.data[:].reshape((-1, 2)).shape[0]

        # A) Relaxation loop
        error = 1
        iter = 0
        slope = -1
        jo = np.zeros(ne)
        alpha = 0.1
        while (error > 0.2) or (slope < 0) and (iter <= 10**2):

            # (1) Update dats
            jn = jumps(F, F_0)
            F.dat.data[:].reshape((-1, 2))[:, 0] -= alpha*jn
            F.dat.data[:].reshape((-1, 2))[:, 1] += alpha*jn

            # (2) Error
            iter += 1
            if np.linalg.norm(jn) == 0:
                error = 0.
            else:
                error = np.linalg.norm(jn - jo, 2)/np.linalg.norm(jn, 2)
            jo = jn

            if iter > 10**2:
                print('Slope limiter relaxation iterations exceeded threshold \n')
           
            slopes = F.dat.data[:].reshape((-1, 2))[:, 1] - F.dat.data[:].reshape((-1, 2))[:, 0]
            slope = np.min(slopes)
            if abs(slope) < 1e-8:
                slope = 0.

            #print('Iteration i=%d'%iter,' error = ',error,'slope =',slope,'\n')
            # if iter%10 == 0:
            #     print('Iteration i=%d'%iter,' error = ',error,'slope =',slope,'\n')
            #     ptp.plot(function='CDF')

        # B) Remove remaining illegal discontinuities
        jn = jumps(F, F_0)
        F.dat.data[:].reshape((-1, 2))[:, 0] -= jn
        F.dat.data[:].reshape((-1, 2))[:, 1] += jn

        return F
