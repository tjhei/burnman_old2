# BurnMan - a lower mantle toolkit
# Copyright (C) 2012, 2013, Heister, T., Unterborn, C., Rose, I. and Cottaar, S.
# Released under GPL v2 or later.

import os, sys, numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate

import seismic
import tools
import averaging_schemes
import geotherm

#phase = namedtuple('phase', ['mineral', 'fraction'])

class elastic_properties:
    """
    Class that contains volume, density, and moduli. This is generated for
    different pressures and temperatures using
    :func:`calculate_moduli`. Several instances of elastic_properties can be
    averaged using :func:`average_moduli`.

    :var float V: volume in [m^3] 
    :var float rho: density in [kg/m^3]
    :var float K: bulk modulus K in [Pa] 
    :var float G: shear modulus G in [Pa] 
    """

    def __init__(self, V=None, rho=None, K=None, G=None, fraction=None):
        """
        create an object with the given parameters.
        """
        self.V = V
        self.rho = rho
        self.K = K
        self.G = G
        self.fraction = fraction


def calculate_moduli(rock, pressures, temperatures):
    """
    Given a composite and a list of pressures [Pa] and temperatures [K],
    calculate the elastic moduli and densities of the individual phases.

    :param burnman.abstract_material rock: this is a rock

    :type pressures: list of float
    :param pressures: list of pressures you want to evaluate the rock at. In
                      [Pa].

    :type temperatures: list of float
    :param temperatures: list of pressures you want to evaluate the rock at.

    :returns: 
      answer -- an array of (n_evaluation_points by n_phases) of
      elastic_properties(), so the result is of the form
      answer[pressure_idx][phase_idx].V
    :rtype: list of list of :class:`burnman.elastic_properties`
    """

    answer = [[] for p in pressures]

    for idx in range(len(pressures)):
        rock.set_state(pressures[idx], temperatures[idx])
        (fractions,minerals) = rock.unroll()
        for (fraction,mineral) in zip(fractions,minerals):
            e = elastic_properties()
            e.V = fraction * mineral.molar_volume()
            e.K = mineral.adiabatic_bulk_modulus()
            e.G = mineral.shear_modulus()
            e.rho = mineral.molar_mass() / mineral.molar_volume()
            e.fraction = fraction
            answer[idx].append(e)
        
    return answer

def average_moduli(moduli_list, averaging_scheme=averaging_schemes.voigt_reuss_hill):
    """
    Given an array of (n_evaluation_points by n_phases) of
    :class:`elastic_properties` (as, for instance, generated by
    :func:`calculate_moduli`), calculate the bulk properties, according to
    some averaging scheme. The averaging scheme defaults to Voigt-Reuss-Hill
    (see :class:`burnman.averaging_schemes.voigt_reuss_hill`), but the user
    may specify, Voigt, Reuss, the Hashin-Shtrikman bounds, or any user
    defined scheme that satisfies the interface
    :class:`burnman.averaging_schemes.averaging_scheme` (also see
    :doc:`averaging`).

    :type moduli_list: list of list of :class:`burnman.elastic_properties`
    :param moduli_list: bla

    :type averaging_scheme: :class:`burnman.averaging_schemes.averaging_scheme`
    :param averaging_scheme: Averaging scheme to use.
    
    :returns: A list of n_evaluation_points instances of elastic_properties.
    :rtype: list of :class:`burnman.elastic_properties`
    """
    n_pressures = len(moduli_list)
    result = [elastic_properties() for i in range(n_pressures)]
    
    for idx in range(n_pressures):
        fractions = np.array([e.fraction for e in moduli_list[idx]])

        V_frac = np.array([m.V for m in moduli_list[idx]])
        K_ph = np.array([m.K for m in moduli_list[idx]])
        G_ph = np.array([m.G for m in moduli_list[idx]])
        rho_ph = np.array([m.rho for m in moduli_list[idx]])
               
        result[idx].V = sum(V_frac)
        result[idx].K = averaging_scheme.average_bulk_moduli(V_frac, K_ph, G_ph)
        result[idx].G = averaging_scheme.average_shear_moduli(V_frac, K_ph, G_ph)
        result[idx].rho = averaging_scheme.average_density(V_frac, rho_ph)
        result[idx].fraction = 1.0

    return result

def compute_velocities(moduli):
    """
    Given a list of elastic_properties, compute the seismic velocities Vp, Vs,
    and Vphi for each entry in the list.

    
    :type moduli: list of :class:`elastic_properties`
    :param moduli: input elastic properties.

    :returns: lists of Vp, Vs, Vphi (in m/s each)
    :rtype: list of float, list of float, list of float


    """
    mat_vs = np.ndarray(len(moduli))
    mat_vp = np.ndarray(len(moduli))
    mat_vphi = np.ndarray(len(moduli))
    
    for i in range(len(moduli)):

        mat_vs[i] = np.sqrt( moduli[i].G / moduli[i].rho)
        mat_vp[i] = np.sqrt( (moduli[i].K + 4./3.*moduli[i].G) / moduli[i].rho)
        mat_vphi[i] = np.sqrt( moduli[i].K / moduli[i].rho)
    
    return mat_vp, mat_vs, mat_vphi
 
 
