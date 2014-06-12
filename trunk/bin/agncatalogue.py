#!/usr/bin/env python
description=">> make catalogue from table"
usage = "%prog image [options] "

import os,string,re,sys
from optparse import OptionParser
import time, math
import agnkey
from numpy import argmin, array,asarray,sqrt,compress

if __name__ == "__main__":
    start_time = time.time()
    parser = OptionParser(usage=usage,description=description)
    parser.add_option("-i", "--interactive",action="store_true",  dest='interactive',default=False,\
            help='Interactive \t\t\t [%default]')
    parser.add_option("-e", "--exzp",dest="exzp",default='',
           type='str',help='external zero point from different field \t\t %default')
    parser.add_option("-c", "--color",action="store_true",  dest='color',default=False,\
            help='use specific color \t\t\t [%default]')
    parser.add_option("-t", "--typemag",dest="typemag",default='fit',
           type='str',help='type of magnitude fit,ph \t\t %default')

    option,args = parser.parse_args()    
    if len(args)<1 : sys.argv.append('--help')
    _typemag=option.typemag
    if _typemag not in ['fit','ph']: sys.argv.append('--help')
    option,args = parser.parse_args()
    imglist = args[0]
    lista=agnkey.util.readlist(imglist)
    hdr=agnkey.util.readhdr(lista[0])
    tel=agnkey.util.readkey3(hdr,'telescop')
    filters=agnkey.sites.filterst(tel)
    filters1=agnkey.sites.filterst1(tel)
    _exzp=option.exzp
    _interactive= option.interactive
    _color=option.color
    dicti=agnkey.agnabsphotdef.makecatalogue(lista)
    namemag={'fit':['smagf','smagerrf'],'ph':['magp3','merrp3']}
    allfilters=''
    for fil in dicti:     allfilters=allfilters+filters1[fil]
    queste0=agnkey.agnloopdef.chosecolor(allfilters,False)
    queste1=agnkey.agnloopdef.chosecolor(allfilters,True)

    if _exzp:
        lista2=agnkey.util.readlist(_exzp)
        dicti2=agnkey.agnabsphotdef.makecatalogue(lista2)
        for _filter2 in dicti2:
            img2=dicti2[_filter2].keys()[0]
            for jj in  dicti2[_filter2][img2].keys():
                if 'ZP' in jj:
                    if _filter2 in dicti:
                        for img in dicti[_filter2].keys():
                            dicti[_filter2][img][jj]=dicti2[_filter2][img2][jj]
                            agnkey.util.updateheader(img,0,{jj:[dicti2[_filter2][img2][jj],'a b sa sb in y=a+bx']})
                            agnkey.util.updateheader(img,0,{'CATALOG':[str(img2),'catalogue source']})
#                            try:
                            mm=jj[2:]
                            result=string.split(dicti2[_filter2][img2][jj])
                            if mm[0]==mm[2]: num=2
                            elif mm[0]==mm[1]: num=1
                            agnkey.agnsqldef.updatevalue('dataredulco','zcol'+str(num),mm[1:],string.split(re.sub('sn2.fits','fits',img),'/')[-1])
                            agnkey.agnsqldef.updatevalue('dataredulco','z'+str(num),result[1],string.split(re.sub('sn2.fits','fits',img),'/')[-1])
                            agnkey.agnsqldef.updatevalue('dataredulco','c'+str(num),result[2],string.split(re.sub('sn2.fits','fits',img),'/')[-1])
                            agnkey.agnsqldef.updatevalue('dataredulco','dz'+str(num),result[3],string.split(re.sub('sn2.fits','fits',img),'/')[-1])
                            agnkey.agnsqldef.updatevalue('dataredulco','dc'+str(num),result[4],string.split(re.sub('sn2.fits','fits',img),'/')[-1])
                            #except:
                            #     print 'module mysqldef not found'
    for _filter in dicti:
        for img in dicti[_filter]:
            secondimage=[]
            jdvec=[]
            filtvec=[]
            colore=[]
            for ii in  dicti[_filter][img].keys():
                if 'ZP' in ii:          #  for each zero point available
                    cc= ii[-2:]         #  color used
                    for filt2 in dicti.keys():
                        if filt2!=_filter:
                            for jj in dicti[filt2].keys():
                                for ll in  dicti[filt2][jj].keys():
                                    if 'ZP' in ll and ll[-2:]==cc:
                                                secondimage.append(jj)
                                                jdvec.append(dicti[filt2][jj]['JD']-dicti[_filter][img]['JD'])                            
                                                filtvec.append(filt2)
                                                colore.append(cc)

            if len(secondimage)>0:
                colorescelto=''
                vv=queste1[agnkey.sites.filterst1(tel)[_filter]]
                if len(vv)>0:
                    if vv[0].upper() in colore:  colorescelto=vv[0].upper()
                else:
                    vv=queste0[agnkey.sites.filterst1(tel)[_filter]]
                    if len(vv)>0:
                        if vv[0].upper() in colore:  colorescelto=vv[0].upper()
                if colorescelto:
                    print 'use '+_filter+' with color '+colorescelto
                    filtvec=compress(array(colore)==colorescelto,filtvec)
                    jdvec=compress(array(colore)==colorescelto,jdvec)
                    secondimage=compress(array(colore)==colorescelto,secondimage)
                    colore=compress(array(colore)==colorescelto,colore)

                dicti[_filter][img]['secondimg']=secondimage[argmin(jdvec)]    #  the closest image
                dicti[_filter][img]['secondfilt']=filtvec[argmin(jdvec)]       #  the closest image
                _filter2=dicti[_filter][img]['secondfilt']
                col=colore[argmin(jdvec)]
                ra0=dicti[_filter][img]['ra0']
                dec0=dicti[_filter][img]['dec0']
                ra=dicti[_filter][img]['ra']
                dec=dicti[_filter][img]['dec']
                if dicti[_filter][img]['telescope'] in ['lsc','1m0-04','1m0-05','1m0-06','1m0-09']:   kk=agnkey.sites.extintion('ctio')
                elif dicti[_filter][img]['telescope'] in ['1m0-08','elp']:                            kk=agnkey.sites.extintion('mcdonald')
                elif dicti[_filter][img]['telescope'] in ['1m0-10','1m0-12','1m0-13','cpt']:          kk=agnkey.sites.extintion('southafrica')
                elif dicti[_filter][img]['telescope'] in ['ftn']:                                     kk=agnkey.sites.extintion('mauna')
                elif dicti[_filter][img]['telescope'] in ['1m0-11','coj','fts']:                      kk=agnkey.sites.extintion('siding')
                else: 
                    print dicti[_filter][img]['telescope']
                    sys.exit('problem with dicti 1')
                #                                                    instrumental mag to exposure 1 second corrected for airmass
