#!/Users/svalenti/usr/Ureka/variants/common/bin/python
description=">> make different image using hotpants"
usage = "%prog imagein  imagetem [options] "
import os,string,re,sys,glob
#from numpy import array, median, argmin, sqrt, round, isnan, compress, std
import agnkey
import time
import pyfits
from optparse import OptionParser,OptionGroup

def crossmatchtwofiles(img1,img2):
    import agnkey
    from numpy import array, argmin, min, sqrt
    xpix1,ypix1,fw1,cl1,cm1,ell1,bkg1=agnkey.agnastrodef.sextractor(img1)
    xpix2,ypix2,fw2,cl2,cm2,ell2,bkg2=agnkey.agnastrodef.sextractor(img2)

    xpix1,ypix1,xpix2,ypix2=array(xpix1,float),array(ypix1,float),array(xpix2,float),array(ypix2,float)    
    distvec=[]
    pos1=[]
    pos2=[]
    f=open('substamplist','w')
    for jj in range(0,len(xpix1)):
            dist = sqrt((xpix2-xpix1[jj])**2+(ypix2-ypix1[jj])**2)
            if min(dist)<=3.:
                f.write('%10.10s\t%10.10s\n' % (str(xpix1[jj]),str(ypix1[jj])))
    f.close()
    return 'substamplist'

