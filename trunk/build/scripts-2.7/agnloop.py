#!/System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
description="> process lsc data  " 
usage= "%prog  -e epoch [-s stage -n name -f filter -d idnumber]\n available stages [wcs,psf,psfmag,zcat,abscat,mag,local,getmag]\n"

import MySQLdb,os,string
import re,sys,glob,string,os
from numpy import take,argsort,asarray,array
from optparse import OptionParser
import datetime
import agnkey

#####################################################################################

if __name__ == "__main__":
     parser = OptionParser(usage=usage,description=description, version="%prog 1.0")
     parser.add_option("-e", "--epoch",dest="epoch",default='20121212',type="str",
                  help='epoch to reduce  \t [%default]')
     parser.add_option("-T", "--telescope",dest="telescope",default='all',type="str",
                  help='-T telescope fts, ftn, coj, lsc, elp, cpt, 1m0-03,1m0-04,1m0-05,1m0-08,1m0-09,1m0-10,1m0-11,1m0-12,1m0-13,1m0,kb,fl \t [%default]')
     parser.add_option("-R", "--RA",dest="ra",default='',type="str",
                  help='-R  ra    \t [%default]')
     parser.add_option("-D", "--DEC",dest="dec",default='',type="str",
                  help='-D dec   \t [%default]')
     parser.add_option("-n", "--name",dest="name",default='',type="str",
                  help='-n image name   \t [%default]')
     parser.add_option("-d", "--id",dest="id",default='',type="str",
                  help='-d identification id   \t [%default]')
     parser.add_option("-f", "--filter",dest="filter",default='',type="str",
                  help='-f filter [sloan,landolt,apass,u,g,r,i,z,U,B,V,R,I] \t [%default]')
     parser.add_option("-F", "--force",dest="force",action="store_true")
     parser.add_option("-b", "--bad",dest="bad",default='',type="str",
                  help='-b bad stage [wcs,psf,psfmag,zcat,abscat,mag,goodcat,getmag,merge,diff,template,apmag] \t [%default]')
     parser.add_option("-s", "--stage",dest="stage",default='',type="str",
                  help='-s stage [wcs,psf,psfmag,zcat,abscat,mag,getmag,merge,diff,makestamp,template,apmag] \t [%default]')
     parser.add_option("--RAS",dest="ras",default='',type="str",
                  help='-RAS  ra    \t [%default]')
     parser.add_option("--DECS",dest="decs",default='',type="str",
                  help='-DECS dec   \t [%default]')
     parser.add_option("-x","--xord",dest="xord",default=3,type=int,
                  help='-x order for bg fit   \t [%default]')
     parser.add_option("-y","--yord",dest="yord",default=3,type=int,
                  help='-y order for bg fit \t [%default]')
     parser.add_option("--bkg",dest="bkg",default=4,type=float,
                  help=' bkg radius for the fit  \t [%default]')
     parser.add_option("--size",dest="size",default=7,type=float,
                  help='size of the stamp for the fit \t [%default]')
     parser.add_option("-t", "--threshold",dest="threshold",default=5.,
                       type='float',help='Source detection threshold \t\t\t %default')
     parser.add_option("-i", "--interactive",action="store_true",\
            dest='interactive',default=False, help='Interactive \t\t\t [%default]')
     parser.add_option("--show",action="store_true",\
            dest='show',default=False, help='show psf fit \t\t\t [%default]')
     parser.add_option("-c", "--center",action="store_false",\
            dest='recenter',default=True, help='recenter \t\t\t [%default]')
     parser.add_option("--fix",action="store_false",\
            dest='fix',default=True, help='fix color \t\t\t [%default]')
     parser.add_option("--cutmag",dest="cutmag",default=99.,type="float",
                  help='--cutmag  [magnitude instrumental cut for zeropoint ]  \t [%default]')
     parser.add_option("--field",dest="field",default='',type="str",
                  help='--field  [landolt,sloan,apass]  \t [%default]')
     parser.add_option("--ref",dest="ref",default='',type="str",
                  help='--ref  sn22_20130303_0111.sn2.fits get sn position from this file \t [%default]')
     parser.add_option("--catalogue",dest="catalogue",default='',type="str",
                  help='--catalogue  sn09ip.cat    \t [%default]')
     parser.add_option("--calib",dest="calib",default='',type="str",
                  help='--calib  (sloan,natural,sloanprime)   \t [%default]')
     parser.add_option("--type",dest="type",default='fit',type="str",
                  help='--type mag for zero point   [fit,ph,mag]    \t [%default]')
     parser.add_option("--standard",dest="standard",default='',type="str",
                  help='--standard namestd  \t use the zeropoint from this standard    \t [%default]')
     parser.add_option("--xshift",dest="xshift",default=0,type="int",
                  help='x shift in the guess astrometry \t [%default]')
     parser.add_option("--fwhm",dest="fwhm",default='',type="str",
                  help='fwhm (in pixel)  \t [%default]')
     parser.add_option("--combine",dest="combine",default=1e-10,type="float",
                  help='range to combine (in days)  \t [%default]')
     parser.add_option("--datamax",dest="dmax",default=51000,type="float",
                  help='data max for saturation (counts)  \t [%default]')
     parser.add_option("--yshift",dest="yshift",default=0,type="int",
                  help='y shift in the guess astrometry \t [%default]')
     parser.add_option("--filetype",dest="filetype",default=1,type="int",
                  help='filetype  1 [single], 2 [merge], 3 differences \t [%default]')
     parser.add_option("-o","--output",dest="output",default='',type="str",
                  help='--output  write magnitude in the output file \t [%default]')
     parser.add_option("--tempdate",dest="tempdate",default='',type="str",
                  help='--tempdate  tamplate date \t [%default]')
     parser.add_option("-X", "--xwindow",action="store_true",\
            dest='xwindow',default=False, help='xwindow \t\t\t [%default]')
     parser.add_option("--z1",dest="z1",default=None,type="int",
                  help='z1 \t [%default]')
     parser.add_option("--z2",dest="z2",default=None,type="int",
                  help='z2 \t [%default]')

     option,args = parser.parse_args()