#                mag0=dicti[_filter][img][namemag[_typemag][0]]+2.5*math.log10(dicti[_filter][img]['exptime'])-kk[filters1[_filter]]*dicti[_filter][img]['airmass']
                mag0=dicti[_filter][img][namemag[_typemag][0]]-kk[filters1[_filter]]*dicti[_filter][img]['airmass']
                dmag0=dicti[_filter][img][namemag[_typemag][1]]

#   img 2  ###############
                img2=dicti[_filter][img]['secondimg']
                ra1=dicti[_filter2][img2]['ra0']
                dec1=dicti[_filter2][img2]['dec0']

                if dicti[_filter2][img2]['telescope'] in ['lsc','1m0-04','1m0-05','1m0-06','1m0-09']:   kk=agnkey.sites.extintion('ctio')
                elif dicti[_filter2][img2]['telescope'] in ['1m0-08','elp']:                            kk=agnkey.sites.extintion('mcdonald')
                elif dicti[_filter2][img2]['telescope'] in ['1m0-10','1m0-12','1m0-13','cpt']:          kk=agnkey.sites.extintion('southafrica')
                elif dicti[_filter2][img2]['telescope'] in ['ftn']:                                     kk=agnkey.sites.extintion('mauna')
                elif dicti[_filter][img]['telescope'] in ['1m0-11','coj','fts']:                        kk=agnkey.sites.extintion('siding')
                else: 
                    print dicti[_filter2][img2]
                    sys.exit('problem with dicti 2')
                #                                                    instrumental mag to exposure 1 second corrected for airmass
