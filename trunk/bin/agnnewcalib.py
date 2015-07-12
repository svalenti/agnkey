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
import pyfits
import numpy as np


def vizq(_ra, _dec, catalogue, radius):
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
        print img
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
        # _ra0,_dec0=agnkey.agnabsphotdef.deg2HMS(_ra0,_dec0)
        # _apass=vizq(_ra0,_dec0,'apass',20)
        #_sloan=vizq(_ra0,_dec0,'sdss7',20)

        _object = agnkey.util.readkey3(hdr, 'object')

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
                if _catalogue:
                    print 'use catalogue from archive for object ' + str(_object)
                    _sloan = agnkey.agnastrodef.readtxt(_catalogue[0])
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

            elif _filter in ['U', 'B', 'V', 'R', 'I']:
                _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/landolt/' + _object + '*')
                if _catalogue:
                    _landolt = agnkey.agnastrodef.readtxt(_catalogue[0])
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
                        if _catalogue:
                            _landolt = agnkey.agnastrodef.readtxt(_catalogue[0])
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
                    _cat = _landolt

        if _cat:
            distvec, pos0, pos1 = crossmatch(_rasex, _decsex, _cat['ra'], _cat['dec'], 5)
        else:
            pos0 = []

        if len(pos0) >= 3:
############################       compute zero point with aperture 2
            xx2 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp2[pos0])) <= 99),
                             np.array(_cat[_filter])[pos1])
            yy2 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp2[pos0])) <= 99), np.array(_magp2[pos0]))

            yy2err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_merrp2[pos0])) <= 99),
                                np.array(magerr[pos0]))
            xx2err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp2[pos0])) <= 99),
                                np.array(_cat[_filter + 'err'])[pos1])
            ZZ2 = np.array(xx2 - yy2)

            if _verbose:
                _show = True
            else:
                _show = False

            data2, std2, ZZ2 = agnkey.agnabsphotdef.zeronew(ZZ2, maxiter=10, nn=2, verbose=_verbose, show=_show)
############################       compute zero point with aperture 3
            xx3 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp3[pos0])) <= 99),
                             np.array(_cat[_filter])[pos1])
            yy3 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp3[pos0])) <= 99), np.array(_magp3[pos0]))

            yy3err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_merrp3[pos0])) <= 99),
                                np.array(magerr[pos0]))
            xx3err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp3[pos0])) <= 99),
                                np.array(_cat[_filter + 'err'])[pos1])
            ZZ3 = np.array(xx3 - yy3)
            data3, std3, ZZ3 = agnkey.agnabsphotdef.zeronew(ZZ3, maxiter=10, nn=2, verbose=_verbose, show=_show)
############################       compute zero point with aperture 4
            xx4 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp4[pos0])) <= 99),
                             np.array(_cat[_filter])[pos1])
            yy4 = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp4[pos0])) <= 99), np.array(_magp4[pos0]))

            yy4err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_merrp4[pos0])) <= 99),
                                np.array(magerr[pos0]))
            xx4err = np.compress((np.array(_cat[_filter])[pos1] <= 99) & ((np.array(_magp4[pos0])) <= 99),
                                np.array(_cat[_filter + 'err'])[pos1])
            ZZ4 = np.array(xx2 - yy2)
            data4, std4, ZZ4 = agnkey.agnabsphotdef.zeronew(ZZ4, maxiter=10, nn=2, verbose=_verbose, show=_show)
            print 'here'
