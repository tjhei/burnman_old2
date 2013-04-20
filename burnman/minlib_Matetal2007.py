# BurnMan - a lower mantle toolkit
# Copyright (C) 2012, 2013, Heister, T., Unterborn, C., Rose, I. and Cottaar, S.
# Released under GPL v2 or later.


from minerals_base import *



class Matas_mg_perovskite(material): # Matas et al 2007 Tables 1&2
    """
    Matas et al. 2007 and references therein
    """
    def __init__(self):
        self.params = {
            'equation_of_state':'mgd2',
            'ref_V': 24.43e-6,
            'ref_K': 250.0e9,   
            'K_prime': 4.0,     
            'ref_mu': 175.0e9,  
            'mu_prime': 1.8,    
            'molar_mass': .1020,
            'n': 5,
            'ref_Debye': 1070.,
            'ref_grueneisen': 1.48,
            'q0': 1.4} 

class Matas_fe_perovskite(material): # Matas et al 2007 Tables 1&2
    """
    Matas et al. 2007 and references therein
    """
    def __init__(self):
        self.params = {
            'equation_of_state':'mgd2',
            'ref_V': 25.34e-6,
            'ref_K': 250.0e9, 
            'K_prime': 4.0,  
            'ref_mu': 135.0e9, 
            'mu_prime': 1.3,  
            'molar_mass': .1319, 
            'n': 5,
            'ref_Debye': 841.,
            'ref_grueneisen': 1.48,
            'q0': 1.4} 

class Matas_periclase (material): # Matas et al 2007 Tables 1&2
    """
    Matas et al. 2007 and references therein
    """
    def __init__(self):
        self.params = {
            'equation_of_state':'mgd2',
            'ref_V': 11.25e-6,
            'ref_K': 160.1e9,
            'K_prime': 3.83,
            'ref_mu': 130.0e9,
            'mu_prime': 2.2,
            'molar_mass': .0403,
            'n': 2,
            'ref_Debye': 673.,
            'ref_grueneisen': 1.41,
            'q0': 1.3 }

class Matas_wuestite (material): # Matas et al 2007 Tables 1&2
    """
    Matas et al. 2007 and references therein
    """
    def __init__(self):
        self.params = {
            'equation_of_state':'mgd2',
            'ref_V': 12.26e-6,
            'ref_K': 160.1e9,
            'K_prime': 3.83,
            'ref_mu': 46.0e9,
            'mu_prime':  0.6,
            'molar_mass': .0718,
            'n': 2,
            'ref_Debye': 673.,
            'ref_grueneisen': 1.41,
            'q0': 1.3 }


