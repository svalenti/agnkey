def deg2HMS(ra='', dec='', round=False):
      import string
      RA, DEC= '', ''
      if dec:
          if string.count(str(dec),':')==2:
              dec00=string.split(dec,':')
              dec0,dec1,dec2=float(dec00[0]),float(dec00[1]),float(dec00[2])
              if '-' in str(dec0):       DEC=(-1)*((dec2/60.+dec1)/60.+((-1)*dec0))
              else:                      DEC=(dec2/60.+dec1)/60.+dec0
          else:
              if str(dec)[0]=='-':      dec0=(-1)*abs(int(dec))
              else:                     dec0=abs(int(dec))
              dec1=int((abs(dec)-abs(dec0))*(60))
              dec2=((((abs(dec))-abs(dec0))*60)-abs(dec1))*60
              DEC='00'[len(str(dec0)):]+str(dec0)+':'+'00'[len(str(dec1)):]+str(dec1)+':'+'00'[len(str(int(dec2))):]+str(dec2)
      if ra:
          if string.count(str(ra),':')==2:
              ra00=string.split(ra,':')
              ra0,ra1,ra2=float(ra00[0]),float(ra00[1]),float(ra00[2])
              RA=((ra2/60.+ra1)/60.+ra0)*15.
          else:
              ra0=int(ra/15.)
              ra1=int(((ra/15.)-ra0)*(60))
              ra2=((((ra/15.)-ra0)*60)-ra1)*60
              RA='00'[len(str(ra0)):]+str(ra0)+':'+'00'[len(str(ra1)):]+str(ra1)+':'+'00'[len(str(int(ra2))):]+str(ra2)
      if ra and dec:          return RA, DEC
      else:                   return RA or DEC

def onkeypress(event):
    import matplotlib.pyplot as plt
    from numpy import polyfit,polyval,argmin,sqrt,mean,array,std,median
    global idd,_col,_dmag,testo,lines,sss,f,fixcol,aa,bb,sigmaa,sigmab
    xdata,ydata = event.xdata,event.ydata
    dist = sqrt((xdata-_col)**2+(ydata-_dmag)**2)
    ii = argmin(dist)
    if event.key == 'd' :
        __col,__dmag = _col.tolist(),_dmag.tolist()
        plt.plot(_col[ii],_dmag[ii],'xk',ms=25)
        del __col[ii],__dmag[ii]
        _col,_dmag = array(__col),array(__dmag)

    idd = range(len(_col))
    _fixcol=fixcol
    if len(_col[idd])==1:  _fixcol=0.0
    else:   _fixcol=fixcol

    if _fixcol=='':
        pol = polyfit(_col,_dmag,1,full=True)  ###
        aa = pol[0][1]
        bb = pol[0][0]
        if len(_col[idd])>2:
            sigmae = sqrt(pol[1][0]/(len(idd)  -2))
            sigmaa = sigmae*sqrt(1./len(idd)+(mean(_col[idd])**2)/sum((_col[idd]-\
                                                                           mean(_col[idd]))**2))
            sigmab = sigmae*sqrt(1/sum((_col[idd]-mean(_col[idd]))**2))
        else:
            sigmaa=0.0
            sigmab=0.0
    else:
#        aa=mean(array(_dmag[idd])-array(_col[idd])*float(_fixcol))
        aa=median(array(_dmag[idd])-array(_col[idd])*float(_fixcol))
        bb=_fixcol
        sigmaa=std(abs(aa-(array(_dmag[idd])-array(_col[idd])*float(_fixcol))))
        sigmab=0.0

    xx = [min(_col)-.1,max(_col)+.1]
    yy = polyval([bb,aa],xx)                ###
    lines.pop(0).remove()
    lines = plt.plot(xx,yy,'r-')
    plt.ylim(min(_dmag)-.2,max(_dmag)+.2)
    plt.xlabel(sss)
    plt.title(f)

    try:
        plt.setp(testo,text='%5.3f + %s* %5.3f [%4.3f  %4.3f]'%\
                     (aa,sss,bb,sigmaa,sigmab))
    except:
        plt.setp(testo,text='%5.3f + %s* %5.3f [%4.3f  %4.3f]'%\
                     (aa,sss,bb,sigmaa,sigmab))

def onclick(event):
    import matplotlib.pyplot as plt
    from numpy import polyfit,polyval,argmin,sqrt,mean,array,std,median
    global idd,_col,_dmag,testo,lines,aa,bb,sss,f,fixcol,sigmaa,sigmab
    xdata,ydata = event.xdata,event.ydata
    dist = sqrt((xdata-_col)**2+(ydata-_dmag)**2)
    ii = argmin(dist)
    if event.button == 2:
        if ii not in idd: idd.append(ii)
    if event.button == 1:  
        if ii in idd: idd.remove(ii)

    nonincl = []
    for i in range(len(_col)):
        if i not in idd: nonincl.append(i)

#    _fixcol=fixcol
    if len(_col[idd])==1:  _fixcol=0.0
    else:   _fixcol=fixcol

    if _fixcol=='':
        pol = polyfit(_col[idd],_dmag[idd],1,full=True) ###
        aa=pol[0][1]
        bb=pol[0][0]
        if len(idd)>2:
            sigmae = sqrt(pol[1][0]/(len(idd)  -2))
            sigmaa = sigmae*sqrt(1./len(idd)+(mean(_col[idd])**2)/sum((_col[idd]-\
                                                                           mean(_col[idd]))**2))
            sigmab = sigmae*sqrt(1/sum((_col[idd]-mean(_col[idd]))**2))
        else:
            sigmaa=0.0
            sigmab=0.0
    else:
#        aa=mean(_dmag[idd]-_col[idd]*float(_fixcol))
        aa=median(_dmag[idd]-_col[idd]*float(_fixcol))
        bb=_fixcol
        sigmaa=std(abs(aa-(array(_dmag[idd])-array(_col[idd])*float(_fixcol))))
        sigmab=0.0

    xx = [min(_col)-.1,max(_col)+.1]
    yy = polyval([bb,aa],xx)                ###

    plt.plot(_col,_dmag,'ok')
    plt.plot(_col[nonincl],_dmag[nonincl],'ow')
    lines.pop(0).remove()
    lines = plt.plot(xx,yy,'r-')
    plt.ylim(min(_dmag)-.2,max(_dmag)+.2)
    plt.xlabel(sss)
    plt.title(f)
    try:
        plt.setp(testo,text='%5.3f + %s* %5.3f [%4.3f  %4.3f]'%\
                     (aa,sss,bb,sigmaa,sigmab))
    except:
        plt.setp(testo,text='%5.3f + %s* %5.3f [%4.3f  %4,3f]'%\
                     (aa,sss,bb,sigmaa,sigmab))


