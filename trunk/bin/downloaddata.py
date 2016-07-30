#!/usr/bin/env python
import requests
import agnkey
import re
import os
import sys
from astropy.io import fits
from scipy.misc import toimage
import numpy as np
import base64

def authenticate(username, password):
    '''Get the authentication token'''
    response = requests.post('https://archive-api.lcogt.net/api-token-auth/',
                             data = {'username': username, 'password': password}).json()
    token = response.get('token')
    authtoken = {'Authorization': 'Token ' + token}
    return authtoken

def get_metadata(authtoken={}, limit=None, **kwargs):
    '''Get the list of files meeting criteria in kwargs'''
    url = 'https://archive-api.lcogt.net/frames/?' + '&'.join(
            [key + '=' + str(val) for key, val in kwargs.items() if val is not None])
    url = url.replace('False', 'false')
    url = url.replace('True', 'true')
    print url

    response = requests.get(url, headers=authtoken).json()
    print response

    frames = response['results']
    while response['next'] and (limit is None or len(frames) < limit):
        print response['next']
        response = requests.get(response['next'], headers=authtoken).json()
        frames += response['results']
    return frames[:limit]

def download_frame(frame, force):
    '''Download a single image from the LCOGT archive and put it in the right directory'''
    filename = frame['filename']
    dayobs = re.search('(20\d\d)(0\d|1[0-2])([0-2]\d|3[01])', filename).group()
    if 'fs' in frame['INSTRUME']:
        daydir = '1mtel/' + dayobs + '/'
    elif frame['INSTRUME'] == 'en06':
        daydir = 'floydsraw2/ogg/' + dayobs + '/raw/'
    elif frame['INSTRUME'] == 'en05':
        daydir = 'floydsraw2/coj/' + dayobs + '/raw/'
    else:
        daydir = '1mtel/' + dayobs + '/'
    filepath = agnkey.util.workingdirectory + daydir
    if 'raw' in filepath:
            if not os.path.isdir(re.sub('raw/','',filepath)):
                os.mkdir(re.sub('raw/','',filepath))
    if not os.path.isdir(filepath):
        os.mkdir(filepath)
    if 'cat' not in filename:
        if (not os.path.isfile(filepath + filename) and 
            not os.path.isfile(filepath + filename[:-3]) and 
            not os.path.isfile(filepath + 'bad/' + filename)) or force:
            print 'downloading', filename, 'to', filepath
            with open(filepath + filename, 'wb') as f:
                f.write(requests.get(frame['url']).content)
        else:
            print filename, 'already in', filepath
        if (filename[-3:] == '.fz' and not os.path.isfile(filepath + filename[:-3]) and
            not os.path.isfile(filepath + 'bad/' + filename[:-3])):
            print 'unpacking', filename
            os.system('funpack ' + filepath + filename)
            if os.path.isfile(filepath + filename):
                os.system('rm ' + filepath + filename)
            filename = filename[:-3]        
        elif filename[-3:] == '.fz':
            print filename, 'already unpacked'
            filename = filename[:-3]
    return filepath, filename

programs = agnkey.util.readpass['proposal']
users = agnkey.util.readpass['users']
odinpasswd = agnkey.util.readpass['odinpasswd']

photlcoraw_to_hdrkey = {'objname': 'OBJECT',
                        'dateobs': 'date-obs',
                        'dateobs2': 'date-obs',
                        'mjd': 'MJD-OBS',  # to be fixed
                        'exptime': 'EXPTIME',
                        'filter': 'FILTER',
                        'telescope': 'TELESCOP',
                        'instrument': 'INSTRUME',
                        'airmass': 'AIRMASS',
                        'ut'        : 'UTSTART',
                        'temperature': 'CCDATEMP',
                        'PROPID': 'PROPID',
                        'wcs':'WCSERR',
#                        'obid': 'BLKUID',
                        'USERID': 'USERID',
                        'fwhm': 'L1FWHM'}
#                        'tracknumber': 'TRACKNUM',
#                        'moonfrac': 'MOONFRAC',
#                        'moondist': 'MOONDIST'}

