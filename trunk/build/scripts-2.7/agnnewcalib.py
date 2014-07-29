#!/usr/bin/python
description=">> new calibration"
usage = "%prog image [options] "

import os,string,re,sys,glob
from optparse import OptionParser
import time
import agnkey
import pyfits
import numpy as np
import math

def vizq(_ra,_dec,catalogue,radius):
    ''' Query vizquery '''
    import os,string,re
    _site='vizier.cfa.harvard.edu'
#    _site='vizier.u-strasbg.fr'
    cat={'usnoa2':['I/252/out','USNO-A2.0','Rmag'],'2mass':['II/246/out','2MASS','Jmag'],\
         'landolt':['II/183A/table2','','Vmag,B-V,U-B,V-R,R-I,Star,e_Vmag'],\
         'apass':['I/322A/out','','Bmag,Vmag,gmag,rmag,imag,e_Vmag,e_Bmag,e_gmag,e_rmag,e_imag,UCAC4'],\
         'usnob1':['I/284/out','USNO-B1.0','R2mag'],'sdss7':['II/294/sdss7','','objID,umag,gmag,rmag,imag,zmag,gc'],\
         'sdss9':['V/139/sdss9','','objID,umag,gmag,rmag,imag,zmag,e_umag,e_gmag,e_rmag,e_imag,e_zmag,gc'],\
         'sdss7':['II/294/sdss7','','objID,umag,gmag,rmag,imag,zmag,e_umag,e_gmag,e_rmag,e_imag,e_zmag,gc'],\
         'sdss8':['II/306/sdss8','','objID,umag,gmag,rmag,imag,zmag,e_umag,e_gmag,e_rmag,e_imag,e_zmag,gc']}

    a=os.popen('vizquery -mime=tsv  -site='+_site+' -source='+cat[catalogue][0]+\
                   ' -c.ra='+str(_ra)+' -c.dec='+str(_dec)+' -c.eq=J2000 -c.rm='+str(radius)+\
                   ' -c.geom=b -oc.form=h -sort=_RA*-c.eq -out.add=_RAJ2000,_DEJ2000 -out.max=10000 -out='+\
                   cat[catalogue][1]+' -out='+cat[catalogue][2]+'').read()
    print 'vizquery -mime=tsv  -site='+_site+' -source='+cat[catalogue][0]+\
                   ' -c.ra='+str(_ra)+' -c.dec='+str(_dec)+' -c.eq=J2000 -c.rm='+str(radius)+\
                   ' -c.geom=b -oc.form=h -sort=_RA*-c.eq -out.add=_RAJ2000,_DEJ2000 -out.max=10000 -out='+\
                   cat[catalogue][1]+' -out='+cat[catalogue][2]+''
    aa=a.split('\n')
    bb=[]
    for i in aa:
        if i and i[0]!='#':   bb.append(i)
    _ra,_dec,_name,_mag=[],[],[],[]
    for ii in bb[3:]:
        aa=ii.split('\t')
        rr,dd=agnkey.agnabsphotdef.deg2HMS(ra=re.sub(' ',':',aa[0]), dec=re.sub(' ',':',aa[1]), round=False)
        _ra.append(rr)
        _dec.append(dd)
        _name.append(aa[2])
    dictionary={'ra':_ra,'dec':_dec,'id':_name}
    sss=string.split(cat[catalogue][2],',')
    for ii in sss: dictionary[ii]=[]
    for ii in bb[3:]:
        aa=ii.split('\t')
        for gg in range(0,len(sss)):
           if sss[gg] not in ['UCAC4','id']:
              try:
                 dictionary[sss[gg]].append(float(aa[2+gg]))
              except:    
                 dictionary[sss[gg]].append(float(9999))
           else:
                 dictionary[sss[gg]].append(str(aa[2+gg]))

    if catalogue in ['sdss7','sdss9','sdss8']:
        dictionary['u']=dictionary['umag']
        dictionary['g']=dictionary['gmag']
        dictionary['r']=dictionary['rmag']
        dictionary['i']=dictionary['imag']
        dictionary['z']=dictionary['zmag']
        dictionary['uerr']=dictionary['e_umag']
        dictionary['gerr']=dictionary['e_gmag']
        dictionary['rerr']=dictionary['e_rmag']
        dictionary['ierr']=dictionary['e_imag']
        dictionary['zerr']=dictionary['e_zmag']
        for key in dictionary.keys():
           if key!='r':
              dictionary[key]=np.compress((np.array(dictionary['r'])<19)&(np.array(dictionary['r']>10)),dictionary[key])
        dictionary['r']=np.compress((np.array(dictionary['r'])<19)&(np.array(dictionary['r']>10)),dictionary['r'])

    elif  catalogue=='landolt':
        dictionary['B']=np.array(dictionary['Vmag'])+np.array(dictionary['B-V'])
        dictionary['U']=np.array(dictionary['B'])+np.array(dictionary['U-B'])
        dictionary['V']=np.array(dictionary['Vmag'])
        dictionary['Verr']=np.array(dictionary['e_Vmag'])
        dictionary['R']=np.array(dictionary['Vmag'])-np.array(dictionary['V-R'])
        dictionary['I']=np.array(dictionary['R'])-np.array(dictionary['R-I'])
        dictionary['id']=np.array(dictionary['Star'])
    elif  catalogue=='apass':
        dictionary['B']=np.array(dictionary['Bmag'])
        dictionary['V']=np.array(dictionary['Vmag'])
        dictionary['g']=np.array(dictionary['gmag'])
        dictionary['r']=np.array(dictionary['rmag'])
        dictionary['i']=np.array(dictionary['imag'])
        dictionary['Berr']=np.array(dictionary['e_Bmag'],float)/100.
        dictionary['Verr']=np.array(dictionary['e_Vmag'],float)/100.
        dictionary['gerr']=np.array(dictionary['e_gmag'],float)/100.
        dictionary['rerr']=np.array(dictionary['e_rmag'],float)/100.
        dictionary['ierr']=np.array(dictionary['e_imag'],float)/100.
        dictionary['id']=np.array(dictionary['UCAC4'],str)
        for key in dictionary.keys():
           if key!='r':
              dictionary[key]=np.compress((np.array(dictionary['r'])<22)&(np.array(dictionary['r']>10.5)),dictionary[key])
        dictionary['r']=np.compress((np.array(dictionary['r'])<22)&(np.array(dictionary['r']>10.5)),dictionary['r'])
    return dictionary