def absphot(img,_field,_catalogue,_fix,_color,rejection,_interactive,_type='fit',redo=False,show=False,cutmag=-1,database='dataredulco',_calib='sloan'):

    try:       from astropy.io import fits as pyfits
    except:    import pyfits

    import agnkey
    import math
    import sys,re,string,os
    from agnkey.util import readkey3, readhdr
    from numpy import array, compress, zeros, median, std, asarray, isfinite,mean
    from pyraf import iraf
    if show:
          from pylab import ion,plot,draw,clf
          import time
    iraf.noao(_doprint=0)
    iraf.digiphot(_doprint=0)
    iraf.daophot(_doprint=0)
    iraf.images(_doprint=0)
    iraf.imcoords(_doprint=0)
    iraf.proto(_doprint=0)
    t = pyfits.open(img)
    tbdata = t[1].data
    hdr2=t[1].header
    hdr=agnkey.util.readhdr(img)
    _cat=readkey3(hdr,'catalog')
    _telescope=agnkey.util.readkey3(hdr,'telescop')
    _instrume=agnkey.util.readkey3(hdr,'instrume')
    _filter=agnkey.util.readkey3(hdr,'filter')
    _airmass=agnkey.util.readkey3(hdr,'airmass')
    _exptime=agnkey.util.readkey3(hdr,'exptime')
    _date=agnkey.util.readkey3(hdr,'date-obs')
    _object=agnkey.util.readkey3(hdr,'object')
    _ra=agnkey.util.readkey3(hdr,'RA')
    _dec=agnkey.util.readkey3(hdr,'DEC')
    if _telescope in ['lsc','1m0-04','1m0-05','1m0-09']:
        kk=agnkey.sites.extintion('ctio')
    elif _telescope in ['elp','1m0-08']:
        kk=agnkey.sites.extintion('mcdonald')
    elif _telescope in ['cpt','1m0-12','1m0-10','1m0-13']:
        kk=agnkey.sites.extintion('southafrica')
    elif _telescope in ['ftn','Faulkes Telescope North']:
        kk=agnkey.sites.extintion('mauna')
    elif _telescope in ['1m0-03','1m0-11','coj','fts','Faulkes Telescope South']:
        kk=agnkey.sites.extintion('siding')

    if _calib=='apass':
        _field='apass'
    if _field=='apass':
        _calib='apass'
    if _calib=='apass' and not _catalogue:
        sys.exit('ERROR: apass option for field or calib is valid only when apass catalogue is also provided')

    if _calib not in ['sloan','sloanprime','natural','apass','']:
        colorefisso=agnkey.sites.colfix(_instrume)
    else:
        colorefisso=agnkey.sites.colfix(_instrume,_calib)

    if _cat and not redo:
        print 'already calibrated'
    else:
     try:
           agnkey.agnsqldef.updatevalue(database,'zcat','X',string.split(re.sub('.sn2.fits','.fits',img),'/')[-1])
           if os.path.isfile(string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1]):
                 agnkey.agnsqldef.updatevalue(database,'zcat','X',string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1])
     except: print 'module mysqldef not found'

     column=agnkey.util.makecatalogue2([img])[_filter][img]

     rasex=array(column['ra0'],float)
     decsex=array(column['dec0'],float)
     if _type=='fit':
        magsex=array(column['smagf'],float)
        magerrsex=array(column['smagerrf'],float)
     elif _type=='ph':
        magsex=array(column['magp3'],float)
        magerrsex=array(column['merrp3'],float)
     else: sys.exit(_type+' not valid (ph or fit)')
     
     if not cutmag: cutmag=99
     #else: cutmag= cutmag-2.5*math.log10(float(_exptime))
     if len(compress( array(magsex) < float(cutmag) , magsex)) < 5 : cutmag=99  # not cut if only few object
     rasex     = compress(array(magsex,float)<=cutmag,rasex)
     decsex    = compress(array(magsex,float)<=cutmag,decsex)
     magerrsex = compress(array(magsex,float)<=cutmag,magerrsex)
     magsex    = compress(array(magsex,float)<=cutmag,array(magsex))

     if _interactive:
        iraf.set(stdimage='imt1024')
        iraf.display(re.sub('.sn2','',img),1,fill=True,Stdout=1)
        vector=[]
        for i in range(0,len(rasex)):
            vector.append(str(rasex[i])+' '+str(decsex[i]))
        xy = iraf.wcsctran('STDIN',output="STDOUT",Stdin=vector,Stdout=1,image=img,inwcs='world',units='degrees degrees',outwcs='logical',\
                               formats='%10.1f %10.1f',verbose='yes')[3:]
        iraf.tvmark(1,'STDIN',Stdin=list(xy),mark="circle",number='yes',label='no',radii=10,nxoffse=5,nyoffse=5,color=207,txsize=2)
        print 'yelow circles sextractor'
        
     if _catalogue:
        ######## use external catalogue
        if _catalogue[0]=='/':   stdcooC=agnkey.agnastrodef.readtxt(_catalogue)
        else:                   stdcooC=agnkey.agnastrodef.readtxt(agnkey.__path__[0]+'/standard/cat/'+_catalogue)
        rastdC,decstdL=array(stdcooC['ra'],float),array(stdcooC['dec'],float)
        agnkey.util.delete('tmp.stdL.pix')
        colonne=str(stdcooC['rapos'])+'   '+str(stdcooC['decpos'])
        if _catalogue[0]=='/': 
            iraf.wcsctran(_catalogue,'tmp.stdL.pix',img,inwcs='world',units='degrees degrees',outwcs='logical',\
                          columns=colonne,formats='%10.1f %10.1f',verbose='no')
        else:
            iraf.wcsctran(agnkey.__path__[0]+'/standard/cat/'+_catalogue,'tmp.stdL.pix',img,inwcs='world',units='degrees degrees',outwcs='logical',\
                          columns=colonne,formats='%10.1f %10.1f',verbose='no')
        standardpixC=agnkey.agnastrodef.readtxt('tmp.stdL.pix')
        if _interactive:
              vector=[k+' '+v for k,v in  zip(standardpixC['ra'],standardpixC['dec'])]
              iraf.tvmark(1,'STDIN',Stdin=list(vector),mark="circle",number='yes',label='no',radii=10,nxoffse=5,nyoffse=5,color=204,txsize=2)
              print 'yellow circles sextractor'

        xstdC=standardpixC['ra']
        ystdC=standardpixC['dec']
        idstdC=standardpixC['id']
        xstdC=compress((array(xstdC,float)<readkey3(hdr,'XDIM'))&(array(xstdC,float)>0)&(array(ystdC,float)>0)&(array(ystdC,float)<readkey3(hdr,'YDIM')),xstdC)
        xstdL=xstdLL=xstdS=xstdC
        standardpixL=standardpixLL=standardpixS=standardpixC
        stdcooL=stdcooLL=stdcooS=stdcooC
     else:
        ######## check if it is landolt field
        stdcooL=agnkey.agnastrodef.readtxt(agnkey.__path__[0]+'/standard/cat/landolt.cat')
        rastdL,decstdL=array(stdcooL['ra'],float),array(stdcooL['dec'],float)
        agnkey.util.delete('tmp.stdL.pix')
        iraf.wcsctran(agnkey.__path__[0]+'/standard/cat/landolt.cat','tmp.stdL.pix',img,inwcs='world',units='degrees degrees',outwcs='logical',\
                          columns='1 2',formats='%10.1f %10.1f',verbose='no')
        standardpixL=agnkey.agnastrodef.readtxt('tmp.stdL.pix')
        if _interactive:
              vector=[k+' '+v for k,v in  zip(standardpixL['ra'],standardpixL['dec'])]
              iraf.tvmark(1,'STDIN',Stdin=list(vector),mark="circle",number='yes',label='no',radii=10,nxoffse=5,nyoffse=5,color=204,txsize=2)
              #iraf.tvmark(1,'tmp.stdL.pix',mark="circle",number='yes',label='no',radii=8,nxoffse=5,nyoffse=5,color=204,txsize=2)
              print 'yellow circles sextractor'

        xstdL=standardpixL['ra']
        ystdL=standardpixL['dec']
        idstdL=standardpixL['id']
        xstdL=compress((array(xstdL,float)<readkey3(hdr,'XDIM'))&(array(xstdL,float)>0)&(array(ystdL,float)>0)&(array(ystdL,float)<readkey3(hdr,'YDIM')),xstdL)

        ######## check if it is Stetson field
        stdcooLL=agnkey.agnastrodef.readtxt(agnkey.__path__[0]+'/standard/cat/StetsonCat.dat')
        ww=asarray([i for i in range(len(stdcooLL['ra'])) if ( abs(float(stdcooLL['ra'][i])-float(_ra))<.2 and  abs(float(stdcooLL['dec'][i])-_dec)<.2    )])
        if len(ww)>0:
            for hh in stdcooLL.keys(): 
                if type(stdcooLL[hh])!=int:
                    if hh not in ['id','ra','dec']:
                        stdcooLL[hh]=array(array(stdcooLL[hh])[ww],float)
                    else:
                        stdcooLL[hh]=array(stdcooLL[hh])[ww]
        lll=[]
        for i in range(0,len(stdcooLL['ra'])): lll.append(stdcooLL['ra'][i]+' '+stdcooLL['dec'][i])

        rastdLL,decstdLL=array(stdcooLL['ra'],float),array(stdcooLL['dec'],float)
        agnkey.util.delete('tmp.stdLL.pix')
        iraf.wcsctran('STDIN','tmp.stdLL.pix',img,inwcs='world',Stdin=lll,units='degrees degrees',outwcs='logical',\
                          columns='1 2',formats='%10.1f %10.1f',verbose='no')

        standardpixLL={}
        for ii in stdcooLL.keys(): standardpixLL[ii]=stdcooLL[ii]
        standardpixLL['ra']=array(iraf.proto.fields('tmp.stdLL.pix',fields='1',Stdout=1),float) #standardpixLL['ra']
        standardpixLL['dec']=array(iraf.proto.fields('tmp.stdLL.pix',fields='2',Stdout=1),float) #standardpixLL['dec']
        xstdLL=array(iraf.proto.fields('tmp.stdLL.pix',fields='1',Stdout=1),float) #standardpixLL['ra']
        ystdLL=array(iraf.proto.fields('tmp.stdLL.pix',fields='2',Stdout=1),float) #standardpixLL['dec']
        idstdLL=standardpixLL['id']

        if _interactive:
              vector=[k+' '+v for k,v in  zip(standardpixLL['ra'],standardpixLL['dec'])]
              iraf.tvmark(1,'STDIN',Stdin=list(vector),mark="circle",number='yes',label='no',radii=10,nxoffse=5,nyoffse=5,color=204,txsize=2)
              #iraf.tvmark(1,'tmp.stdLL.pix',mark="cross",number='yes',label='no',radii=8,nxoffse=5,nyoffse=5,color=204,txsize=2)
              print 'red crosses Stetson'

        xstdLL=compress((array(xstdLL,float)<readkey3(hdr,'XDIM'))&(array(xstdLL,float)>0)&(array(ystdLL,float)>0)&(array(ystdLL,float)<readkey3(hdr,'YDIM')),xstdLL)
        ######## check if it is sloan field
        magsel0,magsel1=12,18
        _ids=agnkey.agnastrodef.sloan2file(_ra,_dec,20,float(magsel0),float(magsel1),'_tmpsloan.cat')
        ascifile='_tmpsloan.cat'
        stdcooS=agnkey.agnastrodef.readtxt(ascifile)
        rastdS,decstdS=array(stdcooS['ra'],float),array(stdcooS['dec'],float)
        agnkey.util.delete('tmp.stdS.pix')
        iraf.wcsctran(ascifile,'tmp.stdS.pix',img,inwcs='world',units='degrees degrees',outwcs='logical',columns='1 2',formats='%10.1f %10.1f',verbose='no')
        standardpixS=agnkey.agnastrodef.readtxt('tmp.stdS.pix')
        if _interactive:
              vector=[k+' '+v for k,v in  zip(standardpixS['ra'],standardpixS['dec'])]
              iraf.tvmark(1,'STDIN',Stdin=list(vector),mark="circle",number='yes',label='no',radii=10,nxoffse=5,nyoffse=5,color=204,txsize=2)
              #iraf.tvmark(1,'tmp.stdS.pix',mark="cross",number='yes',label='no',radii=8,nxoffse=5,nyoffse=5,color=205,txsize=2)
              print 'green cross sloan'

        xstdS=standardpixS['ra']
        ystdS=standardpixS['dec']
        idstdS=standardpixS['id']
        xstdS=compress((array(xstdS,float)<readkey3(hdr,'XDIM'))&(array(xstdS,float)>0)&(array(ystdS,float)>0)&(array(ystdS,float)<readkey3(hdr,'YDIM')),xstdS)
        ##############################################3
     if not _catalogue and len(xstdLL)>0:
             xstdL=xstdLL
             standardpixL=standardpixLL
             stdcooL=stdcooLL

     if _calib=='apass':
           filters={'ip':'i','gp':'g','rp':'r','SDSS-G':'g','SDSS-R':'r','SDSS-I':'i','B':'B', 'V':'V', 'R':'R', 'I':'I','Bessell-B':'B','Bessell-V':'V'}
           if _color:
                 colors=agnkey.agnloopdef.chosecolor(_color,False,'apass')
                 if not colors:             colors={'B':['BV'],'V':['BV','Vg'],'g':['Vg','gr'],'r':['gr','ri'],'i':['ri']}
           else:
                 colors={'B':['BV'],'V':['BV','Vg'],'g':['Vg','gr'],'r':['gr','ri'],'i':['ri']}
           standardpix=standardpixL
           stdcoo=stdcooL
     else:
       if _filter in ['U', 'B', 'V', 'R','I','Bessell-B','Bessell-V','Bessell-R','Bessell-I']:
        filters={'U':'U', 'B':'B', 'V':'V', 'R':'R', 'I':'I','Bessell-B':'B','Bessell-V':'V','Bessell-R':'R','Bessell-I':'I'}
        if _color:
            colors=agnkey.agnloopdef.chosecolor(_color,False)
            if not colors:             colors={'U':['UB'],'B':['UB','BV'],'V':['BV','VR'],'R':['VR','RI'],'I':['RI']}
        else:
            colors={'U':['UB'],'B':['UB','BV'],'V':['BV','VR'],'R':['VR','RI'],'I':['RI']}
        if _field=='sloan':
                standardpix,stdcoo={'ra':[9999],'dec':[9999],'id':[1]},{'ra':[9999],'dec':[9999]}
                print 'filters and field selected do not match'
        else:
            _field='landolt'
            if len(xstdL)>=1:
                    standardpix=standardpixL
                    stdcoo=stdcooL
                    if not _catalogue:
                          if len(xstdLL)>0: _catalogue='StetsonCat.dat'
                          else:             _catalogue='landolt.dat'
            elif len(xstdS)>=1:
                if not _catalogue:  _catalogue='sdss8'  
                standardpix=standardpixS
                stdcoo=stdcooS
                stdcoo=agnkey.agnastrodef.transformsloanlandolt(stdcoo)
                if not _catalogue:  _catalogue='sdss8' 
                print '\n### transform sloan in landolt'
            else:
                print 'landolt, but catalogue not found'
                standardpix,stdcoo={'ra':[9999],'dec':[9999],'id':[1]},{'ra':[9999],'dec':[9999]}
       elif _filter in  ['up','gp','rp','ip','zs','SDSS-G','SDSS-R','SDSS-I','Pan-Starrs-Z']: 
        filters={'up':'u','ip':'i','gp':'g','rp':'r','zs':'z','SDSS-G':'g','SDSS-R':'r','SDSS-I':'i','Pan-Starrs-Z':'z'}
        if _color:
            colors=agnkey.agnloopdef.chosecolor(_color,False)
            if not colors:             colors={'i':['ri','iz'],'r':['gr','ri'],'g':['ug','gr'],'z':['iz'],'u':['ug']}
        else:
            colors={'i':['ri','iz'],'r':['gr','ri'],'g':['ug','gr'],'z':['iz'],'u':['ug']}
        if _field=='landolt':   
                standardpix,stdcoo={'ra':[9999],'dec':[9999],'id':[1]},{'ra':[9999],'dec':[9999]}
                print 'filters and field selected do not match'
        else:
            _field='sloan'
            if len(xstdS)>=1:
                if not _catalogue:  _catalogue='sdss8' 
                standardpix=standardpixS
                stdcoo=stdcooS
            elif len(xstdL)>=1:
                standardpix=standardpixL
                stdcoo=stdcooL
                stdcoo=agnkey.agnastrodef.transformlandoltsloan(stdcoo)
                if not _catalogue:  _catalogue='landolt.dat' 
                print '\n### transform landolt to sloan'
            else:
                print 'sloan, but not in the sdss footprint'
                standardpix,stdcoo={'ra':[9999],'dec':[9999],'id':[1]},{'ra':[9999],'dec':[9999]}        

     xstd=standardpix['ra']
     ystd=standardpix['dec']
     idstd=standardpix['id']
     rastd,decstd=array(stdcoo['ra'],float),array(stdcoo['dec'],float)
     xstd0=compress((array(xstd,float)<readkey3(hdr,'XDIM'))&(array(xstd,float)>0)&(array(ystd,float)>0)&(array(ystd,float)<readkey3(hdr,'YDIM')),xstd)

     if len(xstd0)>1:  ########   go only if standard stars are in the field  ##########
        magstd0={}
        airmass0={}
        result={}
        fileph={}
        print '\n###  standard field: '+str(_field)
        ystd0=compress((array(xstd,float)<readkey3(hdr,'XDIM'))&(array(xstd,float)>0)&(array(ystd,float)>0)\
                               &(array(ystd,float)<readkey3(hdr,'YDIM')),ystd)
        rastd0=compress((array(xstd,float)<readkey3(hdr,'XDIM'))&(array(xstd,float)>0)&(array(ystd,float)>0)\
                                &(array(ystd,float)<readkey3(hdr,'YDIM')),rastd)
        decstd0=compress((array(xstd,float)<readkey3(hdr,'XDIM'))&(array(xstd,float)>0)&(array(ystd,float)>0)\
                                 &(array(ystd,float)<readkey3(hdr,'YDIM')),decstd)
        idstd0=compress((array(xstd,float)<readkey3(hdr,'XDIM'))&(array(xstd,float)>0)&(array(ystd,float)>0)\
                                 &(array(ystd,float)<readkey3(hdr,'YDIM')),idstd)
        stdcoo0={}
        for key in stdcoo.keys():
              if key in 'ugrizUBVRI':
                    stdcoo0[key]=compress((array(xstd,float)<readkey3(hdr,'XDIM'))&(array(xstd,float)>0)&(array(ystd,float)>0)\
                                                &(array(ystd,float)<readkey3(hdr,'YDIM')),stdcoo[key])
        ###############################################################
        #               pos0 = standard                          pos1 = sextractor
        distvec,pos0,pos1=agnkey.agnastrodef.crossmatch(array(rastd0),array(decstd0),array(rasex),array(decsex),5)
        for key in stdcoo0.keys():            stdcoo0[key]=stdcoo0[key][pos0]
        rastd0=rastd0[pos0]
        decstd0=decstd0[pos0]
        idstd0=idstd0[pos0]
        rasex=rasex[pos1]
        decsex=decsex[pos1]
        # after change in may 2013 mag in sn2.fits file are already at 1s
        magsex=magsex[pos1]-kk[filters[_filter]]*float(_airmass)  #   - K x airmass
