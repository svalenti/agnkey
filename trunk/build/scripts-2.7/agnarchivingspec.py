#!/System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
#
#
# archicingspectra
#
#create table datareduspectra (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, namefile VARCHAR(50) UNIQUE KEY, directory VARCHAR(100), objname VARCHAR(50), jd DOUBLE, dateobs DATE, exptime FLOAT, filter VARCHAR(20), grism VARCHAR(20), telescope VARCHAR(20), instrument VARCHAR(20), airmass FLOAT, ut TIME, slit VARCHAR(20), status VARCHAR(50), original VARCHAR(50), note VARCHAR(100), ra0 FLOAT, dec0 FLOAT, PROPID VARCHAR(30), observer VARCHAR(30), dateobs2  VARCHAR(23), targid INT default 0);
#################################################
description=">> archive spectrum "
usage = "%prog spectrum -o output "
from numpy import *
import string,re,sys,glob,os
from optparse import OptionParser
import pyfits
import datetime
import agnkey

#################################################################################

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

def archivereducedspectrum(img):
    import string,re
    import pyfits
    hdr = pyfits.getheader(img)
    from agnkey.agnabsphotdef import deg2HMS
    _targid=targimg(img)
    if 'TELID' in hdr:           _telescope=hdr.get('TELID')
    elif 'TELESCOPE' in hdr:     _telescope=hdr.get('TELESCOP')
    else:                        _telescope='other'

    #    object
    _object=hdr.get('object')
    if not _object: _object='spectrum'
    _object=re.sub('\}','', _object)
    _object=re.sub('\{','', _object)
    _object=re.sub('\[','', _object)
    _object=re.sub('\]','', _object)
    _object=re.sub('\(','', _object)
    _object=re.sub('\)','', _object)
    _object=re.sub('-','', _object)
    _object=re.sub(' ','', _object)
    #    dateobs
    if 'DATE-OBS' in hdr:  
        _dateobs=hdr.get('DATE-OBS')
        if 'T' in _dateobs: _dateobs=string.split(_dateobs,'T')[0]
    else:     _dateobs=''
    #   UT
    if 'UTSTART' in hdr:  _ut=hdr.get('UTSTART')
    elif 'UT' in hdr: _ut=hdr.get('UT')
    else:
        _ut=hdr.get('DATE-OBS')
        if 'T' in _ut:    _ut=string.split(_ut,'T')[1]
    # ra and  dec
    _ra=hdr.get('RA')
    _dec=hdr.get('DEC')
    if ':' in str(_ra):      _ra,_dec=deg2HMS(_ra,_dec)
    # JD
    if 'MJD' in hdr: _jd=hdr.get('MJD')+0.5
    elif 'MJD-OBS' in hdr: _jd=hdr.get('MJD-OBS')+0.5
    elif 'JD' in hdr: _jd=hdr.get('JD')
    elif 'DATE-OBS' in hdr: 
        dd=''
        try:
            dd=datetime.datetime.strptime(hdr.get('DATE-OBS')[0:-6],'%Y-%m-%dT%H:%M:%S')
        except:
            try:
                dd=datetime.datetime.strptime(hdr.get('DATE-OBS')[0:-6],'%Y-%m-%dT%H:%M')
            except: pass
        if dd:     _jd=JDnow(dd,False)
        else:      _jd=None
    

    if _telescope in ['fts','ftn']:
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'jd':float(hdr.get('MJD'))+0.5,\
                    'telescope':_telescope,'airmass':hdr.get('airmass'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('instrume'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('APERWID'),\
                    'targid':_targid,'grism':re.sub('/','_',hdr.get('GRISM')), 'original':hdr.get('arcfile'),'PROPID':hdr.get('PROPID'),\
                    'dateobs2':hdr.get('DATE-OBS')}

    elif 'gemini' in _telescope.lower():
        if 'south' in _telescope.lower(): _telescope='gs'
        else: _telescope='gn'
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'jd':_jd,\
                    'telescope':_telescope,'airmass':hdr.get('AIRMASS'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('INSTRUME'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('slit'),'targid':_targid,'grism':hdr.get('GRATING'),\
                    'original':hdr.get('arcfile')}

    else:
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'jd':_jd,\
                    'telescope':_telescope,'airmass':hdr.get('airmass'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('instrume'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('slit'),'targid':_targid,'grism':hdr.get('GRISM'),\
                    'original':hdr.get('arcfile'),'observer':hdr.get('observer')}
        dictionary['namefile']=string.split(img,'/')[-1]

    dictionary['namefile']=string.split(img,'/')[-1]
    _dir=re.sub(string.split(img,'/')[-1],'',img)
    dictionary['directory']=_dir
    return dictionary

########################################

def targimg(img):
    import pyfits
    import agnkey
    from agnkey.agnabsphotdef import deg2HMS
    import string
    _targid=''
    hdrt=pyfits.getheader(img)
    _ra=hdrt.get('RA')
    _dec=hdrt.get('DEC')
    _object=hdrt.get('object')
    _object=re.sub(' ','',_object)
    _object=re.sub('\[','',_object)
    _object=re.sub('\]','',_object)
    if ':' in str(_ra):         _ra,_dec=deg2HMS(_ra,_dec)
    aa=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'recobjects', 'name', _object,'*')
    if len(aa)>=1: 
       _targid=aa[0]['targid']
       aa=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'lsc_sn_pos','targid',str(_targid),'*')
       _RA,_DEC,_SN=aa[0]['ra_sn'],aa[0]['dec_sn'],aa[0]['name']
    else:
       aa=agnkey.agnsqldef.getfromcoordinate(agnkey.agnsqldef.conn, 'lsc_sn_pos', _ra, _dec,.3)
       if len(aa)==1:
          _RA,_DEC,_SN,_targid=aa[0]['ra_sn'],aa[0]['dec_sn'],aa[0]['name'],aa[0]['targid']
       else:
          _RA,_DEC,_SN,_targid='','','',''
    if not _targid:
       dictionary={'name':_object,'ra_sn':_ra,'dec_sn':_dec}
       agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'lsc_sn_pos',dictionary)
       bb=agnkey.agnsqldef.getfromcoordinate(agnkey.agnsqldef.conn, 'lsc_sn_pos', _ra, _dec,.01056)
       agnkey.agnsqldef.updatevalue('lsc_sn_pos','targid',bb[0]['id'],_object,connection='lcogt',namefile0='name')
       dictionary={'name':_object,'targid':bb[0]['id']}
       agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'recobjects',dictionary)
       _targid=bb[0]['id']
    return _targid

