Tutorials \& Examples
*********************

The following notebooks provide an overview of the functionality provided 
by NumDF including how to compute the CDF, PDF and QDF, how to compute 
compositions of these objects and how work with external data from numerical 
simulations. To  run the notebooks, you will need to 
`install jupyter <https://jupyter.org/install.html>`__ *inside* your activated
Firedrake virtualenv.

These notebooks are maintained in the NumDF repository, so all the
material is available in your NumDF installation source
directory while the notebooks are in the directory ``NumDF/docs/notebooks``.

Thanks to the excellent `FEM on
Colab <https://fem-on-colab.github.io/index.html>`__ by `Francesco
Ballarin <https://www.francescoballarin.it>`__, you can run the notebooks on
Google Colab through your web browser, without installing Firedrake or NumDF.

We also provide links to non-interactive renderings of the notebooks using
`Jupyter nbviewer <https://nbviewer.jupyter.org>`__.

Example 1 - Analytic functions
==============================

In this notebook, we demonstrate the basic functionality of NumDF including how to compute the
CDF, PDF and QDF of a one and two dimensional analytical function. A rendered version of this notebook is available `here
<https://nbviewer.org/github/mannixp/D.stratify-pdfe/blob/main/notebooks/example_notebooks/Example_1_analytic_functions.ipynb>`__
and there is a version `on Colab <https://colab.research.google.com/github/mannixp/D.stratify-pdfe/blob/main/notebooks/example_notebooks/Example_1_analytic_functions.ipynb>`__


Example 2 - Numerical functions
===============================

We then consider a more practically relevant example where the function specified is obtained as the output of a direct numerical simulation. 
Considering a two dimensional Kelvin-Helmholtz instability we present the time evolution of the CDF for which a rendered version of this notebook is available `here
<https://nbviewer.org/github/mannixp/D.stratify-pdfe/blob/main/notebooks/example_notebooks/Example_2_numerical_functions.ipynb>`__
and there is a version `on Colab <https://colab.research.google.com/github/mannixp/D.stratify-pdfe/blob/main/notebooks/example_notebooks/Example_2_numerical_functions.ipynb>`__


Example 3 - Available potential energy
======================================

Next, we discuss how to compute the available potential energy for a simple two dimensional field and compare our methods
estimate with an analytical calculation. This example builds on the previous example by requiring the integral of the composition 
of two CDFs to be evaluated. A rendered version of this notebook is available `here <https://nbviewer.org/github/mannixp/D.stratify-pdfe/blob/main/notebooks/example_notebooks/Example_3_ape_calculation.ipynb>`__
and there is a version `on Colab <https://colab.research.google.com/github/mannixp/D.stratify-pdfe/blob/main/notebooks/example_notebooks/Example_3_ape_calculation.ipynb>`__


Example 4 - Numerical convergence
=================================

Finally we show that the numerical implementation of our numerical method is consistent and discuss the challenges that arise when 
computing the density of common functions whose PDFs typically contain singularities. A rendered version of this notebook is available `here
<https://nbviewer.org/github/mannixp/D.stratify-pdfe/blob/main/notebooks/example_notebooks/Example_4_convergence.ipynb>`__
and there is a version `on Colab <https://colab.research.google.com/github/mannixp/D.stratify-pdfe/blob/main/notebooks/example_notebooks/Example_4_convergence.ipynb>`__
