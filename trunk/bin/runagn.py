#!/usr/bin/env python
description = "> automatic process od lsc data "
usage = "%prog  fileter \t [listfile]"

import datetime
import os
import sys
import re
import string
import time
import agnkey
import glob
from numpy import compress
from optparse import OptionParser

start = time.time()

coomandsn = {'LSQ12fxd': '-c -x 3 -y 3 --bkg 3 --size 6',
             'LSQ13cnl': '-c -x 4 -y 4 --bkg 3 --size 5 --ref cpt1m012-kb75-20131008-0126-e90.sn2.fits'
    }


def runin(epoch,_type):
    import os
    start = string.split(epoch,'-')[0][0:4]+'-'+string.split(epoch,'-')[0][4:6]+'-'+string.split(epoch,'-')[0][6:8]
    end = string.split(epoch,'-')[1][0:4]+'-'+string.split(epoch,'-')[1][4:6]+'-'+string.split(epoch,'-')[1][6:8]
    try:
        print '/dark/hal/anaconda2/envs/dlt40/bin/agndownloaddata.py -r '+_type+' -s '+start + ' -e '+ end
        os.system('/dark/hal/anaconda2/envs/dlt40/bin/agndownloaddata.py -r '+_type+' -s '+start + ' -e '+ end)
    except:
        print 'problem with ingestion'


# ##########################################################

def zerostandard(standard, epoch, field, telescope='lsc'):
    import os, glob
    import agnkey

    catalogue = glob.glob(agnkey.__path__[0] + '/' + 'standard/cat/' + field + '/' + standard + '*')
    try:
        if len(catalogue) >= 1:
            aa = re.sub(agnkey.__path__[0] + '/' + 'standard/cat/', '', catalogue[0])
            print '\nagnloop.py --type ph -b zcat -F -e ' + epoch + ' -n ' + standard + ' -f ' + field + \
                  ' -s zcat --catalog ' + aa + ' --cutmag -6 -T ' + telescope
            os.system(agnkey.util.execdirectory+'agnloop.py --type ph -b zcat -F -e ' + epoch + ' -n ' + standard + ' -f ' + field +
                      ' -s zcat --catalog ' + aa + ' --cutmag -6 -T ' + telescope)
        else:
            print '\nagnloop.py --type ph -b zcat -F -e ' + epoch + ' -n ' + standard + ' -f ' + field + \
                  ' -s zcat --cutmag -6 -T ' + telescope
            os.system(agnkey.util.execdirectory+'agnloop.py --type ph -b zcat -F -e ' + epoch + ' -n ' + standard + ' -f ' + field +
                      ' -s zcat --cutmag -6 -T ' + telescope)
    except:
        print 'problem with zeropoint'

