#!/usr/bin/env python
description=">> make different image using hotpants"
usage = "%prog imagein  imagetem [options] "
import os
import string
import re
import sys
import glob
#from numpy import array, median, argmin, sqrt, round, isnan, compress, std
import agnkey
import numpy as np
import pyfits
from optparse import OptionParser,OptionGroup

def crossmatchtwofiles(img1,img2,radius=3):
    import agnkey
    import pywcs
    from numpy import array, argmin, min, sqrt
    hd1 = pyfits.getheader(img1)
    hd2 = pyfits.getheader(img2)
    wcs1 = pywcs.WCS(hd1)
    wcs2 = pywcs.WCS(hd2)

    xpix1,ypix1,fw1,cl1,cm1,ell1,bkg1,fl1=agnkey.agnastrodef.sextractor(img1)
    xpix2,ypix2,fw2,cl2,cm2,ell2,bkg2,fl2=agnkey.agnastrodef.sextractor(img2)
    xpix1,ypix1,xpix2,ypix2=array(xpix1,float),array(ypix1,float),array(xpix2,float),array(ypix2,float)  

    bb = wcs1.wcs_pix2sky(zip(xpix1,ypix1), 1)    #   transform pixel in coordinate
    xra1,xdec1 = zip(*bb)
    bb = wcs2.wcs_pix2sky(zip(xpix2,ypix2), 1)    #   transform pixel in coordinate
    xra2,xdec2 = zip(*bb)

    xra1,xdec1,xra2,xdec2 = array(xra1,float),array(xdec1,float),array(xra2,float),array(xdec2,float)
    distvec,pos1,pos2 = agnkey.agnastrodef.crossmatch(xra1,xdec1,xra2,xdec2,radius)
    #dict={}
    dict={'ra1':xra1[pos1],'dec1':xdec1[pos1],'ra2':xra2[pos2],'dec2':xdec2[pos2],\
         'xpix1':xpix1[pos1],'ypix1':ypix1[pos1],'xpix2':xpix2[pos2],'ypix2':ypix2[pos2]}
    np.savetxt('substamplist',zip(xpix1[pos1],ypix1[pos1]),fmt='%10.10s\t%10.10s')    
    return 'substamplist',dict