###################################################
if __name__ == "__main__":
     parser = OptionParser(usage=usage,description=description)
     parser.add_option("-c", "--check",dest="check",action="store_true",\
            default=False, help=' check images registration \t\t\t [%default]')
     parser.add_option("-f", "--force",dest="force",action="store_true",\
            default=False, help=' force archiving \t\t\t [%default]')
     parser.add_option("--show",dest="show",action="store_true",\
            default=False, help=' show result  \t\t\t [%default]')
     hotpants = OptionGroup(parser, "hotpants parameters")
     hotpants.add_option("--nrxy",dest="nrxy",default='1,1',\
                             help='Number of image region in x y directions \t [%default]')
     hotpants.add_option("--nsxy",dest="nsxy",default='8,8',
                         help="Number of region's stamps in x y directions\t [%default]")
     hotpants.add_option("--ko",dest="ko",default='1',
                         help='spatial order of kernel variation within region\t [%default]') 
     hotpants.add_option("--bgo",dest="bgo",default='1',
                         help='spatial order of background variation within region \t [%default]')
     hotpants.add_option("--afssc",dest="afssc",default=False,\
                             action="store_true",help='use selected stamps \t\t\t [%default]')
     parser.add_option_group(hotpants)

     option,args = parser.parse_args()    
     if len(args)<2 : sys.argv.append('--help')
     option,args = parser.parse_args()
     imglisttar = agnkey.util.readlist(args[0])
     imglisttemp = agnkey.util.readlist(args[1])
     from numpy import where,mean

     _checkast=option.check
     _force=option.force
     _show=option.show
     saturation=40000
     nrxy=option.nrxy
     nsxy=option.nsxy
     ko=option.ko
     bgo=option.bgo
     afssc=option.afssc

     listatar={}
     for img in imglisttar:
         hdr=agnkey.util.readhdr(img)
         _filter=agnkey.util.readkey3(hdr,'filter')
         _obj=agnkey.util.readkey3(hdr,'object')
         if _filter not in listatar: listatar[_filter]={}
         if _obj not in listatar[_filter]: listatar[_filter][_obj]=[]
         listatar[_filter][_obj].append(img)

     listatemp={}
     for img in imglisttemp:
         hdr=agnkey.util.readhdr(img)
         _filter=agnkey.util.readkey3(hdr,'filter')
         _obj=agnkey.util.readkey3(hdr,'object')
         if _filter not in listatemp: listatemp[_filter]={}
         if _obj not in listatemp[_filter]: listatemp[_filter][_obj]=[]
         listatemp[_filter][_obj].append(img)

     for f in listatar:
         for o in listatar[f]:
             if f in listatemp:
                 if o in listatemp[f]:
                     imglist1=listatar[f][o]
                     imglist2=listatemp[f][o]
                     for imgtar in imglist1:
                        imgtemp=imglist2[0]
                        tarmask=re.sub('.fits','.mask.fits',string.split(imgtar,'/')[-1])
                        tempmask=re.sub('.fits','.mask.fits',string.split(imgtemp,'/')[-1])
                        imgout=re.sub('.fits','.diff.fits',string.split(imgtar,'/')[-1])
                        outmask=re.sub('.fits','.mask.fits',string.split(imgout,'/')[-1])
                        hdtar = pyfits.getheader(imgtar)
                        artar = pyfits.getdata(imgtar)
                        #_dir='/science/supernova/data/lsc/'+agnkey.util.readkey3(hdtar,'date-night')+'/'
                        _dir=agnkey.util.workingdirectory+'lsc/'+agnkey.util.readkey3(hdtar,'date-night')+'/'
                        if not os.path.isfile(_dir+imgout) or _force: 
                            artar = where(artar>saturation,2,0)
                            out_fits = pyfits.PrimaryHDU(header=hdtar,data=artar)
                            out_fits.writeto(tarmask, clobber=True, output_verify='fix')
                            hdtemp = pyfits.getheader(imgtemp)
                            artemp = pyfits.getdata(imgtemp)
                            artemp = where(artemp>saturation,2,0)
                            out_fits = pyfits.PrimaryHDU(header=hdtemp,data=artemp)
                            out_fits.writeto(tempmask, clobber=True, output_verify='fix')
                            hdr0=agnkey.util.readhdr(imgtar)
                            hdr1=agnkey.util.readhdr(imgtemp)
                            _gain_tar=agnkey.util.readkey3(hdr0,'gain')
                            _ron_tar=agnkey.util.readkey3(hdr0,'ron')
                            _gain_temp=agnkey.util.readkey3(hdr1,'gain')
                            _ron_temp=agnkey.util.readkey3(hdr1,'ron')
                            max_fwhm=agnkey.util.readkey3(hdr0,'L1FWHM')  # to be check
                            _tel=agnkey.util.readkey3(hdr1,'TELID')
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
                            normalize = 'i'     #normalize to (t)emplate, (i)mage, or (u)nconvolved (t)
                            _afssc = ''
                            if afssc:
                                 substamplist=crossmatchtwofiles(imgtar,imgtemp)
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
                            agnkey.util.updateheader(imgout,0,{'template':[string.split(imgtemp,'/')[-1],'template image']})
                            agnkey.util.updateheader(imgout,0,{'target':[string.split(imgtar,'/')[-1],'target image']})
                            if hd['CONVOL00']=='TEMPLATE':   agnkey.util.updateheader(imgout,0,{'PSF':[string.split(imgtar,'/')[-1],'image to compute  psf']})
                            else:                            agnkey.util.updateheader(imgout,0,{'PSF':[string.split(imgtemp,'/')[-1],'image to compute  psf']})
                         

                                         #                    copy all information from target 
                            dictionary={}
                            try:
                                ggg0=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'dataredulco', 'namefile',string.split(imgtar,'/')[-1], '*')
                                for voce in ggg0[0].keys(): 
                                    if voce not in ['id']:       dictionary[voce]=ggg0[0][voce] 
                            except:
                                dictionary={'dateobs':agnkey.util.readkey3(hd,'date-obs'),'exptime':agnkey.util.readkey3(hd,'exptime'), 'filter':agnkey.util.readkey3(hd,'filter'),\
                                             'telescope':agnkey.util.readkey3(hd,'telescop'),'airmass':agnkey.util.readkey3(hd,'airmass'),'objname':agnkey.util.readkey3(hd,'object'),\
                                             'wcs':agnkey.util.readkey3(hd,'wcserr'),'ut':agnkey.util.readkey3(hd,'ut'),'jd':agnkey.util.readkey3(hd,'JD'),\
                                             'instrument':agnkey.util.readkey3(hd,'instrume'),'ra0':agnkey.util.readkey3(hd,'RA'),'dec0':agnkey.util.readkey3(hd,'DEC')}

                            dictionary['mag']=9999
                            dictionary['psfmag']=9999
                            dictionary['apmag']=9999
                            dictionary['namefile']=string.split(imgout,'/')[-1]
                            if _tel in ['fts','ftn']:
                                _telescope='fts'
                            else:
                                _telescope='lsc'
                            dictionary['wdirectory']=agnkey.util.workingdirectory+str(_telescope)+'/'+agnkey.util.readkey3(hd,'date-night')+'/'
                            dictionary['filetype']=3
                            if not os.path.isdir(dictionary['wdirectory']): 
                                print dictionary['wdirectory']
                                os.mkdir(dictionary['wdirectory'])
                            if not os.path.isfile(dictionary['wdirectory']+imgout) or _force=='yes': 
                                print 'mv '+imgout+' '+dictionary['wdirectory']+imgout
                                os.system('mv '+imgout+' '+dictionary['wdirectory']+imgout)
                            if os.path.isfile(dictionary['wdirectory']+re.sub('.fits','.sn2.fits',string.split(imgtar,'/')[-1])):
                                os.system('cp '+dictionary['wdirectory']+re.sub('.fits','.sn2.fits',string.split(imgtar,'/')[-1])+' '+dictionary['wdirectory']+re.sub('.fits','.sn2.fits',imgout))
                                agnkey.util.updateheader(dictionary['wdirectory']+re.sub('.fits','.sn2.fits',imgout),0,{'mag':[9999.,'apparent'],'psfmag':[9999.,'inst mag'],\
                                                                                                                     'apmag':[9999.,'aperture mag']})
                            else: print 'fits table not found '+str(dictionary['wdirectory']+re.sub('.fits','.sn2.fits',string.split(imgtar,'/')[-1]))
                            ###################    insert in dataredulco
                            ggg=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'dataredulco', 'namefile',string.split(imgout,'/')[-1], '*')
                            if ggg and _force:   agnkey.agnsqldef.deleteredufromarchive(string.split(imgout,'/')[-1],'dataredulco','namefile')
                            if not ggg or _force:
                                print 'insert'
                                print dictionary
                                agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'dataredulco',dictionary)
                            else:
                                for voce in ggg[0].keys():
                                    if voce not in ['id']: 
                                        agnkey.agnsqldef.updatevalue('dataredulco',voce,dictionary[voce],string.split(imgout,'/')[-1])
                            ggg=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'inoutredu', 'nameout',string.split(imgout,'/')[-1], '*')
                            if ggg:   agnkey.agnsqldef.deleteredufromarchive(string.split(imgout,'/')[-1],'inoutredu','nameout')
                            dictionary={'namein':string.split(imgtar,'/')[-1],'nameout':string.split(imgout,'/')[-1],'nametemp':string.split(imgtemp,'/')[-1],\
                                        'tablein':'dataredulco','tableout':'dataredulco','tabletemp':'dataredulco'}
                            print 'insert in out'
                            print dictionary
                            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'inoutredu',dictionary)
                        else:
                            print 'file '+imgout+'  already there '
