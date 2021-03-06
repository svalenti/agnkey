#!/usr/bin/env python
description = ">> make template "
usage = "%prog image [options] "

import numpy as np
import agnkey
import os
import sys
import string
import re
from pyfits import getheader
from optparse import OptionParser
import math
from pyraf import iraf
import pywcs

if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-R", "--RA", dest="RA", default='',
                      type='str', help='RA coordinate \t\t\t %default')
    parser.add_option("-D", "--DEC", dest="DEC", default='',
                      type='str', help='DEC coordinate \t\t\t %default')
    parser.add_option("-p", "--psf", dest="psf", default='',
                      type='str', help='psf image \t\t\t %default')
    parser.add_option("--mag", dest="mag", type=float, default=0, help='mag to subtract \t\t [%default]')
    parser.add_option("-s", "--show", action='store_true', help='Show output \t\t [%default]')
    parser.add_option("-f", "--force", action='store_true', help='force archiving \t\t [%default]')
    parser.add_option("--uncleaned", dest="clean", action='store_false', help='do not use cosmic ray cleaned image \t\t [%default]')
    parser.add_option("-i", action='store_true', help='choose mag and position interactively \t\t [%default]')
    parser.add_option("--subtract-mag-from-header", action='store_true', help='automatically subtract mag from header of file \t\t [%default]')
    option, args = parser.parse_args()
    if len(args) < 1: 
        sys.argv.append('--help')
    option, args = parser.parse_args()
    imglist = agnkey.util.readlist(args[0])
    imgdic = {}
    for img in imglist:
        hdr0 = agnkey.util.readhdr(img)
        _filter0 = agnkey.util.readkey3(hdr0, 'filter')
        if _filter0 not in imgdic:
            imgdic[_filter0] = {}
            imgdic[_filter0]['img'] = []
            imgdic[_filter0]['psf'] = []
        imgdic[_filter0]['img'].append(img)

    if option.psf:
        psflist = agnkey.util.readlist(option.psf)
        for img in psflist:
            hdr0 = agnkey.util.readhdr(img)
            _filter0 = agnkey.util.readkey3(hdr0, 'filter')
            if _filter0 in imgdic:
                imgdic[_filter0]['psf'].append(img)
    else:
        psflist = ''
    _ra = option.RA
    _dec = option.DEC
    _show = option.show
    _force = option.force
    chosemag = option.i
    chosepos = option.i
    _clean = option.clean
    _mag = option.mag
    _subtract_mag_from_header = option.subtract_mag_from_header
    # #################################
    from pyraf import iraf
    from iraf import digiphot
    from iraf import daophot
    import pywcs
    ##################################
    goon = False
    for fil in imgdic:
        imglist1 = imgdic[fil]['img']
        for img0 in imglist1:
            if not imgdic[fil]['psf']:
                if os.path.exists(re.sub('.fits', '.psf.fits', img0)):
                    imgdic[fil]['psf'].append(re.sub('.fits', '.psf.fits', img0))

            if not imgdic[fil]['psf']:
                psfimg = ''
                print 'psf not found'
            else:
                print '\### found psffile'
                goon = True

            if goon:
                psfimg = imgdic[fil]['psf'][0]
                print img0, psfimg, _ra, _dec
                if os.path.exists(re.sub('.fits', '.sn2.fits', img0)):
                    hdr1 = agnkey.util.readhdr(re.sub('.fits', '.sn2.fits', img0))
                    _xpos = agnkey.util.readkey3(hdr1, 'PSFX1')
                    _ypos = agnkey.util.readkey3(hdr1, 'PSFY1')
                    _mag = agnkey.util.readkey3(hdr1, 'PSFMAG1')
                    if 'ZPN' in hdr1.keys():
                        _ZPN = agnkey.util.readkey3(hdr1, 'ZPN')
                    else:
                        _ZPN = ''
                    _exptime = agnkey.util.readkey3(hdr1, 'exptime')
                    print 'found fits table'
                    print _ZPN
                #######################  chose mag  ##############
                if not chosemag:
                    if _mag:
                        print 'use mag from fits table'
                        try:
                            _mag = float(_mag) + 2.5 * math.log10(float(_exptime))
                        except:
                            _mag = 0.0
                    else:
                        print 'mag not found, mag not input, no modification to the template '
                        _mag = 0
                else:
                    if _ZPN:
                        print '2 magnitude difference'
                        _magobj = raw_input('which is the mag of the object  ? ')
                        if float(_magobj) == 0.0:
                            _mag = 0.0
                        else:
                            _mag = float(_magobj) - (float(_ZPN))  #+2.5*math.log10(float(_exptime)))
                    else:
                        _mag0 = raw_input('which mag do you want to subtract  ' + str(_mag) + ' ? ')
                        if not _mag0:
                            _mag = float(_mag)
                        elif _mag0 == 0.0:
                            _mag = 0.0
                        else:
                            _mag = float(_mag0)
                    print _mag
                #######################  Chose Ra   and    Dec  ##############
                if not chosepos:
                    if not _ra and not _dec:
                        _ra, _dec, _SN0, _type = agnkey.util.checksndb(img0, 'lsc_sn_pos')
                    if _ra and _dec:
                        print 'use ra and dec from input database !!! '
                        hdr0 = agnkey.util.readhdr(img0)
                        wcs = pywcs.WCS(hdr0)
                        pix1 = wcs.wcs_sky2pix(np.array(zip([_ra], [_dec]), float), 1)
                        _xpos, _ypos = pix1[0][0], pix1[0][1]
                else:
                    _xpos, _ypos = '', ''
                if _xpos and _ypos:
                    print 'use xpos and ypos from fits table'
                    print _xpos, _ypos
                else:
                    print 'no xpos and ypos define, do that interactively'
                    jj = 0
                    while not _xpos or not _ypos:
                        print "  MARK SN REGION WITH - x -, EXIT  - q -"
                        try:
                            agnkey.util.delete('tmp.log')
                            zz1, zz2, goon = agnkey.util.display_image(img, 1, '', '', True)
                            #                              iraf.display(img,1,fill=True,Stdout=1)
                            iraf.imexamine(img, 1, wcs='logical', logfile='tmp.log', keeplog=True)
                            xytargets = iraf.fields('tmp.log', '1,2', Stdout=1)
                            _xpos, _ypos = string.split(xytargets[0])[0], string.split(xytargets[0])[1]
                        except:
                            _xpos, _ypos = '', ''
                        jj = jj + 1
                        if jj > 10:
                            goon = False
                            break

            if goon:
                print _xpos, _ypos, _mag
                print img0, psfimg, _xpos, _ypos, _mag
                imgout = re.sub('.fits', '.temp.fits', string.split(img0, '/')[-1])
                agnkey.util.delete('_tmp.fits,_tmp2.fits,_tmp2.fits.art,' + imgout)

                if _clean:
                    if os.path.isfile(re.sub('.fits', '.clean.fits', img0)):
                        img0 = re.sub('.fits', '.clean.fits', img0)
                if _show:
                    _z11, _z22, good = agnkey.util.display_image(img0, 1, '', '', False)
                    z11 = float(_z11)
                    z22 = float(_z22)
                    answ = 'y'
                    answ = raw_input(">>>>> Cuts OK [y/n] [y]?")
                    if not answ:
                        answ = 'y'
                    elif answ == 'no':
                        answ = 'n'
                    while answ == 'n':
                        z11 = raw_input('>>> z1 = ? [' + str(_z11) + '] ? ')
                        z22 = raw_input('>>> z2 = ? [' + str(_z22) + '] ? ')
                        if not z11:
                            z11 = _z11
                        else:
                            z11 = float(z11)
                        if not z22:
                            z22 = _z22
                        else:
                            z22 = float(z22)
                        _z11, _z22, goon = agnkey.util.display_image(img0, 1, z11, z22, False)
                        answ = raw_input(">>>>> Cuts OK [y/n] [y]?")
                        if not answ:
                            answ = 'y'
                        elif answ == 'no':
                            answ = 'n'
                        z11 = float(_z11)
                        z22 = float(_z22)
                else:
                    z11, z22 = '', ''
                answ = 'n'
                while answ == 'n':
                    coordlist = str(_xpos) + '   ' + str(_ypos) + '    ' + str(_mag)
                    os.system('echo ' + coordlist + ' > ddd')
                    iraf.imarith(img0, '-', img0, '_tmp.fits', verbose='no')
                    if float(_mag) != 0.0:
                        iraf.daophot.addstar("_tmp.fits", 'ddd', psfimg, "_tmp2.fits", nstar=1, veri='no', simple='yes',
                                             verb='no')
                        iraf.imarith(img0, '-', '_tmp2.fits', imgout, verbose='yes')
                    else:
                        print '\####  copy file '
                        iraf.imcopy(img0, imgout, verbose='yes')
                    if _show:
                        _z11, _z22, goon = agnkey.util.display_image(imgout, 2, z11, z22, False)
                        answ = raw_input('ok  ? [[y]/n]')
                        if not answ:
                            answ = 'y'
                    else:
                        answ = 'y'
                    agnkey.util.delete('_tmp.fits,_tmp2.fits,_tmp2.fits.art,ddd')
                    if answ == 'n':
                        agnkey.util.delete(imgout)
                        _mag0 = raw_input('which magnitude  ' + str(_mag) + ' ?')
                        if _mag0: _mag = _mag0
                print 'insert in the archive'
                _targid = agnkey.agnsqldef.targimg(imgout)
                hd = agnkey.util.readhdr(imgout)
                dictionary = {'dateobs': agnkey.util.readkey3(hd, 'date-obs'),
                              'exptime': agnkey.util.readkey3(hd, 'exptime'),
                              'filter': agnkey.util.readkey3(hd, 'filter'), 
                              'mjd': agnkey.util.readkey3(hd, 'mjd'),
                              'telescope': agnkey.util.readkey3(hd, 'telescop'),
                              'airmass': agnkey.util.readkey3(hd, 'airmass'),
                              'objname': agnkey.util.readkey3(hd, 'object'), 
                              'ut': agnkey.util.readkey3(hd, 'ut'),
                              'wcs': agnkey.util.readkey3(hd, 'wcserr'),
                              'instrument': agnkey.util.readkey3(hd, 'instrume'),
                              'ra0': agnkey.util.readkey3(hd, 'RA'), 
                              'dec0': agnkey.util.readkey3(hd, 'DEC')}
                dictionary['namefile'] = string.split(imgout, '/')[-1]
                dictionary['wdirectory'] = agnkey.util.workingdirectory + '1mtel/' + \
                                           agnkey.util.readkey3(hd,'date-night') + '/'
                dictionary['filetype'] = 4
                dictionary['targid'] = _targid
                ###################    insert in dataredulco
                ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'dataredulco', 'namefile',
                                                      string.split(imgout, '/')[-1], '*')
                if ggg and _force:
                    agnkey.agnsqldef.deleteredufromarchive(string.split(imgout, '/')[-1], 'dataredulco', 'namefile')
                if not ggg or _force:
                    print 'insert'
                    print dictionary
                    agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn, 'dataredulco', dictionary)
                else:
                    for voce in ggg[0].keys():
                        #                for voce in ['filetype','ra0','dec0']:
                        if voce in dictionary.keys():
                            agnkey.agnsqldef.updatevalue('dataredulco', voce, dictionary[voce],
                                                         string.split(imgout, '/')[-1])
                if not os.path.isdir(dictionary['wdirectory']):
                    print dictionary['wdirectory']
                    os.mkdir(dictionary['wdirectory'])
                if not os.path.isfile(dictionary['wdirectory'] + imgout) or _force:
                    print 'mv ' + imgout + ' ' + dictionary['wdirectory'] + imgout
                    os.system('mv ' + imgout + ' ' + dictionary['wdirectory'] + imgout)
                print 'Warning: if this template still contain the target you want to measure, you need to run'
                print 'stages psf and apmag on the reference image'

# ###############################################################