#        magsex=magsex[pos1]+2.5*math.log10(float(_exptime))-kk[filters[_filter]]*float(_airmass)  #  mag    exptime      - K x airmass
#################################################################################
        if _field=='landolt':
            print '\n###  landolt system'
            for _filtlandolt in 'UBVRI':
                if _filtlandolt==filters[_filter]:  airmass0[_filtlandolt]=  0 #_airmass
                else: airmass0[_filtlandolt]= 0
                magstd0[_filtlandolt]=stdcoo0[_filtlandolt]
            fileph['mU']=zeros(len(rastd0))+999
            fileph['mB']=zeros(len(rastd0))+999
            fileph['mV']=zeros(len(rastd0))+999
            fileph['mR']=zeros(len(rastd0))+999
            fileph['mI']=zeros(len(rastd0))+999
            fileph['V']=magstd0['V']
            fileph['BV']=array(array(magstd0['B'],float)-array(magstd0['V'],float),str)
            fileph['UB']=array(array(magstd0['U'],float)-array(magstd0['B'],float),str)
            fileph['VR']=array(array(magstd0['V'],float)-array(magstd0['R'],float),str)
            fileph['RI']=array(array(magstd0['R'],float)-array(magstd0['I'],float),str)
        elif _field=='sloan':
            for _filtsloan in 'ugriz':
                if _filtsloan==filters[_filter]:  airmass0[_filtsloan]= 0   # _airmass
                else: airmass0[_filtsloan]=0
                magstd0[_filtsloan]=stdcoo0[_filtsloan]
            fileph['mu']=zeros(len(rastd0))+999
            fileph['mg']=zeros(len(rastd0))+999
            fileph['mr']=zeros(len(rastd0))+999
            fileph['mi']=zeros(len(rastd0))+999
            fileph['mz']=zeros(len(rastd0))+999
            fileph['r']=magstd0['r']
            fileph['gr']=array(array(magstd0['g'],float)-array(magstd0['r'],float),str)
            fileph['ri']=array(array(magstd0['r'],float)-array(magstd0['i'],float),str)
            fileph['ug']=array(array(magstd0['u'],float)-array(magstd0['g'],float),str)
            fileph['iz']=array(array(magstd0['i'],float)-array(magstd0['z'],float),str)
        elif _field=='apass':
            for _filtsloan in 'BVgri':
                if _filtsloan==filters[_filter]:  airmass0[_filtsloan]= 0   # _airmass
                else: airmass0[_filtsloan]=0
                magstd0[_filtsloan]=stdcoo0[_filtsloan]
            fileph['mB']=zeros(len(rastd0))+999
            fileph['mV']=zeros(len(rastd0))+999
            fileph['mg']=zeros(len(rastd0))+999
            fileph['mr']=zeros(len(rastd0))+999
            fileph['mi']=zeros(len(rastd0))+999
            fileph['V']=magstd0['V']
            fileph['BV']=array(array(magstd0['B'],float)-array(magstd0['V'],float),str)
            fileph['gr']=array(array(magstd0['g'],float)-array(magstd0['r'],float),str)
            fileph['ri']=array(array(magstd0['r'],float)-array(magstd0['i'],float),str)
            fileph['Vg']=array(array(magstd0['V'],float)-array(magstd0['g'],float),str)