#     _instrument=option.instrument
     _telescope=option.telescope
     _type=option.type
     _stage=option.stage
     _bad=option.bad
     if _telescope not in ['all','lsc','elp','coj', 'ftn','fts','1m0-03','1m0-04','1m0-05','1m0-08','cpt','1m0','kb','fl','1m0-09','1m0-10','1m0-11','1m0-12','1m0-13']:  sys.argv.append('--help')
     if option.force==None: _redo=False
     else:                 _redo=True
     if option.recenter==False:  _recenter=True
     else:                         _recenter=False
     if _type not in ['fit','ph','mag']:  sys.argv.append('--help')
     if _stage:
          if _stage not in ['wcs','psf','psfmag','zcat','abscat','mag','local','getmag','merge','diff','template','apmag','makestamp']: sys.argv.append('--help')
     if _bad:
          if _bad not in ['wcs','psf','psfmag','zcat','abscat','mag','goodcat','quality','apmag']: sys.argv.append('--help')
     option,args = parser.parse_args()
     _id=option.id
     _filter=option.filter
     _ra=option.ra
     _dec=option.dec
     _ras=option.ras
     _output=option.output
     _decs=option.decs
     _name=option.name
     _fwhm=option.fwhm
     _xord=option.xord
     _yord=option.yord
     _bkg=option.bkg
     _size=option.size
     _standard=option.standard
     _threshold=option.threshold
     _interactive=option.interactive
     _xwindow=option.xwindow
     _show=option.show
     _fix=option.fix
     _catalogue=option.catalogue
     _calib=option.calib
     _ref=option.ref
     _field=option.field
     _cutmag=option.cutmag
     _xshift=option.xshift
     _yshift=option.yshift
     _bin=option.combine
     _dmax=option.dmax
     _filetype=option.filetype
     _tempdate=option.tempdate
     _z1=option.z1
     _z2=option.z2

     if _xwindow:
          from stsci.tools import capable
          capable.OF_GRAPHICS = False
          import matplotlib
          matplotlib.use('Agg')
          XX=' -X '
     else:  XX=''


     if _filter: 
          if _filter not in ['landolt','sloan','apass','u','g','r','i','z','U','B','V','R','I',\
                                  'SDSS-I','SDSS-G','SDSS-R','Pan-Starrs-Z','Bessell-B','Bessell-V','Bessell-R','Bessell-I',\
                                  'ug','gr','gri','griz','riz','BVR','BV','BVRI','VRI']: sys.argv.append('--help')
          else: 
               try:  _filter=agnkey.sites.filterst(_telescope)[_filter]
               except: pass

     if _filter and not _field:
          if _filter=='landolt': _field='landolt'
          elif _filter=='sloan': _field='sloan'
          elif _filter=='apass': _field='apass'
     if _field and not _filter:
          if _field=='landolt': _filter='landolt'
          elif _field=='sloan': _filter='sloan'
          elif _field=='apass': _filter='apass'

     option,args = parser.parse_args()
     epoch=option.epoch
     if '-' not in str(epoch): 
          epoch0=datetime.date(int(epoch[0:4]),int(epoch[4:6]),int(epoch[6:8]))
          listepoch=[epoch0]
     else:
          epoch1,epoch2=string.split(epoch,'-')
          start=datetime.date(int(epoch1[0:4]),int(epoch1[4:6]),int(epoch1[6:8]))
          stop=datetime.date(int(epoch2[0:4]),int(epoch2[4:6]),int(epoch2[6:8]))
          listepoch=[re.sub('-','',str(i)) for i in [start + datetime.timedelta(days=x) for x in range(0,1+(stop-start).days)]]

     if not _stage or _stage in ['local','getmag','wcs','psf','psfmag','makestamp','apmag']:
               if len(listepoch)==1:
                    lista=agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn,'dataredulco', 'dateobs', str(listepoch[0]),'','*',_telescope)
               else:
                    lista=agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn,'dataredulco', 'dateobs', str(listepoch[0]),str(listepoch[-1]),'*',_telescope)
               if lista:
                    ll0={}
                    for jj in lista[0].keys(): ll0[jj]=[]
                    for i in range(0,len(lista)):
                         for jj in lista[0].keys(): ll0[jj].append(lista[i][jj])
                    inds = argsort(ll0['jd'])  #  sort by jd
                    for i in ll0.keys():
                         ll0[i]=take(ll0[i], inds)

                    ll0['ra']=ll0['ra0'][:]
                    ll0['dec']=ll0['dec0'][:]

                    ll=agnkey.agnloopdef.filtralist(ll0,_filter,_id,_name,_ra,_dec,_bad,_filetype)
                    print '##'*50
                    print '# IMAGE                                    OBJECT           FILTER           WCS             PSF           PSFMAG    APMAG       ZCAT          MAG      ABSCAT'
                    for i in range(0,len(ll['namefile'])):
                         try:  print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s'%\
                                  (str(re.sub('.fits','',ll['namefile'][i])),str(ll['objname'][i]),str(ll['filter'][i]),str(ll['wcs'][i]),str(re.sub('.fits','',ll['psf'][i])),\
                                        str(round(ll['psfmag'][i],4)),str(ll['apmag'][i]),str(re.sub('.cat','',ll['zcat'][i])),str(round(ll['mag'][i],4)),str(re.sub('.cat','',ll['abscat'][i])))
                         except:  print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s'%\
                                  (str(ll['namefile'][i]),str(ll['objname'][i]),str(ll['filter'][i]),str(ll['wcs'][i]),str(ll['psf'][i]),\
                                        str(ll['psfmag'][i]),str(ll['apmag'][i]),str(ll['zcat'][i]),str(ll['mag'][i]),str(ll['abscat'][i]))
                    print '\n###  total number = '+str(len(ll['namefile']))
