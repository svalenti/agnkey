#!/System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

description=">> clean and combine frames using cosmic and swarp "
usage = "%prog list_image [options] "
import os,string,re,sys,glob

import agnkey
import time
import pyfits
from optparse import OptionParser


def checkast(imglist):
    import agnkey
    import pywcs
    from numpy import median,array,compress,abs,std,argmin,isnan,sqrt
    hdr0=agnkey.util.readhdr(imglist[0])
    #######  check with sources the accuracy of the astrometry
    wcs = pywcs.WCS(hdr0)
    xpix,ypix,fw,cl,cm,ell,bkg=agnkey.agnastrodef.sextractor(imglist1[0])
    pixref=array(zip(xpix,ypix),float)
    sky0 = wcs.wcs_pix2sky(pixref, 1)
    max_sep=10
    for img in imglist1:
        xsex,ysex,fw,cl,cm,ell,bkg=agnkey.agnastrodef.sextractor(img)   # sextractor 
        hdr1=agnkey.util.readhdr(img)
        wcs1 = pywcs.WCS(hdr1)
        pix1 = wcs1.wcs_sky2pix(sky0, 1)       
        xpix1, ypix1 = zip(*pix1)                # pixel position of the obj in image 0
        xdist,ydist=[],[]
        for i in range(len(xpix1)):
            dist = sqrt((xpix1[i]-xsex)**2+(ypix1[i]-ysex)**2)
            idist = argmin(dist)
            if dist[idist]<max_sep:
                xdist.append(xpix1[i]-xsex[idist])
                ydist.append(ypix1[i]-ysex[idist])
        xoff,xstd = round(median(xdist),2),round(std(xdist),2)
        yoff,ystd = round(median(ydist),2),round(std(ydist),2)
        _xdist,_ydist = array(xdist),array(ydist)
        __xdist = compress((abs(_xdist-xoff)<3*xstd)&(abs(_ydist-yoff)<3*ystd),_xdist)
        __ydist = compress((abs(_xdist-xoff)<3*xstd)&(abs(_ydist-yoff)<3*ystd),_ydist)
        xoff,xstd = round(median(__xdist),2),round(std(__xdist),2)
        yoff,ystd = round(median(__ydist),2),round(std(__ydist),2)
        if isnan(xoff): xoff,xstd=0,0
        if isnan(yoff): yoff,ystd=0,0
        print xoff,xstd ,len(__xdist)
        print yoff,ystd
        #if abs(xoff)>=1:        
        agnkey.updateheader(img,0,{'CRPIX1':[hdr1['CRPIX1']-xoff,'Value at ref. pixel on axis 1']})
        #if abs(yoff)>=1:        
        agnkey.updateheader(img,0,{'CRPIX2':[hdr1['CRPIX2']-yoff,'Value at ref. pixel on axis 2']})
#############################################################