speclcoraw_to_hdrkey = {'objname': 'OBJECT',
                        'dateobs': 'date-obs',
                        'dateobs2': 'date-obs',
                        'mjd': 'MJD-OBS',
                        'exptime': 'EXPTIME',
                        'filter': 'FILTER',
                        'telescope': 'TELID',
                        'ut'        : 'UTSTART',
                        'instrument': 'INSTRUME',
                        'type': 'OBSTYPE',
                        'airmass': 'AIRMASS',
                        'slit': 'APERWID',
                        'lamp': 'lamp',
                        'observer': 'OBSERVER',
                        'temperature': 'CCDATEMP',
                        'PROPID': 'PROPID',
                        'BLKUID': 'BLKUID',
                        'OBID': 'GROUPID',
                        'rotskypa': 'ROTSKYPA',
                        'USERID': 'USERID',
                        'fwhm': 'AGFWHM'}#,
#                        'tracknumber': 'TRACKNUM'}

def db_ingest(filepath, filename, force):
    '''Read an image header and add a row to the database'''
    if '-en0' in filename:
        table = 'datarawfloyds'
        db_to_hdrkey = speclcoraw_to_hdrkey
    else:
        table = 'dataredulco'
        db_to_hdrkey = photlcoraw_to_hdrkey
    fileindb = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, table, 'namefile', filename, column2='namefile')
    if not fileindb or args.force:
        if filename[-3:] == '.fz':
            hdr = fits.getheader(filepath + filename, 1)
        else:
            hdr = fits.getheader(filepath + filename)


        _targid=agnkey.agnsqldef.targimg(filepath + filename)
        try:
            _ra, _dec = agnkey.agnabsphotdef.deg2HMS(hdr['ra'],hdr['dec'])
        except:
            _ra, _dec = 0,0

        dbdict = {'targid': _targid,
                  'ut': agnkey.util.readkey3(hdr, 'ut'),
                  'ra0': _ra,
                  'dec0': _dec,
#                    'dateobs': agnkey.util.readkey3(hdr, 'date-obs'),                  
#                    'cat_ra': agnkey.util.readkey3(hdr, 'CAT-RA'),
#                    'cat_dec': agnkey.util.readkey3(hdr, 'CAT-DEC'),
                    'namefile': filename}
        for dbcol, hdrkey in db_to_hdrkey.items():
            if hdrkey in hdr and hdr[hdrkey] not in ['NaN', 'UNKNOWN', None, '']:
                dbdict[dbcol] = hdr[hdrkey]

        if '-en0' not in filename:
            dbdict['filetype']= 1
            dbdict['wdirectory'] = filepath
        else:
            dbdict['directory'] = filepath
                        
        if fileindb:
            agnkey.agnsqldef.query(["delete from " + table + " where namefile='" + filename + "'"])
        print 'ingesting', filename
        agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn, table, dbdict)
    else:
        print filename, 'already ingested'

def fits2png(filename, zclip=5):
    data = fits.getdata(filename)
    z1 = np.percentile(data, zclip)
    z2 = np.percentile(data, 100-zclip)
    image = toimage(data[::-1], cmin=z1, cmax=z2)
    image.save(filename.replace('.fits', '.png'))