#####################################
                    if _stage=='local':                                  #     calibrate local sequence from .cat files
                         agnkey.agnloopdef.run_local(ll['namefile'],_field,_interactive)
                    elif _stage=='getmag':                                 #     get final magnitude from mysql
                         if not _field:  sys.exit('use option --field landolt or sloan')
                         else:           fields=[_field]
                         for ff in fields:
                              agnkey.agnloopdef.run_getmag(ll['namefile'],_field,_output,_interactive,_show,_bin,_type)
                    elif _stage=='psf':
                         agnkey.agnloopdef.run_psf(ll['namefile'],_threshold,_interactive,_fwhm,_show,_redo,XX)
                    elif _stage=='psfmag':
                         agnkey.agnloopdef.run_fit(ll['namefile'],_ras,_decs,_xord,_yord,_bkg,_size,_recenter,_ref,_interactive,_show,_redo,_dmax)
                    elif _stage=='wcs':
                         agnkey.agnloopdef.run_wcs(ll['namefile'],_interactive,_redo,_xshift,_yshift,_catalogue)
                    elif _stage=='makestamp':
                         agnkey.agnloopdef.makestamp(ll['namefile'],'dataredulco',_z1,_z2,_interactive,_redo,_output)
                    elif _stage=='apmag':
                         agnkey.agnloopdef.run_apmag(ll['namefile'],'dataredulco')

               else: print '\n### no data selected'