###########################################################
if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description, version="%prog agnkey")
    parser.add_option("-f", "--filter", dest="filter", default='', type="str",
                      help='-f filter [sloan,landolt,u,g,r,i,z,U,B,V,R,I] \t [%default]')
    parser.add_option("-T", "--telescope", dest="telescope", default='all', type="str",
                      help='-T telescope ' + ', '.join(agnkey.util.telescope0['all']) + ', '.join(agnkey.util.site0) + \
                           ', fts, ftn, 1m0, kb, fl \t [%default]')
    parser.add_option("-e", "--epoch", dest="epoch", default='', type="str", help='epoch to reduce  \t [%default]')
    parser.add_option("-i", "--ingest", action="store_true", dest='ingest', default=False,
                      help='ingest new data \t\t\t [%default]')
    parser.add_option("--field", dest="field", default='', type="str",
                      help='--field  [landolt,sloan]  \t [%default]')
    parser.add_option("--filetype", dest="filetype", default=1, type="int",
                      help='filetype  1 [single], 2 [merge], 3 differences \t [%default]')
    parser.add_option("-X", "--xwindow", action="store_true", dest='xwindow', default=False,
                      help='xwindow \t\t\t [%default]')

    option, args = parser.parse_args()
    _telescope = option.telescope
    _ingest = option.ingest
    _field = option.field
    _filetype = option.filetype
    _filter = option.filter
    _xwindow = option.xwindow

    if _xwindow:
        from stsci.tools import capable
        capable.OF_GRAPHICS = False
        XX = ' -X '
        import matplotlib
        matplotlib.use('Agg')
    else:
        XX = ''

    if _telescope not in agnkey.util.telescope0['all'] + agnkey.util.site0 + ['all', 'ftn', 'fts', '1m0', 'kb', 'fl']:
        sys.argv.append('--help')
    if _filter:
        if _filter not in ['landolt', 'sloan', 'u', 'g', 'r', 'i', 'z', 'U', 'B', 'V', 'R', 'I', 'ug', 'gr', 'gri',
                           'griz', 'riz', 'BVR', 'BV', 'BVRI', 'VRI']:
            sys.argv.append('--help')
    option, args = parser.parse_args()
    epoch = option.epoch
    if epoch:
        if '-' not in str(epoch):
            epoch0 = datetime.date(int(epoch[0:4]), int(epoch[4:6]), int(epoch[6:8]))
        else:
            epoch1, epoch2 = string.split(epoch, '-')
            epoch = epoch1 + '-' + epoch2
    else:
        d = datetime.date.today() + datetime.timedelta(1)
        g = d - datetime.timedelta(4)
        epoch = g.strftime("%Y%m%d") + '-' + d.strftime("%Y%m%d")

    if _telescope:
        if _telescope == 'all':
            tel = agnkey.util.telescope0['all']
        elif _telescope == 'lsc':
            tel = agnkey.util.telescope0['lsc']
        elif _telescope == 'ogg':
            tel = agnkey.util.telescope0['ogg']
        elif _telescope == 'elp':
            tel = agnkey.util.telescope0['elp']
        elif _telescope == 'coj':
            tel = agnkey.util.telescope0['coj']
        elif _telescope == 'cpt':
            tel = agnkey.util.telescope0['cpt']
    else:
        tel = agnkey.util.telescope0['all']

    if _field:
        fil = [_field]
    else:
        fil = ['landolt', 'sloan']


        #  upload req info in logtable
    _JDn = agnkey.agnsqldef.JDnow() - 10
    username, passwd = agnkey.util.readpass['odinuser'], agnkey.util.readpass['odinpasswd']
    token = agnkey.util.readpass['token']

    agnkey.util.downloadfloydsraw(_JDn, token)

    if _ingest:
        print '\n### ingest raw data \n'
        runin(epoch,'image')  # ingest raw images
        runin(epoch,'spectra')  # ingest raw spectra


    if _filter:
        ff = ' -f ' + _filter
    else:
        ff = ''

    if _telescope == 'all':
        tt = ''
    else:
        tt = '  -T ' + _telescope + ' '

    ##########################################################################
    #    added for new idl pipeline
    print '\n####  add hjd, when missing '
    os.system(agnkey.util.execdirectory+'agnloop.py -e ' + epoch + ' -s idlstart ')
    os.system(agnkey.util.execdirectory+'agnloop.py -e ' + epoch + ' -s update --column hjd --header HJD ') 
    #############################################################################

    print '\n####  compute  astrometry, when missing '
    #  compute astrometry when tim astrometry failed
    os.system(agnkey.util.execdirectory+'agnloop.py -e ' + epoch + ' -b wcs -s wcs --mode astrometry ' + ff + tt + XX)

    #  try again or set to bad image
    os.system(agnkey.util.execdirectory+'agnloop.py -e ' + epoch + ' -b wcs -s wcs --xshift 1 --yshift 1 ' + ff + tt + XX)

    #####################################################
    print '\n####  compute  psf, when missing '
    os.system(agnkey.util.execdirectory+'agnloop.py -e ' + epoch + ' -b psf -s psf ' + ff + tt + XX)  #  compute psf

    ######################################################
    #    added for new calibration
    os.system(agnkey.util.execdirectory+'agnloop.py -e ' + epoch + ' -s apmag ')  #  compute psf


    ll = agnkey.agnloopdef.get_list(epoch, 'all', '', '', '', '', '', '', 'dataredulco', _filetype)
    if ll:
        lista = list(set(ll['objname']))
    else:
        lista = []
    sloancal = []
    landoltcal = []
    apasscal = []
    standard = []
    notinthelist = []
    for obj in lista:
        img = compress(ll['objname'] == obj, ll['namefile'])[0]
        _dir = compress(ll['objname'] == obj, ll['wdirectory'])[0]
        _SN0 = ''
        _Std = ''
        _ra0, _dec0, _Std = agnkey.util.checksnlist(_dir + img, 'standardlist.txt')
        if not _Std:  
            _ra0, _dec0, _SN0 = agnkey.util.checksnlist(_dir + img, 'supernovaelist.txt')
        if not _Std and not _SN0:
            _ra0, _dec0, _SS, _type = agnkey.util.checksndb(_dir + img, 'lsc_sn_pos')
            if _SS:
                if _type in ['STD', 'std']:
                    _Std = _SS
                else:
                    _SN0 = _SS
        if _Std:
            print '\n### object in the standard list ' + _Std
            standard.append(obj)
            _temp = _Std
        else:
            _temp = _SN0
        if _temp:
            print '\n### object in the supernova list ' + _temp
            _catlandolt = glob.glob(agnkey.__path__[0] + '/standard/cat/landolt/' + _temp + '*')
            _catsloan = glob.glob(agnkey.__path__[0] + '/standard/cat/sloan/' + _temp + '*')
            _catapass = glob.glob(agnkey.__path__[0] + '/standard/cat/apass/' + _temp + '*')
            if len(_catlandolt) >= 1:
                _catlandolt = _catlandolt[0]
                print '\n### landolt catalogue available ' + _catlandolt
            else:
                _catlandolt = ''
            if len(_catsloan) >= 1:
                _catsloan = _catsloan[0]
                print '\n### sloan catalogue available ' + _catsloan
            else:
                _catsloan = ''
            if len(_catapass) >= 1:
                _catapass = _catapass[0]
                print '\n### apass catalogue available ' + _catapass
            else:
                _catapass = ''
        if not _Std and not _SN0:
            print '\n###warning:  object NOT in the supernova and standard lists ' + obj
            notinthelist.append(obj)
            _catlandolt = ''
            _catsloan = ''
        if _catlandolt:  landoltcal.append(obj)
        if _catsloan:    sloancal.append(obj)
        if _catapass:    apasscal.append(obj)

    print '\n### standard fields: ' + str(standard)
    print '\n### landolt fields:\n' + str(landoltcal)
    print '\n### sloan field:\n' + str(sloancal)
    print '\n### apass field:\n' + str(apasscal)
    print '\n### not in the lists:\n ' + str(notinthelist)
    #                 compute zero point for different fields
    for field in fil:
        if field == 'landolt': 
            listacampi = standard + landoltcal
        if field == 'sloan':   
            listacampi = standard + sloancal
        for _standard in listacampi:
            if _telescope == 'all':
                for _tel in ['elp', 'lsc', 'cpt', 'coj']:
                    zerostandard(_standard, epoch, field, _tel)
            else:
                zerostandard(_standard, epoch, field, _telescope)

    #    compute zeropoint for apass field not in landolt or sloan
    for field in fil:
        if field == 'landolt':
            for _name in apasscal:
                if _name not in landoltcal:
                    if _telescope == 'all':
                        for _tel in ['elp', 'lsc', 'cpt', 'coj']:
                            zerostandard(_name, epoch, 'apass', _tel)
                        else:
                            zerostandard(_name, epoch, 'apass', _telescope)
        if field == 'sloan':
            for _name in apasscal:
                if _name not in sloancal:
                    if _telescope == 'all':
                        for _tel in ['elp', 'lsc', 'cpt', 'coj']:
                            zerostandard(_name, epoch, 'apass', _tel)
                        else:
                            zerostandard(_name, epoch, 'apass', _telescope)

    #               compute catalogues for SN fields
    for field in fil:
        for obj in lista:
            if field == 'landolt':
                #                for obj in lista:
                #                if obj not in landoltcal:
                print obj + ': object not calibrated in landolt'
                for _std in standard:
                    for _tel in ['elp', 'lsc', 'cpt']:
                        os.system(agnkey.util.execdirectory+'agnloop.py --type ph  -F -e ' + epoch + ' -n ' + obj + ' -f ' + field + \
                                  ' -b abscat -s abscat --standard ' + _std + ' -T ' + _tel + XX)
            if field == 'sloan':
                #               if obj not in sloancal:
                print obj + ': object not calibrated in sloan'
                for _std in standard:
                    for _tel in ['elp', 'lsc', 'cpt']:
                        os.system(agnkey.util.execdirectory+'agnloop.py --type ph  -F -e ' + epoch + ' -n ' + obj + ' -f ' + field + \
                                  ' -b abscat -s abscat --standard ' + _std + ' -T ' + _tel + XX)
    # run psffit on all objects
    for field in fil:
        for obj in lista:
            if obj not in standard:
                print '###', obj
                if obj in coomandsn.keys():
                    os.system(agnkey.util.execdirectory+'agnloop.py -b psfmag -n ' + obj + ' -e ' + epoch + ' -f ' + field + ' ' + XX + \
                              ' -s psfmag -c  ' + coomandsn[obj])
                else:
                    os.system(agnkey.util.execdirectory+'agnloop.py -b psfmag -n ' + obj + ' -e ' + epoch + ' -f ' + field + ' ' + XX + \
                              ' -s psfmag -c  -x 3 -y 3 --bkg 4 --size 7 ')

    print '\n### landolt fields:\n' + str(landoltcal)
    print '\n### sloan field:\n' + str(sloancal)
    print '\n### apass field:\n' + str(apasscal)

    for field in fil:
        for obj in lista:
            if obj not in standard:
                if field == 'landolt':
                    if obj in landoltcal:
                        print '###', obj
                        try:
                            os.system(agnkey.util.execdirectory+'agnloop.py -b mag -n ' + obj + ' -e ' + epoch + ' -f ' + field + ' ' + XX + \
                                      ' -s mag --type fit')
                        except:
                            pass
                    elif obj in apasscal:
                        print '###', obj
                        try:
                            os.system(agnkey.util.execdirectory+'agnloop.py -b mag -n ' + obj + ' -e ' + epoch + ' -f apass' + ' ' + XX + \
                                      ' -s mag --type fit')
                        except:
                            pass
                elif field == 'sloan':
                    if obj in sloancal:
                        print '###', obj
                        try:
                            os.system(agnkey.util.execdirectory+'agnloop.py -b mag -n ' + obj + ' -e ' + epoch + ' -f ' + field + ' ' + XX + \
                                      ' -s mag --type fit')
                        except:
                            pass
                    elif obj in apasscal:
                        print '###', obj
                        try:
                            os.system(agnkey.util.execdirectory+'agnloop.py -b mag -n ' + obj + ' -e ' + epoch + ' -f apass' + ' ' + XX + \
                                      ' -s mag --type fit')
                        except:
                            pass


    # make stamps for all new images
    try:
        os.system(agnkey.util.execdirectory+'agnloop.py -e ' + str(epoch) + ' -s makestamp' + ' ' + XX)
    except:
        print 'warning makestap did not work'

    stop = time.time()
    print 'time to process all  data ', str(stop - start)
            