###################################################
if __name__ == "__main__":
     parser = OptionParser(usage=usage,description=description)
     parser.add_option("-c", "--check",dest="check",action="store_true",
                       default=False, help=' check images registration \t\t\t [%default]')
     parser.add_option("-f", "--force",dest="force",action="store_true",
                       default=False, help=' force archiving \t\t\t [%default]')
     parser.add_option("--show",dest="show",action="store_true",
                       default=False, help=' show result  \t\t\t [%default]')
     hotpants = OptionGroup(parser, "hotpants parameters")
     hotpants.add_option("--nrxy",dest="nrxy",default='1,1',
                         help='Number of image region in x y directions \t [%default]')
     hotpants.add_option("--nsxy",dest="nsxy",default='8,8',
                         help="Number of region's stamps in x y directions\t [%default]")
     hotpants.add_option("--ko",dest="ko",default='1',
                         help='spatial order of kernel variation within region\t [%default]')
     hotpants.add_option("--bgo",dest="bgo",default='1',
                         help='spatial order of background variation within region \t [%default]')
     hotpants.add_option("--afssc",dest="afssc",default=False,
                         action="store_true",help='use selected stamps \t\t\t [%default]')
     hotpants.add_option("--normalize",dest="normalize",default='i',
                         help='normalize zero point to image [i] or template [t] \t [%default]')
     hotpants.add_option("--interpolation",dest="interpolation",default='drizzle',
                         help='interpolation algorithm  [drizzle,nearest,linear,poly3,poly5,spline3]\t [%default]')
     parser.add_option_group(hotpants)

     option,args = parser.parse_args()    
     _normalize=option.normalize
     _interpolation=option.interpolation
     if _normalize not in ['i','t']:
         sys.argv.append('--help')
     if _interpolation not in ['drizzle','nearest','linear','poly3','poly5','spline3']:  
     		sys.argv.append('--help')
     if len(args)<2 :
         sys.argv.append('--help')
     option,args = parser.parse_args()
     imglisttar = agnkey.util.readlist(args[0])
     imglisttemp = agnkey.util.readlist(args[1])
     from numpy import where,mean

     _checkast = option.check
     _force = option.force
     _show = option.show
     nrxy = option.nrxy
     nsxy = option.nsxy
     ko = option.ko
     bgo = option.bgo
     afssc = option.afssc

     
     listatar = {}
     for img in imglisttar:
         hdr = agnkey.util.readhdr(img)
         _filter = agnkey.util.readkey3(hdr,'filter')
         _obj = agnkey.util.readkey3(hdr,'object')
         if _filter not in listatar:
             listatar[_filter] = {}
         if _obj not in listatar[_filter]:
             listatar[_filter][_obj] = []
         listatar[_filter][_obj].append(img)

     listatemp = {}
     for img in imglisttemp:
         hdr = agnkey.util.readhdr(img)
         _filter = agnkey.util.readkey3(hdr,'filter')
         _obj = agnkey.util.readkey3(hdr,'object')
         if _filter not in listatemp:
             listatemp[_filter] = {}
         if _obj not in listatemp[_filter]:
             listatemp[_filter][_obj] = []
         listatemp[_filter][_obj].append(img)

     from pyraf import iraf
     from iraf import images
     from iraf import immatch
     for f in listatar:
         for o in listatar[f]:
             if f in listatemp:
                 if o in listatemp[f]:
                     imglist1 = listatar[f][o]
                     imglist2 = listatemp[f][o]
                     for imgtar in imglist1:
                        imgtemp = imglist2[0]
                        tarmask = re.sub('.fits','.mask.fits',string.split(imgtar,'/')[-1])
                        tempmask = re.sub('.fits','.mask.fits',string.split(imgtemp,'/')[-1])
                        imgout = re.sub('.fits','.diff.fits',string.split(imgtar,'/')[-1])
                        outmask = re.sub('.fits','.mask.fits',string.split(imgout,'/')[-1])
                        hdtar = pyfits.getheader(imgtar)
                        artar = pyfits.getdata(imgtar)
                        
                        if os.path.isfile(re.sub('.fits','.sn2.fits',imgtemp)):
                             hdtempsn = pyfits.getheader(re.sub('.fits','.sn2.fits',imgtemp))
                        else: 
                             hdtempsn = {}
                        
                        if 'SATURATE' in hdtar:
                            saturation = hdtar['SATURATE']
                        else:
                            saturation = 50000
                            
##############################       use geomap to register the two images        ############################
                        substamplist,dict = crossmatchtwofiles(imgtar,imgtemp,4)
                        xra1,xdec1,xra2,xdec2,xpix1,ypix1,xpix2,ypix2 = dict['ra1'],dict['dec1'],dict['ra2'],\
                                                                      dict['dec2'],dict['xpix1'],dict['ypix1'],\
                                                                      dict['xpix2'],dict['ypix2']
