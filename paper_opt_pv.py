# BurnMan - a lower mantle toolkit
# Copyright (C) 2012, 2013, Heister, T., Unterborn, C., Rose, I. and Cottaar, S.
# Released under GPL v2 or later.

"""
Vary the amount perovskite vs. ferropericlase and compute the error in the
seismic data against PREM.

requires:
- creating minerals
- compute seismic velocities
- geotherms
- seismic models
- seismic comparison

teaches:
- compare errors between models
- loops over models

"""

import os, sys, numpy as np, matplotlib.pyplot as plt
#hack to allow scripts to be placed in subdirectories next to burnman:
if not os.path.exists('burnman') and os.path.exists('../burnman'):
    sys.path.insert(1,os.path.abspath('..')) 

import burnman
from burnman import minerals

if __name__ == "__main__":    

    
    ### input variables ###
    #######################
    
    #INPUT for method
    """ choose 'slb2' (finite-strain 2nd order shear modulus,       
        stixrude and lithgow-bertelloni, 2005)
    or 'slb3 (finite-strain 3rd order shear modulus,
        stixrude and lithgow-bertelloni, 2005)
    or 'mgd3' (mie-gruneisen-debeye 3rd order shear modulus,
        matas et al. 2007)
    or 'mgd2' (mie-gruneisen-debeye 2nd order shear modulus,
        matas et al. 2007)
    or 'bm2' (birch-murnaghan 2nd order, if you choose to ignore temperature
       (your choice in geotherm will not matter in this case))
    or 'bm3' (birch-murnaghan 3rd order, if you choose to ignore temperature
        (your choice in geotherm will not matter in this case))"""
    method = 'slb2' 
    
    seismic_model = burnman.seismic.prem() # pick from .prem() .slow() .fast() (see burnman/seismic.py)
    number_of_points = 20 #set on how many depth slices the computations should be done
    depths = np.linspace(850e3,2700e3, number_of_points)
    seis_p, seis_rho, seis_vp, seis_vs, seis_vphi = seismic_model.evaluate_all_at(depths)
    
    temperature = burnman.geotherm.brown_shankland(seis_p)
    
    def eval_material(amount_perovskite):
        rock = burnman.composite ( [ (minerals.Murakami_etal_2012.fe_perovskite(), amount_perovskite),
                             (minerals.Murakami_etal_2012.fe_periclase(), 1.0 - amount_perovskite) ] )
    
        rock.set_method(method)
    
        print "Calculations are done for:"
        for ph in rock.phases:
            print ph.fraction, " of phase", ph.mineral.to_string()
    
        mat_rho, mat_vp, mat_vs, mat_vphi, mat_K, mat_G = \
            burnman.velocities_from_rock(rock, seis_p, temperature, burnman.averaging_schemes.voigt_reuss_hill())
    
        #[rho_err,vphi_err,vs_err]=burnman.compare_chifactor(mat_vs,mat_vphi,mat_rho,seis_vs,seis_vphi,seis_rho)
        
    
        return seis_p, mat_vs, mat_vphi, mat_rho

    def material_error(x):
        _, mat_vs, mat_vphi, mat_rho = eval_material(x)
        [rho_err,vphi_err,vs_err]=burnman.compare_l2(depths,mat_vs,mat_vphi,mat_rho,seis_vs,seis_vphi,seis_rho)
        return vs_err, vphi_err

    xx=np.linspace(0.0, 1.0, 50)
    errs=np.array([material_error(x) for x in xx])
    yy_vs=errs[:,0]
    yy_vphi=errs[:,1]
    plt.plot (xx*100,yy_vs,"r-",label=("V_s error"))
    plt.plot (xx*100,yy_vphi,"b-",label=("V_phi error"))

    ymin = 50
    ymax = 1e6
    plt.ylim([ymin,ymax])

    plt.vlines(71,ymin,ymax,colors='c',label='A, 71% pv')
    plt.vlines(79,ymin,ymax,colors='g',label='B, 79% pv')
    plt.vlines(90,ymin,ymax,colors='m',label='C, 90% pv')
    
    plt.yscale('log')
    plt.xlabel('% Perovskite')
    plt.ylabel('Error')
    plt.legend()
    plt.show()

    A_p, A_vs, A_vphi,_ = eval_material(0.71)
    B_p, B_vs, B_vphi,_ = eval_material(0.79)
    C_p, C_vs, C_vphi,_ = eval_material(0.90)
    
    plt.plot(seis_p/1.e9,seis_vs/1.e3,color='k',linestyle='--',marker='o', markersize=4,markerfacecolor='None',label='PREM')
    plt.plot(A_p/1.e9,A_vs/1.e3,color='c',linestyle='-', \
    markerfacecolor='c',markersize=4,label='A, 71% pv')
    plt.plot(B_p/1.e9,B_vs/1.e3,color='g',linestyle='-', \
    markerfacecolor='g',markersize=4,label='B, 79% pv')
    plt.plot(C_p/1.e9,C_vs/1.e3,color='m',linestyle='-', \
    markerfacecolor='m',markersize=4,label='C, 90% pv')
    plt.title("Vs (km/s)")
    plt.xlabel('pressure')
    plt.ylabel('km/s')
    plt.legend(loc='lower right')
    plt.show()
      
    plt.plot(seis_p/1.e9,seis_vphi/1.e3,color='k',linestyle='--',marker='o', markersize=4,markerfacecolor='None',label='PREM')
    plt.plot(A_p/1.e9,A_vphi/1.e3,color='c',linestyle='-', \
    markerfacecolor='c',markersize=4,label='A, 71% pv')
    plt.plot(B_p/1.e9,B_vphi/1.e3,color='g',linestyle='-', \
    markerfacecolor='g',markersize=4,label='B, 79% pv')
    plt.plot(C_p/1.e9,C_vphi/1.e3,color='m',linestyle='-', \
    markerfacecolor='m',markersize=4,label='C, 90% pv')
    plt.title("Vphi (km/s)")
    plt.xlabel('pressure')
    plt.ylabel('km/s')
    plt.legend(loc='lower right')
    plt.show()