#                mag1=dicti[_filter2][img2][namemag[_typemag][0]]+2.5*math.log10(dicti[_filter2][img2]['exptime'])-kk[filters1[_filter2]]*dicti[_filter2][img2]['airmass']
                mag1=dicti[_filter2][img2][namemag[_typemag][0]]-kk[filters1[_filter2]]*dicti[_filter2][img2]['airmass']
                dmag1=dicti[_filter2][img2][namemag[_typemag][1]]

                if _interactive:
                    agnkey.util.marksn2(re.sub('sn2.fits','fits',img),img,1,img2)
                    agnkey.util.marksn2(re.sub('sn2.fits','fits',img2),img2,2,img)
                    print img,img2,_filter,_filter2,2.5*math.log10(dicti[_filter2][img2]['exptime']),kk[filters1[_filter2]]*dicti[_filter2][img2]['airmass']
                    
                distvec,pos0,pos1=agnkey.agnastrodef.crossmatch(array(ra0),array(dec0),array(ra1),array(dec1),10)

                mag0cut=mag0[pos0]
                mag1cut=mag1[pos1]
                dmag0cut=dmag0[pos0]
                dmag1cut=dmag1[pos1]
                ra0cut=ra0[pos0]
                dec0cut=dec0[pos0]
                racut=ra[pos0]
                deccut=dec[pos0]
                ww=asarray([i for i in range(len(mag0cut)) if (abs(float(mag0cut[i]))<99 and  abs(float(mag1cut[i]))<99    )])
                if len(ww)>0:
                    mag0cut,mag1cut,dmag0cut,dmag1cut,ra0cut,dec0cut,racut,deccut=mag0cut[ww],mag1cut[ww],dmag0cut[ww],dmag1cut[ww],ra0cut[ww],dec0cut[ww],racut[ww],deccut[ww]

                if _interactive:
                    from pylab import *
                    ion()
                    clf()
                    #print len(pos0)
                    plot(ra1,dec1,'xb')
                    plot(ra0,dec0,'xr')
                    plot(ra0cut,dec0cut,'xg')

                output=re.sub('sn2.fits','cat',img)
                f=open(output,'w')
                f.write('#daophot+standardfield\n#ra   dec   '+filters1[_filter]+'   d'+filters1[_filter]+'\n')
                if filters1[_filter].upper()==col[0]:
                    Z1=float(string.split(dicti[_filter][img]['ZP'+filters1[_filter].upper()+col.upper()])[1])
                    C1=float(string.split(dicti[_filter][img]['ZP'+filters1[_filter].upper()+col.upper()])[2])
                    Z2=float(string.split(dicti[_filter2][img2]['ZP'+filters1[_filter2].upper()+col.upper()])[1])
                    C2=float(string.split(dicti[_filter2][img2]['ZP'+filters1[_filter2].upper()+col.upper()])[2])
                    DZ1=0.0
                    DZ2=0.0
                    M1,M2=agnkey.agnabsphotdef.finalmag(Z1,Z2,C1,C2,mag0cut,mag1cut)
                    dc1,dc2,dz1,dz2,dm1,dm2=agnkey.agnabsphotdef.erroremag(Z1,Z2,M1,M2,C1,C2,0)
                    DM11=sqrt((dm1*dmag0cut)**2+(dz1*DZ1)**2+(dm2*dmag1cut)**2+(dz2*DZ2)**2)

                    if _interactive:
                        print '\n####  example computation '
                        print 'Z1  Z1  C1   C2   mag1    mag 2'
                        print 'M1   M2 '
                        for gg in range(0,len(mag0cut)):
                                            print racut[gg],deccut[gg],Z1,Z2,C1,C2,mag0cut[gg],mag1cut[gg],M1[gg],M2[gg]

                    for i in range(0,len(ra0cut)):
                        f.write('%15s \t%15s \t%s\t%s\n' % (racut[i],deccut[i],M1[i], dmag0cut[i]))
                else:
                    Z2=float(string.split(dicti[_filter][img]['ZP'+filters1[_filter].upper()+col.upper()])[1])
                    C2=float(string.split(dicti[_filter][img]['ZP'+filters1[_filter].upper()+col.upper()])[2])
                    Z1=float(string.split(dicti[_filter2][img2]['ZP'+filters1[_filter2].upper()+col.upper()])[1])
                    C1=float(string.split(dicti[_filter2][img2]['ZP'+filters1[_filter2].upper()+col.upper()])[2])
                    M1,M2=agnkey.agnabsphotdef.finalmag(Z1,Z2,C1,C2,mag1cut,mag0cut)
                    DZ1=0.0
                    DZ2=0.0
                    dc1,dc2,dz1,dz2,dm1,dm2=agnkey.agnabsphotdef.erroremag(Z1,Z2,mag0cut,mag1cut,C1,C2,1)
                    DM22=sqrt((dm1*dmag0cut)**2+(dz1*DZ1)**2+(dm2*dmag1cut)**2+(dz2*DZ2)**2)

                    if _interactive:
                        print '\n####  example computation '
                        print 'Z1  Z1  C1   C2   mag1    mag 2'
                        print 'M1   M2 '
                        for gg in range(0,len(mag0cut)):
                                            print racut[gg],deccut[gg],Z1,Z2,C1,C2,mag0cut[gg],mag1cut[gg],M1[gg],M2[gg]
                    
                    for i in range(0,len(ra0cut)):
                        f.write('%15s \t%15s \t%s\t%s\n' % (racut[i],deccut[i],M2[i], dmag0cut[i]))
                f.close()
                os.chmod(output,0664)

                if _interactive:    raw_input('go on')
                try:
                    if os.path.isfile(re.sub('sn2.fits','cat',img)):
                        agnkey.agnsqldef.updatevalue('dataredulco','abscat',string.split(output,'/')[-1],re.sub('sn2.fits','fits',string.split(img,'/')[-1]))
                    else:
                        agnkey.agnsqldef.updatevalue('dataredulco','abscat','X',re.sub('sn2.fits','fits',string.split(img,'/')[-1]))
                except:
                    print 'module mysqldef not found'
                #print _filter, col, output
            else:
                print 'no other filters with calibration in '+_filter+' band'
                print img,_filter,dicti[_filter][img].keys()
                try:
                    agnkey.agnsqldef.updatevalue('dataredulco','abscat','X',re.sub('sn2.fits','fits',string.split(img,'/')[-1]))
                except:
                    print 'module mysqldef not found'

