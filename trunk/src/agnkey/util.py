##################################################################
#       change this directory accordingly to your system
#
import socket
host = socket.gethostname()
if host not in ['svalenti-lcogt.att.net','valenti-macbook.physics.ucsb.edu','svalenti-lcogt.local',\
                'svalenti-lcogt.lco.gtn','valenti-mbp-2.lco.gtn','valenti-mbp-2','dhcp42176.physics.ucdavis.edu']:
   workingdirectory='/AGNECHO/AGNKEY/'
   execdirectory='/home/cv21/bin/'
   rawdata='/archive/engineering/'
   realpass='configure'
else:
   workingdirectory='/Users/svalenti/redu2/AGNKEY/'
   execdirectory='/Users/svalenti/bin/'
   rawdata='/archive/engineering/'
   realpass='configure'


###################################################
#
#  configure is the file where all the passwd are stored locally:
#  
#  users        ['xxx','xxxx','xxx']
#  proposal     ['xxx','xxxx','xxx']
#  superusers   ['xx','xx','xx','xxx','xx']
#  ipacuser     xxxx
#  ipacpasswd   xxxx
#  odinpasswd   xxxx
#  mysqlpasswd  xxxx
#
#
#
####################################################
def readpasswd(directory,_file):
    from numpy import genfromtxt
    data=genfromtxt(directory+_file,str)
    gg={}
    for i in data:
        try:
            gg[i[0]]=eval(i[1])
        except:
            gg[i[0]]=i[1]
    return gg

readpass=readpasswd(workingdirectory,realpass)
#################################################################

#try:     
#from agnkey import agnsqldef
#from agnkey import agnsqldef
#hostname, username, passwd, database=agnsqldef.getconnection('agnkey')
#conn = agnkey.agnsqldef.dbConnect(hostname, username, passwd, database)
#except:
#   conn=''
#   '\### warning: problem with the database'
#######################################################################

def ReadAscii2(ascifile):
   import string
   f=open(ascifile,'r')
   ss=f.readlines()
   f.close()
   vec1,vec2=[],[]
   for line in ss:
      if line[0]!='#':
         vec1.append(float(string.split(line)[0]))
         vec2.append(float(string.split(line)[1]))
   return vec1,vec2
#########################################################################
def readlist(listfile):
    from agnkey.util import correctcard
    import string,os,sys,re,glob
    from pyfits import open as opn
    if '*' in listfile:
        imglist=glob.glob(listfile)
    elif ',' in listfile: imglist = string.split(listfile,sep=',')
    else:
        try:            hdulist= opn(listfile)
        except:           hdulist=[]
        if hdulist:            imglist = [listfile]
        else:
           try:
              ff = open(listfile,'r')
              files = ff.readlines()
              ff.close()
              imglist = []
              for ff in files: 
                 ff=re.sub(' ','',ff)
                 if not ff=='\n' and ff[0]!='#':
                    ff=re.sub('\n','',ff)
                    try:
                       hdulist= opn(ff)
                       imglist.append(ff)
                    except:
                       try:
                          correctcard(ff)
                          hdulist= opn(ff)
                          imglist.append(ff)
                       except:                          pass
           except:              sys.exit('\n##### Error ###\n file '+str(listfile)+' do not  exist\n')
    if len(imglist)==0:
           sys.exit('\n##### Error ###\nIf "'+str(listfile)\
                                +'" is an image, it is corrupted \n or is not a list of image\n')
    return imglist
##############################################################################
def delete(listfile):
    import os,string,re,glob
    if listfile[0]=='@':   
        ff = open(listfile[1:])
        files = ff.readlines()
        imglist = []
        for ff in files: 
            ff=re.sub(' ','',ff)
            if not ff=='\n' and ff[0]!='#':
                ff=re.sub('\n','',ff)
                imglist.append(ff)
    elif ',' in listfile: imglist = string.split(listfile,sep=',')
    else:       imglist=[listfile]    
    lista=[]
    for _file in imglist:   lista=lista+glob.glob(_file)
    if lista:
        for _file in lista:
            try:          os.system('rm '+_file)
            except:       pass
###############################################################
def readhdr(img):
   from pyfits import open as popen
   try:    hdr=popen(img)[0].header
   except:
      from agnkey.util import correctcard
      try: 
         correctcard(img)
      except: 
         import sys
         sys.exit('image '+str(img)+' is corrupted, delete it and start again')
      hdr=popen(img)[0].header
   return hdr