#                        substamplist,xra1,xdec1,xra2,xdec2=crossmatchtwofiles(imgtar,imgtemp,4)
#                        substamplist,xpix1,ypix1,xpix2,ypix2=crossmatchtwofiles(imgtar,imgtemp,4)
#                        distvec,pos0,pos1=agnkey.agnastrodef.crossmatch(xra1,xdec1,xra2,xdec2,4)
#                        distvec,pos0,pos1=agnkey.agnastrodef.crossmatchxy(xpix1,ypix1,xpix2,ypix2,4)
                        print len(xpix1)
                        vector4=[str(k)+' '+str(v)+' '+str(j)+' '+str(l) for k,v,j,l in  zip(xpix1,ypix1,xpix2,ypix2)]
                        if len(vector4) >= 12:
                            num=3
                        else:
                            num=2
                        np.savetxt('tmpcoo',vector4,fmt='%1s')
                        iraf.immatch.geomap('tmpcoo',"tmp$db",1,hdtar['NAXIS1'],1,hdtar['NAXIS2'],fitgeom="general",
                                            functio="legendre", xxor=num,xyor=num,xxterms="half",yxor=num,yyor=num,
                                            yxterms="half",calctype="real",inter='No')
                        
                        agnkey.util.delete('_temp0.fits')
                        agnkey.util.delete('_temp.fits')
                        agnkey.util.delete('_tar.fits')

                        iraf.immatch.gregister(imgtemp,"_temp0","tmp$db","tmpcoo",geometr="geometric",
                                               interpo=_interpolation, boundar='constant', constan=0,
                                               flux='yes',verbose='yes')

                        if hdtar['INSTRUME'] in agnkey.util.instrument0['sbig']:
                            iraf.imarith('_temp0.fits','+','200','_temp.fits',verbose='yes')
                            iraf.imarith(imgtar,'+','200','_tar.fits',verbose='yes')
                        else:
                            iraf.imcopy('_temp0.fits','_temp.fits',verbose='yes')
                            iraf.imcopy(imgtar,'_tar.fits',verbose='yes')
                                        
                        imgtemp0 = imgtemp
                        imgtemp = '_temp.fits'
                        imgtar0 = imgtar
                        imgtar = '_tar.fits'
                        
                        if _show:
                                iraf.display(imgtemp0,frame=4,fill='yes')
                                iraf.display(imgtemp,frame=3,fill='yes')
                                iraf.display(imgtar0,frame=2,fill='yes')
                                iraf.display(imgtar,frame=1,fill='yes')
