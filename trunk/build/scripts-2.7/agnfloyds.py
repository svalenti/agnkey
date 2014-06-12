#!/System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

import os,string,re,sys,glob
import datetime
import agnkey

description="> Ingest raw floyds data from fast reducton  " 
usage= "%prog -e epoch"
from optparse import OptionParser

def makeplot(img,_show=False):
  import os,string,pyfits
  import numpy as np
  import pylab as plt
  import agnkey,re
  hdr=pyfits.open(img)
  X=hdr[0].data
  _sky,_sig=agnkey.agnloopdef.getsky(X[0])
  _z1=_sky-_sig
  _z2=_sky+_sig*50
  
  plt.clf()
  fig1 = plt.figure(figsize=(6.0, 1.8))
  try:
    im=plt.imshow(X[0], cmap='gray', norm=None, aspect=None, interpolation='nearest',alpha=None, vmin=float(_z1), vmax=float(_z2), origin='upper', extent=None)
  except:
    im=plt.imshow(X[0], cmap='gray', norm=None, aspect=None, interpolation='nearest',alpha=None, vmin=0, vmax=1000, origin='upper', extent=None)
  output=re.sub('.fits','.png',img)
  if os.path.isfile(output):   os.system('rm '+output)
  if _show==True:
    plt.ion()
    plt.draw()
    plt.show()
  else:
    plt.savefig(output,format='png')
    os.system('chmod 766 '+output)
  return output


def readkeyflo(hdr,keyword):
    import re,string,sys
    import pyfits
    if pyfits.__version__:
         if int(re.sub('\.','',str(pyfits.__version__))[:2])<=30:  aa='HIERARCH '
         else: aa=''
    else:  aa=''
    try:    _instrume=hdr.get('INSTRUME').lower()
    except: _instrume='none'
    if _instrume in ['en05','en06']:
         if not hdr.get('HDRVER'):
              useful_keys = {'object'    : 'OBJECT',\
                             'date-obs'  : 'DATE-OBS',\
                             'ut'        : 'UTSTART',\
                             'obstype'   : 'OBSTYPE',\
                             'RA'        : 'RA',\
                             'DEC'       : 'DEC',\
                             'datamin'   : -100,\
                             'datamax'   : 60000,\
                             'grpid'     : 'GRPUID',\
                             'exptime'   : 'EXPTIME',\
                             'JD'        : 'MJD',\
                             'lamp'      : 'LMP_ID',\
                             'gain'      : 'GAIN',\
                             'instrume'  : 'INSTRUME',\
                             'grism'     : 'GRISM',\
                             'ron'       : 'READNOIS',\
                             'airmass'   : 'AIRMASS',\
                             'slit'      : 'APERWID',\
                             'telescop'  : 'TELESCOP'}
         else:
              useful_keys = {'object'    : 'OBJECT',\
                             'date-obs'  : 'DATE-OBS',\
                             'ut'        : 'UTSTART',\
                             'obstype'   : 'OBSTYPE',\
                             'RA'        : 'RA',\
                             'DEC'       : 'DEC',\
                             'datamin'   : -100,\
                             'datamax'   : 60000,\
                             'grpid'     : 'GRPUID',\
                             'exptime'   : 'EXPTIME',\
                             'JD'        : 'MJD-OBS',\
                             'lamp'      : 'LMP1ID',\
                             'gain'      : 'GAIN',\
                             'instrume'  : 'INSTRUME',\
                             'grism'     : 'GRISM',\
                             'ron'       : 'RDNOISE',\
                             'airmass'   : 'AIRMASS',\
                             'slit'      : 'APERWID',\
                             'telescop'  : 'TELESCOP'}              
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
            elif keyword=='JD':       value=float(value)+0.5
            elif keyword=='instrume':      value=value.lower()
            elif keyword=='grism':
                 if not value: value='full'
            elif keyword=='RA':
                 import string,re
                 value0=string.split(value,':')
                 value=((float(value0[0])+((float(value0[1])+(float(value0[2])/60.))/60.))*15)
            elif keyword=='DEC':
                 import string,re
                 value0=string.split(value,':')
                 if '-' in str(value0[0]):
                      value=((-1)*(abs(float(value0[0]))+((float(value0[1])+(float(value0[2])/60.))/60.)))
                 else:
                      value=(float(value0[0])+((float(value0[1])+(float(value0[2])/60.))/60.))
            elif keyword=='slit':     
                 value=re.sub('\"','',re.sub('slit','',str(value)))
            elif keyword=='object':
                 value=re.sub('\}','',value)
                 value=re.sub('\{','',value)
                 value=re.sub('\[','',value)
                 value=re.sub('\]','',value)
                 value=re.sub('\(','',value)
                 value=re.sub('\)','',value)
                 value=re.sub('-','',value)
                 value=re.sub(' ','',value)
    else:
       if keyword=='date-night':
            import datetime
            _date=readkeyflo(hdr,'DATE-OBS')
            a=(datetime.datetime.strptime(string.split(_date,'.')[0],"20%y-%m-%dT%H:%M:%S")-datetime.timedelta(.0)).isoformat()
            value=re.sub('-','',string.split(a,'T')[0])
       elif keyword=='TELID':
            value=hdr.get(keyword)
            value=re.sub('-','',value)
            if value in ['fts','2m0b']: value='fts'
            elif value in ['ftn','2m0a']: value='ftn'
            else:  sys.exit('Warning: keyword not valid')
       else:
          try:     value=hdr.get(keyword)
          except:       sys.exit('Warning: keyword not valid')
    if type(value) == str:    value=re.sub('\#','',value)
    return value

