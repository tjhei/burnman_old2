# BurnMan - a lower mantle toolkit
# Copyright (C) 2012, 2013, Heister, T., Unterborn, C., Rose, I. and Cottaar, S.
# Released under GPL v2 or later.

#system libs:
import numpy
import scipy.optimize as opt
import scipy.integrate as integrate
import math
import matplotlib.pyplot as pyplot

#own libs:
import os, sys
if not os.path.exists('burnman') and os.path.exists('../burnman'):
    sys.path.insert(1,os.path.abspath('..')) 
sys.path.insert(1,os.path.abspath('.')) 
import burnman

import geotherm
from tools import *

# TODO: add up weight percent and check <100 and tell them how much

molar_mass = {'Fe':55.845/1000., 'Mg':24.305/1000., 'O':15.999/1000., 'Al':26.982/1000., 'Ca':40.078/1000., 'Si':28.085/1000.} # kg/mol
Av = 6.022141e23 # Avogadro constant in 1/mol 
boltzmann_constant = 1.3806503e-23 # in m^2 kg s^-2 K^-1
gas_constant = Av * boltzmann_constant # in J mol^-1 K^-1

lower_mantle_mass = 4.043e24*.75 # in kg




# convert weight percentage (amount, 1.00 = 100%) of a given element to molar mass
def weight_pct_to_mol(element, amount):

    return amount * lower_mantle_mass / molar_mass[element] * Av


def calculate_phase_percents(inp):
    """
    Converts given weight percentages into the requisite percent of each phase
    in mols and also returns the fraction of perovskite versus ferropericlase, 
    assuming all of the silcon goes into the perovskite phase
    and with any remaining Fe or Mg going into the oxide phase.
    Input:
    inp={'Mg': ..., 'Fe': ..., ...} # in weight percent
    Returns:
    phase_per={'fp': ..., 'pv': ...} # as a fraction
    rel_mol_per={'MgO: ..., 'FeO': ..., ...} # in mols 
    """
    names = {'Mg':'MgO','Fe':'FeO','Si':'SiO2', 'Ca':'Ca', 'Al':'Al'}
    rel_mol_per = {}
    out = {}
    for a in inp:
        out[names[a]] = weight_pct_to_mol(a,inp[a])


    norm = out['MgO']+out['FeO']
    for a in inp:
        rel_mol_per[names[a]] = out[names[a]]/norm

    frac_mol_SiO2 = rel_mol_per['SiO2']
    phase_per={'fp':(1.-frac_mol_SiO2),'pv':frac_mol_SiO2}
    return phase_per,rel_mol_per
    
    
    
def part_coef_calc(inp2,StartP,EndP,deltaP):

    a = [] #partition coefficent of Fe in fp
    b = [] #partition coefficent of Fe in pv
    
    Pressure= []
    Temperature=[]
    counter = 0
    
    
   
def calculate_partition_coefficient(pressure, temperature, components, initial_distribution_coefficient):

    """ calculate the partition coefficient given [...] initial_distribution_coefficient is known as Kd_0 """

    frac_mol_FeO = components['FeO']
    frac_mol_SiO2 = components['SiO2']
    Kd_0 = initial_distribution_coefficient

    delV = 2.e-7 #in m^3/mol, average taken from Nakajima et al 2012, JGR
    

    rs = ((25.e9-pressure)*(delV)/(gas_constant*temperature))+math.log(Kd_0) #eq 5 Nakajima et al 2012

    K = math.exp(rs) #The exchange coefficent at P and T

    num_to_sqrt = (-4.*frac_mol_FeO*(K-1.)*K*frac_mol_SiO2)+(pow(1.+(frac_mol_FeO*(K-1))+((K-1.)*frac_mol_SiO2),2.))

    b = (-1. + frac_mol_FeO - (frac_mol_FeO*K)+frac_mol_SiO2 - (frac_mol_SiO2*K) + math.sqrt(num_to_sqrt)) \
         / (2.*frac_mol_SiO2*(1.-K))

    a = b /(((1.-b)*K)+b)
    
    return (a,b) #a is partition coefficient array with P for mw, b is pcarray for pv

# test some composition (Javoy 2010, Table 6, PLoM)
if __name__ == "__main__":
    inp1 = {'Mg':0.213, 'Fe': 0.0626, 'Si':0.242, 'Ca':0., 'Al':0.} # wt%
    phase_per,rel_mol_per = calculate_phase_percents(inp1) 

    StartP = 23.83 #in GPa
    EndP = 110.0
    deltaP = 1.

    #P,T,a,b,frac_mol_pv,frac_mol_mw    = part_coef_calc(inp2,StartP,EndP,deltaP)

    gt = lambda p: geotherm.brown_shankland(p)
    pressure = StartP
    temperature = gt([StartP,])
    calculate_partition_coefficient(pressure, temperature, rel_mol_per, 0.5)
    #part_coef_calc(inp2,StartP,EndP,deltaP)
    #print inp1
    #print inp2
    #print t
