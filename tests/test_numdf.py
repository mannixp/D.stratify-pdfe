"""Tests for the Ptp."""

from firedrake import *
from numdf import Ptp
import numpy as np


def test_initialise():
    """Ensure we can import and initialise Ptp."""
    # 1D
    Ptp(Omega_X={'x1': (-1, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=2)

    # 2D
    Ptp(Omega_X={'x1': (-1, 1), 'x2': (-1, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=2)

    assert True


def test_constant():
    """Check the CDF of Y(X)=0 is correctly calculated."""
    ptp = Ptp(Omega_X={'x1': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=2)
    x1 = ptp.x_coords()
    
    density = ptp.fit(Y=0*x1)
    assert assemble(((density.cdf-1)**2)*dx) < 1e-8


def test_uniform_domain_length():
    """Check the CDF of Y(x1)=x1 is y and PDF is 1."""
    ptp = Ptp(Omega_X={'x1': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=5)
    x1 = ptp.x_coords()

    density = ptp.fit(Y=x1, quadrature_degree=1000)
    assert assemble(((density.cdf-density.y)**2)*dx) < 1e-8

    assert assemble(((density.pdf-1.)**2)*dx) < 1e-8


def test_nonuniform_domain_length():
    """Check the CDF of Y(x1)=x1 is correctly calculated on shifted domain."""
    ptp = Ptp(Omega_X={'x1': (1, 2)}, Omega_Y={'Y': (1, 2)}, n_elements=10)
    x1 = ptp.x_coords()

    density = ptp.fit(Y=x1, quadrature_degree=500)
    assert assemble(((density.cdf-(density.y-1))**2)*dx) < 1e-8


def test_piecewise():
    """Test the CDF of a piecewise continuous function."""
    ptp = Ptp(Omega_X={'x1': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=50)
    x1 = ptp.x_coords()

    expression = conditional(gt(x1, 1/2), x1, x1/2)
    density = ptp.fit(Y=expression, quadrature_degree=1000)   
    y = ptp.y_coord()
    expression = conditional(le(y, 1/4), 2*y, 0) + conditional(And(gt(y, 1/4), le(y, 1/2)), 1/2, 0) + conditional(gt(y, 1/2), y, 0)
    F = Function(ptp.V_F)
    F.interpolate(expression)

    assert assemble(((F - density.cdf)**2)*dx) < 5e-6


def test_quadratic():
    """Check the CDF of Y(x1)=x1^2 is correctly calculated on shifted domain."""
    ptp = Ptp(Omega_X={'x1': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=100)
    x1 = ptp.x_coords()

    density = ptp.fit(Y=x1**2, quadrature_degree=1000)
    cdf = density.y**(1/2)
    assert assemble(((density.cdf-cdf)**2)*dx) < 5e-6


def test_cosine():
    """Check the CDF of Y(x1)=cos(x1)."""
    ptp = Ptp(Omega_X={'x1': (0, 2*np.pi)}, Omega_Y={'Y': (-1, 1)}, n_elements=100)
    x1 = ptp.x_coords()

    density = ptp.fit(Y=cos(x1), quadrature_degree=1000)
    cdf = 1 - acos(density.y)/np.pi
    assert assemble(((density.cdf-cdf)**2)*dx) < 5e-6


def test_qdf_uniform():
    """Check that Q( F(x) ) - x = 0 if Q = F^{-1} for Y(x1) = 0."""
    ptp = Ptp(Omega_X={'x1': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=5)
    x1 = ptp.x_coords()

    # Act
    density = ptp.fit(Y=0*x1, quadrature_degree=1000)
    QF = density.compose(density.qdf, density.cdf, quadrature_degree=10)
    
    assert assemble((QF-density.y)*dx(10)) < 1e-8


def test_qdf_straight_line():
    """Check that Q( F(x) ) - x = 0 if Q = F^{-1} for Y(x1) = x1."""
    # Arrange
    ptp = Ptp(Omega_X={'x1': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=5)
    x1 = ptp.x_coords()

    # Act
    density = ptp.fit(Y=x1, quadrature_degree=1000)
    QF = density.compose(density.qdf, density.cdf, quadrature_degree=10)
    
    assert assemble((QF-density.y)*dx(10)) < 1e-8


def test_qdf_piecewise():
    """Check that Q( F(x) ) - x = 0 for Y(x1) = { if x1 > 1/2: x1 else: x1/2."""
    ptp = Ptp(Omega_X={'x1': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=50)
    x1 = ptp.x_coords()

    expression = conditional(gt(x1, 1/2), x1, x1/2)
    density = ptp.fit(Y=expression, quadrature_degree=1000)
    
    QF = density.compose(density.qdf, density.cdf, quadrature_degree=100)    
    assert assemble((QF-density.y)*dx(100)) < 1e-8


def test_ape_rbc():
    """Validate the APE for RBC against its analytical value."""
    # Arrange
    ptp = Ptp(Omega_X={'x1': (-1, 1), 'x2': (0, 1)}, Omega_Y={'Y': (0, 1)}, n_elements=5)
    x1, x2 = ptp.x_coords()

    # Construct the PDF,CDF,QDF for B
    p_B = ptp.fit(Y=1-x2, quadrature_degree=100)
    
    # Construct the PDF,CDF,QDF for Z
    p_Z = ptp.fit(Y=x2, quadrature_degree=100)

    # Act
    z_ref = p_B.compose(p_Z.qdf, p_B.cdf, quadrature_degree=10)
    b = p_B.y
    bpe = assemble(z_ref*b*p_B.pdf*dx(degree=10))
    tpe = (1/2)*assemble(x2*(1-x2)*dx)

    ape_numerical = bpe-tpe
    ape_exact = 1./6.

    assert abs(ape_numerical - ape_exact)/ape_exact < .01
