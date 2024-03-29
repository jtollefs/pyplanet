import math
import os.path
import numpy as np

# Some constants
coef = 7.244E+21     # coefficient from GEISA_PP.TEX eq. 14
T0 = 296.0           # reference temperature in K
hck = 1.438396       # hc/k  [K cm]
GHz = 29.9792458     # conversion from cm^-1 to GHz
fLower = 26.0        # beginning of transition between S and J (changed from 40 15/5/4)
fHigher = 34.0       # end of transition    "  (changed from 50 15/5/4)
EPS = 1E-12          # a small number

#Set data arrays
f0 = []
I0 = []
E = []
G0 = []
def readInputFiles(path,verbose=False):
    """If needed this reads in the data files for h2s"""
    useLinesUpTo = 200
    global nlin
    nlin = 0
    if verbose:
        print "Reading nh3 lines"
    filename = os.path.join(path,'nh3.lin')
    ifp = open(filename,'r')
    for line in ifp:
        if nlin >= useLinesUpTo:
            break
        nlin+=1
        data = line.split()
        if len(data) == 4:
            f0.append(float(data[0]))
            I0.append(float(data[1]))
            E.append(float(data[2]))
            G0.append(float(data[3]))
        else:
            break
    ifp.close()
    if verbose:
        print '   '+str(nlin)+' lines'
    return nlin

def alpha(freq,T,P,X,P_dict,otherPar,units='dBperkm',path='./',verbose=False):
    global coef, T0, hck, GHz, fLower, fHigher, EPS, f0, I0, E, G0
    Joiner = 0
    Spilker = 1
    Interp = 2

    # Read in data if needed
    if len(f0)==0:
        readInputFiles(path,verbose)

    P_h2 = P*X[P_dict['H2']]
    P_he = P*X[P_dict['HE']]
    P_nh3= P*X[P_dict['NH3']]
    Pscale = 1.0 + P/2.0E4 #ad hoc to make this match Berge-Gulkis for deep Jupiter atmosphere

    # Set Joiner
    GH2 = [1.690]
    GHe = [0.750]
    GNH3= [0.6]
    ZH2 = [1.350]
    ZHe = [0.300]
    ZNH3= [0.200]
    C =   [1.0]
    D =   [-0.45]
    # Set Spilker
    rexp = 8.79*math.exp(-T/83.0)
    GH2a = math.exp(9.024 - T/20.3) - 0.9918 + P_h2
    GH2a = math.pow(GH2a,rexp)
    if GH2a < EPS:  # use Joiner regardless
        GH2.append( 1.690 )
        GHe.append( 0.750 )
        GNH3.append(0.60 )
        ZH2.append( 1.35 )
        ZHe.append( 0.30 )
        ZNH3.append(0.20 )
        C.append(   1.00 )
        D.append(  -0.45 )
    else:
        GH2a = 2.122*math.exp(-T/116.8)/GH2a
        GH2a = 2.34*(1.0 - GH2a)
        GH2.append(GH2a)
        GHe.append(0.46 + T/3000.0)
        GNH3.append(0.74)
        ZH2.append(5.7465 - 7.7644*GH2a  + 9.1931*GH2a**2 - 5.6816*GH2a**3 + 1.2307*GH2a**4)
        ZHe.append(0.28 - T/1750.0)
        ZNH3.append(0.50)
        C.append(-0.337 + T/110.4 - T**2/70600.0)
        D.append(-0.45)
    # Set interp index
    GH2.append( 0.0 )
    GHe.append( 0.0 )
    GNH3.append(0.0 )
    ZH2.append( 0.0 )
    ZHe.append( 0.0 )
    ZNH3.append(0.0 )
    C.append(   0.0 )
    D.append(   0.0 )
    
    n_dvl = 2.0/3.0
    n_int = 3.0/2.0

    alpha_nh3 = []
    for f in freq:
        f2 = f**2
        alpha = 0.0
        if f<=fLower:
            use = Spilker
        elif f>=fHigher:
            use = Joiner
        else:
            use = Interp
            GH2[Interp]  = GH2[Spilker]  + (GH2[Spilker] -GH2[Joiner]) /(fLower-fHigher)*(f - fLower)
            GHe[Interp]  = GHe[Spilker]  + (GHe[Spilker] -GHe[Joiner]) /(fLower-fHigher)*(f - fLower)
            GNH3[Interp] = GNH3[Spilker] + (GNH3[Spilker]-GNH3[Joiner])/(fLower-fHigher)*(f - fLower)
            ZH2[Interp]  = ZH2[Spilker]  + (ZH2[Spilker] -ZH2[Joiner]) /(fLower-fHigher)*(f - fLower)
            ZHe[Interp]  = ZHe[Spilker]  + (ZHe[Spilker] -ZHe[Joiner]) /(fLower-fHigher)*(f - fLower)
            ZNH3[Interp] = ZNH3[Spilker] + (ZNH3[Spilker]-ZNH3[Joiner])/(fLower-fHigher)*(f - fLower)
            C[Interp]    = C[Spilker]    + (C[Spilker]   -C[Joiner])   /(fLower-fHigher)*(f - fLower)
            D[Interp]    = D[Spilker]    + (D[Spilker]   -D[Joiner])   /(fLower-fHigher)*(f - fLower)
        delta = D[use]*P_nh3
        for i in range(nlin):
            gamma = pow((T0/T),n_dvl)*(GH2[use]*P_h2 + GHe[use]*P_he + G0[i]*GNH3[use]*P_nh3)
            g2 = gamma**2
            zeta  = pow((T0/T),n_dvl)*(ZH2[use]*P_h2 + ZHe[use]*P_he + G0[i]*ZNH3[use]*P_nh3)
            z2 = zeta**2
            
            ITG = I0[i]*math.exp(-((1.0/T)-(1.0/T0))*E[i]*hck)
            num = (gamma-zeta)*f2 + (gamma+zeta)*( pow(f0[i]+delta,2.0) + g2 - z2)
            den = pow((f2 - pow(f0[i]+delta,2.0) - g2 + z2),2.0) + 4.0*f2*g2
            shape = GHz*2.0*pow(f/f0[i],2.0)*num/(math.pi*den)
            alpha += shape*ITG

        a = coef*(P_nh3/T0)*pow((T0/T),n_int+2)*alpha*Pscale
        if units=='dBperkm':
            a*=434294.5
        alpha_nh3.append(a)
        
    return alpha_nh3