########################################################################################
        zero=[]
        magcor=[]
        fil = open(re.sub('.fits','.ph',img),'w')
        fil.write(str(_instrume)+' '+str(_date)+'\n')
        fil.write('*** '+_object+' '+str(len(magsex))+'\n')
        if _field=='landolt':
            fil.write('%6.6s\t%6.6s\t%6.6s\t%6.6s\t%6.6s\n' % (str(1),str(1),str(1),str(1),str(1)))  # exptime
            fil.write('%6.6s\t%6.6s\t%6.6s\t%6.6s\t%6.6s\n' % (str(airmass0['U']),str(airmass0['B']),str(airmass0['V']),str(airmass0['R']),str(airmass0['I'])))
        elif _field=='sloan':
            fil.write('%6.6s\t%6.6s\t%6.6s\t%6.6s\t%6.6s\n' % (str(1),str(1),str(1),str(1),str(1)))  # exptime
            fil.write('%6.6s\t%6.6s\t%6.6s\t%6.6s\t%6.6s\n' % (str(airmass0['u']),str(airmass0['g']),str(airmass0['r']),str(airmass0['i']),str(airmass0['z'])))
        elif _field=='apass':
            fil.write('%6.6s\t%6.6s\t%6.6s\t%6.6s\t%6.6s\n' % (str(1),str(1),str(1),str(1),str(1)))  # exptime
            fil.write('%6.6s\t%6.6s\t%6.6s\t%6.6s\t%6.6s\n' % (str(airmass0['B']),str(airmass0['V']),str(airmass0['g']),str(airmass0['r']),str(airmass0['i'])))
        for i in range(0,len(magsex)): 
            fileph['m'+filters[_filter]][i]=magsex[i]    #  instrumental mangitude of std in pos0[i]
            if _field=='landolt':
                stringastandard='%12.12s\t%7.7s\t%7.7s\t%7.7s\t%7.7s\t%7.7s' % (idstd0[i],fileph['V'][i],fileph['BV'][i],fileph['UB'][i],\
                                                                                fileph['VR'][i],fileph['RI'][i])
                fil.write('%7.7s\t%7.7s\t%7.7s\t%7.7s\t%7.7s\t%60.60s\n' \
                              % (str(fileph['mU'][i]),str(fileph['mB'][i]),str(fileph['mV'][i]),str(fileph['mR'][i]),str(fileph['mI'][i]),str(stringastandard)))
            elif _field=='sloan':
                stringastandard='%12.12s\t%7.7s\t%7.7s\t%7.7s\t%7.7s\t%7.7s' % (idstd0[i],fileph['r'][i],fileph['gr'][i],fileph['ug'][i],\
                                                                                fileph['ri'][i],fileph['iz'][i])
                fil.write('%7.7s\t%7.7s\t%7.7s\t%7.7s\t%7.7s\t%60.60s\n' \
                              % (str(fileph['mu'][i]),str(fileph['mg'][i]),str(fileph['mr'][i]),str(fileph['mi'][i]),str(fileph['mz'][i]),str(stringastandard)))
            elif _field=='apass':
                stringastandard='%12.12s\t%7.7s\t%7.7s\t%7.7s\t%7.7s\t%7.7s' % (idstd0[i],fileph['V'][i],fileph['BV'][i],fileph['Vg'][i],\
                                                                                fileph['gr'][i],fileph['ri'][i])
                fil.write('%7.7s\t%7.7s\t%7.7s\t%7.7s\t%7.7s\t%60.60s\n' \
                              % (str(fileph['mB'][i]),str(fileph['mV'][i]),str(fileph['mg'][i]),str(fileph['mr'][i]),str(fileph['mi'][i]),str(stringastandard)))
            zero.append(float(float(magstd0[filters[_filter]][i]))-float(magsex[i]))
            magcor.append(magsex[i])
        fil.close()
        magstd0=agnkey.agnabsphotdef.transform2natural(_instrume,magstd0,_field)

        magsex1=magsex+kk[filters[_filter]]*float(_airmass)  #   add again extinction for natural zero point comparison

        media,mediaerr,mag2,data2=agnkey.agnabsphotdef.zeropoint2(array(magstd0[filters[_filter]],float),array(magsex1,float),10,2,show)

