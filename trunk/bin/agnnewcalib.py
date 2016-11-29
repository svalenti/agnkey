#!/usr/bin/env python
description = ">> new calibration"
usage = "%prog image [options] "

import string
import re
import sys
import glob
from optparse import OptionParser
import time
import agnkey
#import pyfits
import numpy as np
from astropy.io import fits as pyfits
from astropy import wcs as pywcs
import os 

"""
this task:
- query vizier (or local catalog)
- read sn2.fits catalogue 
- compute zeropoint using sn2.fits mag and catalog 
- measure daophot aperture magnitude on target with 3 aperture 
"""
def vizq(_ra, _dec, catalogue, radius,verbose=False):
    ''' Query vizquery '''
    import os, string, re

    _site = 'vizier.cfa.harvard.edu'
    # _site='vizier.u-strasbg.fr'
    cat = {'usnoa2': ['I/252/out', 'USNO-A2.0', 'Rmag'], '2mass': ['II/246/out', '2MASS', 'Jmag'],
           'landolt': ['II/183A/table2', '', 'Vmag,B-V,U-B,V-R,R-I,Star,e_Vmag'],
           'apass': ['I/322A/out', '', 'Bmag,Vmag,gmag,rmag,imag,e_Vmag,e_Bmag,e_gmag,e_rmag,e_imag,UCAC4'],
           'usnob1': ['I/284/out', 'USNO-B1.0', 'R2mag'],
           'sdss9': ['V/139/sdss9', '', 'objID,umag,gmag,rmag,imag,zmag,e_umag,e_gmag,e_rmag,e_imag,e_zmag,gc'],
           'sdss7': ['II/294/sdss7', '', 'objID,umag,gmag,rmag,imag,zmag,e_umag,e_gmag,e_rmag,e_imag,e_zmag,gc'],
           'sdss8': ['II/306/sdss8', '', 'objID,umag,gmag,rmag,imag,zmag,e_umag,e_gmag,e_rmag,e_imag,e_zmag,gc']}

    a = os.popen('vizquery -mime=tsv  -site=' + _site + ' -source=' + cat[catalogue][0] + \
                 ' -c.ra=' + str(_ra) + ' -c.dec=' + str(_dec) + ' -c.eq=J2000 -c.rm=' + str(radius) + \
                 ' -c.geom=b -oc.form=h -sort=_RA*-c.eq -out.add=_RAJ2000,_DEJ2000 -out.max=10000 -out=' + \
                 cat[catalogue][1] + ' -out=' + cat[catalogue][2] + '').read()
    if verbose:
        print 'vizquery -mime=tsv  -site=' + _site + ' -source=' + cat[catalogue][0] + \
            ' -c.ra=' + str(_ra) + ' -c.dec=' + str(_dec) + ' -c.eq=J2000 -c.rm=' + str(radius) + \
                      ' -c.geom=b -oc.form=h -sort=_RA*-c.eq -out.add=_RAJ2000,_DEJ2000 -out.max=10000 -out=' + \
                      cat[catalogue][1] + ' -out=' + cat[catalogue][2] + ''
    aa = a.split('\n')
    bb = []
    for i in aa:
        if i and i[0] != '#':   bb.append(i)
    _ra, _dec, _name, _mag = [], [], [], []
    for ii in bb[3:]:
        aa = ii.split('\t')
        rr, dd = agnkey.agnabsphotdef.deg2HMS(ra=re.sub(' ', ':', aa[0]), dec=re.sub(' ', ':', aa[1]), round=False)
        _ra.append(rr)
        _dec.append(dd)
        _name.append(aa[2])
    dictionary = {'ra': _ra, 'dec': _dec, 'id': _name}
    sss = string.split(cat[catalogue][2], ',')
    for ii in sss: dictionary[ii] = []
    for ii in bb[3:]:
        aa = ii.split('\t')
        for gg in range(0, len(sss)):
            if sss[gg] not in ['UCAC4', 'id']:
                try:
                    dictionary[sss[gg]].append(float(aa[2 + gg]))
                except:
                    dictionary[sss[gg]].append(float(9999))
            else:
                dictionary[sss[gg]].append(str(aa[2 + gg]))

    if catalogue in ['sdss7', 'sdss9', 'sdss8']:
        dictionary['u'] = dictionary['umag']
        dictionary['g'] = dictionary['gmag']
        dictionary['r'] = dictionary['rmag']
        dictionary['i'] = dictionary['imag']
        dictionary['z'] = dictionary['zmag']
        dictionary['uerr'] = dictionary['e_umag']
        dictionary['gerr'] = dictionary['e_gmag']
        dictionary['rerr'] = dictionary['e_rmag']
        dictionary['ierr'] = dictionary['e_imag']
        dictionary['zerr'] = dictionary['e_zmag']
        for key in dictionary.keys():
            if key != 'r':
                dictionary[key] = np.compress((np.array(dictionary['r']) < 19) & (np.array(dictionary['r'] > 10)),
                                              dictionary[key])
        dictionary['r'] = np.compress((np.array(dictionary['r']) < 19) & (np.array(dictionary['r'] > 10)),
                                      dictionary['r'])

    elif catalogue == 'landolt':
        dictionary['B'] = np.array(dictionary['Vmag']) + np.array(dictionary['B-V'])
        dictionary['U'] = np.array(dictionary['B']) + np.array(dictionary['U-B'])
        dictionary['V'] = np.array(dictionary['Vmag'])
        dictionary['Verr'] = np.array(dictionary['e_Vmag'])
        dictionary['R'] = np.array(dictionary['Vmag']) - np.array(dictionary['V-R'])
        dictionary['I'] = np.array(dictionary['R']) - np.array(dictionary['R-I'])
        dictionary['id'] = np.array(dictionary['Star'])
    elif catalogue == 'apass':
        dictionary['B'] = np.array(dictionary['Bmag'])
        dictionary['V'] = np.array(dictionary['Vmag'])
        dictionary['g'] = np.array(dictionary['gmag'])
        dictionary['r'] = np.array(dictionary['rmag'])
        dictionary['i'] = np.array(dictionary['imag'])
        dictionary['Berr'] = np.array(dictionary['e_Bmag'], float) / 100.
        dictionary['Verr'] = np.array(dictionary['e_Vmag'], float) / 100.
        dictionary['gerr'] = np.array(dictionary['e_gmag'], float) / 100.
        dictionary['rerr'] = np.array(dictionary['e_rmag'], float) / 100.
        dictionary['ierr'] = np.array(dictionary['e_imag'], float) / 100.
        dictionary['id'] = np.array(dictionary['UCAC4'], str)
        for key in dictionary.keys():
            if key != 'r':
                dictionary[key] = np.compress((np.array(dictionary['r']) < 22) & (np.array(dictionary['r'] > 10.5)),
                                              dictionary[key])
        dictionary['r'] = np.compress((np.array(dictionary['r']) < 22) & (np.array(dictionary['r'] > 10.5)),
                                      dictionary['r'])
    return dictionary


