#!/usr/bin/env python
description = "> process lsc data  "
usage = "%prog  -e epoch [-s stage -n name -f filter -d idnumber]\n available stages [wcs,psf,psfmag,zcat,abscat,mag,local,getmag]\n"

import string
import re
import os
import sys
from numpy import take, argsort, asarray, array
from optparse import OptionParser
import datetime
import agnkey
from multiprocessing import Pool

def multi_run_makestamp(args):
    return agnkey.agnloopdef.makestamp(*args)

def multi_run_apmag(args):
    return agnkey.agnloopdef.run_apmag(*args)

def multi_run_cosmic(args):
    return agnkey.agnloopdef.run_cosmic(*args)

def multi_run_diff(args):
    return agnkey.agnloopdef.run_diff(*args)
# ####################################################################################

if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description, version="%prog 1.0")
    parser.add_option("-e", "--epoch", dest="epoch", default='20121212', type="str",
                      help='epoch to reduce  \t [%default]')
    parser.add_option("-T", "--telescope", dest="telescope", default='all', type="str",
                      help='-T telescope ' + ', '.join(agnkey.util.telescope0['all']) + ', '.join(agnkey.util.site0) + \
                           ', fts, ftn, 1m0, kb, fl \t [%default]')
    parser.add_option("-R", "--RA", dest="ra", default='', type="str",
                      help='-R  ra    \t [%default]')
    parser.add_option("-D", "--DEC", dest="dec", default='', type="str",
                      help='-D dec   \t [%default]')
    parser.add_option("-n", "--name", dest="name", default='', type="str",
                      help="-n image name   \t [%default]")
    parser.add_option("-d", "--id", dest="id", default='', type="str",
                      help="-d identification id   \t [%default]")
    parser.add_option("-f", "--filter", dest="filter", default='', type="str",
                      help="-f filter [sloan,landolt,apass,u,g,r,i,z,U,B,V,R,I] \t [%default]")
    parser.add_option("-F", "--force", dest="force", action="store_true")
    parser.add_option("-b", "--bad", dest="bad", default='', type="str",
                      help="-b bad stage [wcs,psf,psfmag,zcat,abscat,mag,goodcat,getmag," +
                           'merge,diff,template,apmag,update] \t [%default]')
    parser.add_option("-s", "--stage", dest="stage", default='', type="str",
                      help='-s stage [wcs,psf,psf2,psfmag,zcat,abscat,mag,getmag,merge,diff,mergeall' +
                           'makestamp,template,apmag,cosmic,idlstart,copy,remove] \t [%default]')
    parser.add_option("--RAS", dest="ras", default='', type="str",
                      help='-RAS  ra    \t [%default]')
    parser.add_option("--DECS", dest="decs", default='', type="str",
                      help='-DECS dec   \t [%default]')
    parser.add_option("-x", "--xord", dest="xord", default=3, type=int,
                      help='-x order for bg fit   \t [%default]')
    parser.add_option("-y", "--yord", dest="yord", default=3, type=int,
                      help='-y order for bg fit \t [%default]')
    parser.add_option("--bkg", dest="bkg", default=4, type=float,
                      help=' bkg radius for the fit  \t [%default]')
    parser.add_option("--size", dest="size", default=7, type=float,
                      help='size of the stamp for the fit \t [%default]')
    parser.add_option("-t", "--threshold", dest="threshold", default=5.,
                      type='float', help='Source detection threshold \t\t\t %default')
    parser.add_option("-i", "--interactive", action="store_true",
                      dest='interactive', default=False, help='Interactive \t\t\t [%default]')
    parser.add_option("--show", action="store_true",
                      dest='show', default=False, help='show psf fit \t\t\t [%default]')
    parser.add_option("-c", "--center", action="store_false",
                      dest='recenter', default=True, help='recenter \t\t\t [%default]')
    parser.add_option("--fix", action="store_false",
                      dest='fix', default=True, help='fix color \t\t\t [%default]')
    parser.add_option("--cutmag", dest="cutmag", default=99., type="float",
                      help='--cutmag  [magnitude instrumental cut for zeropoint ]  \t [%default]')
    parser.add_option("--field", dest="field", default='', type="str",
                      help='--field  [landolt,sloan,apass]  \t [%default]')
    parser.add_option("--ref", dest="ref", default='', type="str",
                      help='--ref  sn22_20130303_0111.sn2.fits get sn position from this file \t [%default]')
    parser.add_option("--catalog", dest="catalogue", default='', type="str",
                      help='--catalogue  sn09ip.cat    \t [%default]')
    parser.add_option("--calib", dest="calib", default='', type="str",
                      help='--calib  (sloan,natural,sloanprime)   \t [%default]')
    parser.add_option("--type", dest="type", default='fit', type="str",
                      help='--type mag for zero point   [fit,ph,mag,appmagap1,appmagap2,appmagap3,flux1]   '
                           ' \t [%default]')
    parser.add_option("--standard", dest="standard", default='', type="str",
                      help='--standard namestd  \t use the zeropoint from this standard    \t [%default]')
    parser.add_option("--xshift", dest="xshift", default=0, type="int",
                      help='x shift in the guess astrometry \t [%default]')
    parser.add_option("--fwhm", dest="fwhm", default='', type="str",
                      help='fwhm (in pixel)  \t [%default]')
    parser.add_option("--mode", dest="mode", default='sv', type="str",
                      help='mode for wcs (sv,astrometry)  \t [%default]')
    parser.add_option("--combine", dest="combine", default=1e-10, type="float",
                      help='range to combine (in days)  \t [%default]')
    parser.add_option("--datamax", dest="dmax", default = 0, type="float",
                      help='data max for saturation (counts)  \t [%default]')
    parser.add_option("--yshift", dest="yshift", default=0, type="int",
                      help='y shift in the guess astrometry \t [%default]')
    parser.add_option("--filetype", dest="filetype", default=1, type="int",
                      help='filetype  1 [single], 2 [merge], 3 differences \t [%default]')
    parser.add_option("-o", "--output", dest="output", default='', type="str",
                      help='--output  write magnitude in the output file \t [%default]')
    parser.add_option("--tempdate", dest="tempdate", default='', type="str",
                      help='--tempdate  tamplate date \t [%default]')
    parser.add_option("--normalize", dest="normalize", default='i', type="str",
                      help='--normalize image [i], template [t] \t hotpants parameter  \t [%default]')
    parser.add_option("-X", "--xwindow", action="store_true", \
                      dest='xwindow', default=False, help='xwindow \t\t\t [%default]')
    parser.add_option("--z1", dest="z1", default=None, type="int",
                      help='z1 \t [%default]')
    parser.add_option("--z2", dest="z2", default=None, type="int",
                      help='z2 \t [%default]')
    parser.add_option("--bgo", dest="bgo", default=3, type=float,
                      help=' bgo parameter for hotpants  \t [%default]')
    parser.add_option("-p", "--psf", dest="psf", default='', type=str, 
                      help='psf image for template \t\t\t %default')
    parser.add_option("--mag", dest="mag", type=float, default=0, 
                      help='mag to subtract from template image \t\t [%default]')
    parser.add_option("--uncleaned", dest="clean", action='store_false', default=True, 
                      help='do not use cosmic ray cleaned image as template \t\t [%default]')
    parser.add_option("--subtract-mag-from-header", action='store_true',\
                      help='automatically subtract mag from header of template image \t\t [%default]')
    parser.add_option("--fixpix", dest="fixpix", action="store_true", default=False,
                      help='Run fixpix on the images before doing image subtraction')
    parser.add_option("--multicore", dest="multicore", default=4, type=int,
                      help='--multicore numbers of cores   \t [%default]')
    parser.add_option("--header", dest="header", default='', type=str, 
                      help='header image \t\t\t %default')
    parser.add_option("--column", dest="column", default='', type=str, 
                      help='column database \t\t\t %default')
    parser.add_option("--table", dest="table", default='dataredulco', type=str, 
                      help='table database \t\t\t %default')


    option, args = parser.parse_args()
    # _instrument=option.instrument
    _telescope = option.telescope
    _normalize = option.normalize
    _type = option.type
    _mode = option.mode
    _column = option.column
    _header = option.header
    _table = option.table
    _multicore = option.multicore
    _stage = option.stage
    _bad = option.bad
    _clean = option.clean
    _subtract_mag_from_header = option.subtract_mag_from_header
    _fixpix = option.fixpix
    _mag = option.mag
    _psf = option.psf
    _bgo = option.bgo

    if _normalize not in ['i', 't']:
        sys.argv.append('--help')
    if _telescope not in agnkey.util.telescope0['all'] + agnkey.util.site0 + ['all', 'ftn', 'fts', '1m0', 'kb', 'fl','fs']:
        sys.argv.append('--help')
    if option.force == None:
        _redo = False
    else:
        _redo = True
    if option.recenter == False:
        _recenter = True
    else:
        _recenter = False
    if _type not in ['fit', 'ph', 'mag', 'appmagap1', 'appmagap2', 'appmagap3', 'flux1','flux2','flux3']:
        sys.argv.append('--help')
    if _stage:
        if _stage not in ['wcs', 'psf', 'psf2', 'psfmag', 'zcat', 'abscat', 'mag', 'local', 'getmag',
                          'merge', 'mergeall','diff', 'template', 'apmag', 'makestamp', 'cosmic', 'idlstart','update','copy','remove']:
            sys.argv.append('--help')
    if _bad:
        if _bad not in ['wcs', 'psf', 'psfmag', 'zcat', 'abscat', 'mag', 'goodcat', 'quality', 'apmag','diff']:
            sys.argv.append('--help')
    option, args = parser.parse_args()
    _id = option.id
    _filter = option.filter
    _ra = option.ra
    _dec = option.dec
    _ras = option.ras
    _output = option.output
    _decs = option.decs
    _name = option.name
    _fwhm = option.fwhm
    _xord = option.xord
    _yord = option.yord
    _bkg = option.bkg
    _size = option.size
    _standard = option.standard
    _threshold = option.threshold
    _interactive = option.interactive
    _xwindow = option.xwindow
    _show = option.show
    _fix = option.fix
    _catalogue = option.catalogue
    _calib = option.calib
    _ref = option.ref
    _field = option.field
    _cutmag = option.cutmag
    _xshift = option.xshift
    _yshift = option.yshift
    _bin = option.combine
    _dmax = option.dmax
    _filetype = option.filetype
    _tempdate = option.tempdate
    _z1 = option.z1
    _z2 = option.z2

    if _xwindow:
        from stsci.tools import capable

        capable.OF_GRAPHICS = False
        import matplotlib

        matplotlib.use('Agg')
        XX = ' -X '
    else:
        XX = ''

    if _filter:
        if _filter not in ['landolt', 'sloan', 'apass', 'u', 'g', 'r', 'i', 'z', 'U', 'B', 'V', 'R', 'I',
                           'SDSS-I', 'SDSS-G', 'SDSS-R', 'Pan-Starrs-Z', 'Bessell-B', 'Bessell-V', 'Bessell-R',
                           'Bessell-I', 'ug', 'gr', 'gri', 'griz', 'riz', 'BVR', 'BV', 'BVRI', 'VRI']:
            sys.argv.append('--help')
        else:
            try:
                _filter = agnkey.sites.filterst(_telescope)[_filter]
            except:
                pass

    if _filter and not _field:
        if _filter == 'landolt':
            _field = 'landolt'
        elif _filter == 'sloan':
            _field = 'sloan'
        elif _filter == 'apass':
            _field = 'apass'
    if _field and not _filter:
        if _field == 'landolt':
            _filter = 'landolt'
        elif _field == 'sloan':
            _filter = 'sloan'
        elif _field == 'apass':
            _filter = 'apass'

    option, args = parser.parse_args()
    epoch = option.epoch
    if '-' not in str(epoch):
        epoch0 = datetime.date(int(epoch[0:4]), int(epoch[4:6]), int(epoch[6:8]))
        listepoch = [epoch0]
    else:
        epoch1, epoch2 = string.split(epoch, '-')
        start = datetime.date(int(epoch1[0:4]), int(epoch1[4:6]), int(epoch1[6:8]))
        stop = datetime.date(int(epoch2[0:4]), int(epoch2[4:6]), int(epoch2[6:8]))
        listepoch = [re.sub('-', '', str(i)) for i in
                     [start + datetime.timedelta(days=x) for x in range(0, 1 + (stop - start).days)]]

    if not _stage or _stage in ['local', 'getmag', 'wcs', 'psf', 'psf2', 'psfmag', 'makestamp', 'mergeall','apmag',\
                                'cosmic', 'idlstart','diff','update','copy','remove']:
        if len(listepoch) == 1:
            lista = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, _table, 'dateobs', str(listepoch[0]),
                                                    '', '*', _telescope)
        else:
            lista = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, _table, 'dateobs', str(listepoch[0]),
                                                    str(listepoch[-1]), '*', _telescope)
        if lista:
            ll0 = {}
            for jj in lista[0].keys():
                ll0[jj] = []
            for i in range(0, len(lista)):
                for jj in lista[0].keys():
                    ll0[jj].append(lista[i][jj])
            inds = argsort(ll0['mjd'])  # sort by jd
            for i in ll0.keys():
                ll0[i] = take(ll0[i], inds)
            ll0['ra'] = ll0['ra0'][:]
            ll0['dec'] = ll0['dec0'][:]
            ll = agnkey.agnloopdef.filtralist(ll0, _filter, _id, _name, _ra, _dec, _bad, _filetype)
            print '##' * 50
            print "# IMAGE                                  OBJECT           FILTER           WCS           PSF   " + \
                  "        PSFMAG    APMAG       ZCAT          MAG      ABSCAT"
            for i in range(0, len(ll['namefile'])):
                try:
                    print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                          (str(re.sub('.fits', '', ll['namefile'][i])), str(ll['objname'][i]), str(ll['filter'][i]),
                           str(ll['wcs'][i]), str(re.sub('.fits', '', ll['psf'][i])),
                           str(round(ll['psfmag'][i], 4)), str(ll['apmag'][i]), str(re.sub('.cat', '', ll['zcat'][i])),
                           str(round(ll['mag'][i], 4)), str(re.sub('.cat', '', ll['abscat'][i])))
                except:
                    print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                          (str(ll['namefile'][i]), str(ll['objname'][i]), str(ll['filter'][i]), str(ll['wcs'][i]),
                           str(ll['psf'][i]), str(ll['psfmag'][i]), str(ll['apmag'][i]), str(ll['zcat'][i]),
                           str(ll['mag'][i]), str(ll['abscat'][i]))
            print '\n###  total number = ' + str(len(ll['namefile']))
            # ####################################
            if _stage == 'local':  # calibrate local sequence from .cat files
                agnkey.agnloopdef.run_local(ll['namefile'], _field, _interactive)

            elif _stage == 'getmag':  # get final magnitude from mysql
                if not _field:
                    sys.exit('use option --field landolt or sloan')
                else:
                    fields = [_field]
                for ff in fields:
                    setup = agnkey.agnloopdef.run_getmag(ll, _field, _output, _interactive, _show, _bin, _type,
                                                         _table, _ra, _dec)

            elif _stage == 'psf':
                agnkey.agnloopdef.run_psf(ll['namefile'], _threshold, _interactive, _fwhm, _show, _redo,
                                          XX, _fix, _catalogue, _table, _dmax)

            elif _stage == 'psf2':
                agnkey.agnloopdef.run_psf2(ll['namefile'], _threshold, _interactive, _fwhm, _show, _redo,
                                           XX, _fix, _catalogue, _table, _dmax)

            elif _stage == 'psfmag':
                agnkey.agnloopdef.run_fit(ll['namefile'], _ras, _decs, _xord, _yord, _bkg, _size, _recenter, _ref,
                                          _interactive, _show, _redo, _dmax)

            elif _stage == 'wcs':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                agnkey.agnloopdef.run_wcs(listfile, _interactive, _redo, _xshift, _yshift, _catalogue,_table,_mode)

            elif _stage == 'copy':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                for imgname in listfile:
                    if _clean:
                        if os.path.isfile(re.sub('.fits','.clean.fits',imgname)):
                            print('cp '+re.sub('.fits','.clean.fits',imgname)+' ./')
                            os.system('cp '+re.sub('.fits','.clean.fits',imgname)+' ./')
                        else:
                            print('warning: cosmic rejection not done: '+imgname)
                    else:
                            os.system('cp ' + imgname + ' ./')
                            print('cp ' + imgname + ' ./')
            elif _stage == 'remove':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                agnkey.agnloopdef.run_remove(listfile, _filetype, _redo)
            elif _stage == 'makestamp':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                if _show:
                    p = Pool(1)
                else:
                    p = Pool(_multicore)
                inp = [([i],_table,_z1, _z2, _interactive,_redo,_output) for i in listfile]
                p.imap_unordered(multi_run_makestamp, inp)
                p.close()
                p.join()
