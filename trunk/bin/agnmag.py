#!/usr/bin/env python
description = ">> make final magnitude"
usage = "%prog image [options] "

import os
import string
import re
import sys
from optparse import OptionParser
import time
import math
import agnkey
import numpy as np


if __name__ == "__main__":
    start_time = time.time()
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-i", "--interactive", action="store_true", dest='interactive', default=False,
                      help='Interactive \t\t\t [%default]')
    parser.add_option("-e", "--exzp", dest="exzp", default='',
                      type='str', help='external zero point from different field \t\t %default')
    parser.add_option("-t", "--typemag", dest="typemag", default='fit',
                      type='str', help='type of magnitude fit,ph \t\t %default')
    parser.add_option("--datatable", dest="datatable", default='dataredulco',
                      type='str', help='mysql table where stroe reduction info \t\t %default')
    parser.add_option("--calib", dest="calibration", default='sloan',
                      type='str', help='calibration to  (sloan,sloanprime,natural,apass) \t\t %default')
    parser.add_option("-s", "--system", dest="field", default='',
                      type='str', help='photometric system [sloan, landolt] \t\t %default')

    option, args = parser.parse_args()
    if len(args) < 1:
        sys.argv.append('--help')
    _typemag = option.typemag
    if _typemag not in ['fit', 'ph']:
        sys.argv.append('--help')
    option, args = parser.parse_args()
    imglist = args[0]
    lista = agnkey.util.readlist(imglist)
    hdr = agnkey.util.readhdr(lista[0])
    tel = agnkey.util.readkey3(hdr, 'telescop')
    filters = agnkey.sites.filterst(tel)
    filters1 = agnkey.sites.filterst1(tel)
    _datatable = option.datatable
    _exzp = option.exzp
    _calib = option.calibration
    _field = option.field
    _interactive = option.interactive
    typemag = 'PSFMAG1'
    typemagerr = 'PSFDMAG1'
    namemag = {'fit': ['PSFMAG1', 'PSFDMAG1'], 'ph': ['APMAG1', 'PSFDMAG1']}
    dicti0 = agnkey.util.makecatalogue(lista)
    dicti = {}
    for _filter in dicti0:
        for img in dicti0[_filter]:
            if dicti0[_filter][img][namemag[_typemag][0]] != 9999:
                if _filter not in dicti:
                    dicti[_filter] = {}
                if img not in dicti[_filter]:
                    dicti[_filter][img] = {}
                for key in dicti0[_filter][img].keys():
                    dicti[_filter][img][key] = dicti0[_filter][img][key]

    if len(dicti) > 0:
        allfilters = ''
        for fil in dicti:
            allfilters = allfilters + filters1[fil]
        if _interactive:
            print allfilters
        if _field == 'apass' or _calib == 'apass':
            queste0 = agnkey.agnloopdef.chosecolor(allfilters, False, 'apass')
            queste1 = agnkey.agnloopdef.chosecolor(allfilters, True, 'apass')
        else:
            queste0 = agnkey.agnloopdef.chosecolor(allfilters, False)
            queste1 = agnkey.agnloopdef.chosecolor(allfilters, True)
        if _exzp:
            lista2 = agnkey.util.readlist(_exzp)
            dicti2 = agnkey.util.makecatalogue(lista2)
            for _filter2 in dicti2:
                img2 = dicti2[_filter2].keys()[0]
                for jj in dicti2[_filter2][img2].keys():
                    if 'ZP' in jj:
                        if _filter2 in dicti:
                            for img in dicti[_filter2].keys():
                                dicti[_filter2][img][jj] = dicti2[_filter2][img2][jj]
                                agnkey.util.updateheader(img, 0,
                                                         {jj: [dicti2[_filter2][img2][jj], 'a b sa sb in y=a+bx']})
                                agnkey.util.updateheader(img, 0, {'CATALOG': [str(img2), 'catalogue source']})
                                print jj, dicti2[_filter2][img2][jj]

        for _filter in dicti:
            for img in dicti[_filter]:
                if _interactive: print '\#### ', img
                # if dicti[_filter][img][namemag[_typemag][0]]!=9999:
                # start calibrating image 1
                secondimage = []
                jdvec = []
                filtvec = []
                colore = []
                for ii in dicti[_filter][img].keys():
                    if 'ZP' in ii:  #  for each zero point available
                        cc = ii[-2:]  #  color used
                        for filt2 in dicti.keys():
                            if filt2 != _filter:
                                for jj in dicti[filt2].keys():
                                    for ll in dicti[filt2][jj].keys():
                                        if 'ZP' in ll and ll[-2:] == cc:
                                            secondimage.append(jj)
                                            jdvec.append(dicti[filt2][jj]['MJD'] - dicti[_filter][img]['MJD'])
                                            filtvec.append(filt2)
                                            colore.append(cc)
                if len(secondimage) > 0:
                    colorescelto = ''
                    vv = queste1[agnkey.sites.filterst1(tel)[_filter]]
                    if len(vv) > 0:
                        if vv[0].upper() in colore:
                            colorescelto = vv[0].upper()
                    else:
                        vv = queste0[agnkey.sites.filterst1(tel)[_filter]]
                        if len(vv) > 0:
                            if vv[0].upper() in colore:
                                colorescelto = vv[0].upper()
                    if colorescelto:
                        print 'use ' + _filter + ' with color ' + colorescelto
                        filtvec = np.compress(np.array(colore) == colorescelto, filtvec)
                        jdvec = np.compress(np.array(colore) == colorescelto, jdvec)
                        secondimage = np.compress(np.array(colore) == colorescelto, secondimage)
                        colore = np.compress(np.array(colore) == colorescelto, colore)

                    dicti[_filter][img]['secondimg'] = secondimage[np.argmin(jdvec)]
                    dicti[_filter][img]['secondfilt'] = filtvec[np.argmin(jdvec)]
                    _filter2 = dicti[_filter][img]['secondfilt']
                    img2 = dicti[_filter][img]['secondimg']
                    col = colore[np.argmin(jdvec)]

                    if dicti[_filter][img]['telescope'] in ['lsc', '1m0-04', '1m0-05', '1m0-06', '1m0-09']:
                        kk = agnkey.sites.extintion('ctio')
                    elif dicti[_filter][img]['telescope'] in ['elp', '1m0-08']:
                        kk = agnkey.sites.extintion('mcdonald')
                    elif dicti[_filter][img]['telescope'] in ['cpt', '1m0-12', '1m0-10', '1m0-13']:
                        kk = agnkey.sites.extintion('southafrica')
                    elif dicti[_filter][img]['telescope'] in ['ftn']:
                        kk = agnkey.sites.extintion('mauna')
                    elif dicti[_filter][img]['telescope'] in ['1m0-03', '1m0-11', 'fts', 'coj']:
                        kk = agnkey.sites.extintion('siding')
                    else:
                        print _filter, img, dicti[_filter][img]
                        sys.exit('problem with dicti')

                    if _interactive:
                        print dicti[_filter][img]['airmass']
                        print kk[filters1[_filter]]
                        print 2.5 * math.log10(dicti[_filter][img]['exptime'])
                        print dicti[_filter][img][namemag[_typemag][0]]
                        #  instrumental mag corrected for exp time and airmass
                    #                mag0=dicti[_filter][img][namemag[_typemag][0]]+2.5*math.log10(dicti[_filter][img]['exptime'])-kk[filters1[_filter]]*dicti[_filter][img]['airmass']
                    mag0 = dicti[_filter][img][namemag[_typemag][0]] - kk[filters1[_filter]] * dicti[_filter][img][
                        'airmass']
                    dmag0 = dicti[_filter][img][namemag[_typemag][1]]

                    if dicti[_filter2][img2]['telescope'] in ['1m0-04', '1m0-05', '1m0-06', '1m0-09']:
                        kk = agnkey.sites.extintion('ctio')
                    elif dicti[_filter2][img2]['telescope'] in ['elp', '1m0-08']:
                        kk = agnkey.sites.extintion('mcdonald')
                    elif dicti[_filter2][img2]['telescope'] in ['cpt', '1m0-12', '1m0-10', '1m0-13']:
                        kk = agnkey.sites.extintion('southafrica')
                    elif dicti[_filter][img]['telescope'] in ['ftn']:
                        kk = agnkey.sites.extintion('mauna')
                    elif dicti[_filter][img]['telescope'] in ['1m0-03', '1m0-11', 'coj', 'fts']:
                        kk = agnkey.sites.extintion('siding')
                    else:
                        print dicti[_filter2][img2]
                        sys.exit('problem with dicti')  #  instrumental mag corrected for exp time and airmass
                    #                mag1=dicti[_filter2][img2][namemag[_typemag][0]]+2.5*math.log10(dicti[_filter2][img2]['exptime'])-kk[filters1[_filter2]]*dicti[_filter2][img2]['airmass']
                    mag1 = dicti[_filter2][img2][namemag[_typemag][0]] - kk[filters1[_filter2]] * dicti[_filter2][img2][
                        'airmass']
                    dmag1 = dicti[_filter2][img2][namemag[_typemag][1]]

                    if filters1[_filter].upper() == col[0]:
                        Z1 = float(string.split(dicti[_filter][img]['ZP' + filters1[_filter].upper() + col.upper()])[1])
                        C1 = float(string.split(dicti[_filter][img]['ZP' + filters1[_filter].upper() + col.upper()])[2])
                        Z2 = float(
                            string.split(dicti[_filter2][img2]['ZP' + filters1[_filter2].upper() + col.upper()])[1])
                        C2 = float(
                            string.split(dicti[_filter2][img2]['ZP' + filters1[_filter2].upper() + col.upper()])[2])
                        M1, M2 = agnkey.agnabsphotdef.finalmag(Z1, Z2, C1, C2, mag0, mag1)

                        DZ1 = 0.0
                        DZ2 = 0.0
                        dc1, dc2, dz1, dz2, dm1, dm2 = agnkey.agnabsphotdef.erroremag(Z1, Z2, mag0, mag1, C1, C2, 0)
                        DM11 = np.sqrt((dm1 * dmag0) ** 2 + (dz1 * DZ1) ** 2 + (dm2 * dmag1) ** 2 + (dz2 * DZ2) ** 2)

                        if _interactive:
                            print '\n####  example computation '
                            print 'Z1  Z1  C1   C2   mag1    mag 2'
                            print 'M1   M2 '
                            print img, img2
                            print _filter, _filter2
                            print Z1, Z2, C1, C2, mag0, mag1
                            print M1, M2
                        try:
                            if np.isfinite(M1) and M1 < 999:
                                agnkey.agnsqldef.updatevalue(_datatable, 'mag', M1,
                                                             re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                if _typemag == 'fit':
                                    agnkey.agnsqldef.updatevalue(_datatable, 'magtype', 2,
                                                                 re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                elif _typemag == 'ph':
                                    agnkey.agnsqldef.updatevalue(_datatable, 'magtype', 3,
                                                                 re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                agnkey.util.updateheader(img, 0, {'mag': [M1, 'calibrated mag']})
                            else:
                                agnkey.agnsqldef.updatevalue(_datatable, 'mag', 9999,
                                                             re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                agnkey.util.updateheader(img, 0, {'mag': [9999, 'calibrated mag']})
                            if np.isfinite(DM11):
                                agnkey.agnsqldef.updatevalue(_datatable, 'dmag', DM11,
                                                             re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                agnkey.util.updateheader(img, 0, {'dmag': [DM11, 'calibrated mag error']})
                            else:
                                agnkey.agnsqldef.updatevalue(_datatable, 'dmag', 9999,
                                                             re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                agnkey.util.updateheader(img, 0, {'dmag': [9999, 'calibrated mag error']})
                        except:
                            print 'module mysqldef not found'
                    else:
                        Z2 = float(string.split(dicti[_filter][img]['ZP' + filters1[_filter].upper() + col.upper()])[1])
                        C2 = float(string.split(dicti[_filter][img]['ZP' + filters1[_filter].upper() + col.upper()])[2])
                        Z1 = float(
                            string.split(dicti[_filter2][img2]['ZP' + filters1[_filter2].upper() + col.upper()])[1])
                        C1 = float(
                            string.split(dicti[_filter2][img2]['ZP' + filters1[_filter2].upper() + col.upper()])[2])
                        M1, M2 = agnkey.agnabsphotdef.finalmag(Z1, Z2, C1, C2, mag1, mag0)

                        DZ1 = 0.0
                        DZ2 = 0.0
                        dc1, dc2, dz1, dz2, dm1, dm2 = agnkey.agnabsphotdef.erroremag(Z1, Z2, mag0, mag1, C1, C2, 1)
                        DM22 = np.sqrt((dm1 * dmag0) ** 2 + (dz1 * DZ1) ** 2 + (dm2 * dmag1) ** 2 + (dz2 * DZ2) ** 2)

                        if _interactive:
                            print '\n####  example computation '
                            print 'Z1  Z1  C1   C2   mag1    mag 2'
                            print 'M1   M2 '
                            print Z1, Z2, C1, C2, mag1, mag0
                            print M1, M2
                        try:
                            if np.isfinite(M2) and M2 < 999:
                                agnkey.agnsqldef.updatevalue(_datatable, 'mag', M2,
                                                             re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                if _typemag == 'fit':
                                    agnkey.agnsqldef.updatevalue(_datatable, 'magtype', 2,
                                                                 re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                elif _typemag == 'ph':
                                    agnkey.agnsqldef.updatevalue(_datatable, 'magtype', 3,
                                                                 re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                agnkey.util.updateheader(img, 0, {'mag': [M2, 'calibrated mag']})
                            else:
                                agnkey.agnsqldef.updatevalue(_datatable, 'mag', 9999,
                                                             re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                agnkey.util.updateheader(img, 0, {'mag': [9999, 'calibrated mag']})
                            if np.isfinite(DM22):
                                agnkey.agnsqldef.updatevalue(_datatable, 'dmag', DM22,
                                                             re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                agnkey.util.updateheader(img, 0, {'dmag': [DM22, 'calibrated mag error']})
                            else:
                                agnkey.agnsqldef.updatevalue(_datatable, 'dmag', 9999,
                                                             re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                                agnkey.util.updateheader(img, 0, {'dmag': [9999, 'calibrated mag error']})
                        except:
                            print 'module mysqldef not found'
                    print _filter, col
                else:
                    if dicti[_filter][img]['telescope'] in ['lsc', '1m0-04', '1m0-05', '1m0-06', '1m0-09']:
                        kk = agnkey.sites.extintion('ctio')
                    elif dicti[_filter][img]['telescope'] in ['elp', '1m0-08']:
                        kk = agnkey.sites.extintion('mcdonald')
                    elif dicti[_filter][img]['telescope'] in ['cpt', '1m0-12', '1m0-10', '1m0-13']:
                        kk = agnkey.sites.extintion('southafrica')
                    elif dicti[_filter][img]['telescope'] in ['ftn']:
                        kk = agnkey.sites.extintion('mauna')
                    elif dicti[_filter][img]['telescope'] in ['1m0-03', '1m0-11', 'coj', 'fts']:
                        kk = agnkey.sites.extintion('siding')
                    else:
                        print _filter, img, dicti[_filter][img]
                        sys.exit('problem with dicti')
                    Z1 = ''
                    for ww in dicti[_filter][img].keys():
                        if 'ZP' + filters1[_filter].upper() == ww[0:3] and float(
                                string.split(dicti[_filter][img][ww])[1]) < 99:
                            Z1 = float(string.split(dicti[_filter][img][ww])[1])
                            C1 = float(string.split(dicti[_filter][img][ww])[2])
                            break
                        #                mag0=dicti[_filter][img][namemag[_typemag][0]]+2.5*math.log10(dicti[_filter][img]['exptime'])-kk[filters1[_filter]]*dicti[_filter][img]['airmass']
                    mag0 = dicti[_filter][img][namemag[_typemag][0]] - kk[filters1[_filter]] * dicti[_filter][img][
                        'airmass']
                    dmag0 = dicti[_filter][img][namemag[_typemag][1]]
                    if Z1 and mag0 < 99:
                        M1 = mag0 + Z1
                        agnkey.agnsqldef.updatevalue(_datatable, 'mag', M1,
                                                     re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                        if _typemag == 'fit':
                            agnkey.agnsqldef.updatevalue(_datatable, 'magtype', 2,
                                                         re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                        elif _typemag == 'ph':
                            agnkey.agnsqldef.updatevalue(_datatable, 'magtype', 3,
                                                         re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                        agnkey.util.updateheader(img, 0, {'mag': [M1, 'calibrated mag']})
                    else:
                        print 'no other filters with calibration in ' + _filter + ' band'
                        print img, _filter, mag0, dmag0, Z1, C1
                        agnkey.agnsqldef.updatevalue(_datatable, 'mag', 9999,
                                                     re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                        agnkey.util.updateheader(img, 0, {'mag': [9999, 'calibrated mag']})
                        #                try:
                        #                except:
                        print 'module mysqldef not found'
    else:
        print '\n### warning: no measurement in sn2 files'