def readkey3(hdr,keyword):
    import re,string,sys
    import pyfits
    if int(re.sub('\.','',str(pyfits.__version__))[:2])<=30:  aa='HIERARCH '
    else: aa=''
    try:    _instrume=hdr.get('INSTRUME').lower()
    except: _instrume='none'
    if _instrume in ['kb05','kb70','kb71','kb73','kb74','kb75','kb76','kb77','kb78','kb79']:    # SBIG
        useful_keys = {'object'    : 'OBJECT',\
                           'date-obs'  : 'DATE-OBS',\
                           'ut'        : 'DATE-OBS',\
                           'RA'        : 'RA',\
                           'DEC'       : 'DEC',\
                           'datamin'   :  -100.0,\
                           'datamax'   : 'SATURATE',\
                           'observer'  : 'OBSERVER',\
                           'exptime'   : 'EXPTIME',\
                           'wcserr'    : 'WCSERR',\
                           'instrume'  : 'INSTRUME',\
                           'JD'        : 'MJD-OBS',\
                           'filter'    : 'FILTER',\
                           'gain'      : 'GAIN',\
                           'ron'       : 'RDNOISE',\
#                           'gain'      : 10.,\
#                           'ron'       : 100.,\
                           'airmass'   : 'AIRMASS',\
                           'type'      : 'OBSTYPE',\
                           'propid'      : 'PROPID',\
                           'telescop'  : 'TELESCOP'} 
    elif _instrume in ['fl02','fl03','fl04','fl05','fl06']:   # sinistro
        useful_keys = {'object'    : 'OBJECT',\
                           'date-obs'  : 'DATE-OBS',\
                           'ut'        : 'DATE-OBS',\
                           'RA'        : 'RA',\
                           'DEC'       : 'DEC',\
                           'datamin'   :  -100.0,\
                           'datamax'   : 'SATURATE',\
                           'observer'  : 'OBSERVER',\
                           'exptime'   : 'EXPTIME',\
                           'wcserr'    : 'WCSERR',\
                           'instrume'  : 'INSTRUME',\
                           'JD'        : 'MJD-OBS',\
                           'filter'    : 'FILTER',\
                           'gain'      : 'GAIN',\
                           'ron'       : 'RDNOISE',\
                           'airmass'   : 'AIRMASS',\
                           'type'      : 'OBSTYPE',\
                           'propid'      : 'PROPID',\
                           'telescop'  : 'TELESCOP'} 
    elif _instrume in ['fs01','em03','fs02','em01','fs03']:
       useful_keys = {'object'    : 'OBJECT',\
                         'date-obs'  : 'DATE-OBS',\
                         'ut'        : 'DATE-OBS',\
                         'RA'        : 'RA',\
                         'DEC'       : 'DEC',\
                         'datamin'   : -100,\
                         'datamax'   : 60000,\
                         'wcserr'    : 'WCS_ERR',\
                         'observer'  : 'OBSERVER',\
                         'exptime'   : 'EXPTIME',\
                         'instrume'  : 'INSTRUME',\
                         'JD'        : 'MJD',\
                         'filter'    : 'FILTER',\
                         'gain'      : 'GAIN',\
                         'ron'       : 'RDNOISE',\
                         'airmass'   : 'AIRMASS',\
                         'type'      : 'OBSTYPE',\
                         'telescop'  : 'TELID'} 
    else: 
       useful_keys = {'object'    : 'OBJECT',\
                           'date-obs'  : 'DATE-OBS'}
    if keyword in useful_keys:
       if type(useful_keys[keyword])==float:
          value=useful_keys[keyword]
       else:
          value=hdr.get(useful_keys[keyword])
          if keyword=='date-obs':
             import string,re
             try:
                value=re.sub('-','',string.split(value,'T')[0])
             except:
                pass
          elif keyword=='ut':
             import string,re
             try:
                value=string.split(value,'T')[1]
             except:
                pass
          elif keyword=='object':
             value=re.sub('\}','',value)
             value=re.sub('\{','',value)
             value=re.sub('\[','',value)
             value=re.sub('\]','',value)
             value=re.sub('\(','',value)
             value=re.sub('\)','',value)
             value=re.sub('-','',value)
             value=re.sub(' ','',value)
          elif keyword=='JD':       
             value=value+0.5
          elif keyword=='instrume':      value=value.lower()
          elif keyword=='filter':      
             value1=hdr.get('FILTER2')
             value2=hdr.get('FILTER1')
             value3=hdr.get('FILTER3')
             value=[a for a in [value1,value2,value3] if 'air' not in a]
             if not value: value='air'
             else: value=value[0]
          elif keyword=='RA':
             value=(((float(string.split(value,':')[2])/60+float(string.split(value,':')[1]))/60)\
                 +float(string.split(value,':')[0]))*15
          elif keyword=='DEC':
                if string.count(string.split(value,':')[0],'-')==0:
                    value=((float(string.split(value,':')[2])/60+float(string.split(value,':')[1]))/60)\
                        +float(string.split(value,':')[0])
                else:
                    value=(-1)*(((abs(float(string.split(value,':')[2])/60)+float(string.split(value,':')[1]))/60)\
                                    +abs(float(string.split(value,':')[0])))
    else:
       if keyword=='date-night':
            try:
               _tel=hdr.get('TELID').lower()
               if _tel in ['1m0-08']:                       # elp  shift
                  delta=0.0
               elif _tel in ['fts','ftn']:  # FTS,FTN no shift
                  delta=0.0
               elif _tel in ['1m0-10','1m0-12','1m0-13']:  # south africa
                  delta=0.4
               elif _tel in ['1m0-03','1m0-11']:           # south spring
                  delta=0.0
               elif _tel in ['1m0-05','1m0-04','1m0-09']:  # cile shift
                  delta=0.5
               else:
                  delta=0.5
            except:   delta=0.5
            import datetime
            _date=readkey3(hdr,'DATE-OBS')
            a=(datetime.datetime.strptime(string.split(_date,'.')[0],"20%y-%m-%dT%H:%M:%S")-datetime.timedelta(delta)).isoformat()
            value=re.sub('-','',string.split(a,'T')[0])
       else:
          if keyword in hdr:   
             value=hdr.get(keyword)
          else:
             value=''
    if type(value) == str:    value=re.sub('\#','',value)
    return value

#######################################################
def writeinthelog(text,logfile):
    f=open(logfile,'a')
    f.write(text)
    f.close()
################################################
def correctcard(img):
    from  pyfits import open as popen
    from numpy  import asarray
    import re
    hdulist=popen(img)
    a=hdulist[0]._verify('fix')    
    _header=hdulist[0].header
    for i in range(len(a)):
        if not a[i]:
            a[i]=['']
    ww=asarray([i for i in range(len(a)) if (re.sub(' ','',a[i][0])!='')])
    if len(ww)>0:
        newheader=[]
        headername=[]
        for j in _header.items():
            headername.append(j[0])
            newheader.append(j[1])
        hdulist.close()
        imm=popen(img,mode='update')
        _header=imm[0].header
        for i in ww:
            if headername[i]:
                try:
                    _header.update(headername[i],newheader[i])
                except:
                    _header.update(headername[i],'xxxx')
        imm.flush()
        imm.close()
######################################################################################################
def updateheader(image,dimension,headerdict):
    from pyfits import open as opp
    try:
        imm=opp(image,mode='update')
        _header=imm[dimension].header
################################
#   change way to update to speed up the process
#   now get dictionary   08 12  2012
################################
        for i in headerdict.keys():
           _header.update(i,headerdict[i][0],headerdict[i][1])
###################################################
#        _header.update(_headername,_value,commento)
        imm.flush()
        imm.close()
    except:
        import agnkey
        from agnkey.util import correctcard
        print 'warning: problem to update header, try to correct header format ....'
        correctcard(image)
        try:
            imm=opp(image,mode='update')
            _header=imm[dimension].header
###################################################
            for i in headerdict.keys():
               _header.update(i,headerdict[i][0],headerdict[i][1])
###################################################
            _header.update(_headername,_value,commento)
            imm.flush()
            imm.close()
        except:
           print 'niente'