#################################################
     else:
       for epo in listepoch:
          print '\n#### '+str(epo)
          lista=agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn,'dataredulco', 'dateobs', str(epo),'','*',_telescope)
          if lista:
            ll0={}
            for jj in lista[0].keys(): ll0[jj]=[]
            for i in range(0,len(lista)):
               for jj in lista[0].keys(): ll0[jj].append(lista[i][jj])

            inds = argsort(ll0['jd'])  #  sort by jd
            for i in ll0.keys():
              ll0[i]=take(ll0[i], inds)
            ll0['ra']=ll0['ra0'][:]
            ll0['dec']=ll0['dec0'][:]
            print _filter,_id,_name,_ra,_dec
            ll=agnkey.agnloopdef.filtralist(ll0,_filter,_id,_name,_ra,_dec,_bad,_filetype)
            if len(ll['namefile'])>0:
#                 print '##'*50
#                 print '# IMAGE                                    OBJECT           FILTER           WCS             PSF           PSFMAG          ZCAT          MAG      ABSCAT'
                 for i in range(0,len(ll['namefile'])):
                      print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s'%\
                          (str(ll['namefile'][i]),str(ll['objname'][i]),str(ll['filter'][i]),str(ll['wcs'][i]),str(ll['psf'][i]),\
                                str(ll['psfmag'][i]),str(ll['zcat'][i]),str(ll['mag'][i]),str(ll['abscat'][i]))
                 print '\n###  total number = '+str(len(ll['namefile']))
#            else: print '\n### no images for epoch '+str(epo)
            if _stage and len(ll['namefile'])>0:
               print '##'*50
               print _stage
               ll3={}
               for ii in ll.keys():       ll3[ii]     = ll[ii]
               if _stage=='zcat':
                         if not _field: 
                              if _filter in ['U','B','V','R','I','landolt']:  _field='landolt'
                              elif _filter in ['u','g','r','i','z','sloan']:  _field='sloan'
                              elif _filter in ['apass']:                      _field='apass'
                              else:                                           _field='sloan'
                         if _field:
                              print ll3['namefile']
                              _color=''
                              if len(ll3['namefile'])>1:
                                   for jj in ['u','g','r','i','z','U','B','V','R','I']:
                                        if jj in list(set(ll3['filter'])): 
                                             _color=_color+agnkey.sites.filterst1(_telescope)[jj]
