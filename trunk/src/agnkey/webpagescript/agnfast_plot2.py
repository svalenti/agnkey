#!/dark/usr/anaconda/bin/python                                                                                                                               
#/usr/bin/env python                                                                                                                                          

import sys,os,cgi,string,glob
os.environ['HOME']='../tmp/'

from socket import gethostname, gethostbyname
ip = gethostbyname(gethostname())
import urllib,urllib2
hostname=gethostname()

if hostname in ['engs-MacBook-Pro-4.local','valenti-macbook.physics.ucsb.edu','valenti-mbp-2',\
                'svalenti-lcogt.local','svalenti-lcogt.lco.gtn','valenti-mbp-2.lco.gtn',\
                'valenti-mbp-2.attlocal.net','dhcp43168.physics.ucdavis.edu',\
                'valenti-MacBook-Pro-2.local']:
    sys.path.append('/Users/svalenti/lib/python2.7/site-packages/')
    location='SV'
elif hostname in ['dark']:
    sys.path.append('/dark/hal/lib/python2.7/site-packages/')
    location='dark'
else:
    location='deneb'
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')

from numpy import array
import scipy
import pyfits,os,glob
import matplotlib
#matplotlib.use('Agg')
import numpy as np
from pylab import *


form = cgi.FieldStorage()
SN = form.getlist('SN')
directory = form.getlist('directory')

if not SN:
    SN=['ttMrk1048_20140907_None_2014-09-07.fits']
    directory=['/dark/hal/public_html/AGNKEY/test/']

print "Content-Type: text/html\n"
print '<html><body>'
#print str(directory[0])+str(SN[0])

fi=str(directory[0])+str(SN[0])

spec = pyfits.open(fi)
head = spec[0].header
graf=1
      
if spec[0].data.ndim == 1: fl = spec[0].data
elif spec[0].data.ndim == 2: fl = spec[0].data[:,0]
elif spec[0].data.ndim == 3: fl = spec[0].data[0,0,:]
naxis1 = head['naxis1']
try:
    crpix1 = head['crpix1']
    crval1 = head['crval1']
    try: cdelt1 = head['cdelt1']
    except: cdelt1 = head['cd1_1']
    pix = array(range(1,naxis1+1,1))
    pix = array(range(1,len(fl)+1,1))
    lam = (pix-crpix1)*cdelt1+crval1
except:
    try:
        WAT= head['WAT2_001']
        pix = array(range(1,naxis1+1,1))
        crpix1=string.split(string.split(WAT,'"')[1])[0]
        crval1=string.split(string.split(WAT,'"')[1])[3]
        cdelt1=string.split(string.split(WAT,'"')[1])[4]
        lam = (pix-float(crpix1))*float(cdelt1)+float(crval1)
    except:
        graf=0


if graf:
   massimo=np.sort(fl)[len(fl)-len(fl)/10]
   minimo=np.sort(fl)[len(fl)/10]
   delta=(massimo-minimo)/10   
   fileoutput='../tmp/pippo.png'
   titlin=SN[0]
   xlabel('Angstrom')
   ylabel('Flux')
   title(' '+str(titlin)+'')
   plot(lam,fl)
   ylim(minimo-4*delta,massimo+5*delta)
   savefig(fileoutput, format='png')

if graf:
   print '<img src="'+fileoutput+'" alt="" height="500" width="800">'
else:
    print '<h2> ERROR: problem to read the fits </h2>'
print '</body></html>'