#                agnkey.agnloopdef.makestamp(listfile, _table, _z1, _z2, _interactive, _redo, _output)

            elif _stage == 'apmag':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                listfile = [re.sub('.fits', '.sn2.fits',i) for i in listfile]
                if _show:
                    p = Pool(1)
                else:
                    p = Pool(_multicore)
                inp = [([i],_table,_ra, _dec, _catalogue,_show) for i in listfile]
                p.map(multi_run_apmag, inp)
                p.close()
                p.join()
#                agnkey.agnloopdef.run_apmag(ll['namefile'], _table,_ra,_dec,_catalogue,_show)

            elif _stage == 'cosmic':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]

                p = Pool(_multicore)
                inp = [([i], _table,4.5, 0.2, 4,_redo) for i in listfile]
                p.map(multi_run_cosmic, inp)
                p.close()
                p.join()
                #agnkey.agnloopdef.run_cosmic(listfile, _table, 4.5, 0.2, 4, _redo)

            elif _stage == 'idlstart':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                agnkey.agnloopdef.run_idlstart(listfile, _table, _redo)

            elif _stage == 'mergeall':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                agnkey.agnloopdef.run_merge(array(listfile), _redo)

            elif _stage == 'update':
                listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                agnkey.agnloopdef.updatefromheader(listfile,_header, _column, _table)

            elif _stage == 'diff':  # difference images using hotpants
                        if not _name:
                            sys.exit('you need to select one object: use option -n/--name')
                        if _tempdate:
                            lista1 = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, _table, 'dateobs',
                                                                     str(_tempdate), '', '*', _telescope)
                        else:
                            lista1 = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, _table, 'dateobs',
                                                                     '20120101', '20150101', '*', _telescope)
                        if lista1:
                            ll00 = {}
                            for jj in lista1[0].keys():
                                ll00[jj] = []
                            for i in range(0, len(lista1)):
                                for jj in lista1[0].keys():
                                    ll00[jj].append(lista1[i][jj])
                            inds = argsort(ll00['mjd'])  #  sort by jd
                            for i in ll00.keys():
                                ll00[i] = take(ll00[i], inds)
                            lltemp = agnkey.agnloopdef.filtralist(ll00, _filter, '', _name, _ra, _dec, _bad, 4)
                        else:
                            sys.exit('template not found')

                        imglisttar = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                        imglisttemp = [k + v for k, v in zip(lltemp['wdirectory'], lltemp['namefile'])]