#################################################################
if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Downloads LCOGT data from archive.lcogt.net')
    parser.add_argument("-u", "--username")
    parser.add_argument("-p", "--password")
    parser.add_argument("-l", "--limit", type=int, help="maximum number of frames to return")
    parser.add_argument("-d", "--download", action="store_true", help="actually download the files")
    parser.add_argument("-F", "--force", action="store_true", help="download files even if they already exist")

    parser.add_argument("-S", "--site", choices=['bpl', 'coj', 'cpt', 'elp', 'lsc', 'ogg', 'sqa', 'tfn'])
    parser.add_argument("-T", "--telescope", choices=['0m4a', '0m4b', '0m4c', '0m8a', '1m0a', '2m0a'])
    parser.add_argument("-I", "--instrument")
    parser.add_argument("-f", "--filter", choices=['up', 'gp', 'rp', 'ip', 'zs', 'U', 'B', 'V', 'R', 'I'])
    parser.add_argument("-P", "--proposal", help="proposal ID (PROPID in the header)")
    parser.add_argument("-n", "--name", help="target name")
    parser.add_argument("-s", "--start", help="start date")
    parser.add_argument("-e", "--end", help="end date")

    parser.add_argument("-t", "--obstype", choices=['ARC', 'BIAS', 'CATALOG', 'DARK', 'EXPERIMENTAL',
                                        'EXPOSE', 'LAMPFLAT', 'SKYFLAT', 'SPECTRUM', 'STANDARD'])
    parser.add_argument("-r", "--reduction", choices=['raw', 'quicklook', 'reduced','image','spectra'])
    parser.add_argument("-x", "--experimental", action='store_true', help="get products from Curtis's pipeline")
    parser.add_argument("--public", action='store_true', help="include public data")

    args = parser.parse_args()

    if not args.proposal:
        _proposal = programs[0]
    else:
        _proposal = args.proposal

    if not args.start:
        _start = '2016-04-13'
    else:
        _start = args.start

    if args.username and args.password:
        authtoken = authenticate(args.username, args.password)
    else:
        username = users[0]
        password = odinpasswd
        authtoken = authenticate(username, password)

    if args.reduction == 'raw':
        rlevel = 0
    elif args.reduction == 'quicklook' and args.experimental:
        rlevel = 11
    elif args.reduction == 'quicklook':
        rlevel = 10
    elif args.reduction == 'reduced' and args.experimental:
        rlevel = 91
    elif args.reduction == 'reduced':
        rlevel = 91
    elif args.reduction == 'image':
        rlevel = 91
        if args.telescope == '2m0a':
            telid = ['2m0a']
            _basename = ['fs']
        elif args.telescope == '1m0a':
            telid = ['1m0a','1m0a']
            _basename = ['kb','fl']
        else:
            telid = ['1m0a','1m0a', '2m0a']
            _basename = ['kb','fl','fs']
    elif args.reduction == 'spectra':
        rlevel = 0
        _basename= ['en05','en06']
        telid = ['2m0a', '2m0a']
    else:
        rlevel = None
    
    if  args.reduction not in ['image','spectra']:
        frames = get_metadata(authtoken, limit=args.limit, SITEID=args.site, TELID=args.telescope,
                              INSTRUME=args.instrument, FILTER=args.filter, PROPID=_proposal, OBJECT=args.name,
                              start=_start, end=args.end, OBSTYPE=args.obstype, RLEVEL=rlevel, public=args.public)
    else:
        frames=[]
        for kk,jj in enumerate(telid):
            frames0 = get_metadata(authtoken, limit=args.limit, SITEID=args.site, 
                                   TELID=telid[kk],basename=_basename[kk],
                                   INSTRUME=args.instrument, FILTER=args.filter, PROPID=_proposal, OBJECT=args.name,
                                   start=_start, end=args.end, OBSTYPE=args.obstype, RLEVEL=rlevel, public=args.public)
            frames= frames+frames0

    print 'Total number of frames:', len(frames)

    blk=[]
    req=[]
    for frame in frames:
      print frame
      print frame['OBJECT'],frame['filename'],frame['TELID']
      if 'cat' not in frame['filename']:
        filepath, filename = download_frame(frame, args.force)        
        db_ingest(filepath, filename, args.force)
        if '-en0' in filename and '-e00.fits' in filename and (not os.path.isfile(filepath + filename.replace('.fits', '.png')) or args.force):
            fits2png(filepath + filename)
            _blk = fits.getheader(filepath+filename)['BLKUID']
            if _blk not in blk:
                blk.append(_blk)
                req.append(fits.getheader(filepath+filename)['REQNUM'])
    
    import tarfile
    directory = agnkey.util.workingdirectory + 'floydsraw/'
    if blk:
        for jj,kk in enumerate(blk):
            print blk[jj]
            print req[jj]
            data = agnkey.agnsqldef.query(['select directory,namefile from datarawfloyds where BLKUID='+blk[jj]])
            imglist = [i['directory']+i['namefile'] for i in data] 
            imglist1 = [i['namefile'] for i in data] 

            # go in the directory with data
            current = os.getcwd()
            os.chdir(data[0]['directory'])
            #  make tar file
            tarname = str(req[jj])+'_'+str(blk[jj])+'.tar'
            tFile = tarfile.open(tarname, 'w')
            for f in imglist1:
                tFile.add(f)
            tFile.close()
            
            os.system('mv '+ tarname + ' '+directory)
            agnkey.agnsqldef.updatevalue('triggerslog', 'tarfile',tarname, req[jj],
                                         connection='agnkey',namefile0='reqnumber')
            
            os.chdir(current)
