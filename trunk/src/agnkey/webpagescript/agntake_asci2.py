#!/usr/bin/env python

import sys,os,cgi,string,glob
from socket import gethostname, gethostbyname,gethostname
ip = gethostbyname(gethostname())
import urllib,urllib2
hostname=gethostname()
os.environ['HOME']='../tmp/'

if hostname in ['engs-MacBook-Pro-4.local','valenti-macbook.physics.ucsb.edu','svalenti-lcogt.local','svalenti-lcogt.lco.gtn']:
    sys.path.append('/Users/svalenti/lib/python2.7/site-packages/')
else:
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')

from scipy import array
import scipy
import pyfits,os,glob

form = cgi.FieldStorage()
SN = form.getlist('SN')
spettro = form.getlist('nomespettro')
directory = form.getlist('directory')
#asa = '../QUBA/spectra/'
#fi=str(asa[0])+str(SN[0])+'/'+str(spettro[0])

fi=str(directory[0])+str(SN[0])

#jd = fi[fi.rindex(SN[0]):]
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

spettro2=string.split(spettro[0],'.fits')[0]

os.system('rm -rf ../tmp/*.asci')
ff = file('../tmp/'+spettro2+'.asci','w')
for i in range(len(lam)):
    ff.write('%10.10g\t%10.10g\n' % (lam[i],fl[i]))
ff.close()
os.system('chmod 777 ../tmp/'+spettro2+'.asci')


print "Content-Type: text/html\n"
print '<html><body>'
if graf==1:
      print '<h4> The asci file has been created correctly <h4>'
      print '<h4> <a href="../tmp/'+spettro2+'.asci"><b>&bull;</b> asci file</a></h4>'
else:
         print '<h4> Problem with the lambda calibration header <h4>'
print '</body></html>'