##################################
#################    adding here the split by filter to be able to run multicore
##################################
                        listatar = {}
                        # divide targets by filter and targetid
                        for img in imglisttar:
                            hdr = agnkey.util.readhdr(img)
                            try:
                                _targetid = agnkey.agnsqldef.targimg(img)
                            except:
                                _targetid = 1
                        
                            _filt = agnkey.util.readkey3(hdr, 'filter')
                            _filter = agnkey.sites.filterst1(agnkey.util.readkey3(hdr, 'telescop'))[_filt]
                        
                            _obj = agnkey.util.readkey3(hdr, 'object')
                            if _filter not in listatar:
                                listatar[_filter] = {}
                            if _targetid not in listatar[_filter]:
                                listatar[_filter][_targetid] = []
                            listatar[_filter][_targetid].append(img)
                        
                        # divide template by filter and targetid
                        listatemp = {}
                        for img in imglisttemp:
                            hdr = agnkey.util.readhdr(img)
                            try:
                                _targetid = agnkey.agnsqldef.targimg(img)
                            except:
                                _targetid = 1
                            _filt = agnkey.util.readkey3(hdr, 'filter')
                            _filter = agnkey.sites.filterst1(agnkey.util.readkey3(hdr, 'telescop'))[_filt]
                        
                            _obj = agnkey.util.readkey3(hdr, 'object')
                            if _filter not in listatemp:
                                listatemp[_filter] = {}
                            if _targetid not in listatemp[_filter]:
                                listatemp[_filter][_targetid] = []
                            listatemp[_filter][_targetid].append(img)
                        inp = []
                        for f in listatar:
                            for o in listatar[f]:
                                if f in listatemp:
                                    if o in listatemp[f]:
                                        imglist1 = listatar[f][o]
                                        imglist2 = listatemp[f][o]
                                        inp = list(inp)+list([(array([i]),array(imglist2[0:1]),
                                                               _show, _redo,_normalize) for i in imglist1])

                        if len(inp):

                            if _show:
                                p = Pool(1)
                            else:
                                p = Pool(_multicore)
                            p.map(multi_run_diff, inp)
                            p.close()
                            p.join()
                        else:
                            sys.exit('no data selected ')