###########################################################
                        _dir = agnkey.util.workingdirectory+'1mtel/'+agnkey.util.readkey3(hdtar,'date-night')+'/'
                        if not os.path.isfile(_dir+imgout) or _force: 
                            artar = where(artar>saturation,2,0)
                            out_fits = pyfits.PrimaryHDU(header=hdtar,data=artar)
                            out_fits.writeto(tarmask, clobber=True, output_verify='fix')
                            hdtemp = pyfits.getheader(imgtemp)
                            artemp = pyfits.getdata(imgtemp)
                            artemp = where(artemp>saturation,2,0)
                            out_fits = pyfits.PrimaryHDU(header=hdtemp,data=artemp)
                            out_fits.writeto(tempmask, clobber=True, output_verify='fix')
                            hdr0 = agnkey.util.readhdr(imgtar)
                            hdr1 = agnkey.util.readhdr(imgtemp)
                            _gain_tar = agnkey.util.readkey3(hdr0,'gain')
                            _ron_tar = agnkey.util.readkey3(hdr0,'ron')
                            _gain_temp = agnkey.util.readkey3(hdr1,'gain')
                            _ron_temp = agnkey.util.readkey3(hdr1,'ron')
                            
                            
                            max_fwhm = agnkey.util.readkey3(hdr0,'L1FWHM')  # to be check
                            _tel = agnkey.util.readkey3(hdr1,'TELID')
                            satnew = float(saturation)
                            satref = float(saturation)
                            # hotpants parameters
                            iuthresh  = satnew           # upper valid data count, image
                            iucthresh = satnew*0.9       # upper valid data count for kernel, image 
                            tuthresh  = satref           # upper valid data count, template 
                            tucthresh = satref*0.9       # upper valid data count for kernel, template 
                            rkernel = 1.5*max_fwhm     # convolution kernel half width 
                            rkernel = max(7,rkernel)   # minimum
                            rkernel = min(15,rkernel)  # maximum
                            radius =  2.0*max_fwhm     # HW substamp to extract around each centroid 
                            radius = max(10,radius)    # minimum
                            radius = min(20,radius)    # maximum
                            sconv = '-sconv'          # all regions convolved in same direction (0)
                            normalize = _normalize       #normalize to (t)emplate, (i)mage, or (u)nconvolved (t)
                            
                            _afssc = ''
                            if afssc:
                                 substamplist,xpix1,ypix1,xpix2,ypix2=crossmatchtwofiles(imgtar,imgtemp)
                                 _afssc = ' -cmp '+str(substamplist)+' -afssc 1 '
                            line = agnkey.util.execdirectory+"hotpants -inim "+\
                                   str(imgtar)+" -tmplim "+str(imgtemp)+\
                                   " -imi "+str(tarmask)+\
                                   ' -outim '+str(imgout)+\
                                   ' -nrx '+nrxy.split(',')[0]+' -nry '+nrxy.split(',')[1]+\
                                   ' -nsx '+nsxy.split(',')[0]+' -nsy '+nsxy.split(',')[1]+\
                                   ' -r '+str(rkernel)+' -rss '+str(radius)+\
                                   ' -iu '+str(iuthresh)+' -iuk '+str(iucthresh)+\
                                   ' -tu '+str(tuthresh)+' -tuk '+str(tucthresh)+\
                                   ' -ko '+ko+' -bgo '+bgo+\
                                   ' '+sconv+' -n '+normalize+_afssc+\
                                   ' -savexy '+re.sub('.fits','xy',imgout)+' -oci '+re.sub('.fits','.conv.fits',imgout)
                            print line
                            os.system(line)
                            hd = pyfits.getheader(imgout)
                            agnkey.util.updateheader(imgout,0,{'template':[string.split(imgtemp0,'/')[-1],'template image']})
                            agnkey.util.updateheader(imgout,0,{'target':[string.split(imgtar0,'/')[-1],'target image']})
                            if hd['CONVOL00']=='TEMPLATE':
                                agnkey.util.updateheader(imgout,0,{'PSF':[string.split(imgtar0,'/')[-1],
                                                                          'image to compute  psf']})
                            else:
                                agnkey.util.updateheader(imgout,0,{'PSF':[string.split(imgtemp0,'/')[-1],
                                                                          'image to compute  psf']})

                            if _show:
                                #iraf.display(imgtar,frame=1,fill='yes')
                                #iraf.display(imgtemp,frame=2,fill='yes')
                                iraf.display(imgout,frame=3,fill='yes')
#                            raw_input('stop here')

                                         #                    copy all information from target 
                            dictionary={}
                            try:
                                ggg0=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'dataredulco',
                                                                     'namefile',string.split(imgtar0,'/')[-1], '*')
                                for voce in ggg0[0].keys(): 
                                    if voce not in ['id']:
                                        dictionary[voce]=ggg0[0][voce]
                            except:
                                dictionary={'dateobs':agnkey.util.readkey3(hd,'date-obs'),
                                            'exptime':agnkey.util.readkey3(hd,'exptime'),
                                            'filter':agnkey.util.readkey3(hd,'filter'),
                                            'telescope':agnkey.util.readkey3(hd,'telescop'),
                                            'airmass':agnkey.util.readkey3(hd,'airmass'),
                                            'objname':agnkey.util.readkey3(hd,'object'),
                                            'wcs':agnkey.util.readkey3(hd,'wcserr'),
                                            'ut':agnkey.util.readkey3(hd,'ut'),
                                            'jd':agnkey.util.readkey3(hd,'JD'),
                                            'instrument':agnkey.util.readkey3(hd,'instrume'),
                                            'ra0':agnkey.util.readkey3(hd,'RA'),'dec0':agnkey.util.readkey3(hd,'DEC')}

                            dictionary['mag'] = 9999
                            dictionary['psfmag'] = 9999
                            dictionary['apmag'] = 9999
                            dictionary['namefile'] = string.split(imgout,'/')[-1]
                            dictionary['wdirectory'] = agnkey.util.workingdirectory+'1mtel/'+\
                                                       agnkey.util.readkey3(hd,'date-night')+'/'
                            dictionary['filetype']=3
                            if not os.path.isdir(dictionary['wdirectory']): 
                                print dictionary['wdirectory']
                                os.mkdir(dictionary['wdirectory'])
                            if not os.path.isfile(dictionary['wdirectory']+imgout) or _force in ['yes',True]: 
                                print 'mv '+imgout+' '+dictionary['wdirectory']+imgout
                                os.system('mv '+imgout+' '+dictionary['wdirectory']+imgout)
                                os.system('mv '+imgtemp+' '+dictionary['wdirectory']+re.sub('.diff.','.ref.',imgout))
                                
