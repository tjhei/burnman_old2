# BurnMan - a lower mantle toolkit
# Copyright (C) 2012, 2013, Heister, T., Unterborn, C., Rose, I. and Cottaar, S.
# Released under GPL v2 or later.

"""
This example is under construction.

requires:

teaches:


"""

import os, sys, numpy as np, matplotlib.pyplot as plt
#hack to allow scripts to be placed in subdirectories next to burnman:
if not os.path.exists('burnman') and os.path.exists('../burnman'):
        sys.path.insert(1,os.path.abspath('..')) 

import burnman
from burnman import minerals

import pymc

seismic_model = burnman.seismic.prem() # pick from .prem() .slow() .fast() (see code/seismic.py)
number_of_points = 20 #set on how many depth slices the computations should be done
depths = np.linspace(750.e3,2890.e3, number_of_points)
seis_p, seis_rho, seis_vp, seis_vs, seis_vphi = seismic_model.evaluate_all_at(depths)

print "preparations done"


def calc_velocities(ref_rho, K_0, K_prime, G_0, G_prime): 

    test = burnman.minerals_base.material()

    test.params['V_0'] = 10.e-6
    test.params['molar_mass'] = ref_rho*test.params['V_0']
    test.params['K_0'] = K_0
    test.params['K_prime'] = K_prime
    test.params['G_0'] = G_0
    test.params['G_prime'] = G_prime

    rock = burnman.composite( [(test, 1.0 )] )
    rock.set_method('bm3')

    temperature = np.empty_like(seis_p)
    mat_rho, mat_vp, mat_vs, mat_vphi, mat_K, mat_G = burnman.velocities_from_rock(rock,seis_p, temperature)	

    return mat_rho, mat_vphi, mat_vs

def error(ref_rho, K_0, K_prime, G_0, G_prime):
    rho, vphi, vs = calc_velocities(ref_rho, K_0, K_prime, G_0, G_prime)

    vphi_chi = burnman.chi_factor(vphi, seis_vphi)
    vs_chi = burnman.chi_factor(vs, seis_vs)
    rho_chi = burnman.chi_factor(rho, seis_rho)

    return rho_chi+vphi_chi+vs_chi


# Priors on unknown parameters:
ref_rho = pymc.Uniform('ref_rho', lower=3300., upper=4500.)
K_0 = pymc.Uniform('K_0', lower=200.e9, upper=300.e9)
K_prime = pymc.Uniform('K_prime', lower=3., upper=6.)
G_0 = pymc.Uniform('G_0', lower=50.e9, upper=250.e9)
G_prime = pymc.Uniform('G_prime', lower=0., upper=3.)


minerr = 1e100
@pymc.deterministic
def theta(p1=ref_rho,p2=K_0,p3=K_prime,p4=G_0,p5=G_prime):
    global minerr
    if (p1<0 or p2<0 or p3<0 or p4<0 or p5 < 0):
        return 1e30
    try:
        e = error(p1,p2,p3,p4,p5)
        if (e<minerr):
            minerr=e
            print "best fit", e, "values:", p1,p2/1.e9,p3,p4/1.e9,p5
        return e
    except ValueError:
        return 1e20


sig = 1e-4
misfit = pymc.Normal('d',mu=theta,tau=1.0/(sig*sig),value=0,observed=True,trace=True)
model = dict(ref_rho=ref_rho, K_0=K_0, K_prime=K_prime, G_0=G_0, G_prime=G_prime, misfit=misfit)
things = ['ref_rho', 'K_0', 'K_prime', 'G_0', 'G_prime']

S = pymc.MAP(model)
S.fit( method = 'fmin')

rho, vphi, vs = calc_velocities(S.ref_rho.value, S.K_0.value, S.K_prime.value, S.G_0.value, S.G_prime.value)

plt.subplot(2,2,1)
plt.plot(seis_p/1.e9,vs/1000.,color='r',linestyle='-',marker='^',markerfacecolor='r',markersize=4)
plt.plot(seis_p/1.e9,seis_vs/1000.,color='k',linestyle='-',marker='v',markerfacecolor='k',markersize=4)
plt.ylim([4, 8])
plt.title("Vs (km/s)")

plt.subplot(2,2,2)
plt.plot(seis_p/1.e9,vphi/1000.,color='r',linestyle='-',marker='^',markerfacecolor='r',markersize=4)
plt.plot(seis_p/1.e9,seis_vphi/1000.,color='k',linestyle='-',marker='v',markerfacecolor='k',markersize=4)
plt.ylim([7, 12])
plt.title("Vphi (km/s)")
   
    
# plot density
plt.subplot(2,2,3)
plt.plot(seis_p/1.e9,rho/1000.,color='r',linestyle='-',marker='^',markerfacecolor='r',markersize=4,label='model 1')
plt.plot(seis_p/1.e9,seis_rho/1000.,color='k',linestyle='-',marker='v',markerfacecolor='k',markersize=4,label='ref')
plt.title("density (kg/m^3)")
plt.legend(loc='upper left')
plt.ylim([3, 7 ])
plt.show()

print "done"