########################################################################
def crossmatch(_ra0,_dec0,_ra1,_dec1,tollerance):  #   degree,degree,degree,degree,arcsec
    from numpy import pi, cos, sin, array, argmin, min,arccos, array, float64
    scal=pi/180.
    distvec=[]
    pos0=[]
    pos1=[]
    i=0
    _ra0,_dec0,_ra1,_dec1=array(_ra0,float),array(_dec0,float),array(_ra1,float),array(_dec1,float)
    for jj in range(0,len(_ra0)):
        try:
            distance=arccos(array(sin(array(_dec1,float64)*scal)*sin(_dec0[jj]*scal))+\
                            array(cos(array(_dec1,float64)*scal)*cos(_dec0[jj]*scal)*cos((array(_ra1,float64)-_ra0[jj])*scal)))
            if min(distance)<=tollerance*pi/(180*3600):
                distvec.append(min(distance))
                pos0.append(jj)
                pos1.append(argmin(distance))
        except: pass
    return  distvec,pos0,pos1  #  

########################################################################

if __name__ == "__main__":
  start_time = time.time()
  parser = OptionParser(usage=usage,description=description)
  option,args = parser.parse_args()
  if len(args)<1 : sys.argv.append('--help')
  option,args = parser.parse_args()
  imglist = agnkey.util.readlist(args[0])    
  for img in imglist:
    table=agnkey.agnabsphotdef.makecatalogue([img])
    _filter=table.keys()[0]
    _rasex=table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['ra0']
    _decsex=table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['dec0']
    _magp2=table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['magp2']
    _magp3=table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['magp3']
    _magp4=table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['magp4']
    _merrp2=table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['merrp2']
    _merrp3=table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['merrp3']
    _merrp4=table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['merrp4']
    hdr=pyfits.open(img)[0].header
    _ra0=hdr['RA']
    _dec0=hdr['DEC']

    _exptime=hdr['exptime']
    #_ra0,_dec0=agnkey.agnabsphotdef.deg2HMS(_ra0,_dec0)
    #_apass=vizq(_ra0,_dec0,'apass',20)
    #_sloan=vizq(_ra0,_dec0,'sdss7',20)

    _object=agnkey.util.readkey3(hdr,'object')
    
    mag=_magp4
    magerr=_merrp4
    _filter=re.sub('p','',_filter)
    _filter=re.sub('s','',_filter)

    _cat=''
    if _filter in ['u','g','r','i','z']:
        _catalogue=glob.glob(agnkey.__path__[0]+'/standard/cat/sloan/'+_object+'*')
        if _catalogue:
            _sloan=agnkey.agnastrodef.readtxt(_catalogue[0])
            for _id in _sloan:
                try:
                    _sloan[_id]=np.array(_sloan[_id],float)
                except: 
                    pass

            print 'use catalogue from archive for object '+str(_object)
        else: _sloan=''
        if not _sloan:
            _sloan=vizq(_ra0,_dec0,'sdss7',20)

        if _sloan:  _cat=_sloan
        else:
            if _filter in ['g','r','i']:
                _apass=vizq(_ra0,_dec0,'apass',20)
                if _apass:   _cat=_apass
    elif _filter in ['U','B','V','R','I']:
        _catalogue=glob.glob(agnkey.__path__[0]+'/standard/cat/landolt/'+_object+'*')
        if _catalogue:
            _landolt=agnkey.agnastrodef.readtxt(_catalogue[0])
            print 'use catalogue from archive for object '+str(_object)
            for _id in _landolt:
                try:
                    _landolt[_id]=np.array(_landolt[_id],float)
                except: 
                    pass

        else: _landolt=''
        if not _landolt:
            if _filter in ['B','V']:
                _landolt=vizq(_ra0,_dec0,'apass',20)

        if _landolt:   _cat=_landolt
                
    if _cat:
        distvec,pos0,pos1=crossmatch(_rasex,_decsex,_cat['ra'],_cat['dec'],5)
    else:  
        pos0=[]

    if len(pos0)>=3:
#        _apass=agnkey.util.transform2natural(_instrument,_apass,'apass')
#        _apass=agnkey.util.transform2natural(_instrument,_apass,'apass')
        xx=np.compress(   (np.array(_cat[_filter])[pos1]<=99)&((np.array(mag[pos0]))<=99), np.array(_cat[_filter])[pos1])
        yy=np.compress(   (np.array(_cat[_filter])[pos1]<=99)&((np.array(mag[pos0]))<=99), np.array(mag[pos0]))
        yyerr=np.compress((np.array(_cat[_filter])[pos1]<=99)&((np.array(mag[pos0]))<=99), np.array(magerr[pos0]))
        xxerr=np.compress((np.array(_cat[_filter])[pos1]<=99)&((np.array(mag[pos0]))<=99), np.array(_cat[_filter+'err'])[pos1])
        
        ZZ=np.array(xx-yy)
        data2,std2,ZZ0=agnkey.agnabsphotdef.zeronew(ZZ,maxiter=10,nn=2,verbose=True,show=False)
        agnkey.agnsqldef.updatevalue('dataredulco','ZPN',float(ZZ0),string.split(re.sub('sn2.','',img),'/')[-1])
        agnkey.agnsqldef.updatevalue('dataredulco','ZPNERR',float(std2),string.split(re.sub('sn2.','',img),'/')[-1])
        agnkey.agnsqldef.updatevalue('dataredulco','ZPNNUM',len(data2),string.split(re.sub('sn2.','',img),'/')[-1])
        targ=agnkey.agnsqldef.targimg(img)
        aa=agnkey.agnsqldef.query(['select ra_sn,dec_sn from lsc_sn_pos where id="'+str(targ)+'"'])
        if len(aa)>0:
            rasn=aa[0]['ra_sn']
            decsn=aa[0]['dec_sn']        
            from pyraf import iraf
            iraf.astcat(_doprint=0)
            iraf.imcoords(_doprint=0)
            iraf.digiphot(_doprint=0)
            iraf.daophot(_doprint=0)
            from iraf import digiphot
            from iraf import daophot
            from iraf import ptools
            lll=[str(rasn)+'    '+str(decsn)]
            sss=iraf.wcsctran('STDIN','STDOUT',img,Stdin=lll,inwcs='world',units='degrees degrees',outwcs='logical',columns='1 2',formats='%10.1f %10.1f',Stdout=1)
            f=open('_coord','w')
            f.write(sss[-1])
            f.close()
            a1,a2,a3,a4,= int(5),int(8),int(10),int(12)
            ap = str(a2)+","+str(a3)+","+str(a4)
            _gain=agnkey.util.readkey3(hdr,'gain')
            _ron=agnkey.util.readkey3(hdr,'ron')
            _exptime=agnkey.util.readkey3(hdr,'exptime')
            _datamin=-100
            _datamax=45000
            iraf.noao.digiphot.daophot.photpars.zmag = 0
            iraf.noao.digiphot.daophot.datapars.readnoi = _gain  #1.4   #_ron
            iraf.noao.digiphot.daophot.datapars.epadu = _ron  #  13      #_gain
            iraf.noao.digiphot.daophot.datapars.datamin = -100  # -100  #_datamin
            iraf.noao.digiphot.daophot.datapars.datamax = 51000 #_datamax
            iraf.noao.daophot.fitskypars.annulus=a4+4
            iraf.noao.daophot.photpars.apertures = ap
            iraf.noao.digiphot.daophot.datapars.exposure = 'exptime'
            iraf.noao.digiphot.daophot.datapars.airmass = 'airmass'
            iraf.noao.digiphot.daophot.datapars.filter = 'filter2'
            iraf.noao.digiphot.daophot.daopars.psfrad = a4
            iraf.noao.digiphot.daophot.daopars.fitrad = a1
            iraf.noao.digiphot.daophot.daopars.sannulus = int(a4)+4
            iraf.noao.digiphot.daophot.daopars.recenter = 'yes'
            iraf.noao.digiphot.daophot.daopars.fitsky = 'yes'
            iraf.noao.digiphot.daophot.centerpars.cbox = 4
            iraf.noao.digiphot.daophot.centerpars.calgori = 'gauss'
            aaa=iraf.noao.digiphot.daophot.phot(re.sub('sn2.','',img),'_coord','STDOUT',veri='no',verbose='no',Stdout=1)   
            aaa=[i for i in aaa if i[0]!='#']
            mag1,dmag1=string.split(aaa[-3])[4],string.split(aaa[-3])[5]
            mag2,dmag2=string.split(aaa[-2])[4],string.split(aaa[-2])[5]
            mag3,dmag3=string.split(aaa[-1])[4],string.split(aaa[-1])[5]
            if float(mag1): 
                print float(mag1)+ZZ0
                try:
                    agnkey.agnsqldef.updatevalue('dataredulco','appmagap1',float(mag1)+ZZ0,string.split(re.sub('sn2.','',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue('dataredulco','dappmagap1',float(dmag1),string.split(re.sub('sn2.','',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue('dataredulco','instmagap1',float(mag1),string.split(re.sub('sn2.','',img),'/')[-1])
                except: pass
            if float(mag2): 
                print float(mag2)+ZZ0
                try:
                    agnkey.agnsqldef.updatevalue('dataredulco','appmagap2',float(mag3)+ZZ0,string.split(re.sub('sn2.','',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue('dataredulco','dappmagap2',float(dmag1),string.split(re.sub('sn2.','',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue('dataredulco','instmagap2',float(mag3),string.split(re.sub('sn2.','',img),'/')[-1])
                except: pass
            if float(mag3): 
                print float(mag3)+ZZ0
                try:
                    agnkey.agnsqldef.updatevalue('dataredulco','appmagap3',float(mag3)+ZZ0,string.split(re.sub('sn2.','',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue('dataredulco','dappmagap3',float(dmag1),string.split(re.sub('sn2.','',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue('dataredulco','instmagap3',float(mag3),string.split(re.sub('sn2.','',img),'/')[-1])
                except: pass