#        if float(_cutmag)!=99:
#              print 'cut mag '+str(_cutmag)
#              xx=np.compress(mag<_cutmag,xx)
#              mag=np.compress(mag<_cutmag,mag)
#              data=np.array(xx-mag)
#              array(magstd0[filters[_filter]],float)
#              array(magsex1,float)
#              ZZcut,sigmacut,mediancut=zeronew(ZZ,maxiter=10,nn=5,verbose=False,show)

        if media!=9999: 
              agnkey.agnsqldef.updatevalue('dataredulco','ZPN',media,string.split(re.sub('.sn2.fits','.fits',img),'/')[-1],'agnkey','namefile')
              agnkey.agnsqldef.updatevalue('dataredulco','ZPNERR',mediaerr,string.split(re.sub('.sn2.fits','.fits',img),'/')[-1],'agnkey','namefile')
              agnkey.agnsqldef.updatevalue('dataredulco','ZPNNUM',len(data2),string.split(re.sub('.sn2.fits','.fits',img),'/')[-1],'agnkey','namefile')

#        if show:
#              media,mediaerr,mag2,data2=agnkey.agnabsphotdef.zeropoint(zero,magcor,10,2,True)
#              print media,mediaerr,len(data2)
#              raw_input('go on ')

        colorvec=colors[filters[_filter]]
        for col in colorvec:
            col0=magstd0[col[0]] 
            col1=magstd0[col[1]]
            colstd0=array(col0,float)-array(col1,float)
            ################## sex  ######################
            colore=[]
            for i in range(0,len(pos1)):   colore.append(colstd0[i])

            colore1=compress(abs(array(zero))<50,array(colore))
            zero1=compress(abs(array(zero))<50,array(zero))
            zero2=compress(abs(array(colore1))<2,array(zero1))
            colore2=compress(abs(array(colore1))<2,array(colore1))
            if _fix: fisso=colorefisso[filters[_filter]+col]
            else: fisso=''

            if len(colore2)==0:
                print 'no calibration, '+_filter+' '+_field
                b,a,sa,sb=9999,9999,0,0
            else:
                if _interactive:    a,sa,b,sb=fitcol(colore2,zero2,_filter,col,fisso)
                else:               a,sa,b,sb=fitcol2(colore2,zero2,_filter,col,fisso,show,rejection)

            print a,sa,b,sb
            result[filters[_filter]+col]=[a,sa,b,sb]
        if result:
            print '\n### zeropoint ..... done at airmass 0'
            if _catalogue:
                agnkey.util.updateheader(img,0,{'CATALOG':[str(string.split(_catalogue,'/')[-1]),'catalogue source']})
            stringa=''
            for ll in result:
                for kk in range(0,len(result[ll])):
                                    if not isfinite(result[ll][kk]): result[ll][kk]=0.0 
                valore='%3.3s %6.6s %6.6s  %6.6s  %6.6s' %  (str(ll),str(result[ll][0]),str(result[ll][2]),str(result[ll][1]),str(result[ll][3]))
                print '### ',valore
                agnkey.util.updateheader(img,0,{'zp'+ll:[str(valore),'a b sa sb in y=a+bx']})
                if ll[0]==ll[2]: 
                      num=2
                elif ll[0]==ll[1]: 
                      num=1
                else: 
                      sys.exit('somthing wrong with color '+ll)
                try:
                    print 'zcol'+str(num),ll[1:],string.split(re.sub('.sn2.fits','.fits',img),'/')[-1]
                    agnkey.agnsqldef.updatevalue(database,'zcol'+str(num),ll[1:],string.split(re.sub('.sn2.fits','.fits',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue(database,'z'+str(num),result[ll][0],string.split(re.sub('.sn2.fits','.fits',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue(database,'c'+str(num),result[ll][2],string.split(re.sub('.sn2.fits','.fits',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue(database,'dz'+str(num),result[ll][1],string.split(re.sub('.sn2.fits','.fits',img),'/')[-1])
                    agnkey.agnsqldef.updatevalue(database,'dc'+str(num),result[ll][3],string.split(re.sub('.sn2.fits','.fits',img),'/')[-1])
                    if os.path.isfile(string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1]):
                          agnkey.agnsqldef.updatevalue(database,'zcol'+str(num),ll[1:],string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1])
                          agnkey.agnsqldef.updatevalue(database,'z'+str(num),result[ll][0],string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1])
                          agnkey.agnsqldef.updatevalue(database,'c'+str(num),result[ll][2],string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1])
                          agnkey.agnsqldef.updatevalue(database,'dz'+str(num),result[ll][1],string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1])
                          agnkey.agnsqldef.updatevalue(database,'dc'+str(num),result[ll][3],string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1])
                    if result[ll][0]!=9999:
                          agnkey.agnsqldef.updatevalue(database,'zcat',string.split(_catalogue,'/')[-1],string.split(re.sub('.sn2.fits','.fits',img),'/')[-1])
                          if os.path.isfile(string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1]):
                                agnkey.agnsqldef.updatevalue(database,'zcat',string.split(_catalogue,'/')[-1],string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1])
                    else:
                        agnkey.agnsqldef.updatevalue(database,'zcat','X',string.split(re.sub('.sn2.fits','.fits',img),'/')[-1])
                        if os.path.isfile(string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1]):
                              agnkey.agnsqldef.updatevalue(database,'zcat','X',string.split(re.sub('.diff.sn2.fits','.fits',img),'/')[-1])
                except: print 'module mysqldef not found'
                