def velocities_from_rock(rock, pressures, temperatures, averaging_scheme=averaging_schemes.voigt_reuss_hill()):
    """
    A function that rolls several steps into one: given a rock and a list of
    pressures and temperatures, it calculates the elastic moduli of the
    individual phases using calculate_moduli(), averages them using
    average_moduli(), and calculates the seismic velocities using
    compute_velocities().

    Returns arrays for density [kg/m^3], Vp [m/s], Vs [m/s], Vphi [m/s], K [m/s], G [m/s]
    """
    moduli_list = calculate_moduli(rock, pressures, temperatures)
    moduli = average_moduli(moduli_list, averaging_scheme)
    mat_vp, mat_vs, mat_vphi = compute_velocities(moduli)
    mat_rho = np.array([m.rho for m in moduli])
    mat_K = np.array([m.K for m in moduli])
    mat_G = np.array([m.G for m in moduli])
    return mat_rho, mat_vp, mat_vs, mat_vphi, mat_K, mat_G

def depths_for_rock(rock,pressures, temperatures,averaging_scheme=averaging_schemes.voigt_reuss_hill()):
    """
        Function computes the self-consistent depths (to avoid using the PREM depth-pressure conversion) (Cammarano, 2013)
        Only simplification is using g from PREM
        """
    moduli_list = calculate_moduli(rock, pressures, temperatures)
    moduli = average_moduli(moduli_list, averaging_scheme)
    mat_rho = np.array([m.rho for m in moduli])
    seismic_model = seismic.prem()
    depthsref=np.array(map(seismic_model.depth,pressures))
    pressref=np.zeros_like(pressures)
    g=seismic_model.grav(depthsref) # G for prem
    depths= np.hstack((depthsref[0],depthsref[0]+integrate.cumtrapz(1./(g*mat_rho),pressures)))
    return depths

def pressures_for_rock(rock, depths, T0, averaging_scheme=averaging_schemes.voigt_reuss_hill()):
    """
        Function computes the self-consistent pressures (to avoid using the PREM depth-pressure conversion) (Cammarano, 2013)
        Only simplification is using g from PREM
        """
    # use PREM pressures as inital guestimate
    seismic_model = seismic.prem()
    pressures,_,_,_,_ = seismic_model.evaluate_all_at(depths)
    pressref=np.zeros_like(pressures)
    #gets table with PREM gravities
    g=seismic_model.grav(depths)
    #optimize pressures for this composition
    while nrmse(len(pressures),pressures,pressref)>1.e-6:
        # calculate density
        temperatures= geotherm.adiabatic(pressures,T0,rock)
        moduli_list = calculate_moduli(rock, pressures, temperatures)
        moduli = average_moduli(moduli_list, averaging_scheme)
        mat_rho = np.array([m.rho for m in moduli])
        # calculate pressures
        pressref=pressures
        pressures=np.hstack((pressref[0], pressref[0]+integrate.cumtrapz(g*mat_rho,depths)))
    return pressures

def apply_attenuation_correction(v_p,v_s,v_phi,Qs,Qphi):
    """
    Returns lists of corrected Vp Vs and Vphi for a given Qs and Qphi
    """
    length = len(v_p)
    ret_v_p = np.zeros(length)
    ret_v_s = np.zeros(length)
    ret_v_phi = np.zeros(length)
    for i in range(length):
        ret_v_p[i],ret_v_s[i],ret_v_phi[i] = \
            seismic.attenuation_correction(v_p[i], v_s[i], v_phi[i],Qs,Qphi)
    
    return ret_v_p, ret_v_s, ret_v_phi


def compare_l2(depth,mat_vs,mat_vphi,mat_rho,seis_vs,seis_vphi,seis_rho):
    """
    It computes the L2 norm for three profiles at a time (assumed to be linear between points).
    Input list of depths, three computed profiles, and three profiles to compare to.
    """
    rho_err_tot = l2(depth,mat_rho,seis_rho)
    vphi_err_tot = l2(depth,mat_vphi,seis_vphi)
    vs_err_tot = l2(depth,mat_vs,seis_vs)
    err_tot=rho_err_tot+vphi_err_tot+vs_err_tot

    return rho_err_tot, vphi_err_tot, vs_err_tot

def compare_chifactor(mat_vs,mat_vphi,mat_rho,seis_vs,seis_vphi,seis_rho):
    """
    It computes the chifactor for three profiles at a time
    """
    rho_err_tot = chi_factor(mat_rho,seis_rho)
    vphi_err_tot = chi_factor(mat_vphi,seis_vphi)
    vs_err_tot = chi_factor(mat_vs,seis_vs)
    err_tot=rho_err_tot+vphi_err_tot+vs_err_tot

    return rho_err_tot, vphi_err_tot, vs_err_tot

def l2(x,funca,funcb):
    """ L2 norm """
    diff=np.array(funca-funcb)
    diff=diff*diff
    return integrate.trapz(diff,x)


def nrmse(x,funca,funcb):
    """ normalized root mean square error """
    diff=np.array(funca-funcb)
    diff=diff*diff
    rmse=np.sqrt(np.sum(diff)/x)
    nrmse=rmse/(np.max(funca)-np.min(funca))
    return nrmse

def chi_factor(calc,obs):
    #assuming 1% a priori uncertainty on the seismic model

    err=np.empty_like(calc)
    for i in range(len(calc)):
        err[i]=pow((calc[i]-obs[i])/(0.01*np.mean(obs)),2.)

    err_tot=np.sum(err)/len(err)

    return err_tot
