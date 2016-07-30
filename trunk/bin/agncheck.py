#!/usr/bin/env python
description = "> Ingest raw data "
usage = "%prog  instrument -e epoch"

import sys
import string
from optparse import OptionParser
import datetime
import agnkey

if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description, version="%prog 1.0")
    parser.add_option("-e", "--epoch", dest="epoch", default='20121212', type="str",
                      help='epoch to reduce  \t [%default]')
    parser.add_option("-T", "--telescope", dest="telescope", default='all', type="str",
                      help='-T telescope ' + ', '.join(agnkey.util.telescope0['all']) + ', '.join(agnkey.util.site0) +
                           ', fts, ftn, 1m0, kb, fl \t [%default]')
    parser.add_option("-R", "--RA", dest="ra", default='', type="str",
                      help='-R  ra    \t [%default]')
    parser.add_option("-D", "--DEC", dest="dec", default='', type="str",
                      help='-D dec   \t [%default]')
    parser.add_option("-n", "--name", dest="name", default='', type="str",
                      help='-n image name   \t [%default]')
    parser.add_option("-d", "--id", dest="id", default='', type="str",
                      help='-d identification id   \t [%default]')
    parser.add_option("-f", "--filter", dest="filter", default='', type="str",
                      help='-f filter [sloan,landolt,u,g,r,i,z,U,B,V,R,I] \t [%default]')
    parser.add_option("-F", "--force", dest="force", action="store_true")
    parser.add_option("-b", "--bad", dest="bad", default='', type="str",
                      help='-b bad stage [wcs,psf,psfmag,zcat,abscat,mag,goodcat,getmag,quality,diff,apmag] \t [%default]')
    parser.add_option("-s", "--stage", dest="stage", default='', type="str",
                      help='-s stage [checkwcs,checkpsf,checkmag,checkquality,checkpos,checkcat,'
                           'checkmissing,checkfvd,checkclean] \t [%default]')
    parser.add_option("--filetype", dest="filetype", default=1, type="int",
                      help='filetype  1 [single], 2 [merge], 3 differences \t [%default]')
    parser.add_option("--z1", dest="z1", default=None, type="int",
                      help='z1 \t [%default]')
    parser.add_option("--z2", dest="z2", default=None, type="int",
                      help='z2 \t [%default]')

    option, args = parser.parse_args()
    _telescope = option.telescope
    if _telescope not in agnkey.util.telescope0['all'] + agnkey.util.site0 + ['all', 'ftn', 'fts', '1m0', 'kb', 'fl']:
        sys.argv.append('--help')
    option, args = parser.parse_args()
    _id = option.id
    _filter = option.filter
    _ra = option.ra
    _dec = option.dec
    _name = option.name
    _bad = option.bad
    _stage = option.stage
    _z1 = option.z1
    _z2 = option.z2
    _filetype = option.filetype
    if option.force == None:
        _redo = False
    else:
        _redo = True
    if _stage:
        if _stage not in ['checkfast', 'checkwcs', 'checkpsf', 'checkmag', 'checkdiff', 'checkquality', 
                          'checkpos', 'checkcat', 'checkmissing', 'checkfvd', 'checkclean']: sys.argv.append('--help')
    if _bad:
        if _bad not in ['wcs', 'psf', 'psfmag', 'zcat', 'abscat', 'mag', 'goodcat', 'quality','diff','apmag']:
            sys.argv.append('--help')
    if _filter:
        if _filter not in ['landolt', 'sloan', 'u', 'g', 'r', 'i', 'z', 'U', 'B', 'V', 'R', 'I']:
            sys.argv.append('--help')
        else:
            _filter = agnkey.sites.filterst(_telescope)[_filter]
    option, args = parser.parse_args()
    epoch = option.epoch
    if '-' not in str(epoch):
        epoch0 = datetime.date(int(epoch[0:4]), int(epoch[4:6]), int(epoch[6:8]))
        lista = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, 'dataredulco', 'dateobs',
                                                str(epoch0), '', '*', _telescope)
        # lista=getfromdataraw(agnkey.src.agnsqldef.conn, 'dataredulco', 'dateobs',str(epoch0), 'all')
    else:
        epoch1, epoch2 = string.split(epoch, '-')
        start = datetime.date(int(epoch1[0:4]), int(epoch1[4:6]), int(epoch1[6:8]))
        stop = datetime.date(int(epoch2[0:4]), int(epoch2[4:6]), int(epoch2[6:8]))
        print _telescope
        lista = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, 'dataredulco', 'dateobs', str(start),
                                                str(stop), '*', _telescope)

    if lista:
        ll0 = {}
        for jj in lista[0].keys():
            ll0[jj] = []
        for i in range(0, len(lista)):
            for jj in lista[0].keys():
                ll0[jj].append(lista[i][jj])
        ll = agnkey.agnloopdef.filtralist(ll0, _filter, _id, _name, _ra, _dec, _bad, _filetype)
        print '##' * 50
        print '# IMAGE                                    OBJECT           FILTER           WCS             PSF    ' \
              '       PSFMAG          ZCAT          MAG      ABSCAT'
        for i in range(0, len(ll['namefile'])):
            print '%s\t%12s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s\t%9s' % \
                  (str(ll['namefile'][i]), str(ll['objname'][i]), str(ll['filter'][i]), str(ll['wcs'][i]),
                   str(ll['psf'][i]), str(ll['psfmag'][i]), str(ll['zcat'][i]), str(ll['mag'][i]), str(ll['abscat'][i]))
        print '\n###  total number = ' + str(len(ll['namefile']))
        if _stage:
            print '##' * 50
            print _stage
            if _stage == 'checkpsf':
                agnkey.agnloopdef.checkpsf(ll['namefile'])
            elif _stage == 'checkmag':
                agnkey.agnloopdef.checkmag(ll['namefile'])
            elif _stage == 'checkwcs':
                agnkey.agnloopdef.checkwcs(ll['namefile'], _redo, 'dataredulco', _z1, _z2)
            elif _stage == 'checkfast':
                agnkey.agnloopdef.checkfast(ll['namefile'], _redo)
            elif _stage == 'checkquality':
                agnkey.agnloopdef.checkquality(ll['namefile'])
            elif _stage == 'checkpos':
                agnkey.agnloopdef.checkpos(ll['namefile'], _ra, _dec)
            elif _stage == 'checkcat':
                agnkey.agnloopdef.checkcat(ll['namefile'])
            elif _stage == 'checkmissing':
                agnkey.agnloopdef.check_missing(ll['namefile'])
            elif _stage == 'checkfvd':
                agnkey.agnloopdef.checkfilevsdatabase(ll)
            elif _stage == 'checkclean':
                agnkey.agnloopdef.checkclean(ll['namefile'])
            elif _stage == 'checkdiff':
                agnkey.agnloopdef.checkdiff(ll['namefile'])
            else:
                print _stage + ' not defined'
    else:
        print '\n### no data selected'