###########################################################################################################
#                           choose sn2 file depending on 
#                           normalization parameter 
#                           
########################################################################################################## 
                            if normalize == 'i':
                                print 'scale to target'
                                imgscale = imgtar0
                                pathscale = os.path.split(imgtar0)[0]+'/'
                            elif normalize == 't':
                                print 'scale to reference'
                                imgscale = imgtemp0
                                pathscale = os.path.split(imgtemp0)[0]+'/'
                                
                                
                            if os.path.isfile(pathscale+re.sub('.fits','.sn2.fits',string.split(imgscale,'/')[-1])):
                                os.system('cp '+pathscale+re.sub('.fits','.sn2.fits',string.split(imgscale,'/')[-1])+
                                          ' '+dictionary['wdirectory']+re.sub('.fits','.sn2.fits',imgout))
                                agnkey.util.updateheader(dictionary['wdirectory']+re.sub('.fits','.sn2.fits',imgout),
                                                          0,{'mag':[9999.,'apparent'], 'psfmag':[9999.,'inst mag'],
                                                             'apmag':[9999.,'aperture mag']})
                                                            
                                if 'ZPN' in hdtempsn:
                                      agnkey.util.updateheader(dictionary['wdirectory']+\
                                            re.sub('.fits','.sn2.fits',imgout),0,{'ZPNref':[hdtempsn['ZPN'],
                                                                                            'ZPN reference image']})
                                            
                                if 'apflux1' in hdtempsn:
                                    agnkey.util.updateheader(dictionary['wdirectory']+\
                                            re.sub('.fits','.sn2.fits',imgout),0,{
                                            'apfl1re':[hdtempsn['apflux1'],'flux reference image'],
                                            'dapfl1re':[hdtempsn['dapflux1'],'error flux reference image']})
                            else: print 'fits table not found '+str(dictionary['wdirectory']+\
                            		re.sub('.fits','.sn2.fits',string.split(imgscale,'/')[-1]))
                           
                            
                            ###################    insert in dataredulco
                            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'dataredulco',
                                                                'namefile',string.split(imgout,'/')[-1], '*')
                            if ggg and _force:   agnkey.agnsqldef.deleteredufromarchive(string.split(imgout,'/')[-1],
                                                                                        'dataredulco','namefile')
                            if not ggg or _force:
                                print 'insert'
                                print dictionary
                                agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'dataredulco',dictionary)
                            else:
                                for voce in ggg[0].keys():
                                    if voce not in ['id']: 
                                        agnkey.agnsqldef.updatevalue('dataredulco',voce,
                                                                     dictionary[voce],string.split(imgout,'/')[-1])
                            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'inoutredu',
                                                                'nameout',string.split(imgout,'/')[-1], '*')
                            if ggg:
                                agnkey.agnsqldef.deleteredufromarchive(string.split(imgout,'/')[-1],
                                                                       'inoutredu','nameout')
                            dictionary = {'namein':string.split(imgtar0,'/')[-1],'nameout':string.split(imgout,'/')[-1],
                                        'nametemp':string.split(imgtemp0,'/')[-1],'tablein':'dataredulco',
                                        'tableout':'dataredulco','tabletemp':'dataredulco'}
                            print 'insert in out'
                            print dictionary
                            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'inoutredu',dictionary)
                        else:
                            print 'file '+imgout + '  already there '