##################################
##################################
#                        agnkey.agnloopdef.run_diff(array(listtar), array(listtemp), _show, _redo, _normalize)
#                        if len(listtemp) == 0 or len(listtar) == 0:
#                            sys.exit('no data selected ')




        else:
            print '\n### no data selected'
    # ################################################
    else:
        for epo in listepoch:
            print '\n#### ' + str(epo)
            lista = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, _table, 'dateobs', str(epo), '', '*',
                                                    _telescope)
            if lista:
                ll0 = {}
                for jj in lista[0].keys():
                    ll0[jj] = []
                for i in range(0, len(lista)):
                    for jj in lista[0].keys():
                        ll0[jj].append(lista[i][jj])

                inds = argsort(ll0['mjd'])  # sort by jd
                for i in ll0.keys():
                    ll0[i] = take(ll0[i], inds)
                ll0['ra'] = ll0['ra0'][:]
                ll0['dec'] = ll0['dec0'][:]
                ll = agnkey.agnloopdef.filtralist(ll0, _filter, _id, _name, _ra, _dec, _bad, _filetype)
                if len(ll['namefile']) > 0:
                    for i in range(0, len(ll['namefile'])):
                        print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                              (str(ll['namefile'][i]), str(ll['objname'][i]), str(ll['filter'][i]), str(ll['wcs'][i]),
                               str(ll['psf'][i]), str(ll['psfmag'][i]), str(ll['zcat'][i]), str(ll['mag'][i]),
                               str(ll['abscat'][i]))
                    print '\n###  total number = ' + str(len(ll['namefile']))
                if _stage and len(ll['namefile']) > 0:
                    print '##' * 50
                    ll3 = {}
                    for ii in ll.keys():       
                        ll3[ii] = ll[ii]
                    if _stage == 'zcat':
                        if not _field:
                            if _filter in ['U', 'B', 'V', 'R', 'I', 'landolt']:
                                _field = 'landolt'
                            elif _filter in ['u', 'g', 'r', 'i', 'z', 'sloan']:
                                _field = 'sloan'
                            elif _filter in ['apass']:
                                _field = 'apass'
                            else:
                                _field = 'sloan'

                        if _field == 'apass':
                            ww0 = asarray([i for i in range(len(ll3['filter'])) if (ll['filter'][i] in ['V', 'B'])])
                            ww1 = asarray(
                                [i for i in range(len(ll3['filter'])) if (ll['filter'][i] in ['gp', 'rp', 'ip'])])
                            _color = ''
                            if len(ww0) >= 1:
                                _color = 'BV'
                                agnkey.agnloopdef.run_zero(ll3['namefile'][ww0], _fix, _type, _field, _catalogue,
                                                           _color, _interactive, _redo, _show, _cutmag, _table,
                                                           _calib)

                            if len(ww1) >= 1:
                                _color = ''
                                for jj in ['gp', 'rp', 'ip']:
                                    if jj in list(set(ll3['filter'])):
                                        _color = _color + agnkey.sites.filterst1(_telescope)[jj]
                                agnkey.agnloopdef.run_zero(ll3['namefile'][ww1], _fix, _type, _field, _catalogue,
                                                           _color, _interactive, _redo, _show, _cutmag, _table,
                                                           _calib)
                        elif _field == 'landolt':
                            ww0 = asarray([i for i in range(len(ll3['filter'])) if
                                           (ll['filter'][i] in ['U', 'I', 'R', 'V', 'B'])])
                            _color = ''
                            for jj in ['U', 'I', 'R', 'V', 'B']:
                                if jj in list(set(ll3['filter'])):
                                    _color = _color + agnkey.sites.filterst1(_telescope)[jj]
                            if len(ww0) >= 1:
                                agnkey.agnloopdef.run_zero(ll3['namefile'][ww0], _fix, _type, _field, _catalogue,
                                                           _color, _interactive, _redo, _show, _cutmag, _table,
                                                           _calib)
                        elif _field == 'sloan':
                            ww0 = asarray([i for i in range(len(ll3['filter'])) if
                                           (ll['filter'][i] in ['us', 'gp', 'rp', 'ip', 'zs'])])
                            _color = ''
                            for jj in ['gp', 'us', 'rp', 'ip', 'zs']:
                                if jj in list(set(ll3['filter'])):
                                    _color = _color + agnkey.sites.filterst1(_telescope)[jj]
                            if len(ww0) >= 1:
                                agnkey.agnloopdef.run_zero(ll3['namefile'][ww0], _fix, _type, _field, _catalogue,
                                                           _color, _interactive, _redo, _show, _cutmag, _table,
                                                           _calib)
                        else:
                            print 'warning: field not defined, zeropoint not computed'

                    elif _stage == 'abscat':  # compute magnitudes for sequence stars > img.cat
                        if _standard:
                            mm = agnkey.agnloopdef.filtralist(ll0, _filter, '', _standard, '', '', '', _filetype)
                            if len(mm['namefile']) > 0:
                                for i in range(0, len(mm['namefile'])):
                                    print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                                          (str(mm['namefile'][i]), str(mm['objname'][i]), str(mm['filter'][i]),
                                           str(mm['wcs'][i]), str(mm['psf'][i]),
                                           str(mm['psfmag'][i]), str(mm['zcat'][i]), str(mm['mag'][i]),
                                           str(mm['abscat'][i]))
                                agnkey.agnloopdef.run_cat(ll3['namefile'], mm['namefile'], _interactive, 1, _type, _fix,
                                                          _table, _field)
                            else:
                                print '\n### warning : standard not found for this night ' + str(epo)
                        else:
                            agnkey.agnloopdef.run_cat(ll3['namefile'], '', _interactive, 1, _type, _fix, _table,
                                                      _field)
                    elif _stage == 'mag':  # compute final magnitude using:   mag1  mag2  Z1  Z2  C1  C2
                        if _standard:
                            mm = agnkey.agnloopdef.filtralist(ll0, _filter, '', _standard, '', '', '', _filetype)
                            if len(mm['namefile']) > 0:
                                for i in range(0, len(mm['namefile'])):
                                    print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                                          (str(mm['namefile'][i]), str(mm['objname'][i]), str(mm['filter'][i]),
                                           str(mm['wcs'][i]), str(mm['psf'][i]),
                                           str(mm['psfmag'][i]), str(mm['zcat'][i]), str(mm['mag'][i]),
                                           str(mm['abscat'][i]))
                                agnkey.agnloopdef.run_cat(ll3['namefile'], mm['namefile'], _interactive, 2, _type,
                                                          False, _table, _field)
                            else:
                                print '\n### error: standard not found for this night' + str(epo)
                        else:
                            agnkey.agnloopdef.run_cat(ll3['namefile'], '', _interactive, 2, _type, False, _table,
                                                      _field)
                    elif _stage == 'merge':  # merge images using lacos and swarp
                        listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                        agnkey.agnloopdef.run_merge(array(listfile), _redo)
                    elif _stage == 'template':  # merge images using lacos and swarp
                        listfile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
                        agnkey.agnloopdef.run_template(array(listfile), _show, _redo, _interactive,\
                                                       _ra, _dec, _psf, _mag, _clean, _subtract_mag_from_header)
                        #agnkey.agnloopdef.run_template(array(listfile), _show, _redo)
                    else:
                        print _stage + ' not defined'
            else:
                print '\n### no data selected'