#################################################################

def fitcol(col,dmag,band,color,fissa=''):
    import matplotlib.pyplot as plt 
    from numpy import polyfit,polyval,argmin,sqrt,mean,array,std,median
    global idd,_col,_dmag,testo,lines,pol,sss,f,fixcol,sigmaa,sigmab,aa,bb
    plt.ion()
    fig = plt.figure()
    _dmag = dmag[:]
    _col  = col[:]
    sss=band
    f=color
    fixcol=fissa
    _col = array(_col)
    _dmag = array(_dmag)
    idd = range(len(_col))
    plt.plot(_col,_dmag,'ok')

    _fixcol=fixcol
    if len(_col[idd])==1:  _fixcol=0.0
    else:   _fixcol=fixcol

    if _fixcol=='':
        pol = polyfit(_col[idd],_dmag[idd],1,full=True) ###
        aa=pol[0][1]
        bb=pol[0][0]

        if len(idd)>2:
            sigmae = sqrt(pol[1][0]/(len(idd)  -2))
            sigmaa = sigmae*sqrt(1./len(idd)+(mean(_col[idd])**2)/sum((_col[idd]-\
                                                                           mean(_col[idd]))**2))
            sigmab = sigmae*sqrt(1/sum((_col[idd]-mean(_col[idd]))**2))
        else:
            sigmaa=0.0
            sigmab=0.0
    else:
#            aa=mean(array(_dmag)[idd]-array(_col)[idd]*fixcol)
            aa=median(array(_dmag)[idd]-array(_col)[idd]*fixcol)
            bb=fixcol
            sigmaa=std(abs(aa-(array(_dmag)-array(_col)*float(_fixcol))))
            sigmab=0.0

    xx = [min(_col)-.1,max(_col)+.1]
    yy = polyval([bb,aa],xx)                ###
    lines = plt.plot(xx,yy,'r-')
    plt.ylim(min(_dmag)-.2,max(_dmag)+.2)
    plt.xlim(min(xx),max(xx))
    plt.xlabel(sss)
    plt.title(f)
    try:
        testo = plt.figtext(.2,.85,'%5.3f + %s* %5.3f [%4.3f  %4.3f]'%\
                             (aa,sss,bb,sigmaa,sigmab))
    except:
        testo = plt.figtext(.2,.85,'%5.3f + %s* %5.3f [%4.3f  %4.3f]'%\
                             (aa,sss,bb,sigmaa,sigmab))

    kid = fig.canvas.mpl_connect('key_press_event',onkeypress)
    cid = fig.canvas.mpl_connect('button_press_event',onclick)
    plt.draw()
    raw_input('left-click mark bad, right-click unmark, <d> remove. Return to exit ...')
    plt.close()
    print '####'
    print sigmaa,sigmab, aa,bb
    return aa,sigmaa,bb,sigmab

#################################################################

def fitcol2(_col,_dmag,band,col,fixcol='',show=False,rejection=2):
    from numpy import polyfit,polyval,argmin,sqrt,mean,array,std,compress
    import agnkey
    print '####'+str(rejection)
    sss=band
    f=col
    if len(_col)>1:
        if fixcol!='':
            slope=fixcol
            mean0,sig0,yy0,xx0=agnkey.agnabsphotdef.meanclip2(_col,_dmag,fixcol, clipsig=rejection, maxiter=5, converge_num=.99, verbose=0)
            xx = [min(_col)-.1,max(_col)+.1]
            yy = polyval([fixcol,mean0],_col)                ###
            try:      sigmae = sqrt(sig0/(len(xx0)  -2))
            except:   sigmae=0
            sigmaa = sigmae*sqrt(1./len(xx0)+(mean(xx0)**2)/sum((xx0-mean(xx0))**2))
            sigmab=0.0
        else:
            mean0,sig0,slope,yy0,xx0=agnkey.agnabsphotdef.meanclip3(_col,_dmag,fixcol, clipsig=rejection, maxiter=5, converge_num=.99, verbose=0)
            xx = [min(_col)-.1,max(_col)+.1]
            yy = polyval([slope,mean0],_col)                ###
            try:      sigmae = sqrt(sig0/(len(xx0)  -2))
            except:   sigmae=0
            sigmaa = sigmae*sqrt(1./len(xx0)+(mean(xx0)**2)/sum((xx0-mean(xx0))**2))
            sigmab = sigmae*sqrt(1/sum((xx0-mean(xx0))**2))
        if show:
            import time
            from pylab import plot,ion,clf,draw,xlabel,ylabel,title
            ion()
            clf()
            plot(_col,_dmag,'ob')
            plot(xx0,yy0,'xr')
            plot(_col,yy,'-g')
            ylabel('zeropoint')
            xlabel(f)
            title(sss)
            draw()
            time.sleep(1)
    try:
        print '##### ',mean0,sigmaa,slope,sigmab
    except:
        print '\n### zeropoint not computed'
        mean0,sigmaa,slope,sigmab=9999,9999,9999,9999
    return mean0,sigmaa,slope,sigmab

def meanclip2(xx,yy,slope, clipsig=3.0, maxiter=5, converge_num=0.1, verbose=0):
    from numpy import array
    import numpy
    xx=array(xx)
    yy=array(yy)
    xx0=array(xx[:])
    yy0=array(yy[:])
    ct=len(yy)
    slope=float(slope)
    iter = 0; c1 = 1.0 ; c2 = 0.0
    while (c1 >= c2) and (iter < maxiter):
        lastct = ct
        sig=numpy.std(yy0-xx0*slope)
#        mean=numpy.mean(array(yy0)-array(xx0)*slope)
        mean=numpy.median(array(yy0)-array(xx0)*slope)
        wsm = numpy.where( abs(yy0-xx0*slope) < mean+clipsig*sig )
        ct = len(wsm[0])
        if ct > 0:
            xx0=xx0[wsm]
            yy0=yy0[wsm]
        c1 = abs(ct - lastct)
        c2 = converge_num * lastct
        iter += 1
# End of while loop
#    mean=numpy.mean(array(yy0)-array(xx0)*slope)
    mean=numpy.median(array(yy0)-array(xx0)*slope)
    sig=numpy.std(array(yy0)-array(xx0)*float(slope))
    if verbose: pass
    return mean, sig,yy0,xx0

def meanclip3(xx,yy,slope, clipsig=3.0, maxiter=5, converge_num=0.1, verbose=0):
    from numpy import array, polyfit
    import numpy
    xx=array(xx)
    yy=array(yy)
    xx0=array(xx[:])
    yy0=array(yy[:])
    ct=len(yy)
    iter = 0; c1 = 1.0 ; c2 = 0.0
    while (c1 >= c2) and (iter < maxiter):
        lastct = ct
        pol = polyfit(xx0,yy0,1,full=True) ###
        mean0=pol[0][1]
        slope=pol[0][0]
        sig=numpy.std(yy0-mean0-slope*xx0)
        wsm = numpy.where( abs(yy0-xx0*slope) < mean0+clipsig*sig )
        ct = len(wsm[0])
        if ct > 0:
            xx0=xx0[wsm]
            yy0=yy0[wsm]
        c1 = abs(ct - lastct)
        c2 = converge_num * lastct
        iter += 1
# End of while loop
    pol = polyfit(xx0,yy0,1,full=True) ###
    mean0=pol[0][1]
    slope=pol[0][0]
    sig=numpy.std(yy0-mean0-slope*xx0)
    if verbose: pass
    return mean0, sig,slope,yy0,xx0

########################################################################
######################################################################################################
def finalmag(Z1,Z2,C1,C2,m1,m2):
    color=(Z1-Z2+m1-m2)/(1-(C1-C2))
    print 'color ',color
    print Z1,C1,m1
    print Z2,C2,m2
    M1=Z1+C1*color+m1
    M2=Z2+C2*color+m2
    return M1,M2