#           import sys
#            sys.exit('error: not possible update header')
#################################################################################################
def display_image(img,frame,_z1,_z2,scale,_xcen=0.5,_ycen=0.5,_xsize=1,_ysize=1,_erase='yes'):
    goon='True'
    import glob, subprocess, os, time
    ds9 = subprocess.Popen("ps -U"+str(os.getuid())+"|grep -v grep | grep ds9",shell=True,stdout=subprocess.PIPE).stdout.readlines()
    if len(ds9)== 0 :   
       subproc = subprocess.Popen('ds9',shell=True)
       time.sleep(3)

    if glob.glob(img):
       from pyraf import iraf
       iraf.images(_doprint=0)
       iraf.tv(_doprint=0)
       import string,os
       if _z2: 
          try:
              sss=iraf.display(img, frame, xcen=_xcen, ycen=_ycen, xsize=_xsize, ysize=_ysize, erase=_erase,\
                                   fill='yes', zscale='no', zrange='no', z1=_z1, z2=_z2,Stdout=1)
          except:
              print ''
              print '### ERROR: PROBLEM OPENING DS9'
              print ''
              goon='False'                 
       else:
        try:  
            sss=iraf.display(img, frame, xcen=_xcen, ycen=_ycen, xsize=_xsize, ysize=_ysize, erase=_erase, fill='yes', Stdout=1)
        except:
            print ''
            print '### ERROR: PROBLEM OPENING DS9'
            print ''
            goon=False
 
       if scale and goon:
          answ0 = raw_input('>>> Cuts OK ? [y/n] ? [y] ')
          if not answ0: answ0='y'
          elif answ0=='no' or answ0=='NO': answ0='n' 

          while answ0=='n':
              _z11=float(string.split(string.split(sss[0])[0],'=')[1])
              _z22=float(string.split(string.split(sss[0])[1],'=')[1])
              z11 = raw_input('>>> z1 = ? ['+str(_z11)+'] ? ')
              z22 = raw_input('>>> z2 = ? ['+str(_z22)+'] ? ')
              if not z11: z11=_z11
              else: z11=float(z11)
              if not z22: z22=_z22
              else: z22=float(z22)
              print z11,z22
              sss=iraf.display(img,frame,fill='yes', xcen=_xcen, ycen=_ycen, xsize=_xsize, ysize=_ysize, erase=_erase,\
                                   zrange='no', zscale='no', z1=z11, z2=z22, Stdout=1)
              answ0 = raw_input('>>> Cuts OK ? [y/n] ? [y] ')
              if not answ0: answ0='y'
              elif answ0=='no' or answ0=='NO': answ0='n'
       if goon:
          _z1,_z2=string.split(string.split(sss[0])[0],'=')[1],string.split(string.split(sss[0])[1],'=')[1]
    else:
        print 'Warning: image '+str(img)+' not found in the directory '
    return _z1,_z2,goon

###########################################################################
def readstandard(standardfile):
    import agnkey
    from numpy import array,abs
    import string,os
    if os.path.isfile(standardfile):
       listastandard=standardfile
    elif standardfile[0]=='/':
       listastandard=standardfile
    else:
       listastandard=agnkey.__path__[0]+'/standard/stdlist/'+standardfile
    f=open(listastandard,'r')
    liststd=f.readlines()
    f.close()
    star,ra,dec=[],[],[]
    magnitude=[]
    for i in liststd:
       if i[0]!='#':
          star.append(string.split(i)[0])
          _ra=string.split(string.split(i)[1],':')
          _dec=string.split(string.split(i)[2],':')
          ra.append((float(_ra[0])+((float(_ra[1])+(float(_ra[2])/60.))/60.))*15)
          if '-' in str(_dec[0]):
             dec.append((-1)*(abs(float(_dec[0]))+((float(_dec[1])+(float(_dec[2])/60.))/60.)))
          else:
             dec.append(float(_dec[0])+((float(_dec[1])+(float(_dec[2])/60.))/60.))
          try:   magnitude.append(string.split(i)[3])
          except:  magnitude.append(999)
    return array(star),array(ra),array(dec),array(magnitude)

#################################################################################################
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
        if spec[0].data.ndim == 1: fl = spec[0].data
        elif spec[0].data.ndim == 2: fl = spec[0].data[:,0]
        elif spec[0].data.ndim == 3: fl = spec[0].data[0,0,:]
    except:
        if spec[0].data.rank == 1: fl = spec[0].data
        elif spec[0].data.rank == 2: fl = spec[0].data[:,0]
        elif spec[0].data.rank == 3: fl = spec[0].data[0,0,:]
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
    return lam,fl
###########################################################################
def pval(_xx, p):
    _y=+p[0]+p[1]*_xx
    return _y

def residual(p,y,x):
    for i in range(len(p)):
        err = (y-p[i]*x**i)
    return err
#########################################################################
def defsex(namefile):
    import agnkey
    import string,re,os
    sexfile=agnkey.__path__[0]+'/standard/sex/default.sex'
    f=open(sexfile,'r')
    ss=f.readlines()
    f.close()   
    ff=open(namefile,'w')
    for i in ss:
        if string.count(i,'PARAMETERS_NAME')==1:
            ff.write('PARAMETERS_NAME  "'+agnkey.__path__[0]+'/standard/sex/default.param"\n')
        elif string.count(i,'FILTER_NAME')==1:
            ff.write('FILTER_NAME  "'+agnkey.__path__[0]+'/standard/sex/default.conv"\n')
        elif string.count(i,'STARNNW_NAME')==1:
            ff.write('STARNNW_NAME "'+agnkey.__path__[0]+'/standard/sex/default.nnw"\n')
        else:
            ff.write(i)
    ff.close()
    return namefile

############################################################

def defswarp(namefile,imgname,_combine,gain='',ron='',pixelscale=0.4699,_ra='',_dec=''):
    import agnkey
    import string,re,os
    if _combine.lower() in ['median']: _combine='MEDIAN'
    elif _combine.lower() in ['average']: _combine='AVERAGE'
    elif _combine.lower() in ['sum']: _combine='SUM'
    swarpfile=agnkey.__path__[0]+'/standard/sex/default.swarp'
    f=open(swarpfile,'r')
    ss=f.readlines()
    f.close()   
    ff=open(namefile,'w')
    for i in ss:
        if string.count(i,'IMAGEOUT_NAME')==1:
            ff.write('IMAGEOUT_NAME    '+str(imgname)+'  # Output filename \n')
        elif string.count(i,'WEIGHTOUT_NAME')==1:
            ff.write('WEIGHTOUT_NAME   '+str(re.sub('.fits','.weight.fits',imgname))+'  # Output weight-map filename  \n')
        elif string.count(i,'COMBINE_TYPE')==1:
            ff.write('COMBINE_TYPE    '+str(_combine)+'  # MEDIAN,AVERAGE,MIN,MAX,WEIGHTED,CHI2 \n')
        elif string.count(i,'GAIN_DEFAULT')==1:
           if gain:
              ff.write('GAIN_DEFAULT    '+str(gain)+'  # Default gain if no FITS keyword found \n')
           else:     ff.write(i)
        elif string.count(i,'RDNOISE_DEFAULT')==1:
           if ron:
              ff.write('RDNOISE_DEFAULT    '+str(ron)+'  # Default ron if no FITS keyword found \n')
           else:     ff.write(i)
        elif string.count(i,'PIXEL_SCALE')==1:
              ff.write('PIXEL_SCALE    '+str(pixelscale)+','+str(pixelscale)+'  #  \n')
        elif string.count(i,'PIXELSCALE_TYPE')==1:
              ff.write('PIXELSCALE_TYPE MANUAL,MANUAL  #  \n')
        elif string.count(i,'CENTER_TYPE')==1:
              ff.write('CENTER_TYPE MANUAL,MANUAL  #  \n')
        elif string.count(i,'Coordinates of the image center')==1:
              ff.write('CENTER '+str(_ra)+','+str(_dec)+'  #  \n')
        else:
            ff.write(i)
    ff.close()
    return namefile