# #######################################################################
def crossmatch(_ra0, _dec0, _ra1, _dec1, tollerance):  # degree,degree,degree,degree,arcsec
    from numpy import pi, cos, sin, array, argmin, min, arccos, array, float64

    scal = pi / 180.
    distvec = []
    pos0 = []
    pos1 = []
    i = 0
    _ra0, _dec0, _ra1, _dec1 = array(_ra0, float), array(_dec0, float), array(_ra1, float), array(_dec1, float)
    for jj in range(0, len(_ra0)):
        try:
            distance = arccos(array(sin(array(_dec1, float64) * scal) * sin(_dec0[jj] * scal)) +
                              array(cos(array(_dec1, float64) * scal) * cos(_dec0[jj] * scal) * cos(
                                  (array(_ra1, float64) - _ra0[jj]) * scal)))
            if min(distance) <= tollerance * pi / (180 * 3600):
                distvec.append(min(distance))
                pos0.append(jj)
                pos1.append(argmin(distance))
        except:
            pass
    return distvec, pos0, pos1  #

# #######################################################################

if __name__ == "__main__":
    start_time = time.time()
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-R", "--RA", dest="ra", default='', type="str", help='-R  ra    \t [%default]')
    parser.add_option("-D", "--DEC", dest="dec", default='', type="str", help='-D dec   \t [%default]')
    parser.add_option("-v", "--verbose", action="store_true",
                      dest='verbose', default=False, help='verbose \t\t\t [%default]')
    parser.add_option("-c", "--catalog", dest="catalog", default='', type='str',
                      help='use input catalog  \t\t %default')

    option, args = parser.parse_args()
    if len(args) < 1: sys.argv.append('--help')
    _ra = option.ra
    _dec = option.dec
    _verbose  = option.verbose
    _catalogue=option.catalog

    option, args = parser.parse_args()
    imglist = agnkey.util.readlist(args[0])
    for img in imglist:
        #
        #   read sn2.fits catalog  
        # 
        table = agnkey.util.makecatalogue2([img])
        _filter = table.keys()[0]
        _rasex = table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['ra0']
        _decsex = table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['dec0']
        _magp2 = table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['magp2']
        _magp3 = table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['magp3']
        _magp4 = table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['magp4']
        _merrp2 = table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['merrp2']
        _merrp3 = table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['merrp3']
        _merrp4 = table[table.keys()[0]][table[table.keys()[0]].keys()[0]]['merrp4']

        hdr = pyfits.open(img)[0].header
        _ra0 = hdr['RA']
        _dec0 = hdr['DEC']
        _exptime = hdr['exptime']
        _object = agnkey.util.readkey3(hdr, 'object')

        # _ra0,_dec0=agnkey.agnabsphotdef.deg2HMS(_ra0,_dec0)
        # _apass=vizq(_ra0,_dec0,'apass',20)
        #_sloan=vizq(_ra0,_dec0,'sdss7',20)

        mag = _magp4
        magerr = _merrp4
        _filter = re.sub('p', '', _filter)
        _filter = re.sub('s', '', _filter)

        if _catalogue:
            _cat = agnkey.agnastrodef.readtxt(_catalogue)
            for _id in _cat:
                try:
                    _cat[_id] = np.array(_cat[_id], float)
                except:
                    pass
            print 'use catalogue from user' + _catalogue
        else:
            _cat = ''
            print 'no catalog provided '
            if _filter in ['u', 'g', 'r', 'i', 'z']:
                _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/sloan/' + _object + '*')
                if len(_catalogue):
                    _catalogue = _catalogue[0]
                    print 'use catalogue from archive for object ' + str(_object)
                    _sloan = agnkey.agnastrodef.readtxt(_catalogue)
                    for _id in _sloan:
                        try:
                            _sloan[_id] = np.array(_sloan[_id], float)
                        except:
                            pass
                    _cat = _sloan
                else:
                    _sloan = vizq(_ra0, _dec0, 'sdss7', 20)
                    if _sloan['id'].size == 0:
                        print 'sloan catalog NOT found'
                        if _filter in ['g', 'r', 'i']:
                            _apass = vizq(_ra0, _dec0, 'apass', 20)
                            if _apass['id'].size == 0:
                                print 'apass catalog NOT found'
                            else:
                                print 'apass catalog found with vizq'
                                _cat = _apass
                    else:
                        print 'sloan catalog found with vizq'
                        _cat = _sloan
                        _catalogue = 'sdss7'

            elif _filter in ['U', 'B', 'V', 'R', 'I']:
                _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/landolt/' + _object + '*')
                if len(_catalogue):
                    _catalogue = _catalogue[0]
                    _landolt = agnkey.agnastrodef.readtxt(_catalogue)
                    print 'use catalogue from archive for object ' + str(_object)
                    for _id in _landolt:
                        try:
                            _landolt[_id] = np.array(_landolt[_id], float)
                        except:
                            pass
                else:
                    _landolt = ''
                if not _landolt:
                    if _filter in ['B', 'V']:
                        _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/apass/' + _object + '*')
                        if len(_catalogue):
                            _catalogue = _catalogue[0]
                            _landolt = agnkey.agnastrodef.readtxt(_catalogue)
                            print 'use catalogue from archive for object ' + str(_object)
                            for _id in _landolt:
                                try:
                                    _landolt[_id] = np.array(_landolt[_id], float)
                                except:
                                    pass
                        else:
                            _landolt = ''
                        if not _landolt:
                            _landolt = vizq(_ra0, _dec0, 'apass', 20)
                            if _landolt:
                                _catalogue = 'apass'
                if _landolt:
                    _cat = _landolt


        if _cat:
            distvec, pos0, pos1 = crossmatch(_rasex, _decsex, _cat['ra'], _cat['dec'], 5)
        else:
            pos0 = []

        if len(pos0) >= 3:
############################       compute zero point with aperture 1
            xx1 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp2[pos0])) <= 99),
                             np.array(_cat[_filter])[pos1])
            yy1 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp2[pos0])) <= 99), np.array(_magp2[pos0]))

            yy1err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_merrp2[pos0])) <= 99),
                                np.array(magerr[pos0]))
            xx1err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp2[pos0])) <= 99),
                                np.array(_cat[_filter + 'err'])[pos1])
            ZZ1 = np.array(xx1 - yy1)

            if _verbose:
                _show = True
            else:
                _show = False

            data1, std1, ZZ1 = agnkey.agnabsphotdef.zeronew(ZZ1, maxiter=10, nn=2, verbose=_verbose, show=_show)
            std1N= std1 / np.sqrt(len(data1))
############################       compute zero point with aperture 2
            xx2 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp3[pos0])) <= 99),
                             np.array(_cat[_filter])[pos1])
            yy2 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp3[pos0])) <= 99), np.array(_magp3[pos0]))

            yy2err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_merrp3[pos0])) <= 99),
                                np.array(magerr[pos0]))
            xx2err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp3[pos0])) <= 99),
                                np.array(_cat[_filter + 'err'])[pos1])
            ZZ2 = np.array(xx2 - yy2)
            data2, std2, ZZ2 = agnkey.agnabsphotdef.zeronew(ZZ2, maxiter=10, nn=2, verbose=_verbose, show=_show)
            std2N= std2 / np.sqrt(len(data2))