def uploadspectrum(img,_output,_force):
    import pyfits
    import agnkey
    note='input= '+img+'\n'
    hdr=pyfits.open(img)[0].header
    if 'TELID' in hdr:  _tel=hdr.get('TELID')
    elif 'TELESCOP' in hdr:    _tel=hdr.get('TELESCOP')
    else:                    _tel='other'
    if not _tel: _tel='other'
    _tel=re.sub(' ','',_tel)
    note=note+'telescope= '+_tel+'\n'
###################################### # gemini files in jerord format needs some trick
    if 'gemini' in _tel.lower():      
        data,hdr0 = pyfits.getdata(img, 'sci', header=True)
        try:        hdr0.__delitem__('AIRMASS')
        except:     hdr0.remove('AIRMASS') 
        hed=['TELESCOP','OBSERVAT','RA','DEC','UT','ST','EXPTIME','MASKNAME','GRATING','CENTWAVE','OBSMODE','GAIN','RDNOISE','MJD-OBS',\
                 'PIXSCALE','DATE-OBS','AIRMASS']
        for jj in hed:
            hdr0.update(jj,hdr[jj])
        if 'south' in _tel.lower(): _tel='gs'
        else: _tel='gn'
        pyfits.writeto(re.sub('.fits','0.fits',img), float32(data), hdr0)
        img=re.sub('.fits','0.fits',img)
############################################# 

    dictionary=archivereducedspectrum(img)
    _grism=dictionary['grism']
    _date=dictionary['dateobs']
    _date=re.sub('-','',_date)
    if 'T' in _date: string.split(_date,'T')[0]
    _ut=dictionary['ut']
    _object=dictionary['objname']
    if not _output:
            _output=str(_object)+'_'+str(_date)+'_'+str(_grism)+'_'+re.sub(':','',str(_ut))+'.fits'
    
    directory=agnkey.util.workingdirectory+'/spectra/'+_date+'_'+_tel+'/'
    dictionary['directory']=directory
    dictionary['namefile']=_output

    note=note+'output= '+_output+'\n'
    if not dictionary['objname']: note=note+'ERROR= OBJECT not defined '
    else:                         note=note+'objname= '+str(dictionary['objname'])+'\n'
    if not dictionary['ra0']:     note=note+'ERROR= RA not defined \n'
    else:                         note=note+'ra= '+str(dictionary['ra0'])+'\n'
    if not dictionary['dec0']:    note=note+'ERROR= DEC not defined \n'
    else:                         note=note+'dec= '+str(dictionary['dec0'])+'\n'
    if not dictionary['targid']:  note=note+'ERROR= TARGID not defined \n'
    else:                         note=note+'targid= '+str(dictionary['targid'])+'\n'
    if not dictionary['dateobs']: note=note+'ERROR= DATE-OBS not defined \n'
    else:                         note=note+'dateobs= '+str(dictionary['dateobs'])+'\n'

    if 'ERROR' in note: 
        return note
    else:
        if os.path.isdir(directory): print 'directory there'
        else:                        os.system('mkdir '+directory)
        if os.path.isfile(directory+_output): 
            note=note+'file already there'+'\n'
            if _force=='force':
                note=note+'replace file'+'\n'
                os.system('rm '+directory+_output)
                os.system('cp '+img+' '+directory+_output)
        else:
            os.system('cp '+img+' '+directory+_output)
        if _tel in ['ftn','fts']:
            datarawtable='datareduspectra'
        else:
            datarawtable='dataspectraexternal'
        note=note+'database= '+datarawtable+'\n'
        if not agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn,datarawtable,'namefile', string.split(_output,'/')[-1],column2='namefile'):
            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,datarawtable,dictionary)
        else:
            if _force=='update':
                note=note+'update database'+'\n'
                for voce in dictionary:
                    if voce!='id' and voce!='namefile':
                        agnkey.agnsqldef.updatevalue(datarawtable,voce,dictionary[voce],string.split(_output,'/')[-1])
            elif _force=='force':
                note=note+'replace line in the database'+'\n'
                agnkey.agnsqldef.deleteredufromarchive(string.split(_output,'/')[-1],datarawtable,'namefile')
                agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,datarawtable,dictionary)
            else: note=note+'database not changed'+'\n'
        return note

######################################

if __name__ == "__main__":
    glob.glob('*fits')
    parser = OptionParser(usage=usage,description=description)
    parser.add_option("-o", "--output",dest="output",default='',type="str",
                      help='output \t [%default]')
    parser.add_option("-f", "--force",dest="force",default="add",help='force,update,add')
    option,args = parser.parse_args()
    if len(args)==0 : sys.argv.append('--help')
    _output=option.output
    _force=option.force
    img=args[0]
    note=uploadspectrum(img,_output,_force)
    print note
###################