def erroremag(z0,z1,m0,m1,c0,c1,position): #  z=zeropoint,m=magnitude,colorterm  
    if position==0:   #    error for first band in the color: (e.g.  V in VR) 
        dm0=1+(c0/(1-(c0-c1)))
        dz0=1+(c0/(1-(c0-c1)))
        dm1=(-1)*(c0/(1-(c0-c1)))
        dz1=(-1)*(c0/(1-(c0-c1)))
        dc0=(z0+m0-z1-m1)*(1+c1)*(1/(1-(c0-c1))**2)
        dc1=(-1)*(z0+m0-z1-m1)*(c0)*(1/(1-(c0-c1))**2)
    elif position==1:   #    error for second band in the color: (e.g.  R in VR) 
        dm0=1-(c1/(1-(c0-c1)))
        dz0=1-(c1/(1-(c0-c1)))
        dm1=(-1)*(c1/(1-(c0-c1)))
        dz1=(-1)*(c1/(1-(c0-c1)))
        dc0=(z0+m0-z1-m1)*(1-c0)*(1/(1-(c0-c1))**2)
        dc1=(z0+m0-z1-m1)*(c1)*(1/(1-(c0-c1))**2) 
    else:
        # added to make the pipeline working, but error not good
        dm0=1
        dz0=0
        dm1=1
        dz1=0
        dc0=0
        dc1=0
    return dc0,dc1,dz0,dz1,dm0,dm1

#################################################################

def zeropoint(data,mag,maxiter=10,nn=2,show=False):
    import numpy as np
    z0=np.mean(data)
    std0=np.std(data)
    data1=data[:]
    mag1=mag[:]
    data2=np.compress((data < (z0+std0)) & (data>(z0-std0)),data)
    mag2=np.compress((data < (z0+std0)) & (data>(z0-std0)),mag)
    z2=np.mean(data2)
    std2=np.std(data2)
    iter=0; 
    if show:  
        import pylab as pl
        pl.ion()

    while iter < maxiter and len(data2)>5:
        z1=np.mean(data1)
        std1=np.std(data1)
        z2=np.mean(data2)
        std2=np.std(data2)
        if show:
            print 'rejected '+str(len(data1)-len(data2))+' point'
            print z1,std1,len(data1)
            print z2,std2,len(data2)

        if np.abs(z2-z1)<std2/np.sqrt(len(data2)):
            if show:
                print 'zero points are within std2 '
                pl.clf()
                pl.plot(mag1,data1,'or')
                pl.plot(mag2,data2,'xg')
            break
        else:
            data1=np.compress((data < (z1+nn*std1)) & (data>(z1-nn*std1)),data)
            data2=np.compress((data < (z2+nn*std2)) & (data>(z2-nn*std2)),data)
            mag1=np.compress((data < (z1+nn*std1)) & (data>(z1-nn*std1)),mag)
            mag2=np.compress((data < (z2+nn*std2)) & (data>(z2-nn*std2)),mag)
            z1=np.mean(data1)
            std1=np.std(data1)
            z2=np.mean(data2)
            std2=np.std(data2)
        iter += 1
        if show:
            print 'iteration '+str(iter)
            print z1,std1,len(data1)
            print z2,std2,len(data2)
            pl.clf()
            pl.plot(mag,data,'or')
            pl.plot(mag2,data2,'*g')
    return z2,std2,mag2,data2

#############################################

def zeropoint2(xx,mag,maxiter=10,nn=2,show=False,_cutmag=99):
   if len(xx):
      import numpy as np
      if float(_cutmag)!=99:
         print 'cut mag '+str(_cutmag)
         xx=np.compress(mag<_cutmag,xx)
         mag=np.compress(mag<_cutmag,mag)
      data=np.array(xx-mag)
      z0=np.median(data)
      std0=np.std(data)
      data1=data[:]
      mag1=mag[:]
      data2=np.compress((data < (z0+std0)) & (data>(z0-std0)),data)
      mag2=np.compress((data < (z0+std0)) & (data>(z0-std0)),mag)
      z2=np.mean(data2)
      std2=np.std(data2)
      iter=0; 
      if show:  
            print len(data2)
            import pylab as pl
            pl.ion()
            pl.clf()
            pl.plot(mag,data,'or')
            pl.plot(mag2,data2,'*g')
      while iter < maxiter and len(data2)>5:
          z1=np.mean(data1)
          std1=np.std(data1)
          z2=np.mean(data2)
          std2=np.std(data2)
          if show:
              print 'rejected '+str(len(data1)-len(data2))+' point'
              print z1,std1,len(data1)
              print z2,std2,len(data2)
          if np.abs(z2-z1)<std2/np.sqrt(len(data2)):
              if show:
                  print 'zero points are within std2 '
                  pl.clf()
                  pl.plot(mag1,data1,'or')
                  pl.plot(mag2,data2,'xg')
              break
          else:
              data1=np.compress((data < (z1+nn*std1)) & (data>(z1-nn*std1)),data)
              data2=np.compress((data < (z2+nn*std2)) & (data>(z2-nn*std2)),data)
              mag1=np.compress((data < (z1+nn*std1)) & (data>(z1-nn*std1)),mag)
              mag2=np.compress((data < (z2+nn*std2)) & (data>(z2-nn*std2)),mag)
              z1=np.mean(data1)
              std1=np.std(data1)
              z2=np.mean(data2)
              std2=np.std(data2)
          iter += 1
          if show:
              print 'iteration '+str(iter)
              print z1,std1,len(data1)
              print z2,std2,len(data2)
              pl.clf()
              pl.plot(mag,data,'or')
              pl.plot(mag2,data2,'*g')
      if np.isnan(z2): z2,std2= 9999, 9999
   else:
      z2,std2,mag2,data2=9999,9999,9999,9999
   return z2,std2,mag2,data2

########################################################################