def targimg(img):  # maybe I can remove it
    import agnkey
    import string
    _targid=''
    hdrt=agnkey.util.readhdr(img)
    _ra=agnkey.util.readkey3(hdrt,'RA')
    _dec=agnkey.util.readkey3(hdrt,'DEC')
    _object=agnkey.util.readkey3(hdrt,'object')
    if ':' in str(_ra):         _ra,_dec=agnkey.agnabsphotdef.deg2HMS(_ra,_dec)
    print _ra,_dec,_object
    aa=agnkey.agnsqldef.getfromdataraw(agnkey.util.conn, 'recobjects', 'name', _object,'*')
    if len(aa)>=1: 
       _targid=aa[0]['targid']
       print _targid
       aa=agnkey.agnsqldef.getfromdataraw(agnkey.util.conn, 'lsc_sn_pos','targid',str(_targid),'*')
       _RA,_DEC,_SN=aa[0]['ra_sn'],aa[0]['dec_sn'],aa[0]['name']
    else:
       aa=agnkey.agnsqldef.getfromcoordinate(agnkey.util.conn, 'lsc_sn_pos', _ra, _dec,.3)
       if len(aa)==1:
          _RA,_DEC,_SN,_targid=aa[0]['ra_sn'],aa[0]['dec_sn'],aa[0]['name'],aa[0]['targid']
       else:
          _RA,_DEC,_SN,_targid='','','',''
    if not _targid:
       dictionary={'name':_object,'ra_sn':_ra,'dec_sn':_dec}
       agnkey.agnsqldef.insert_values(agnkey.util.conn,'lsc_sn_pos',dictionary)
       bb=agnkey.agnsqldef.getfromcoordinate(agnkey.util.conn, 'lsc_sn_pos', _ra, _dec,.01056)
       agnkey.agnsqldef.updatevalue('lsc_sn_pos','targid',bb[0]['id'],_object,connection='agnkey',namefile0='name')
       dictionary={'name':_object,'targid':bb[0]['id']}
       agnkey.agnsqldef.insert_values(agnkey.util.conn,'recobjects',dictionary)
       _targid=bb[0]['id']
    if _targid:
       cc=agnkey.agnsqldef.getfromdataraw(agnkey.util.conn,'permissionlog','targid', str(_targid),column2='groupname')
       if len(cc)==0:
          _JDn=agnkey.agnsqldef.JDnow()
          dictionary2={'targid':_targid,'jd':_JDn,'groupname':32769}
          agnkey.agnsqldef.insert_values(agnkey.util.conn,'permissionlog',dictionary2)
    return _targid