###################################################
if __name__ == "__main__":
     parser = OptionParser(usage=usage,description=description)
     parser.add_option("-c", "--check",dest="check",action="store_true",\
            default=False, help=' check images registration \t\t\t [%default]')
     parser.add_option("-f", "--force",dest="force",action="store_true",\
            default=False, help=' force archiving \t\t\t [%default]')
     option,args = parser.parse_args()    
     if len(args)<1 : sys.argv.append('--help')
     option,args = parser.parse_args()
     imglist = agnkey.util.readlist(args[0])
     from numpy import where,mean

     _checkast=option.check
     force=option.force
     saturation=40000

     lista={}
     for img in imglist:
         hdr=agnkey.util.readhdr(img)
         _filter=agnkey.util.readkey3(hdr,'filter')
         _obj=agnkey.util.readkey3(hdr,'object')
         if _filter not in lista: lista[_filter]={}
         if _obj not in lista[_filter]: lista[_filter][_obj]=[]
         lista[_filter][_obj].append(img)
     for f in lista:
        for o in lista[f]:
             imglist1=lista[f][o]
             hdr0=agnkey.util.readhdr(imglist1[0])
             _tel=agnkey.util.readkey3(hdr0,'TELID')
             _gain=agnkey.util.readkey3(hdr0,'gain')
             _ron=agnkey.util.readkey3(hdr0,'ron')
             _instrume= agnkey.util.readkey3(hdr0,'instrume')

             _ra,_dec,_SN0=agnkey.util.checksnlist(img,'supernovaelist.txt')
             _tt=''
             if not _ra and not _dec:  _ra,_dec,_SN0,_tt=agnkey.util.checksndb(img,'lsc_sn_pos')
             if _tt=='STD':
                 _ra=''
                 _dec=''

             if not _ra and not _dec:
                 _ra=agnkey.util.readkey3(hdr0,'RA')
                 _dec=agnkey.util.readkey3(hdr0,'DEC')
                 
             if _instrume in ['em03','em01']:   _imagesize=1050
             else:                              _imagesize=2100

             if 'PIXSCALE' in hdr0: pixelscale= hdr0['PIXSCALE']
             elif 'CCDSCALE' in hdr0: pixelscale= hdr0['CCDSCALE']
             else:
                 print 'Warning: pixel scale not defined'
                 pixelscale=''

             if _tel in ['fts','ftn']:
                 outname=hdr0['SITEID']+re.sub('-','',hdr0['TELID'])+'_'+\
                     hdr0['instrume']+'_'+re.sub('-','',string.split(hdr0['DATE-OBS'],'T')[0])+'_'+o+'_'+f+'.fits'
             else:
                 outname=hdr0['SITEID']+re.sub('-','',hdr0['telescop'])+'_'+\
                     hdr0['instrume']+'_'+hdr0['DAY-OBS']+'_'+o+'_'+f+'.fits'
             print outname

             imglist2=''
             imglistnoise=''
             imgmask=''
             imglist22=[]
             for gg in imglist1:  
                 kkk=agnkey.agnastrodef.finewcs(gg)
                 print gg
                 output,mask,satu=agnkey.util.Docosmic(gg)                            #  cosmic correction on a fly ....not really fly
                 hdm = pyfits.getheader(output)
                 dmask = pyfits.getdata(mask)
                 dsat = pyfits.getdata(satu)
                 #ar1=where(arm>saturation,2,0)
                 out_fits = pyfits.PrimaryHDU(header=hdm,data=dsat+dmask)
                 out_fits.writeto(re.sub('.fits','.mask.fits',string.split(gg,'/')[-1]), clobber=True, output_verify='fix')
                 imglist2=imglist2+','+output
                 imgmask=imgmask+','+re.sub('.fits','.mask.fits',string.split(gg,'/')[-1])
                 imglistnoise=imglistnoise+','+re.sub('.fits','.noise.fits',string.split(gg,'/')[-1])
                 imglist22.append(output)
                                                                 #  check registration among images
             if _checkast:    checkast(imglist22)

             line='swarp '+imglist2[1:]+' -IMAGEOUT_NAME '+str(outname)+' -WEIGHTOUT_NAME '+re.sub('.fits','',outname)+'.weight.fits -RESAMPLE_DIR '+\
                 './ -RESAMPLE_SUFFIX .swarptemp.fits -COMBINE Y -RESAMPLING_TYPE LANCZOS3 -VERBOSE_TYPE NORMAL -SUBTRACT_BACK Y  -INTERPOLATE Y '+\
                 '-PIXELSCALE_TYPE MANUAL,MANUAL -COMBINE_TYPE MEDIAN -PIXEL_SCALE '+str(pixelscale)+','+str(pixelscale)+\
                 ' -IMAGE_SIZE '+str(_imagesize)+','+str(_imagesize)+' -CENTER_TYPE MANUAL,MANUAL -CENTER '+str(_ra)+','+str(_dec)+' -RDNOISE_DEFAULT '+\
                 str(_ron)+' -GAIN_KEYWORD NONONO '+'-GAIN_DEFAULT '+str(_gain)+' -WEIGHT_TYPE MAP_WEIGHT -WEIGHT_THRESH 0.5 -WEIGHT_IMAGE '+str(imgmask[1:])
 #            if _tel in ['fts','ftn']:                 line=line+' -IMOUT_BITPIX 16 -IMOUT_BSCALE 1.0 -IMOUT_BZERO 32768.0'

             line2='swarp '+imglist2[1:]+' -IMAGEOUT_NAME  '+re.sub('.fits','',outname)+'.noise.fits'+\
                 ' -WEIGHTOUT_NAME '+re.sub('.fits','',outname)+'.mask.fits'+' -SM_MKNOISE Y -BPMAXWEIGHTFRAC 0.2 '+\
                 '-BPADDFRAC2NOISE 0.1 -RESAMPLE_DIR ./ -RESAMPLE_SUFFIX .swarptemp.fits -COMBINE Y -RESAMPLING_TYPE LANCZOS3 -VERBOSE_TYPE NORMAL '+\
                 '-SUBTRACT_BACK N  -INTERPOLATE Y -PIXELSCALE_TYPE MANUAL,MANUAL -PIXEL_SCALE '+str(pixelscale)+','+str(pixelscale)+\
                 ' -IMAGE_SIZE '+str(_imagesize)+','+str(_imagesize)+' -CENTER_TYPE MANUAL,MANUAL -CENTER '+str(_ra)+','+str(_dec)+' -WEIGHT_TYPE MAP_WEIGHT -WEIGHT_THRESH 0.5 '+\
                 '-WEIGHT_IMAGE '+str(imgmask[1:])+' -RDNOISE_DEFAULT '+str(_ron)+' -GAIN_KEYWORD NONONO -GAIN_DEFAULT '+str(_gain)
