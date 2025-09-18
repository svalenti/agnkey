#!/dark/usr/anaconda2/bin/python                                                                                                                               
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
elif hostname in ['phys-dark']:
    sys.path.append('/dark/anaconda/anaconda27/envs/halenv/lib/python2.7/site-packages/')
#    sys.path.append('/dark/hal/anaconda2/envs/dlt40/lib/python2.7/site-packages/')
    location='phys-dark'
else:
    location='deneb'
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')

from astropy.io import fits as pyfits
import os,glob

form = cgi.FieldStorage()
SN = form.getlist('SN')
spettro = form.getlist('nomespettro')
directory = form.getlist('directory')

fi=str(directory[0])+str(SN[0])
#else:
#    spettro=['Mrk1048_20140903_red_blu_122349.437.fits']
#    fi='Mrk1048_20140903_red_blu_122349.437.fits'

def readspectrum(img):
    from numpy import array
    import pyfits
    import string
    fl=''
    lam=''
    graf=1
    spec = pyfits.open(img)
    head = spec[0].header
    try:
        if spec[0].data.ndim == 1: 
            fl = spec[0].data
            fl1=''
        elif spec[0].data.ndim == 2: 
            fl = spec[0].data[:,0]
            fl1=''
        elif spec[0].data.ndim == 3: 
            fl = spec[0].data[0,0,:]
            fl1= spec[0].data[3,0,:]
    except:
        if spec[0].data.rank == 1: 
            fl = spec[0].data
            fl1=''
        elif spec[0].data.rank == 2: 
            fl = spec[0].data[:,0]
            fl1=''
        elif spec[0].data.rank == 3: 
            fl = spec[0].data[0,0,:]
            fl1= spec[0].data[3,0,:]
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
    return lam,fl,fl1

###############################################################################

lam,fl,fl1=readspectrum(fi)

if len(fl): graf=1
else:  graf=0

spettro2=string.split(spettro[0],'.fits')[0]
os.system('rm -rf ../../tmp/*.asci')
ff = file('../../tmp/'+spettro2+'.asci','w')
if len(fl1):
    for i in range(len(lam)):
        ff.write('%10.10g\t%10.10g\t%10.10g\n' % (lam[i],fl[i],fl1[i]))
else:
    for i in range(len(lam)):
        ff.write('%10.10g\t%10.10g\n' % (lam[i],fl[i]))
ff.close()

os.system('chmod 777 ../../tmp/'+spettro2+'.asci')

print "Content-Type: text/html\n"
print '<html><body>'
if graf==1:
      print '<h4> The asci file has been created correctly <h4>'
      print '<h4> <a href="../../tmp/'+spettro2+'.asci"><b>&bull;</b> asci file</a></h4>'
else:
         print '<h4> Problem with the lambda calibration header <h4>'
print '</body></html>'