#################################################################################

def ingestfloyds(imglist,date,_force):
    import glob,string,os,re
    import agnkey
    datarawtable='datarawfloyds'
    for img in imglist:
      hdr=agnkey.util.readhdr(img)
      telescope=hdr.get('TELID')
      instrument=hdr.get('instrume')
      if not agnkey.agnsqldef.getfromdataraw(agnkey.util.conn,datarawtable,'namefile', string.split(img,'/')[-1],column2='namefile') or _force:
         if telescope in ['fts','ftn']:
               if instrument in ['en05','en06']:
                  _tech=None
                  print img
                  _targid=targimg(img)
                  dictionary={ 'lamp':readkeyflo(hdr,'lamp'), 'grism':readkeyflo(hdr,'grism'),'telescope':readkeyflo(hdr,'TELID'),\
                           'instrument':readkeyflo(hdr,'instrume'),'dec0':readkeyflo(hdr,'DEC'),'ra0':readkeyflo(hdr,'RA'),'ut':readkeyflo(hdr,'ut'),\
                           'dateobs':readkeyflo(hdr,'date-obs'),'exptime':readkeyflo(hdr,'exptime'), 'filter':readkeyflo(hdr,'filter'),'jd':readkeyflo(hdr,'JD'),\
                           'slit':readkeyflo(hdr,'APERWID'),'airmass':readkeyflo(hdr,'airmass'),'objname':readkeyflo(hdr,'object'),'type':readkeyflo(hdr,'OBSTYPE'),\
                           'category':readkeyflo(hdr,'catg'),'tech':_tech,'observer':readkeyflo(hdr,'OBSERVER'),'propid':readkeyflo(hdr,'PROPID'),\
                           'rotskypa':readkeyflo(hdr,'ROTSKYPA'),'OBID':readkeyflo(hdr,'GRPUID'),'USERID':readkeyflo(hdr,'USERID'),\
                               'temperature':readkeyflo(hdr,'CCDATEMP'),'dateobs2':readkeyflo(hdr,'DATE-OBS')}
               dictionary['namefile']=string.split(img,'/')[-1]
               directory=agnkey.util.workingdirectory+'floydsraw/'+date
               dictionary['directory']=directory
               dictionary['targid']=_targid
               if 'bad' in dictionary['directory']: dictionary['note']='bad'
         else: dictionary={}
         if telescope in ['fts','ftn']:
               if instrument in ['en05','en06']:
                  if not agnkey.agnsqldef.getfromdataraw(agnkey.util.conn,datarawtable,'namefile', string.split(img,'/')[-1],column2='namefile'):
                     agnkey.agnsqldef.insert_values(agnkey.util.conn,datarawtable,dictionary)
                  elif _force:
                     for voce in dictionary:
                        if voce!='id' and voce!='namefile':
                           agnkey.agnsqldef.updatevalue(datarawtable,voce,dictionary[voce],string.split(img,'/')[-1])
                  if not os.path.isdir(directory):       os.mkdir(directory) 
                   
                  if not os.path.isfile(directory+img) or _force=='yes': 
                      os.system('cp '+img+ ' '+directory)
                      if  hdr.get('OBSTYPE')=='SPECTRUM':
                          html=makeplot(directory+'/'+img,False)
                          print html
         else:
              raw_input('go on ? ') 

##########################################################################################

