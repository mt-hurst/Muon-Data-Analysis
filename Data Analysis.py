%matplotlib inline
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import math
import numpy.matlib as ml
import scipy.integrate as ig
import scipy.interpolate as ip
import scipy.optimize as op

from google.colab import files
from google.colab import drive

drive.mount('/content/drive')


f = open('/content/drive/MyDrive/Spring 22/Physics 352/22-03-03-15-50.txt')
g = open('/content/drive/MyDrive/Spring 22/Physics 352/22-03-10-14-52.data')
h = open('/content/drive/MyDrive/Spring 22/Physics 352/22-03-24-15-25.data')
ff = open('/content/drive/MyDrive/Spring 22/Physics 352/muon.data')
lines = f.readlines() # raw data from first week of experiment
lines_week_2_3 = g.readlines() #raw data from weeks 2-3 of experiement
lines_week_4 = h.readlines() #raw data from fourth week of experiment
lines_total = ff.readlines() #total raw data

def dat_split(dataline):
  '''Takes in list of data lines in format generated by program, outputs two lists of tuples,
  with the UNIX time in the first index of the tuple, and in the first list the amount of
  total detections in second index, and in the second list the time of decay in the second index'''
  times_undetected = []
  times_detected = []
  for datlin in dataline:
    if int(datlin.rsplit()[0]) > 39999:
      times_undetected.append((int(datlin.rsplit()[0]),int(datlin.rsplit()[1])))
    else:
      times_detected.append((int(datlin.rsplit()[0]),int(datlin.rsplit()[1])))
  return times_undetected, times_detected
  
'''
Creating undetected counts(#'s > 39999) 
and Detected decay times
'''
undetect, detected = dat_split(lines)
undetect_week_2_3, detected_week_2_3 = dat_split(lines_week_2_3)
undetect_week4, detected_week4 =dat_split(lines_week_4)
undetect_total, detected_total = dat_split(lines_total)

decaytimes = []
for i in range(len(detected)):
  decaytimes.append(detected[i][0])
decaytimes_week2 = []
for i in range(len(detected_week_2_3)):
  decaytimes_week2.append(detected_week_2_3[i][0])
decaytimes_week4 = []
for i in range(len(detected_week4)):
  decaytimes_week4.append(detected_week4[i][0])
decaytimes_total = []
for i in range(len(detected_total)):
  decaytimes_total.append(detected_total[i][0])

'''
fitting functions for later
'''
def exp_fit(x,A,T):
  return A*np.exp(-(x/T))
def flat_fit(x,A):
  return A
  
#Main error reduction formula to take out the flat background rate of muon coincidences
#from the actual decay times
def cleanup_hists(dec_data,num = 3, cutoff = 5, printoutsteps=True, plots = False):
  '''Cleanup function to account for and remove flate background rate of muon coincidences
  dec_data is raw decay times, num is number of flat background rate checks '''
  h0, bins= np.histogram(dec_data, bins = 20)#creating first histogram of raw data
  #bin_centers = []
  #for i in range(0,20):
  #  bin_centers.append((bins[i] + bins[i+1])/2)
  cf0, cv0 = op.curve_fit(exp_fit, range(0,20000,1000),h0, p0=(max(h0),(max(h0)/2))) #need to find the decay time of uncleaned data
  h_old = h0 #making the first instance of the counts' recursive piece of the loop
  cf_old = cf0 #making the first instance of the coeff's recursive piece of the loop
  print('flat rate of pass 0',cf_old)
  h_flat0, bins_flat = np.histogram(dec_data, bins=10,range=(cutoff*(cf_old[1]),20000))
  if plots:
    plt.semilogy(np.delete(bins,20), h0, 'o',ms= 4, label = "Raw Data")#plotting the 
  h_flat = sum(h_flat0)/len(h_flat0)
  for i in range(0,num):
    flatratenew = h_flat
    h_new = abs(h_old - flatratenew)
    cf_new, cv_new = op.curve_fit(exp_fit, range(0,20000,1000),h_new, p0=(max(h_new),(max(h_new)/2)))
    if printoutsteps: #When enabled, prints out the intermediate steps of the fits
      print("Flat rate of pass", i+1,flatratenew)
      print("Dec rate of pass", i+1, cf_new[1])
    h_old = h_new
    if i == num-1 and plots: #when enables, makes plots of the fit function
      plt.errorbar(np.delete(bins,20), h_old,xerr=500,yerr=np.sqrt(h_old) ,fmt = 'x',label = "BackRemoved",ms = 2*(i+1))
      plt.plot(np.linspace(0,20000,20),exp_fit(np.linspace(0,20000,20),cf_new[0],cf_new[1]),'--',label = "Fit")
      plt.legend()
    h_flat, h_flat_var = op.curve_fit(flat_fit,np.linspace(cutoff*cf_new[1],20000,10),h_new[11:], p0=sum(h_new[12:])/len(h_new[12:]))
  print("Final rate",cf_new[1], "/pm", np.sqrt(cv_new[1][1]))
  print("Final covar", cv_new)
  return cf_new[1] , np.sqrt(cv_new[1][1]) # returns the final decay lifetime in ns, and the error in the decay lifetime
#end backround removal function
t_obs , t_obs_err = cleanup_hists(decaytimes_total, num = 3 , )

rho_obs = -(2197/2043)*((2043-t_obs)/(2197-t_obs))
#print(rho_obs)
def partial_rho_tpos(A,B,C):
  return C*(B-C)/(B*(A-C)**2)
def partial_rho_tneg(A,B,C):
  return (-1)*(A*C)/((B**2)*(A-C))
def partial_rho_tobs(A,B,C):
  return (A*(A-B))/(B*(A-C)**2)

def error_rho(p,A,B,C,Aerr,Berr,Cerr):
  err = p*np.sqrt((Aerr*partial_rho_tpos(A,B,C))**2+(Berr*partial_rho_tneg(A,B,C))**2+(Cerr*partial_rho_tobs(A,B,C))**2)
  print("Ratio +/- = ", round(p,2) , "/pm", round(err,2))
  return p,err

error_rho(rho_obs, 2197,2043,t_obs,0.4,3,terr) 
# it should be noted that the error calculation is only affected in the third significant figure by Aerr and Berr
# it is sufficient to only calculate the contribution from Cerr


 