#######################################################################
            ZZ0=ZZ4
            std0=std4
            agnkey.agnsqldef.updatevalue('dataredulco', 'ZPN', float(ZZ0),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])
            agnkey.agnsqldef.updatevalue('dataredulco', 'ZPNERR', float(std0),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])
            agnkey.agnsqldef.updatevalue('dataredulco', 'ZPNNUM', len(data2),
                                         string.split(re.sub('sn2.', '', img), '/')[-1])
            headers = {'ZPN': [float(ZZ0), 'zeropoint'], 'ZPNERR': [float(std0), 'zeropoint std'],
                       'ZPNNUM': [len(data2), 'number of stars used for zeropoint']}
            agnkey.util.updateheader(img, 0, headers)

            agnkey.util.updateheader(img, 0, {'ZZ2': [ZZ2, 'zeropoint with aperture 2']})
            agnkey.util.updateheader(img, 0, {'ZZ3': [ZZ3, 'zeropoint with aperture 3']})
            agnkey.util.updateheader(img, 0, {'ZZ4': [ZZ4, 'zeropoint with aperture 4']})


            if _ra and _dec:
                print 'use ra and dec from user'
                print _ra,_dec
                rasn = _ra
                decsn = _dec

                distvec, pos0, pos1 = crossmatch(_rasex, _decsex, [_ra], [_dec], 5)
                print distvec, pos0, pos1
                print _magp2[pos0]
                print _magp3[pos0]
                print _magp4[pos0]
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
                sss = iraf.wcsctran('STDIN', 'STDOUT', img, Stdin=lll, inwcs='world', units='degrees degrees',
                                    outwcs='logical', columns='1 2', formats='%10.1f %10.1f', Stdout=1)

                if _verbose:
                    iraf.display(re.sub('sn2.','',img),fill='yes',frame=1)
                    print sss[-1]
                    iraf.tvmark(1, 'STDIN', Stdin = list(sss) ,mark = "circle" , number = 'yes' ,label = 'no' ,
                                radii = 10, nxoffse = 5, nyoffse = 5, color = 204, txsize = 2)