#################################################################################
def airmass(img,overwrite=True,_observatory='lasilla'):
   import agnkey
   from agnkey.util import readhdr,readkey3, delete, updateheader
   from pyraf import iraf
   iraf.astutil(_doprint=0)
   hdr=readhdr(img)
   if readkey3(hdr,'UTC'):    
      _UT=(readkey3(hdr,'UTC')+(readkey3(hdr,'exptime')/2))/3600
      _date=readkey3(hdr,'date-obs')
      _date=_date[0:4]+'-'+_date[4:6]+'-'+_date[6:8]
      _RA=readkey3(hdr,'RA')/15
      _DEC=readkey3(hdr,'DEC')
      f = file('airmass.txt','w')
      f.write('mst = mst ("'+str(_date)+'",'+str(_UT)+', obsdb ("'+str(_observatory)+'", "longitude"))\n')
      f.write('air = airmass ('+str(_RA)+','+str(_DEC)+',mst, obsdb ("'+str(_observatory)+'", "latitude"))\n')
      f.write('print(air)\n')
      f.close()
      _air=iraf.astcalc(image=img, command="airmass.txt",Stdout=1)[0]
      try: _air=float(_air)
      except: _air=999
      delete('airmass.txt')
      if overwrite and _air<99.:
         updateheader(img,0,{'AIRMASS':[_air,'mean airmass computed with astcalc']})
   else:   _air=''
   return _air
####################################################################################

def  name_duplicate(img,nome,ext):  ###########################
   import re,string,os,glob
   import agnkey
   from agnkey.util import readhdr,readkey3, delete
   dimg=readkey3(readhdr(img),'DATE-OBS')
   listafile=glob.glob(nome+'_?'+ext+'.fits')+glob.glob(nome+'_??'+ext+'.fits')
   if len(listafile) == 0: nome = nome+"_1"+ext+'.fits'
   else:
      date=[]
      for l in listafile:
         date.append(readkey3(readhdr(l),'DATE-OBS'))
      if dimg in date:
         nome=listafile[date.index(dimg)]
#         if overwrite:
#            delete(nome)
      else:
         n=1
         while nome+'_'+str(n)+str(ext)+'.fits' in listafile:
            n=n+1
         nome=nome+'_'+str(n)+str(ext)+'.fits'
   return nome
###############################################################################
def correctobject(img,coordinatefile):
    import os,re,sys,string
    from numpy import arccos, sin,cos,pi,argmin
    import agnkey
    from agnkey.util import readstandard, readhdr,readkey3, updateheader
    scal=pi/180.
    std,rastd,decstd,magstd=readstandard(coordinatefile)
    img=re.sub('\n','',img)
    correctcard(img)
    hdr=readhdr(img)
    _ra=readkey3(hdr,'RA')
    _dec=readkey3(hdr,'DEC')
    dd=arccos(sin(_dec*scal)*sin(decstd*scal)+cos(_dec*scal)*cos(decstd*scal)*cos((_ra-rastd)*scal))*((180/pi)*3600)
    if min(dd)<200:
       updateheader(img,0,{'OBJECT':[std[argmin(dd)],'Original target.']})
       aa,bb,cc=rastd[argmin(dd)],decstd[argmin(dd)],std[argmin(dd)]
    else: aa,bb,cc='','',''
    return aa,bb,cc

##################################################################################################
def repstringinfile(filein,fileout,string1,string2):
    import re
    f=open(filein,'r')
    ss=f.readlines()
    f.close()
    f=open(fileout,'w')
    for n in range(len(ss)):
        if string1 in ss[n]:   f.write(re.sub(string1,string2,ss[n]))
        else:                 f.write(ss[n])
    f.close()
###################################################

def limmag(img):
   import agnkey
   from agnkey.util import readhdr
   hdr=readhdr(img)
   _ZP=readkey3(hdr,'PHOTZP')
   _gain=readkey3(hdr,'gain')
   _exptime=readkey3(hdr,'exptime')
   _fwhm=readkey3(hdr,'PSF_FWHM')  
   _mbkg=readkey3(hdr,'MBKG')   # background from sextractor
   _instrume=readkey3(hdr,'instrume')  
   check=1
   if not _ZP:     check=0
   if not _gain:   check=0
   if not _fwhm:   check=0
   if not _mbkg:   check=0
   else:  
      if _mbkg<=0: _mbkg=0
   if check==1:
      # formula from McLean 1997)
      from numpy import pi,log10
      if _instrume=='efosc':   ps=readkey3(hdr,'binx')*.12
      else:   ps=0.288
      n=pi*((_fwhm/ps)**2) 
      sn=5       # signal to noise
      maglim=_ZP -2.5 * log10(sn * (1/_gain) * ((n*_mbkg/_exptime)**(.5)) )
      return maglim
   else: return ''
##########################################################################
def marksn2(img,fitstab,frame=1,fitstab2='',verbose=False):
   from pyraf import iraf
   import pyfits
   from numpy import array   #,log10
   import agnkey
   iraf.noao(_doprint=0)
   iraf.digiphot(_doprint=0)
   iraf.daophot(_doprint=0)
   iraf.images(_doprint=0)
   iraf.imcoords(_doprint=0)
   iraf.proto(_doprint=0)
   iraf.set(stdimage='imt1024')
   hdr=agnkey.util.readhdr(fitstab)
   _filter=agnkey.util.readkey3(hdr,'filter')
   column=agnkey.agnabsphotdef.makecatalogue([fitstab])[_filter][fitstab]

   rasex=array(column['ra0'],float)
   decsex=array(column['dec0'],float)


   if fitstab2:
      hdr=agnkey.util.readhdr(fitstab2)
      _filter=agnkey.util.readkey3(hdr,'filter')
      _exptime=agnkey.util.readkey3(hdr,'exptime')
      column=agnkey.agnabsphotdef.makecatalogue([fitstab2])[_filter][fitstab2]
      rasex2=array(column['ra0'],float)
      decsex2=array(column['dec0'],float)

   iraf.set(stdimage='imt1024')
   iraf.display(img,frame,fill=True,Stdout=1)
   vector=[]
   for i in range(0,len(rasex)):
      vector.append(str(rasex[i])+' '+str(decsex[i]))

   xy = iraf.wcsctran('STDIN',output="STDOUT",Stdin=vector,Stdout=1,image=img,inwcs='world',units='degrees degrees',outwcs='logical',\
                         formats='%10.1f %10.1f',verbose='yes')[3:]
   iraf.tvmark(frame,'STDIN',Stdin=list(xy),mark="circle",number='yes',label='no',radii=10,nxoffse=5,nyoffse=5,color=207,txsize=2)

   if verbose:
 #     print 2.5*log10(_exptime)
      for i in range(0,len(column['ra0'])):
         print xy[i],column['ra0'][i],column['dec0'][i],column['magp3'][i],column['magp4'][i],column['smagf'][i],column['magp2'][i]

   if fitstab2:
      vector2=[]
      for i in range(0,len(rasex2)):
         vector2.append(str(rasex2[i])+' '+str(decsex2[i]))
      xy1 = iraf.wcsctran('STDIN',output="STDOUT",Stdin=vector2,Stdout=1,image=img,inwcs='world',units='degrees degrees',outwcs='logical',\
                            formats='%10.1f %10.1f',verbose='yes')[3:]
      iraf.tvmark(frame,'STDIN',Stdin=list(xy1),mark="cross",number='yes',label='no',radii=10,nxoffse=5,nyoffse=5,color=205,txsize=2)