#             if _tel in ['fts','ftn']:                 line2=line2+' -IMOUT_BITPIX 16 -IMOUT_BSCALE 1.0 -IMOUT_BZERO 32768.0'

             print line
             print line2
             os.system(line)

             hd = pyfits.getheader(outname)
             ar = pyfits.getdata(outname)
             ar=where(ar<=0,mean(ar[where(ar>0)]),ar)
             keyw=['OBJECT', 'DATE', 'ORIGIN', 'EXPTIME', 'HDUCLAS1', 'HDUCLAS2', 'HDSTYPE', 'DATADICV', 'HDRVER', 'SITEID', 'SITE','MJD-OBS', 'MJD',\
                   'ENCID', 'ENCLOSUR', 'TELID', 'TELESCOP', 'LATITUDE', 'LONGITUD', 'HEIGHT', 'OBSGEO-X', 'OBSGEO-Y', 'OBSGEO-Z',\
                   'OBSTYPE', 'FRAMENUM', 'MOLTYPE', 'MOLNUM', 'MOLFRNUM', 'FRMTOTAL', 'ORIGNAME', 'OBSTELEM', 'TIMESYS', 'DATE-OBS',\
                   'DAY-OBS', 'UTSTART', 'UTSTOP', 'FILTER1', 'FILTERI1', 'FILTER2', 'FILTERI2', 'FILTER3', 'FILTERI3', 'FILTER', 'FWID',\
                   'INSTRUME', 'INSSTATE', 'ICSVER', 'CONFMODE', 'CONFNAME', 'DETECTOR', 'DETECTID', 'RDNOISE', 'DARKCURR', 'MAXLIN',\
                   'RDSPEED', 'DETSIZE', 'AMPNAME', 'CCDSEC', 'CCDSUM', 'BIASSEC', 'DATASEC', 'TRIMSEC', 'ROI', 'DETSEC', 'CCDXPIXE','CCDXBIN','CCDYBIN','CCDSCALE',\
                   'CCDYPIXE', 'PIXSCALE', 'CCDSTEMP', 'CCDATEMP', 'CCDSESIG', 'TELMODE', 'TAGID', 'USERID', 'PROPID', 'GROUPID', 'OBSID',\
                   'OBSNOTE', 'SCHEDNAM', 'TRACKNUM', 'REQNUM', 'MOLUID', 'BLKTYPE', 'BLKUID', 'BLKSDATE', 'BLKEDATE', 'BLKNOMEX', 'BLKMNPH',\
                   'BLKMNDST', 'BLKSEECO', 'BLKTRNCO', 'BLKAIRCO', 'SCHEDSEE', 'SCHEDTRN', 'TRIGGER', 'OBRECIPE', 'PCRECIPE', 'PPRECIPE', 'RA',\
                   'DEC', 'LST', 'CAT-RA', 'CAT-DEC', 'CAT-EPOC', 'OFST-RA', 'OFST-DEC', 'TPT-RA', 'TPT-DEC', 'SRCTYPE', 'PM-RA', 'PM-DEC',\
                   'PARALLAX', 'RADVEL', 'RATRACK', 'DECTRACK', 'TELSTATE', 'ENGSTATE', 'TCSSTATE', 'TCSVER', 'TPNTMODL', 'UT1-UTC', 'POLARMOX',\
                   'POLARMOY', 'EOPSRC', 'ROLLERDR', 'ROLLERND', 'AZDMD', 'AZIMUTH', 'AZSTAT', 'ALTDMD', 'ALTITUDE', 'ALTSTAT', 'AIRMASS',\
                   'AMSTART', 'AMEND', 'ENC1STAT', 'ENC2STAT', 'ENCAZ', 'ENCWLIGT', 'ENCRLIGT', 'FOLDSTAT', 'FOLDPORT', 'FOLDPOSN', 'M1COVER',\
                   'M1HRTMN', 'FOCDMD', 'FOCPOSN', 'FOCTELZP', 'FOCINOFF', 'FOCTOFF', 'FOCZOFF', 'FOCAFOFF', 'FOCOBOFF', 'FOCFLOFF', 'FOCSTAT',\
                   'M2PITCH', 'M2ROLL', 'QV1_0', 'QV1_1', 'QV1_7', 'QV1_9', 'QV1_17', 'QV1_21', 'QV1_31', 'QV1_37', 'QV2_0', 'QV2_1', 'QV2_7',\
                   'QV2_9', 'QV2_17', 'QV2_21', 'QV2_31', 'QV2_37', 'WMSSTATE', 'WMSHUMID', 'WMSTEMP', 'WMSPRES', 'WINDSPEE', 'WINDDIR',\
                   'WMSRAIN', 'WMSMOIST', 'WMSDEWPT', 'WMSCLOUD', 'WMSSKYBR', 'SKYMAG', 'TUBETEMP', 'M1TEMP', 'FOCTEMP', 'ISSTEMP', 'REFPRES',\
                   'REFTEMP', 'REFHUMID', 'AGSTATE', 'AGCAM', 'AGLCKFRC', 'AGMODE', 'AGRA', 'AGDEC', 'AGGMAG', 'AGFWHM', 'AGMIRDMD', 'AGMIRPOS',\
                   'AGMIRST', 'AGFOCDMD', 'AGFOCUS', 'AGFOCOFF', 'AGFOCST', 'AGFILTER', 'AGFILTID', 'AGFILST', 'MOONSTAT', 'MOONFRAC', 'MOONDIST',\
                   'MOONALT', 'SUNDIST', 'SUNALT', 'SECPIX', 'WCSSOLVR', 'WCSRFCAT', 'WCSIMCAT', 'WCSNREF', 'WCSMATCH', 'WCCATTYP', 'WCNTERMS',\
                   'WCSRDRES', 'WCSDELRA', 'WCSDELDE', 'WCSERR', 'WCS_ERR', 'PIPEVER', 'L1STATOV', 'L1STATBI', 'L1STATDA', 'L1STATTR', 'L1STATFL', 'L1STATFR',\
                   'L1IDBIAS', 'L1IDDARK', 'L1IDFLAT', 'L1IDSHUT', 'L1IDMASK', 'L1IDFRNG', 'L1MEAN', 'L1MEDIAN', 'L1SIGMA', 'L1SKYBRT', 'L1PHOTOM',\
                   'L1ZP', 'L1ZPERR', 'L1ZPSRC', 'L1FWHM', 'L1ELLIP', 'L1ELLIPA', 'L1QCVER', 'L1QOBCON', 'L1QIMGST', 'L1QCATST', 'L1QPHTST',\
                   'L1PUBPRV', 'L1PUBDAT','L1SEEING']
             for jj in keyw:
                 try:
                     hd.update(jj,hdr0[jj],hdr0.comments[jj])
                 except:    pass
             out_fits = pyfits.PrimaryHDU(header=hd,data=ar)
             out_fits.writeto(outname, clobber=True, output_verify='fix')
             os.system(line2)     # make noise image

             print outname
             hd = pyfits.getheader(outname)
             _targid=agnkey.agnsqldef.targimg(outname)
             _tel=agnkey.util.readkey3(hd,'telid')
             dictionary={'dateobs':agnkey.util.readkey3(hd,'date-obs'),'exptime':agnkey.util.readkey3(hd,'exptime'), 'filter':agnkey.util.readkey3(hd,'filter'),'jd':agnkey.util.readkey3(hd,'JD'),\
                           'telescope':agnkey.util.readkey3(hd,'telescop'),'airmass':agnkey.util.readkey3(hd,'airmass'),'objname':agnkey.util.readkey3(hd,'object'),'ut':agnkey.util.readkey3(hd,'ut'),\
                           'wcs':agnkey.util.readkey3(hd,'wcserr'),'instrument':agnkey.util.readkey3(hd,'instrume'),'ra0':agnkey.util.readkey3(hd,'RA'),'dec0':agnkey.util.readkey3(hd,'DEC')}
             dictionary['namefile']=string.split(outname,'/')[-1]
             dictionary['targid']=_targid
             if _tel in ['fts','ftn']:
#                 dictionary['wdirectory']='/science/supernova/data/fts/'+agnkey.util.readkey3(hd,'date-night')+'/'
                 dictionary['wdirectory']=agnkey.util.workingdirectory+'fts/'+agnkey.util.readkey3(hd,'date-night')+'/'
             else:
                 dictionary['wdirectory']=agnkey.util.workingdirectory+'1mtel/'+agnkey.util.readkey3(hd,'date-night')+'/'
             dictionary['filetype']=2
            ###################    insert in dataredulco
             ggg=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'dataredulco', 'namefile',string.split(outname,'/')[-1], '*')
             if ggg and force:   agnkey.agnsqldef.deleteredufromarchive(string.split(outname,'/')[-1],'dataredulco','namefile')
             if not ggg or force:
                 print 'insert'
                 print dictionary
                 agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'dataredulco',dictionary)
             else:
                for voce in ggg[0].keys():
                    print 'update'
                    try:    agnkey.agnsqldef.updatevalue('dataredulco',voce,dictionary[voce],string.split(outname,'/')[-1])
                    except: pass
             if not os.path.isdir(dictionary['wdirectory']): 
                 print dictionary['wdirectory']
                 os.mkdir(dictionary['wdirectory'])
             print force
             if not os.path.isfile(dictionary['wdirectory']+outname) or force: 
                 print 'mv '+outname+' '+dictionary['wdirectory']+outname
                 os.system('mv '+outname+' '+dictionary['wdirectory']+outname)
                 os.chmod(dictionary['wdirectory']+outname,0664)

             ggg=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'inoutredu', 'nameout',string.split(outname,'/')[-1], '*')
             if ggg:   agnkey.agnsqldef.deleteredufromarchive(string.split(outname,'/')[-1],'inoutredu','nameout')
             for img in imglist1:
                 dictionary={'namein':string.split(img,'/')[-1],'nameout':string.split(outname,'/')[-1],'tablein':'dataredulco','tableout':'dataredulco'}
                 print 'insert in out'
                 print dictionary
                 agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'inoutredu',dictionary)

             for gg in imglist1:  
                 os.system('rm '+re.sub('.fits','.mask.fits',string.split(gg,'/')[-1]))
                 os.system('rm '+re.sub('.fits','.clean.fits',string.split(gg,'/')[-1]))
                 os.system('rm '+re.sub('.fits','.sat.fits',string.split(gg,'/')[-1]))
             
             if os.path.isfile(re.sub('.fits','.noise.fits',outname)): os.system('rm -rf '+re.sub('.fits','.noise.fits',outname))
             if os.path.isfile(re.sub('.fits','.mask.fits',outname)): os.system('rm -rf '+re.sub('.fits','.mask.fits',outname))
             if os.path.isfile(re.sub('.fits','.weight.fits',outname)): os.system('rm -rf '+re.sub('.fits','.weight.fits',outname))