#                                   for jj in list(set(ll3['filter'])): _color=_color+lsc.sites.filterst1(_telescope)[jj]
                              agnkey.agnloopdef.run_zero(ll3['namefile'],_fix,_type,_field,_catalogue,_color,_interactive,_redo,_show,_cutmag,'dataredulco',_calib)
               elif _stage=='abscat':                                #    compute magnitudes for sequence stars > img.cat
                         if _standard:
                              mm=agnkey.agnloopdef.filtralist(ll0,_filter,'',_standard,'','','',_filetype)
                              if len(mm['namefile'])>0:
                                   for i in range(0,len(mm['namefile'])):
                                        print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s'%\
                                            (str(mm['namefile'][i]),str(mm['objname'][i]),str(mm['filter'][i]),str(mm['wcs'][i]),str(mm['psf'][i]),\
                                                  str(mm['psfmag'][i]),str(mm['zcat'][i]),str(mm['mag'][i]),str(mm['abscat'][i]))
                                   agnkey.agnloopdef.run_cat(ll3['namefile'],mm['namefile'],_interactive,1,_type,_fix,'dataredulco',_field)
                              else:
                                   print '\n### warning : standard not found for this night '+str(epo)
                         else: 
                              agnkey.agnloopdef.run_cat(ll3['namefile'],'',_interactive,1,_type,_fix,'dataredulco',_field)
               elif _stage=='mag':                                    #    compute final magnitude using:   mag1  mag2  Z1  Z2  C1  C2
                         if _standard:
                              mm=agnkey.agnloopdef.filtralist(ll0,_filter,'',_standard,'','','',_filetype)
                              if len(mm['namefile'])>0:
                                   for i in range(0,len(mm['namefile'])):
                                        print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s'%\
                                            (str(mm['namefile'][i]),str(mm['objname'][i]),str(mm['filter'][i]),str(mm['wcs'][i]),str(mm['psf'][i]),\
                                                  str(mm['psfmag'][i]),str(mm['zcat'][i]),str(mm['mag'][i]),str(mm['abscat'][i]))
                                   agnkey.agnloopdef.run_cat(ll3['namefile'],mm['namefile'],_interactive,2,_type,False,'dataredulco',_field)
                              else:
                                   print '\n### error: standard not found for this night'+str(epo)
                         else:
                              agnkey.agnloopdef.run_cat(ll3['namefile'],'',_interactive,2,_type,False,'dataredulco',_field)
               elif _stage=='merge':                                    #    merge images using lacos and swarp
                    listfile=[k+v for k,v in  zip(ll['wdirectory'],ll['namefile'])]
                    agnkey.agnloopdef.run_merge(array(listfile),_redo)
               elif _stage=='diff':                                    #    difference images using hotpants
                    if not _name: sys.exit('you need to select one object: use option -n/--name')
                    if _tempdate:
                         lista1=agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn,'dataredulco', 'dateobs', str(_tempdate),'','*',_telescope)
                    else:
                         lista1=agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn,'dataredulco', 'dateobs', '20120101','20150101','*',_telescope)
                    if lista1:
                         ll00={}
                         for jj in lista1[0].keys(): ll00[jj]=[]
                         for i in range(0,len(lista1)):
                              for jj in lista1[0].keys(): ll00[jj].append(lista1[i][jj])
                         inds = argsort(ll00['jd'])  #  sort by jd
                         for i in ll00.keys():   ll00[i]=take(ll00[i], inds)
                         lltemp=agnkey.agnloopdef.filtralist(ll00,_filter,_id,_name,_ra,_dec,_bad,4)
                    else:  sys.exit('template not found')

                    listtar=[k+v for k,v in  zip(ll['wdirectory'],ll['namefile'])]
                    listtemp=[k+v for k,v in  zip(lltemp['wdirectory'],lltemp['namefile'])]
                    agnkey.agnloopdef.run_diff(array(listtar),array(listtemp),_show,_redo)
                    if len(listtemp)==0 or len(listtar)==0: sys.exit('no data selected ')
               elif _stage=='template':                               #    merge images using lacos and swarp
                    listfile=[k+v for k,v in  zip(ll['wdirectory'],ll['namefile'])]
                    agnkey.agnloopdef.run_template(array(listfile),_show,_redo)
               else: print _stage+' not defined'
          else: print '\n### no data selected'
