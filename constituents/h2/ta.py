import h2_jj
import h2_orton
import matplotlib.pyplot as plt
import numpy as np

verbosity = True
otherPar = {'h2_state':'e','newset':True}

###############Test orton vs joiner in freq
JJCMP = True
if JJCMP:
    plt.figure(100)
    f = []
    for i in range(300):
        f.append(float(i)/3.0+0.1)
    P = 10.0
    X_ch4 = 3.3E-5
    X_he = 0.1
    X_h2 = 1.0 - (X_ch4+X_he)
    X_dict={'H2':0,'HE':1,'CH4':2}
    X=[X_h2,X_he,X_ch4]

    Tease = [30.0,100.0,300.0,600.0]
    for T in Tease:
        a = h2_jj.alpha(f,T,P,X,X_dict)
        s = 'joiner %.0f K' % (T)
        plt.semilogy(f,a,'--',label=s)
        if T==Tease[0]:
            otherPar['newset'] = True
        else:
            otherPar['newset'] = False
        a = h2_orton.alpha(f,T,P,X,X_dict,otherPar,verbose=verbosity)
        s = 'orton (e) %.0f K' % (T)
        plt.semilogy(f,a,label=s)
        a = h2_orton.alpha(f,T,P,X,X_dict,otherPar,verbose=verbosity)
        s = 'orton (n) %.0f K' % (T)
        plt.semilogy(f,a)

    ##import h2_orton_linear
    ##a = h2_orton_linear.alpha(f,T,P,X,X_dict,h2_state='e',newset=True,verbose=verbosity)
    ##plt.semilogy(f,a,label='orton-lin (e)')
    ##a = h2_orton_linear.alpha(f,T,P,X,X_dict,h2_state='n',newset=False,verbose=verbosity)
    ##plt.semilogy(f,a,label='orton-lin (n)')

    plt.legend(loc='lower right')
    plt.xlabel('GHz')
    plt.ylabel('dB/km')


###############Test orton vs joiner in temperature
T_TEST = True
if T_TEST:
    otherPar['newset'] = False
    plt.figure(200)
    P = 10.0
    X_ch4 = 3.3E-5
    X_he = 0.1
    X_h2 = 1.0 - (X_ch4+X_he)
    X_dict={'H2':0,'HE':1,'CH4':2}
    X=[X_h2,X_he,X_ch4]
    Tease = np.arange(10.0,600.0,2.0)
    freq = [[1.0],[10.0],[100.0],[300.0]]
    for f in freq:
        print f[0]
        h2_orton.readInputFiles(f)
        jj=[]
        orton=[]
        orton_lin = []
        for T in Tease:
            a = h2_jj.alpha(f,T,P,X,X_dict)
            jj.append(a[0])
            a = h2_orton.alpha(f,T,P,X,X_dict,otherPar,verbose=verbosity)
            orton.append(a[0])
        s = 'joiner %.0f GHz' % (f[0])
        plt.semilogy(Tease,jj,label=s)
        s = 'orton %.0f GHz' % (f[0])
        plt.semilogy(Tease,orton,label=s)
    plt.legend()
    plt.xlabel('K')
    plt.ylabel('dB/km')


    
################ plot to compare with measured values in Birnbaum JQSRT 19:51
JQSRT = True
if JQSRT:
    plt.figure(300)
    f = []
    for i in range(300):
        f.append(float(i)*100.0+.6)
    P = 10.0
    X_ch4 = 0.0
    X_he = 0.6
    X_h2 = 1.0 - (X_ch4+X_he)
    X_dict={'H2':0,'HE':1,'CH4':2}
    X=[X_h2,X_he,X_ch4]

    h2stateList = ['e','n']

    h2_orton.readInputFiles(f)
    for h2state in h2stateList:  # but don't need to reset on h2state type, just frequencies
        T = 77.0
        a = h2_orton.alpha(f,T,P,X,X_dict,units='invcm',newset=False,h2_state=h2state,verbose=False)
        rho = (P/1.01325)*(273.15/T)
        ff = np.array(f)/29.97
        aa = np.array(a)*1.0E7/rho**2
        s = 'T(%s)=%.1f K' % (h2state,T)
        plt.plot(ff,aa,label=s)

        T = 195.0
        a = h2_orton.alpha(f,T,P,X,X_dict,units='invcm',newset=False,h2_state=h2state,verbose=False)
        rho = (P/1.01325)*(273.15/T)
        ff = np.array(f)/29.97
        aa = np.array(a)*1.0E7/rho**2
        s = 'T(%s)=%.1f K' % (h2state,T)
        plt.plot(ff,aa,label=s)

        T = 292.0
        a = h2_orton.alpha(f,T,P,X,X_dict,units='invcm',newset=False,h2_state=h2state,verbose=False)
        rho = (P/1.01325)*(273.15/T)
        ff = np.array(f)/29.97
        aa = np.array(a)*1.0E7/rho**2
        s = 'T(%s)=%.1f K' % (h2state,T)
        plt.plot(ff,aa,label=s)

    plt.xlabel(r'cm$^{-1}$')
    plt.ylabel(r'cm$^{-1}$ amagat$^{-2}$ 10$^7$')
    plt.legend(loc='upper left')