############################       compute zero point with aperture 3
            xx3 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp4[pos0])) <= 99),
                             np.array(_cat[_filter])[pos1])
            yy3 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp4[pos0])) <= 99), np.array(_magp4[pos0]))

            yy3err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_merrp4[pos0])) <= 99),
                                np.array(magerr[pos0]))
            xx3err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp4[pos0])) <= 99),
                                np.array(_cat[_filter + 'err'])[pos1])
            ZZ3 = np.array(xx3 - yy3)
            data3, std3, ZZ3 = agnkey.agnabsphotdef.zeronew(ZZ3, maxiter=10, nn=2, verbose=_verbose, show=_show)
            std3N= std3 / np.sqrt(len(data3))
#######################################################################
            if _catalogue:
                print string.split(_catalogue,'/')[-1],'#########'
                agnkey.agnsqldef.updatevalue('dataredulco', 'zcat', string.split(_catalogue,'/')[-1],
                                             string.split(re.sub('sn2.', '', img), '/')[-1])
            else:
                print 'no catalog !!!!!!!'

            agnkey.agnsqldef.updatevalue('dataredulco', 'ZZ1', float(ZZ1),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])
            agnkey.agnsqldef.updatevalue('dataredulco', 'ZZ1err', float(std1),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])

            agnkey.agnsqldef.updatevalue('dataredulco', 'ZZ2', float(ZZ2),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])
            agnkey.agnsqldef.updatevalue('dataredulco', 'ZZ2err', float(std2),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])

            agnkey.agnsqldef.updatevalue('dataredulco', 'ZZ3', float(ZZ3),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])
            agnkey.agnsqldef.updatevalue('dataredulco', 'ZZ3err', float(std3),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])

            agnkey.util.updateheader(img, 0, {'ZZ1': [ZZ1, 'zeropoint with aperture 2']})
            agnkey.util.updateheader(img, 0, {'ZZ2': [ZZ2, 'zeropoint with aperture 3']})
            agnkey.util.updateheader(img, 0, {'ZZ3': [ZZ3, 'zeropoint with aperture 4']})


            if _ra and _dec:
                print 'use ra and dec from user'
                print _ra,_dec
                rasn = _ra
                decsn = _dec
                distvec, pos0, pos1 = crossmatch(_rasex, _decsex, [_ra], [_dec], 5)

            else:
                targ = agnkey.agnsqldef.targimg(img)
                aa = agnkey.agnsqldef.query(['select ra_sn,dec_sn from lsc_sn_pos where id="' + str(targ) + '"'])
                if len(aa) > 0:
                    rasn = aa[0]['ra_sn']
                    decsn = aa[0]['dec_sn']
                else:
                    rasn = ''
                    decsn = ''

            if rasn and decsn:
                from pyraf import iraf
                iraf.astcat(_doprint=0)
                iraf.imcoords(_doprint=0)
                iraf.digiphot(_doprint=0)
                iraf.daophot(_doprint=0)

                lll = [str(rasn) + '    ' + str(decsn)]
                sss = iraf.wcsctran('STDIN', 'STDOUT', re.sub('sn2.','',img)+'[0]', Stdin=lll, inwcs='world', units='degrees degrees',
                                    outwcs='logical', columns='1 2', formats='%10.1f %10.1f', Stdout=1)

                if _verbose:
                    iraf.display(re.sub('sn2.','',img)+'[0]',fill='yes',frame=1)
                    iraf.tvmark(1, 'STDIN', Stdin = list(sss) ,mark = "circle" , number = 'yes' ,label = 'no' ,
                                radii = 10, nxoffse = 5, nyoffse = 5, color = 204, txsize = 2)
                    if 'diff' in img:
                        diffimg = re.sub('diff.sn2.','',img)
                        iraf.display(diffimg+'[0]',fill='yes',frame=2)
                        iraf.tvmark(2, 'STDIN', Stdin = list(sss) ,mark = "circle" , number = 'yes' ,label = 'no' ,
                                    radii = 10, nxoffse = 5, nyoffse = 5, color = 204, txsize = 2)

                _gain = agnkey.util.readkey3(hdr, 'gain')
                _ron = agnkey.util.readkey3(hdr, 'ron')
                _exptime = agnkey.util.readkey3(hdr, 'exptime')
                _pixelscale = agnkey.util.readkey3(hdr, 'PIXSCALE')

                a1, a2, a3, a4, = float(5. / _pixelscale), float(5. / _pixelscale), float(8. / _pixelscale), float(
                    10. / _pixelscale)

                zmag= 0 #25
                _datamax=45000
                _center='no'
                iraf.fitskypars.annulus = a4
                iraf.fitskypars.dannulus = a4
                iraf.noao.digiphot.daophot.daopars.sannulus = int(a4)
                iraf.noao.digiphot.daophot.daopars.wsannul = int(a4)
                iraf.fitskypars.salgori = 'mean'  #mode,mean,gaussian
                iraf.photpars.apertures = '%d,%d,%d' % (a2, a3, a4)
                iraf.datapars.datamin = -100
                iraf.datapars.datamax = _datamax
                iraf.datapars.readnoise = agnkey.util.readkey3(hdr, 'ron')
                iraf.datapars.epadu = agnkey.util.readkey3(hdr, 'gain')
                iraf.datapars.exposure = 'exptime'  #agnkey.util.readkey3(hdr,'exptime')
                iraf.datapars.airmass = 'airmass'
                iraf.datapars.filter = 'filter2'
                iraf.centerpars.calgori = 'gauss'
                iraf.centerpars.cbox = 1
                iraf.daopars.recenter = _center
                iraf.photpars.zmag = zmag

                ####################################################
                #                    this is in the case we want to measure magnitudes on images cleaned from cosmic
                ####################################################
                #            if os.path.isfile(re.sub('sn2.','clean.',img)):
                #                print 'compute aperture mag on clean image'
                #                aaa=iraf.noao.digiphot.daophot.phot(re.sub('sn2.','clean.',img),'_coord','STDOUT',veri='no',verbose='no',Stdout=1)
                #            else:
                #                aaa=iraf.noao.digiphot.daophot.phot(re.sub('sn2.','',img),'_coord','STDOUT',veri='no',verbose='no',Stdout=1)
                ####################################################
                bbb = iraf.noao.digiphot.daophot.phot(re.sub('sn2.', '', img)+'[0]', 'STDIN', 'STDOUT', veri='no',
                                                      verbose='no', Stdin=[sss[-1]], Stdout=1)
                
                if _verbose:
                    for line in bbb:
                        print line

                #############################
                #epadu = float(string.split([i for i in bbb if 'EPADU' in i][0])[3])
                #print epadu,'dddd'
                #   keep in counts 
                #################
                epadu = 1
                bbb = [i for i in bbb if i[0] != '#']
                bbb=bbb[:-1]
                rad3, sum3, area3, flux3, mag3, dmag3 = string.split(bbb[-1])[0:6]
                rad2, sum2, area2, flux2, mag2, dmag2 = string.split(bbb[-2])[0:6]
                rad1, sum1, area1, flux1, mag1, dmag1 = string.split(bbb[-3])[0:6]

                #  error in IRAF  mag and error re connected 
                if str(mag1).count('.')==2:
                    dmag1='0.'+mag1.rsplit('.',mag1.count('.')-1)[1]
                    mag1=mag1.rsplit('.',mag1.count('.')-1)[0]
                if str(mag2).count('.')==2:
                    dmag2='0.'+mag2.rsplit('.',mag2.count('.')-1)[1]
                    mag2=mag2.rsplit('.',mag2.count('.')-1)[0]
                if str(mag3).count('.')==2:
                    dmag3='0.'+mag3.rsplit('.',mag3.count('.')-1)[1]
                    mag3=mag3.rsplit('.',mag3.count('.')-1)[0]

                MSKY, STDEV, SSKEW, NSKY, NSREJ, SIER, SERROR, _ = string.split(bbb[3])
                try:
                    aaa = float(flux1) / float(epadu) +\
                          float(area1) * (float(STDEV) ** 2) +\
                          ((float(area1) ** 2) * float(STDEV) ** 2) / float(NSKY)
                    if aaa>=0:
                        error1 = np.sqrt(aaa)
                    else:
                        error1 = 0
                except:
                    error1 = 0
                try:
                    aaa = float(flux2) / float(epadu) +\
                          float(area2) * (float(STDEV) ** 2) +\
                          (float(area2) ** 2) * float(STDEV) ** 2 / float(NSKY)
                    if aaa>=0:
                        error2 = np.sqrt(aaa)
                    else:
                        error2 = 0
                except:
                    error2 = 0
                try:
                    aaa = float(flux3) / float(epadu) +\
                          float(area3) * (float(STDEV) ** 2) +\
                          (float(area3) ** 2) * float(STDEV) ** 2 / float(NSKY)
                    if aaa>=0:
                        error3 = np.sqrt(aaa)
                    else:
                        error3 = 0
                except:
                    error3 = 0

                print flux1, flux2, flux3
                print error1,error2, error3
                print mag1,mag2,mag3
                print dmag1,dmag2,dmag3
                print ZZ1,ZZ2,ZZ3
                print std1N,std2N,std3N
                flux10 = 0
                flux20 = 0
                flux30 = 0
                dflux10 = 0
                dflux20 = 0
                dflux30 = 0

                if 'diff' in img:
                    print 'difference image add flux from reference image'
                    img0 = string.split(re.sub('sn2.', '', img), '/')[-1]
                    _dir = os.path.dirname(img)+'/'
                    hdr = pyfits.open(_dir+img0)[0].header
                    if 'TEMPLATE' in hdr:
                        img1= hdr['TEMPLATE']
                        print img1
                        #    #######################################################
                        command1=['select *  from dataredulco where namefile = "'+str(img1)+'"']
                        data1 = agnkey.agnsqldef.query(command1)

                        flux10 = data1[0]['apflux1']
                        flux20 = data1[0]['apflux2']
                        flux30 = data1[0]['apflux3']
                        dflux10 = data1[0]['dapflux1']
                        dflux20 = data1[0]['dapflux2']
                        dflux30 = data1[0]['dapflux3']

        
                if str(flux1)!='nan' and str(error1)!='nan':
                    apparentflux1 = (float(flux1) / _exptime) * 10** ((-1) * ZZ1 /2.5) + flux10
                    dapparentflux1 = np.sqrt( ( apparentflux1 * std1N)**2 + ( 10** ((-1) * ZZ1 /2.5) * (error1/_exptime) )**2 +dflux10**2)
                    agnkey.agnsqldef.updatevalue('dataredulco', 'apflux1', apparentflux1,
                                                 string.split(re.sub('sn2.', '', img), '/')[-1])
                    agnkey.agnsqldef.updatevalue('dataredulco', 'dapflux1', dapparentflux1,
                                             string.split(re.sub('sn2.', '', img), '/')[-1])
                    print apparentflux1
                    print dapparentflux1
                if str(flux2)!='nan' and str(error2)!='nan':
                    apparentflux2 = (float(flux2) / _exptime) * 10** ((-1) * ZZ2 /2.5) + flux20
                    dapparentflux2 = np.sqrt( ( apparentflux2 * std2N)**2 + ( 10** ((-1) * ZZ2 /2.5) * (error2/_exptime) )**2 +dflux20**2)

                    agnkey.agnsqldef.updatevalue('dataredulco', 'apflux2', apparentflux2,
                                                 string.split(re.sub('sn2.', '', img), '/')[-1])

                    agnkey.agnsqldef.updatevalue('dataredulco', 'dapflux2', dapparentflux2,
                                                 string.split(re.sub('sn2.', '', img), '/')[-1])
                    print apparentflux2
                    print dapparentflux2
                if str(flux3)!='nan' and str(error3)!='nan':

                    apparentflux3 = (float(flux3) / _exptime) * 10** ((-1) * ZZ3 /2.5) + flux30
                    dapparentflux3 = np.sqrt( ( apparentflux3 * std3N)**2 + ( 10** ((-1) * ZZ3 /2.5) * (error3/_exptime) )**2 +dflux30**2)

                    agnkey.agnsqldef.updatevalue('dataredulco', 'apflux3',  apparentflux3,
                                                 string.split(re.sub('sn2.', '', img), '/')[-1])

                    agnkey.agnsqldef.updatevalue('dataredulco', 'dapflux3', dapparentflux3,
                                                 string.split(re.sub('sn2.', '', img), '/')[-1])
                    print apparentflux3
                    print dapparentflux3

                if mag1 != 'INDEF':
                    try:
                        apparentmag1 = float(mag1) + ZZ1
                        dapparentmag1 = np.sqrt(std1N**2 + float(dmag1)**2)

                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap1', apparentmag1,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap1', dapparentmag1,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap1', float(mag1),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                    except:
                        print 'no possible mag1'
                else:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap1', 'NULL',
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap1', float(0.0),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap1', 'NULL',
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])

                if mag2 != 'INDEF':
                    try:
                        apparentmag2 = float(mag2) + ZZ2
                        dapparentmag2 = np.sqrt(std2N**2 + float(dmag2)**2)

                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap2', apparentmag2,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap2', dapparentmag2,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap2', float(mag2),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                    except:
                        print 'no possible mag 2'
                else:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap2', 'NULL',
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap2', float(0.0),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap2', 'NULL',
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                if mag3 != 'INDEF':
                    try:
                        apparentmag3 = float(mag3) + ZZ3
                        dapparentmag3 = np.sqrt(std3N**2 + float(dmag3)**2)

                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap3', apparentmag3,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap3', dapparentmag3,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap3', float(mag3),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                    except:
                        print 'no possible mag3 '
                else:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap3', 'NULL',
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap3', float(0.0),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap3', 'NULL',
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])

                headers = {'apflux1': [apparentflux1, ''], 'dapflux1': [ dapparentflux1, ''],
                           'apflux2': [apparentflux2, ''], 'dapflux2': [ dapparentflux2, ''],
                           'apflux3': [apparentflux3, ''], 'dapflux3': [ dapparentflux3, '']}
                agnkey.util.updateheader(img, 0, headers)
            else:
                print 'ra and dec not defined'
###################################################################