def transform2natural(_instrument,_catalogue,_inputsystem='sloan'):
   import agnkey
   import numpy as np
   _catalogue2={}
   for i in _catalogue.keys():
      _catalogue2[i]=np.array(_catalogue[i][:],float)
   if _inputsystem in ['sloan','sloanprime']:
      colorefisso=agnkey.sites.colfix(_instrument,_inputsystem)
      #colorefisso=lcogtcal.util.colorfix(_instrument,_inputsystem) 
      col={}
      col['ug']=[(_catalogue2['u'][i]-_catalogue2['g'][i]) if (_catalogue2['u'][i]<99 and _catalogue2['g'][i]<99) else  (_catalogue2['u'][i]-_catalogue2['u'][i]) for i in range(0,len(_catalogue2['u']))]
      col['gr']=[(_catalogue2['g'][i]-_catalogue2['r'][i]) if (_catalogue2['g'][i]<99 and _catalogue2['r'][i]<99) else  (_catalogue2['g'][i]-_catalogue2['g'][i]) for i in range(0,len(_catalogue2['g']))]
      col['ri']=[(_catalogue2['r'][i]-_catalogue2['i'][i]) if (_catalogue2['r'][i]<99 and _catalogue2['i'][i]<99) else  (_catalogue2['r'][i]-_catalogue2['r'][i]) for i in range(0,len(_catalogue2['r']))]
      col['iz']=[(_catalogue2['i'][i]-_catalogue2['z'][i]) if (_catalogue2['i'][i]<99 and _catalogue2['z'][i]<99) else  (_catalogue2['i'][i]-_catalogue2['i'][i]) for i in range(0,len(_catalogue2['i']))]
      _catalogue2['u']=_catalogue2['u']-colorefisso['uug']*np.array(col['ug'])#(_catalogue['u']-_catalogue['g'])
      _catalogue2['g']=_catalogue2['g']-colorefisso['ggr']*np.array(col['gr'])#(_catalogue['g']-_catalogue['r'])
      _catalogue2['r']=_catalogue2['r']-colorefisso['rri']*np.array(col['ri'])#(_catalogue['r']-_catalogue['i'])
      _catalogue2['i']=_catalogue2['i']-colorefisso['iri']*np.array(col['ri'])#(_catalogue['r']-_catalogue['i'])
      _catalogue2['z']=_catalogue2['z']-colorefisso['ziz']*np.array(col['iz'])#(_catalogue['i']-_catalogue['z'])
      print 'transform '+str(_inputsystem)+' to natural system'
      print 'un = u - '+str(colorefisso['uug'])+' * (u-g)'
      print 'gn = g - '+str(colorefisso['ggr'])+' * (g-r)'
      print 'rn = r - '+str(colorefisso['rri'])+' * (r-i)'
      print 'in = i - '+str(colorefisso['iri'])+' * (r-i)'
      print 'zn = z - '+str(colorefisso['ziz'])+' * (i-z)'
   elif _inputsystem in ['landolt']:
      colorefisso=agnkey.sites.colfix(_instrument,_inputsystem)
      #colorefisso=lcogtcal.util.colorfix(_instrument,_inputsystem)
      col={}
      col['UB']=[(_catalogue2['U'][i]-_catalogue2['B'][i]) if (_catalogue2['U'][i]<99 and _catalogue2['B'][i]<99) else  (_catalogue2['B'][i]-_catalogue2['B'][i]) for i in range(0,len(_catalogue2['U']))]
      col['BV']=[(_catalogue2['B'][i]-_catalogue2['V'][i]) if (_catalogue2['B'][i]<99 and _catalogue2['V'][i]<99) else  (_catalogue2['B'][i]-_catalogue2['B'][i]) for i in range(0,len(_catalogue2['B']))]
      col['VR']=[(_catalogue2['V'][i]-_catalogue2['R'][i]) if (_catalogue2['V'][i]<99 and _catalogue2['R'][i]<99) else  (_catalogue2['V'][i]-_catalogue2['V'][i]) for i in range(0,len(_catalogue2['V']))]
      col['RI']=[(_catalogue2['R'][i]-_catalogue2['I'][i]) if (_catalogue2['R'][i]<99 and _catalogue2['I'][i]<99) else  (_catalogue2['R'][i]-_catalogue2['R'][i]) for i in range(0,len(_catalogue2['R']))]
      _catalogue2['U']=_catalogue2['U']-colorefisso['UUB']*np.array(col['UB'])#(_catalogue['U']-_catalogue['B'])
      _catalogue2['B']=_catalogue2['B']-colorefisso['BBV']*np.array(col['BV'])#(_catalogue['B']-_catalogue['V'])
      _catalogue2['V']=_catalogue2['V']-colorefisso['VVR']*np.array(col['VR'])#(_catalogue['V']-_catalogue['R'])
      _catalogue2['R']=_catalogue2['R']-colorefisso['RVR']*np.array(col['VR'])#(_catalogue['V']-_catalogue['R'])
      _catalogue2['I']=_catalogue2['I']-colorefisso['IRI']*np.array(col['RI'])#(_catalogue['R']-_catalogue['I'])
      print 'transform '+str(_inputsystem)+' to natural system'
      print "Un = U - "+str(colorefisso['UUB'])+" * (U-B)"
      print "Bn = B - "+str(colorefisso['BBV'])+" * (B-V)"
      print "Vn = V - "+str(colorefisso['VVR'])+" * (V-R)"
      print "Rn = R - "+str(colorefisso['RVR'])+" * (V-R)"
      print "In = I - "+str(colorefisso['IRI'])+" * (R-I)"
   elif _inputsystem in ['apass']:
      colorefisso=agnkey.sites.colfix(_instrument,_inputsystem)
      #colorefisso=lcogtcal.util.colorfix(_instrument,_inputsystem)
      col={}
      col['BV']=[(_catalogue2['B'][i]-_catalogue2['V'][i]) if (_catalogue2['B'][i]<99 and _catalogue2['V'][i]<99) else  (_catalogue2['B'][i]-_catalogue2['B'][i]) for i in range(0,len(_catalogue2['V']))]
      col['gr']=[(_catalogue2['g'][i]-_catalogue2['r'][i]) if (_catalogue2['g'][i]<99 and _catalogue2['r'][i]<99) else  (_catalogue2['g'][i]-_catalogue2['g'][i]) for i in range(0,len(_catalogue2['g']))]
      col['ri']=[(_catalogue2['r'][i]-_catalogue2['i'][i]) if (_catalogue2['r'][i]<99 and _catalogue2['i'][i]<99) else  (_catalogue2['r'][i]-_catalogue2['r'][i]) for i in range(0,len(_catalogue2['r']))]
      _catalogue2['B']=_catalogue2['B']-colorefisso['BBV']*np.array(col['BV']) #(_catalogue['B']-_catalogue['V'])
      _catalogue2['V']=_catalogue2['V']-colorefisso['BBV']*np.array(col['BV']) #(_catalogue['B']-_catalogue['V'])
      _catalogue2['g']=_catalogue2['g']-colorefisso['ggr']*np.array(col['gr']) #(_catalogue['g']-_catalogue['r'])
      _catalogue2['r']=_catalogue2['r']-colorefisso['rri']*np.array(col['ri']) #(_catalogue['r']-_catalogue['i'])
      _catalogue2['i']=_catalogue2['i']-colorefisso['iri']*np.array(col['ri']) #(_catalogue['r']-_catalogue['i'])
      print 'transform '+str(_inputsystem)+' to natural system'
      print "Bn = B - "+str(colorefisso['BBV'])+" * (B-V)"
      print "Vn = V - "+str(colorefisso['BBV'])+" * (B-V)"
      print "gn = g' - "+str(colorefisso['ggr'])+" * (g'-g')"
      print "rn = r' - "+str(colorefisso['rri'])+" * (r'-i')"
      print "in = i' - "+str(colorefisso['iri'])+" * (r'-i')"
   return _catalogue2

##################################################################################

def zeronew(ZZ,maxiter=10,nn=5,verbose=False,show=False):
     import numpy as np
     #         compute first median and error
     median=np.median(ZZ)                    
     sigma=(np.percentile(ZZ,75)-np.percentile(ZZ,25))*1.349
     # cut around median and new median
     ZZcut=np.compress((ZZ < (median+nn*sigma)) & (ZZ>(median-nn*sigma)),ZZ)
     xx=np.arange(len(ZZ))
     mediancut=np.median(ZZcut)      
     sigmacut=(np.percentile(ZZcut,75)-np.percentile(ZZcut,25))*1.349
     cut=len(ZZ)-len(ZZcut)
     iter=0
     while iter < maxiter and len(ZZcut)>5 and cut>0:
          iter+=1
          if verbose:
               print 'reject  '+str(cut)+' objects'  
               print 'number of object= '+str(len(ZZcut))
               print 'median=  '+str(mediancut)
               print 'sigma= '+str(sigmacut)
          # new cut around new median after rejection 
          ZZcut2=np.compress((ZZ < (mediancut+nn*sigmacut)) & (ZZ>(mediancut-nn*sigmacut)),ZZ)  

          median2=np.median(ZZcut2)
          sigma2=(np.percentile(ZZcut2,75)-np.percentile(ZZcut2,25))*1.349
          cut=len(ZZcut)-len(ZZcut2)
          if len(ZZcut2)>=5:
               ZZcut=ZZcut2
               sigmacut=sigma2
               mediancut=np.median(ZZcut2)
          if verbose:   print len(ZZcut2),sigmacut,mediancut
     if show:
          import pylab as pl
          pl.ion()
          xxc=np.arange(len(ZZcut))
          pl.plot(xx,ZZ,'or')
          pl.plot(xxc,ZZcut,'b*')
          pl.draw()
          import time
          time.sleep(1)
                      
     return ZZcut,sigmacut,mediancut

#######################################################################