###############################

def Docosmic(img):
   import time
   start=time.time()
   import pyfits
   import agnkey
   import re,os,string
   from numpy import array,where,int16
   hd = pyfits.getheader(img)
   ar = pyfits.getdata(img)
   _tel=hd['TELID']
   if _tel in ['fts','ftn']:
      agnkey.delete('new.fits')
      out_fits = pyfits.PrimaryHDU(header=hd,data=ar)
      out_fits.scale('float32',bzero=0,bscale=1)
      out_fits.writeto('new.fits', clobber=True, output_verify='fix')
      ar = pyfits.getdata('new.fits')
      hd = pyfits.getheader('new.fits')
      agnkey.delete('new.fits')
      gain    = hd['GAIN']
      sat     = 35000
      rdnoise = hd['RDNOISE']
   else:
      gain    = hd['GAIN']
      sat     = hd['SATURATE']
      rdnoise = hd['RDNOISE']
   niter=1
   print gain,sat,rdnoise
   c = agnkey.cosmics.cosmicsimage(ar
                                 ,gain=gain
                                 ,readnoise=rdnoise
                                 ,sigclip=5
                                 ,sigfrac=0.3 
                                 ,objlim=5
                                 ,satlevel=sat
                                 )
   c.run(maxiter = niter)
   out=re.sub('.fits','.clean.fits',string.split(img,'/')[-1])
   outmask=re.sub('.fits','.mask.fits',string.split(img,'/')[-1])
   outsat=re.sub('.fits','.sat.fits',string.split(img,'/')[-1])

   out1=c.cleanarray
   out2=c.cleanarray-c.rawarray
   out3=c.getsatstars()

   out_fits = pyfits.PrimaryHDU(header=hd,data=out1)
   out_fits.writeto(out, clobber=True, output_verify='fix')

   out_fits = pyfits.PrimaryHDU(header=hd,data=where(out2==0,0,1))
   out_fits.writeto(outmask, clobber=True, output_verify='fix')

   out_fits = pyfits.PrimaryHDU(header=hd,data=where(out3,1,0))
   out_fits.writeto(outsat, clobber=True, output_verify='fix')

#   if bp==16:           out_fits.scale('int16', 'old')
#   if bp==16:  lsc.util.updateheader(outsat,0,{'BZERO':[bz,'Number to offset data values by '],'BSCALE':[bs,'Number to multiply data values by']})
   print time.time()-start
   return out,outmask,outsat

##############################################

def checksnlist(img,listfile):
    import agnkey
    import string
    from agnkey.util import readkey3,readhdr
    from numpy import cos,sin,arccos,pi, argmin
    scal=pi/180.    
    std,rastd,decstd,magstd=agnkey.util.readstandard(listfile)
    hdrt=readhdr(img)
    _ra=readkey3(hdrt,'RA')
    _dec=readkey3(hdrt,'DEC')
    _object=readkey3(hdrt,'object')
    _xdimen=readkey3(hdrt,'XDIM')
    _ydimen=readkey3(hdrt,'YDIM')
    if not _xdimen: _xdimen=readkey3(hdrt,'NAXIS1')
    if not _ydimen: _ydimen=readkey3(hdrt,'NAXIS2')
    dd=arccos(sin(_dec*scal)*sin(decstd*scal)+cos(_dec*scal)*cos(decstd*scal)*cos((_ra-rastd)*scal))*((180/pi)*3600)
    lll=[str(rastd[argmin(dd)])+' '+str(decstd[argmin(dd)])]
    from pyraf import iraf
    bbb=iraf.wcsctran('STDIN','STDOUT',img,Stdin=lll,inwcs='world',units='degrees degrees',outwcs='logical',columns='1 2',formats='%10.5f %10.5f',Stdout=1)[3]
    if    float(string.split(bbb)[0])<=_xdimen and float(string.split(bbb)[1])<=_ydimen and float(string.split(bbb)[0])>=0 and float(string.split(bbb)[1])>=0:
        #print str(std[argmin(dd)])+' in the field '+str(bbb)
        _RA=rastd[argmin(dd)]
        _DEC=decstd[argmin(dd)]
        _SN=std[argmin(dd)]
    else: 
        #print 'out '+str(bbb)
        _RA,_DEC,_SN='','',''
    return _RA,_DEC,_SN

##########################################################################################################
def checksndb(img,table):
   import agnkey
   hostname, username, passwd, database=agnkey.agnsqldef.getconnection('agnkey')
   conn = agnkey.agnsqldef.dbConnect(hostname, username, passwd, database)

   hdrt=agnkey.util.readhdr(img)
   _ra=agnkey.util.readkey3(hdrt,'RA')
   _dec=agnkey.util.readkey3(hdrt,'DEC')
   aa=agnkey.agnsqldef.getfromcoordinate(conn, table, _ra, _dec,.5)
   if len(aa)>=1:
      _RA,_DEC,_SN,_type=aa[0]['ra_sn'],aa[0]['dec_sn'],aa[0]['name'],aa[0]['objtype']
   else:
      _RA,_DEC,_SN,_type='','','',''
   return _RA,_DEC,_SN,_type
##################################################################3