if __name__=='__main__':
    parser = OptionParser(usage=usage,description=description, version="%prog 1.0")
    parser.add_option("-e", "--epoch",dest="epoch",default='20130603',type="str",
                  help='-e epoch \t [%default]')
    parser.add_option("-T", "--telescope",dest="telescope",default='fts',type="str",
                  help='-T telescope fts,ftn\t [%default]')
    parser.add_option("-f", "--force",dest="force",default='no',type="str",
                      help='force ingestion \t [no/yes/update] \n')
    option,args = parser.parse_args()
    epoch=option.epoch
    _telescope=option.telescope
    _force=option.force

    if _telescope not in ['ftn','fts']: sys.argv.append('--help')
    elif _telescope =='ftn':        _telescope='ft1'
    elif _telescope =='fts':         _telescope='ft2'

    if '-' not in str(epoch): 
        epoch0=datetime.date(int(epoch[0:4]),int(epoch[4:6]),int(epoch[6:8]))
        listepoch=[re.sub('-','',str(epoch0))]
    else:
        epoch1,epoch2=string.split(epoch,'-')
        start=datetime.date(int(epoch1[0:4]),int(epoch1[4:6]),int(epoch1[6:8]))
        stop=datetime.date(int(epoch2[0:4]),int(epoch2[4:6]),int(epoch2[6:8]))
        listepoch=[re.sub('-','',str(i)) for i in [start + datetime.timedelta(days=x) for x in range(0,(stop-start).days)]]

    #    proposal ID that you want to download
#    propids = ['LCO2013B-007']
#    propids = ['LCO2013B-002']
#    propids = ['LCO2013B-009']
    propids = ['LCO2013B-010']

    ubases = []
    for p in propids: 
#        ubases.append(r'http://sci-archive.lcogt.net/data/webfiles/quicklook/'+_telescope+'/%s' % p)
        ubases.append(r'http://sci-archive.lcogt.net/data/webfiles/new/%s' % p)
    #   file with store all the passwd for different proposal
        '''############ 2013A
        LCO2013A-009 xxxxxxx
        LCO2013A-102 xxxxxxx
        LCO2013A-013 xxxxxxx'''
    #################################################
    pfile = agnkey.__path__[0]+'/standard/stdlist/lco_pass.txt'
    pswd = {}
    for l in open(pfile):
        if len(l.split())<2:
            continue
        if l[0]=='#':
            continue
        k, val = l.strip().split()
        pswd[k] = val
    print pswd

    #  directory where all logs and tar files are stored
    os.chdir(agnkey.util.workingdirectory+'logfile/')
    # if a log is empty, you may do not have data or data will still not be processed
    # so better to cancel all empty logs and try download again  
    aa=os.popen('wc -l '+agnkey.util.workingdirectory+'logfile/*log').read()
    for gg in string.split(aa,'\n'):
          try:
              if float(string.split(gg)[0]) == 0: 
                  print 'empy log file '+string.split(gg)[1]
                  os.system('rm '+string.split(gg)[1])
          except: 
              pass
    # 
    idates = []
    for d in listepoch:
          yr, mn, day = int(d[0:0+4]), int(d[4:4+2]), int(d[6:6+2])
          print yr, mn, day
          idates.append(datetime.date(yr, mn, day).toordinal())
    for d in listepoch:
          for iubase, ubase in enumerate(ubases):
            propid = propids[iubase]
            k = propid
            val = pswd[propid]
            nf2 = '%s_%s.log' % (d, propid)
            url2 = '%s/%s/%s.log' % (ubase, d, d)
            cmd2 = 'wget -O %s %s ' % (nf2, url2)
            cmd3 = cmd2[:]
            cmd3 += ' --user=%s --password=%s ' % (k, val)
            img=''
            if not os.path.exists(nf2):
                print cmd3
                os.system(cmd3)
                nlog = open(nf2).readlines()
                imglist=[]
                for line in nlog[4:]:     imglist.append(string.split(line)[-2]+'.fits')
                for img in imglist:
                    url = '%s/%s/%s' % (ubase, d, img)
                    cmd0 = 'wget -O %s %s' % (img,url)
                    cmd = cmd0[:]
                    cmd += ' --user=%s --password=%s ' % (k, val)
                    os.system(cmd)
                    print cmd
            else:
                print '\n### log and files already downloaded'
######################################################
#           MOVE FILE IN THE ARCHIVE
            imglist=glob.glob('g_*.fits')+glob.glob('f_*.fits')
            ingestfloyds(imglist,d,_force)