#                    raw_input('ddddd')


                f = open('_coord', 'w')
                f.write(sss[-1])
                f.close()
                _gain = agnkey.util.readkey3(hdr, 'gain')
                _ron = agnkey.util.readkey3(hdr, 'ron')
                _exptime = agnkey.util.readkey3(hdr, 'exptime')
                _pixelscale = agnkey.util.readkey3(hdr, 'PIXSCALE')

                a1, a2, a3, a4, = float(5. / _pixelscale), float(5. / _pixelscale), float(8. / _pixelscale), float(
                    10. / _pixelscale)

                zmag= 0.0
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
                aaa = iraf.noao.digiphot.daophot.phot(re.sub('sn2.', '', img), '_coord', 'STDOUT', veri='no',
                                                      verbose='no', Stdout=1)

                #            for ii in aaa: print ii

                epadu = float(string.split([i for i in aaa if 'EPADU' in i][0])[3])
                aaa = [i for i in aaa if i[0] != '#']
                print aaa
                rad3, sum3, area3, flux3, mag3, dmag3 = string.split(aaa[-1])[0:6]
                rad2, sum2, area2, flux2, mag2, dmag2 = string.split(aaa[-2])[0:6]
                rad1, sum1, area1, flux1, mag1, dmag1 = string.split(aaa[-3])[0:6]

                if str(mag1).count('.')==2:
                    dmag1='0.'+mag1.rsplit('.',mag1.count('.')-1)[1]
                    mag1=mag1.rsplit('.',mag1.count('.')-1)[0]
                if str(mag2).count('.')==2:
                    dmag2='0.'+mag2.rsplit('.',mag2.count('.')-1)[1]
                    mag2=mag2.rsplit('.',mag2.count('.')-1)[0]
                if str(mag3).count('.')==2:
                    dmag3='0.'+mag3.rsplit('.',mag3.count('.')-1)[1]
                    mag3=mag3.rsplit('.',mag3.count('.')-1)[0]

                MSKY, STDEV, SSKEW, NSKY, NSREJ, SIER, SERROR, _ = string.split(aaa[2])
                error3 = np.sqrt(
                    float(flux3) / float(epadu) + float(area3) * (float(STDEV) ** 2) + (float(area3) ** 2) * float(
                        STDEV) ** 2 / float(NSKY))

                if 'diff' in img:
                    if 'apfl1re' in hdr and 'dapfl1re':
                        print 'zeropoint there'
                        FLUXref = hdr['apfl1re']
                        dFLUXref = hdr['dapfl1re']
                    else:
                        FLUXref = ''

                    if 'ZPNref' in hdr:
                        print 'flux there'
                        ZZ0ref = hdr['ZPNref']
                    else:
                        ZZ0ref = ''

                    if FLUXref and ZZ0ref:
                        #print FLUXref, dFLUXref, flux3, error3
                        if float(ZZ0ref) == float(ZZ0):
                            print 'difference image scaled to the reference, zero point of the difference ' \
                                  'image is the same'
                            magfromflux = -2.5 * np.log10((float(FLUXref)) + (float(flux3) / _exptime))
                            dmagfromflux = 1.0857 * np.sqrt((error3 / _exptime) ** 2 + (float(dFLUXref)) ** 2) / (
                                (float(flux3) / _exptime) + float(FLUXref))
                        else:
                            magfromflux = -2.5 * np.log10(
                                (float(FLUXref)) * 10 ** ((float(ZZ0ref) - ZZ0) / -2.5) + (float(flux3) / _exptime))
                            dmagfromflux = 1.0857 * np.sqrt((error3 / _exptime) ** 2 + (float(dFLUXref)) ** 2) / (
                                (float(flux3) / _exptime) + float(FLUXref))
                            print 'difference image scaled to target image, need  zeropoint of both images'

                        print  'this is a difference image\n I found a zeropoint and flux measurment in the ' \
                               'reference image'
                        print  "I'm going to replace tha magnitude at aperture 3 with this value"
                        mag3 = magfromflux
                        dmag3 = dmagfromflux
                        #print mag3, dmag3
                    else:
                        print 'Warning: this is a difference image, but I did not find a flux and zeropoint\n'
                        print 'for the reference image, the reference image does not include the target we ' \
                              'are measuring'

                        #            mag1,dmag1=string.split(aaa[-3])[4],string.split(aaa[-3])[5]
                        #            mag2,dmag2=string.split(aaa[-2])[4],string.split(aaa[-2])[5]
                        #            mag3,dmag3=string.split(aaa[-1])[4],string.split(aaa[-1])[5]
                        #            flux1,dflux1=string.split(aaa[-1])[3],string.split(aaa[-1])[3]
                        #            totalflux=(float(flux1)/_exptime)*10**(float(ZZ0)/-2.5)   #  compute total flux
                        #            print totalflux

                        #            raw_input('go on')
                agnkey.agnsqldef.updatevalue('dataredulco', 'apflux1', float(flux3) / _exptime,
                                             string.split(re.sub('sn2.', '', img), '/')[-1])
                agnkey.agnsqldef.updatevalue('dataredulco', 'dapflux1', float(error3) / _exptime,
                                             string.split(re.sub('sn2.', '', img), '/')[-1])

                if mag1 != 'INDEF':
                    print float(mag1)
                    print float(mag1) + float(ZZ2)
                    try:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap1', float(mag1) + ZZ2,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap1', float(dmag1),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap1', float(mag1),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                    except:
                        print 'no possible'
                else:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap1', float(9999),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap1', float(0.0),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap1', float(9999),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])

                if mag2 != 'INDEF':
                    print float(mag2)
                    print float(mag2) + float(ZZ3)
                    try:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap2', float(mag2) + ZZ3,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap2', float(dmag1),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap2', float(mag2),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                    except:
                        print 'no possible'
                else:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap2', float(9999),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap2', float(0.0),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap2', float(9999),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                if mag3 != 'INDEF':
                    print float(mag3)
                    print float(mag3) + float(ZZ4)
                    try:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap3', float(mag3) + ZZ4,
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap3', float(dmag1),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap3', float(mag3),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                    except:
                        print 'no possible'
                else:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'appmagap3', float(9999),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'dappmagap3', float(0.0),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])
                        agnkey.agnsqldef.updatevalue('dataredulco', 'instmagap3', float(9999),
                                                     string.split(re.sub('sn2.', '', img), '/')[-1])

                headers = {'apflux1': [float(flux3) / _exptime, ''], 'dapflux1': [float(error3) / _exptime, '']}
                agnkey.util.updateheader(img, 0, headers)
            else:
                print 'ra and dec not defined'
#            raw_input('go on')

            #'appmagap1':[float(mag1)+ZZ0,''],'appmagap2':[float(mag2)+ZZ0,''],'appmagap3':[float(mag3)+ZZ0,''],\
            #'dappmagap1':[float(dmag1),''],'dappmagap2':[float(dmag2),''],'dappmagap3':[float(dmag3),''],\
            #'instmagap1':[float(mag1),''],'instmagap2':[float(mag2),''],'instmagap3':[float(mag3),'']
        