def sendtrigger(_name,_ra,_dec,_site,_exp,_nexp,_filters,_airmass,_utstart,_utend,_prop,_user):
    from reqdb.requests import Request, UserRequest
    from reqdb.client   import SchedulerClient
    from datetime import datetime
    import time
    import string,re,sys,os

    def JDnow(datenow='',verbose=False):
        import datetime
        import time
        _JD0=2455927.5
        if not datenow:
            datenow=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
        _JDtoday=_JD0+(datenow-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
                   (datenow-datetime.datetime(2012, 01, 01,00,00,00)).days
        if verbose: print 'JD= '+str(_JDtoday)
        return _JDtoday

    if _site in ['elp','cpt','ogg','lsc','coj']:
       location = {
          'telescope_class' : '1m0', 
          'site'            : _site,   
       } 
    else:
       location = {
          'telescope_class' : '1m0',
       } 
    proposal = {
        'proposal_id'   : _prop,
        'user_id'       : _user,
        }
    constraints = {'max_airmass' : _airmass,
                   }
    window1 = {
        'start'    : _utstart,
        'end'      : _utend,
        }
    target = {
        'name'              : _name,  
        'ra'                : _ra,    
        'dec'               : _dec,   
        'proper_motion_ra'  : 0,     
        'proper_motion_dec' : 0,     
        'parallax'          : 0,     
        'epoch'             : 2000,  
        }

    req = Request()
    req.set_target(target)
    req.set_location(location)
    req.set_constraints(constraints)
    req.add_window(window1)
    
    fildic={'1m0':{'U':'U','B':'B','V':'V','R':'R','I':'I','u':'up','g':'gp','r':'rp','i':'ip','z':'zs','up':'up','gp':'gp','rp':'rp','ip':'ip','zs':'zs'}}
    n  = len(_filters)
    for f in range(n):
       if _filters[f] in fildic['1m0'].keys():
          molecule = {
             'exposure_time'   : _exp[f],
             'exposure_count'  : _nexp[f],
             'filter'          : fildic['1m0'][_filters[f]],
             'type'            : 'EXPOSE', 
             'ag_name'         : '',         
             'ag_mode'         : 'Optional',
             'instrument_name' : 'SCICAM',       
             'bin_x'           : 2,              
             'bin_y'           : 2,
             'defocus'         : 0.0             
             }
          req.add_molecule(molecule) 

#    ur = UserRequest(group_id=_name)
#    ur.add_request(req)
#    ur.operator = 'single'
#    ur.set_proposal(proposal)
#    client        = SchedulerClient('http://scheduler-dev.lco.gtn/requestdb/')
#    response_data = client.submit(ur, keep_record=True)
#    client.print_submit_response()

    response_data ={'tracking_number': 9999, 'request_numbers': 9999}

    _start=datetime.strptime(string.split(str(_utstart),'.')[0],"20%y-%m-%d %H:%M:%S")
    _end=datetime.strptime(string.split(str(_utend),'.')[0],"20%y-%m-%d %H:%M:%S")
    input_datesub=JDnow(verbose=False)
    input_str_smjd=JDnow(_start,verbose=False)
    input_str_emjd=JDnow(_end,verbose=False)
    _seeing=9999
    _sky=9999
    _instrument='1m'
    _priority=99

    try:
       lineout = str(input_datesub)+' '+str(input_str_smjd)+' '+str(input_str_emjd)+'   '+str(_site)+\
                 ' '+','.join(_filters)+' '+','.join(_nexp)+' '+','.join(_exp)+'   '+\
                 str(_airmass)+'   '+str(_prop)+' '+str(_user)+' '+str(_seeing)+' '+str(_sky)+\
                 ' '+str(_instrument)+' '+str(_priority)+' '+str(response_data.get('tracking_number'))+' '+str(response_data.get('request_numbers')[0])
    except:
       lineout = str(input_datesub)+' '+str(input_str_smjd)+' '+str(input_str_emjd)+'   '+str(_site)+\
                 ' '+','.join(_filters)+' '+','.join(_nexp)+' '+','.join(_exp)+'   '+\
                 str(_airmass)+'   '+str(_prop)+' '+str(_user)+' '+str(_seeing)+' '+str(_sky)+\
                 ' '+str(_instrument)+' '+str(_priority)+' 0  0'
    return lineout

###############################################################################

def sendtrigger2(_name,_ra,_dec,expvec,nexpvec,filtervec,_utstart,_utend,username,passwd,proposal,camera='sbig',_airmass=2.0,_site=''):
    import httplib
    import urllib
    import json
    import string,re
    from datetime import datetime
    def JDnow(datenow='',verbose=False):
        import datetime
        import time
        _JD0=2455927.5
        if not datenow:
            datenow=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
        _JDtoday=_JD0+(datenow-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
                   (datenow-datetime.datetime(2012, 01, 01,00,00,00)).days
        if verbose: print 'JD= '+str(_JDtoday)
        return _JDtoday

    fildic={'1m0':{'U':'U','B':'B','V':'V','R':'R','I':'I',\
                   'u':'up','g':'gp','r':'rp','i':'ip','z':'zs',\
                   'up':'up','gp':'gp','rp':'rp','ip':'ip','zs':'zs'}}

    _inst={'sinistro':'1M0-SCICAM-SINISTRO','sbig':'1M0-SCICAM-SBIG','spectral':'2M0-SCICAM-SPECTRAL','oneof':'oneof'}
    binx={'sbig':2,'sinistro':1,'spectral':2}

    if camera in ['sbig','sinistro','oneof']:        telclass='1m0'
    else:        telclass='2m0'

    if _site in ['elp','cpt','ogg','lsc','coj']:
       _location={ "telescope_class": telclass, 'site' : _site}
    else:     _location={ "telescope_class": telclass}

    if camera in ['sbig','sinistro','spectral']:          
       molecules=[]
       for i in range(0,len(filtervec)):
          molecules.append({"ag_mode": "OPTIONAL", "ag_name": "", "bin_x": int(binx[camera]), "bin_y": int(binx[camera]),
                            "defocus": 0.0, "exposure_count": int(nexpvec[i]), "exposure_time": float(expvec[i]),
                            "filter": fildic[telclass][filtervec[i]], "instrument_name": _inst[camera], "priority": 1,
                            "type": "EXPOSE"})

       user_request =  {"group_id":_name, 
                     "operator": "single", 
                     "type": "compound_request",
                     "requests": [ { "operator": "single",
                                     "type": "compound_request", 
                                     "requests": [ {
                                         "constraints": {"max_airmass": float(_airmass) },
                                         "location": _location, 
                                         "molecules": molecules,  
                                         "observation_note": "C#",
                                         "type": "request",
                                         "windows": [ {"end": _utend, "start": _utstart }  ],
                                         "target": {"coordinate_system": "ICRS", 
                                                    "epoch": 2000.0, 
                                                    "equinox": "J2000", 
                                                    "parallax": 0.0, 
                                                    "proper_motion_dec": 0.0, 
                                                    "proper_motion_ra": 0.0, 
                                                    "ra": float(_ra), 
                                                    "dec": float(_dec), 
                                                    "name": _name, 
                                                    "type": "SIDEREAL"}} ]}]}
    elif camera in ['oneof']:
       molecules1=[]
       for i in range(0,len(filtervec)):
          molecules1.append({"ag_mode": "OPTIONAL", "ag_name": "", "bin_x": 2, "bin_y": 2,
                            "defocus": 0.0, "exposure_count": int(nexpvec[i]), "exposure_time": float(expvec[i]),
                            "filter": fildic[telclass][filtervec[i]], "instrument_name": "SCICAM", "priority": 1,
                            "type": "EXPOSE"})

       molecules2=[]
       for i in range(0,len(filtervec)):
          molecules2.append({"ag_mode": "OPTIONAL", "ag_name": "", "bin_x": 1, "bin_y": 1,
                            "defocus": 0.0, "exposure_count": int(nexpvec[i]), "exposure_time": float(expvec[i]),
                            "filter": fildic[telclass][filtervec[i]], "instrument_name": "1M0-SCICAM-SINISTRO", "priority": 1,
                            "type": "EXPOSE"})

       user_request =  {"group_id":_name, 
                     "operator": "ONEOF", 
                     "type": "compound_request",
                     "requests": [ { "operator": "single",
                                     "type": "compound_request", 
                                     "requests": [ {
                                         "constraints": {"max_airmass": float(_airmass) },
                                         "location": _location, 
                                         "molecules": molecules1,  
                                         "observation_note": "C#",
                                         "type": "request",
                                         "windows": [ {"end": _utend, "start": _utstart }  ],
                                         "target": {"coordinate_system": "ICRS", 
                                                    "epoch": 2000.0, 
                                                    "equinox": "J2000", 
                                                    "parallax": 0.0, 
                                                    "proper_motion_dec": 0.0, 
                                                    "proper_motion_ra": 0.0, 
                                                    "ra": float(_ra), 
                                                    "dec": float(_dec), 
                                                    "name": _name, 
                                                    "type": "SIDEREAL"}} ]},\
                                   { "operator": "single",
                                     "type": "compound_request", 
                                     "requests": [ {
                                         "constraints": {"max_airmass": float(_airmass) },
                                         "location": _location, 
                                         "molecules": molecules2,  
                                         "observation_note": "C#",
                                         "type": "request",
                                         "windows": [ {"end": _utend, "start": _utstart }  ],
                                         "target": {"coordinate_system": "ICRS", 
                                                    "epoch": 2000.0, 
                                                    "equinox": "J2000", 
                                                    "parallax": 0.0, 
                                                    "proper_motion_dec": 0.0, 
                                                    "proper_motion_ra": 0.0, 
                                                    "ra": float(_ra), 
                                                    "dec": float(_dec), 
                                                    "name": _name, 
                                                    "type": "SIDEREAL"}} ]}]
       }

############################################################################################################

    json_user_request = json.dumps(user_request)
    params = urllib.urlencode({'username': username ,'password': passwd, 'proposal': proposal, 'request_data' : json_user_request})
#    conn = httplib.HTTPSConnection("test.lcogt.net") 
    conn = httplib.HTTPSConnection("lcogt.net") 
    conn.request("POST", "/observe/service/request/submit", params) 
    response = conn.getresponse().read()

    python_dict = json.loads(response)
    if 'id' in python_dict:
       tracking_number=str(python_dict['id'])
    else:
       tracking_number=str('0')

    _start=datetime.strptime(string.split(str(_utstart),'.')[0],"20%y-%m-%d %H:%M:%S")
    _end=datetime.strptime(string.split(str(_utend),'.')[0],"20%y-%m-%d %H:%M:%S")
    input_datesub=JDnow(verbose=False)
    input_str_smjd=JDnow(_start,verbose=False)
    input_str_emjd=JDnow(_end,verbose=False)
    _seeing=9999
    _sky=9999
    _instrument=telclass
    priority=1

    try:
       lineout = str(input_datesub)+' '+str(input_str_smjd)+' '+str(input_str_emjd)+'   '+str(_site)+\
                 ' '+','.join(filtervec)+' '+','.join(nexpvec)+' '+','.join(expvec)+'   '+\
                 str(_airmass)+'   '+str(proposal)+' '+str(username)+' '+str(_seeing)+' '+str(_sky)+\
                 ' '+str(_instrument)+' '+str(priority)+' '+str(tracking_number)+'  0'
    except:
       lineout = str(input_datesub)+' '+str(input_str_smjd)+' '+str(input_str_emjd)+'   '+str(_site)+\
                 ' '+','.join(filtervec)+' '+','.join(nexpvec)+' '+','.join(expvec)+'   '+\
                 str(_airmass)+'   '+str(proposal)+' '+str(username)+' '+str(_seeing)+' '+str(_sky)+\
                 ' '+str(_instrument)+' '+str(priority)+' 0  0'
    return lineout

################################################################################


def sendfloydstrigger(_name,_exp,_ra,_dec,_utstart,_utend,username,passwd,proposal,_airmass=2.0,_site='',_slit=1.6,_calibration='after'):
    ''' This definition will trigger new observations using the API Web Server
        - it takes most of the input by command line
        - some input have a default value (eg telclass,airmass,binx,biny
        - if site is specify will triger a specific telescope, otherwise will trigger on the full network
        - filters, number of exposure per filter, exposure time are vector of the same lenght
    '''
    import httplib
    import urllib
    import json
    import string
    from datetime import datetime

    def JDnow(datenow='',verbose=False):
        import datetime
        import time
        _JD0=2455927.5
        if not datenow:
            datenow=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
        _JDtoday=_JD0+(datenow-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
                   (datenow-datetime.datetime(2012, 01, 01,00,00,00)).days
        if verbose: print 'JD= '+str(_JDtoday)
        return _JDtoday

    if _site in ['ogg','coj']:
       _location={"telescope_class": "2m0", "site": _site} 
    else:
       _location={"telescope_class": "2m0"}                
    slitvec={ '1.6' :"SLIT_1.6AS", '2.0' :"SLIT_2.0AS", '0.9':"SLIT_0.9AS", '6.0' :"SLIT_6AS", '1.2':"SLIT_1.2AS"}

    if _calibration=='all':
        _molecules= [{"exposure_time": 20.0, "spectra_slit": slitvec[_slit], "ag_filter": "", 
                      "priority": 1, "instrument_name": "2M0-FLOYDS-SCICAM", 
                      "type": "LAMP_FLAT", "exposure_count": 1, "ag_exp_time": 10.0, 
                      "spectra_lamp": "", "ag_mode": "OPTIONAL", "readout_mode": "", "bin_y": 1, "bin_x": 1}, 
                     {"exposure_time": _exp, "spectra_slit":  slitvec[_slit], "ag_filter": "", 
                      "priority": 3, "instrument_name": "2M0-FLOYDS-SCICAM", 
                      "type": "SPECTRUM", "exposure_count": 1, "ag_exp_time": 10.0, 
                      "spectra_lamp": "", "ag_mode": "ON", "readout_mode": "", "bin_y": 1, "bin_x": 1}, 
                     {"exposure_time": 60.0, "spectra_slit":  slitvec[_slit], "ag_filter": "", 
                      "priority": 4, "instrument_name": "2M0-FLOYDS-SCICAM", "type": "ARC", "exposure_count": 1, 
                      "ag_exp_time": 10.0, "spectra_lamp": "", 
                      "ag_mode": "ON", "readout_mode": "", "bin_y": 1, "bin_x": 1}, 
                     {"exposure_time": 20.0, "spectra_slit":  slitvec[_slit], "ag_filter": "", 
                      "priority": 5, "instrument_name": "2M0-FLOYDS-SCICAM", "type": "LAMP_FLAT", 
                      "exposure_count": 1, "ag_exp_time": 10.0, 
                      "spectra_lamp": "", "ag_mode": "ON", "readout_mode": "", "bin_y": 1, "bin_x": 1}]
    elif _calibration=='after':
        _molecules= [{"exposure_time": _exp,  "spectra_slit":  slitvec[_slit], "ag_filter": "", 
                      "priority": 1, "instrument_name": "2M0-FLOYDS-SCICAM", 
                      "type": "SPECTRUM", "exposure_count": 1, "ag_exp_time": 10.0, 
                      "spectra_lamp": "", "ag_mode": "ON", "readout_mode": "", "bin_y": 1, "bin_x": 1}, 
                     {"exposure_time": 60.0, "spectra_slit":  slitvec[_slit], "ag_filter": "", 
                      "priority": 2, "instrument_name": "2M0-FLOYDS-SCICAM", "type": "ARC", "exposure_count": 1, 
                      "ag_exp_time": 10.0, "spectra_lamp": "", 
                      "ag_mode": "ON", "readout_mode": "", "bin_y": 1, "bin_x": 1}, 
                     {"exposure_time": 20.0, "spectra_slit":  slitvec[_slit], "ag_filter": "", 
                      "priority": 3, "instrument_name": "2M0-FLOYDS-SCICAM", "type": "LAMP_FLAT", 
                      "exposure_count": 1, "ag_exp_time": 10.0, 
                      "spectra_lamp": "", "ag_mode": "ON", "readout_mode": "", "bin_y": 1, "bin_x": 1}]
    else:
        _molecules= [{"exposure_time": _exp, "spectra_slit":  slitvec[_slit], "ag_filter": "", 
                      "priority": 1, "instrument_name": "2M0-FLOYDS-SCICAM", 
                      "type": "SPECTRUM", "exposure_count": 1, "ag_exp_time": 10.0, 
                      "spectra_lamp": "", "ag_mode": "ON", "readout_mode": "", "bin_y": 1, "bin_x": 1}]

    user_request =  {"group_id":_name, 
                     "operator": "single", 
                     "type": "compound_request",
                     "requests": [ { "operator": "single",
                                     "type": "compound_request", 
                                     "requests": [ {
                                           "constraints": {"max_airmass": float(_airmass)},
                                         "location": _location, 
                                         "molecules": _molecules,  
                                         "observation_note": "C#",
                                         "type": "request",
                                         "windows": [ {"end": _utend, "start": _utstart }  ],
                                         "target": {"equinox": "J2000", "rot_angle": 0.0, 
                                                    "proper_motion_ra": 0.0, "acquire_mode": "ON",  "rot_mode": "VFLOAT", 
                                                    "epoch": 2000.0, "parallax": 0.0, 
                                                    "ra": float(_ra), "dec": float(_dec), 
                                                    "name": _name, "coordinate_system": "ICRS", "type": "SIDEREAL", "proper_motion_dec": 0.0}  } ]}]}

########################################################
    json_user_request = json.dumps(user_request)
    params = urllib.urlencode({'username': username ,'password': passwd, 'proposal': proposal, 'request_data' : json_user_request})
###############################################################################################################
#                                            triggering at the moment to the test scheduler
#                                            comment this line and un-comment next line if you want to schedule for real observations
#    conn = httplib.HTTPSConnection("test.lcogt.net") 
    conn = httplib.HTTPSConnection("lcogt.net") 
################################################################################################################
    conn.request("POST", "/observe/service/request/submit", params)
    response = conn.getresponse().read()

    python_dict = json.loads(response)
    if 'id' in python_dict:
       tracking_number=str(python_dict['id'])
    else:
       tracking_number=str('0')

###################################################################################################

    _start=datetime.strptime(string.split(str(_utstart),'.')[0],"20%y-%m-%d %H:%M:%S")
    _end=datetime.strptime(string.split(str(_utend),'.')[0],"20%y-%m-%d %H:%M:%S")
    input_datesub=JDnow(verbose=False)
    input_str_smjd=JDnow(_start,verbose=False)
    input_str_emjd=JDnow(_end,verbose=False)
    _seeing=9999
    _sky=9999
    _instrument='2m0'
    priority=1

    try:
       lineout = str(input_datesub)+' '+str(input_str_smjd)+' '+str(input_str_emjd)+'   '+str(_site)+' floyds '+str(_slit)+' '+str(_exp)+'   '+\
                 str(_airmass)+'   '+str(proposal)+' '+str(username)+' '+str(_seeing)+' '+str(_sky)+\
                 ' '+str(priority)+' '+str(tracking_number)+'  0'
    except:
       lineout = str(input_datesub)+' '+str(input_str_smjd)+' '+str(input_str_emjd)+'   '+str(_site)+' floyds '+str(_slit)+' '+str(_exp)+'   '+\
                 str(_airmass)+'   '+str(proposal)+' '+str(username)+' '+str(_seeing)+' '+str(_sky)+\
                 ' '+str(priority)+' 0  0'
    return lineout

####################################################################################################3

def getstatus(username,passwd,tracking_id):
    import httplib
    import urllib
    import json
    params = urllib.urlencode({'username': username ,'password': passwd})
    conn = httplib.HTTPSConnection("lcogt.net")
    #print "/observe/service/request/get/userrequeststatus/" + tracking_id
    conn.request("POST", "/observe/service/request/get/userrequeststatus/" + tracking_id, params)
    response = conn.getresponse().read()
    python_dict = json.loads(response)
    return python_dict

########################################################################################

def downloadfloydsraw(JD,username,passwd):
    import agnkey
    import os,string,re,sys
    command=['select * from obslog where tracknumber and windowstart >'+str(JD)]
    lista=agnkey.agnsqldef.query(command)
    ll0={}
    for jj in lista[0].keys():
        ll0[jj]=[]
    for i in range(0,len(lista)):
        for jj in lista[0].keys():
            ll0[jj].append(lista[i][jj])

    for track in ll0['tracknumber']:
        print track
        _dict=agnkey.util.getstatus(username,passwd,str(track).zfill(10))
        print _dict
        if 'state' in _dict.keys(): _status=_dict['state']
        else:  _status='xxxx'
        if 'requests' in _dict.keys(): 
           _reqnumber=_dict['requests'].keys()[0]
        else: 
           _reqnumber=''
        if _reqnumber and _status in ['UNSCHEDULABLE','COMPLETED']:
            for ii in  _dict['requests'].keys():
                _tracknumber=str(ii).zfill(10)
                try:
                   _date=re.sub('-','',_dict['requests'][ii]['schedule'][0]['frames'][0]['day_obs'])
                   print _status,_reqnumber
                   _tarfile=_reqnumber+'_'+str(_date)+'.tar.gz'
                except: 
                   _tarfile=''
                directory=agnkey.util.workingdirectory+'floydsraw/'
                if _tracknumber!='xxxx' and _tarfile:
                    if not os.path.isfile(directory+_tarfile):
#                        ata='http://data.lcogt.net/download/package/spectroscopy/request/'+_tarfile+' --directory-prefix='
#                        line='wget --http-user='+re.sub('@','%40',username)+' --http-password='+passwd+' '+ata+directory
                        line='wget --post-data "username='+re.sub('@','%40',username)+'&password='+passwd+\
                           '" https://data.lcogt.net/download/package/spectroscopy/request/'+_tarfile+' --directory-prefix='+directory
                        print line
                        os.system(line)
                        agnkey.agnsqldef.updatevalue('obslog','tarfile',_tarfile,track,connection='agnkey',namefile0='tracknumber')
                    else:
                        print 'file already there'
                else:   print 'request number not defined'
        if str(track)=='53874':
           raw_input('gogon')
##########################################################################################
