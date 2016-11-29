#!/usr/bin/env python

description = ">> New automated psf version"
usage = "%prog image [options] "
# ###############################################################
# EC 2012 Feb 20  
# modified by SV for lsc 
################################################################
import os, sys, shutil, subprocess
import time
from optparse import OptionParser
from pyraf import iraf

try:       from astropy.io import fits as pyfits
except:    import pyfits

import agnkey
import traceback
import numpy as np

iraf.noao(_doprint=0)
iraf.obsutil(_doprint=0)


def runsex(img, fwhm, thresh, pix_scale):  ## run_sextractor  fwhm in pixel
    import agnkey
    from agnkey.util import defsex

    mina = 5.
    seeing = fwhm * pix_scale

    cdef = open(agnkey.__path__[0] + '/standard/sex/default2.param')
    riga = cdef.readlines()
    cparam = []
    for r in riga:
        if r[0] != '#' and len(r.strip()) > 0: \
                cparam.append(r.split()[0])

    pid = subprocess.Popen("sex " + img + ".fits -catalog_name tmp.cat" + \
                           " -c  " + agnkey.__path__[0] +
                           "/standard/sex/default2.sex  -PARAMETERS_NAME " + agnkey.__path__[0] +
                           "/standard/sex/default2.param" + " -STARNNW_NAME " + agnkey.__path__[0] +
                           "/standard/sex/default2.nnw" + " -PIXEL_SCALE " + str(pix_scale) + \
                           " -DETECT_MINAREA " + str(mina) + " -DETECT_THRESH  " + str(thresh) + \
                           " -ANALYSIS_THRESH  " + str(thresh) + " -PHOT_FLUXFRAC 0.5" + \
                           " -SEEING_FWHM " + str(seeing), stdout=subprocess.PIPE, shell=True)

    output, error = pid.communicate()

    csex = open("tmp.cat")
    tab = {}
    riga = csex.readlines()
    for k in cparam: tab[k] = []
    for r in riga:
        if r[0] != '#':
            for i in range(len(cparam)):
                tab[cparam[i]].append(float(r.split()[i]))
    for k in cparam: tab[k] = np.array(tab[k])

    xdim, ydim = iraf.hselect(img, 'i_naxis1,i_naxis2', 'yes', Stdout=1) \
        [0].split()

    xcoo, ycoo, ra, dec, magbest, classstar, fluxrad, bkg = [], [], [], [], [], [], [], []
    for i in range(len(tab['X_IMAGE'])):
        x, y = tab['X_IMAGE'][i], tab['Y_IMAGE'][i]
        if 5 < x < int(xdim) - 5 and 5 < y < int(ydim) - 5:  # trim border
            xcoo.append(x)
            ycoo.append(y)
            ra.append(tab['X_WORLD'][i])
            dec.append(tab['Y_WORLD'][i])
            magbest.append(tab['MAG_BEST'][i])
            classstar.append(tab['CLASS_STAR'][i])
            fluxrad.append(tab['FLUX_RADIUS'][i])
            bkg.append(tab['BACKGROUND'][i])

    return np.array(xcoo), np.array(ycoo), np.array(ra), np.array(dec), np.array(magbest), \
           np.array(classstar), np.array(fluxrad), np.array(bkg)


def apfit(img, fwhm, hdr, interactive, _datamax=45000, fixaperture=False):
    import agnkey

    iraf.digiphot(_doprint=0)
    iraf.daophot(_doprint=0)
    zmag = 0.
    varord = 0  # -1 analitic 0 - numeric

    if fixaperture:
        print 'use fix aperture 5 8 10'
        hdr = agnkey.util.readhdr(img+'.fits')
        _pixelscale = agnkey.util.readkey3(hdr, 'PIXSCALE')
        a1, a2, a3, a4, = float(5. / _pixelscale), float(5. / _pixelscale), float(8. / _pixelscale), float(
                    10. / _pixelscale)
    else:
        a1, a2, a3, a4, = int(fwhm + 0.5), int(fwhm * 2 + 0.5), int(fwhm * 3 + 0.5), int(fwhm * 4 + 0.5)

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
    iraf.delete('_ap.ma*', verify=False)
    iraf.phot(img, '_ap.coo', '_ap.mag', interac=False, verify=False, verbose=False)
    photmag = iraf.txdump("_ap.mag", 'xcenter,ycenter,id,mag,merr', expr='yes', Stdout=1)
    return photmag

def ecpsf(img, ofwhm, threshold, interactive, ds9, fixaperture=False,_catalog=''):
    try:
        import agnkey
        import string

        hdr = agnkey.util.readhdr(img + '.fits')
        instrument = agnkey.util.readkey3(hdr, 'instrume')
        print 'INSTRUMENT:', instrument

        if 'PIXSCALE' in hdr:
            pixelscale = agnkey.util.readkey3(hdr, 'PIXSCALE')
        elif 'CCDSCALE' in hdr:
            if 'CCDXBIN' in hdr:
                pixelscale = agnkey.util.readkey3(hdr, 'CCDSCALE') * agnkey.util.readkey3(hdr, 'CCDXBIN')
            elif 'CCDSUM' in hdr:
                pixelscale = agnkey.util.readkey3(hdr, 'CCDSCALE') * int(
                    string.split(agnkey.util.readkey3(hdr, 'CCDSUM'))[0])

        if instrument in ['kb05', 'kb70', 'kb71', 'kb73', 'kb74', 'kb75', 'kb76', 'kb77', 'kb78', 'kb79']:
            scale = pixelscale
            _datamax = 45000
        elif instrument in ['fl02', 'fl03', 'fl04']:
            scale = pixelscale
            _datamax = 120000
        elif instrument in ['fs01', 'em03']:
            scale = pixelscale
            _datamax = 65000
        elif instrument in ['fs02', 'fs03']:
            scale = pixelscale
            _datamax = 65000
        elif instrument in ['em01']:
            scale = pixelscale
            _datamax = 65000
        try:
            _wcserr = agnkey.util.readkey3(hdr, 'wcserr')
            if float(_wcserr) == 0:
                if instrument in ['kb05', 'kb70', 'kb71', 'kb73', 'kb74', 'kb75', 'kb76', 'kb77', 'kb78', 'kb79']:
                    seeing = float(agnkey.util.readkey3(hdr, 'L1FWHM')) * .75
                elif instrument in ['fl02', 'fl03', 'fl04']:
                    seeing = float(agnkey.util.readkey3(hdr, 'L1FWHM')) * .75
                elif instrument in ['fs01', 'fs02', 'fs03', 'em03', 'em01']:
                    if 'L1FWHM' in hdr:
                        seeing = float(agnkey.util.readkey3(hdr, 'L1FWHM')) * .75
                    elif 'L1SEEING' in hdr:
                        seeing = float(agnkey.util.readkey3(hdr, 'L1SEEING')) * scale
                    else:
                        seeing = 3
                else:
                    seeing = 3
            else:
                seeing = float(agnkey.util.readkey3(hdr, 'PSF_FWHM'))
                sys.exit('astrometry not good')
        except:
            sys.exit('astrometry not good')

        fwhm = seeing / scale
        print 'FWHM[header]  ', fwhm, '   in pixel'
        if ofwhm:
            fwhm = float(ofwhm)
        print '    FWHM[input]  ', fwhm, ' in pixel'

        if interactive:
            iraf.display(img, 1, fill=True)
            iraf.delete('tmp.lo?', verify=False)
            print '_' * 80
            print '>>> Mark reference stars with "a". Then "q"'
            print '-' * 80
            iraf.imexamine(img, 1, wcs='logical', logfile='tmp.log', keeplog=True)
            xyrefer = iraf.fields('tmp.log', '1,2,6,15', Stdout=1)
            xns, yns, _fws = [], [], []
            ff = open('_ap.coo', 'w')
            for i in range(len(xyrefer)):
                xns.append(float(xyrefer[i].split()[0]))
                yns.append(float(xyrefer[i].split()[1]))
                _fws.append(float(xyrefer[i].split()[3]))
                ff.write('%10.3f %10.3f %7.2f \n' % (xns[i], yns[i], float(_fws[i])))
            ff.close()

        elif _catalog:
#            cat1=agnkey.agnastrodef.readtxt(_catalog)
#            cat1['ra'],cat1['dec']
            ddd=iraf.wcsctran(input=_catalog,output='STDOUT',Stdout=1,image=img,inwcs='world',outwcs='logical',
                              units='degrees degrees',columns='1 2',formats='%10.1f %10.1f',verbose='no')
            ddd=[i for i in ddd if i[0]!='#']
            ddd=['  '.join(i.split()[0:3]) for i in ddd]
            ff = open('_ap.coo', 'w')
            for i in ddd:
                a,b,c = string.split(i)
                #print a,b,c
                ff.write('%10s %10s %10s \n' % (a, b, c))
            ff.close()
            print 'use catalog'
        else:
            xs, ys, ran, decn, magbest, classstar, fluxrad, bkg = runsex(img, fwhm, threshold, scale)
            ff = open('_ap.coo', 'w')
            for i in range(len(xs)):
                    ff.write('%10.3f %10.3f %7.2f \n' % (xs[i], ys[i], float(fluxrad[i])))
            ff.close()  ## End automatic selection

        print 80 * "#"
        photmag = apfit(img, fwhm, hdr, interactive, _datamax, fixaperture)

        radec = iraf.wcsctran(input='STDIN', output='STDOUT', Stdin=photmag, \
                              Stdout=1, image=img, inwcs='logical', outwcs='world', columns="1 2", \
                              format='%13.3H %12.2h', min_sig=9, mode='h')[3:]

        exptime = agnkey.util.readkey3(hdr, 'exptime')
        object = agnkey.util.readkey3(hdr, 'object').replace(' ', '')
        filtro = agnkey.util.readkey3(hdr, 'filter')

        #######################################
        rap, decp, magp2, magp3, magp4, smagf = [], [], [], [], [], []
        merrp2, merrp3, merrp4, smagerrf = [], [], [], []
        rap0, decp0 = [], []
        for i in range(len(radec)):
            aa = radec[i].split()
            rap.append(aa[0])
            decp.append(aa[1])
            rap0.append(agnkey.agnabsphotdef.deg2HMS(ra=aa[0]))
            decp0.append(agnkey.agnabsphotdef.deg2HMS(dec=aa[1]))
            idp = aa[2]
            magp2.append(aa[3])
            magp3.append(aa[4])
            magp4.append(aa[5])
            merrp2.append(aa[6])
            merrp3.append(aa[7])
            merrp4.append(aa[8])

        tbhdu = pyfits.new_table(pyfits.ColDefs([
            pyfits.Column(name='ra', format='20A', array=np.array(rap)),
            pyfits.Column(name='dec', format='20A', array=np.array(decp)),
            pyfits.Column(name='ra0', format='E', array=np.array(rap0)),
            pyfits.Column(name='dec0', format='E', array=np.array(decp0)),
            pyfits.Column(name='magp2', format='E', array=np.array(np.where((np.array(magp2) != 'INDEF'),
                                                                            np.array(magp2), 9999), float)),
            pyfits.Column(name='magp3', format='E', array=np.array(np.where((np.array(magp3) != 'INDEF'),
                                                                            np.array(magp3), 9999), float)),
            pyfits.Column(name='magp4', format='E', array=np.array(np.where((np.array(magp4) != 'INDEF'),
                                                                            np.array(magp4), 9999), float)),
            pyfits.Column(name='merrp2', format='E', array=np.array(np.where((np.array(merrp2) != 'INDEF'),
                                                                             np.array(merrp2), 9999), float)),
            pyfits.Column(name='merrp3', format='E', array=np.array(np.where((np.array(merrp3) != 'INDEF'),
                                                                             np.array(merrp3), 9999), float)),
            pyfits.Column(name='merrp4', format='E', array=np.array(np.where((np.array(merrp4) != 'INDEF'),
                                                                             np.array(merrp4), 9999), float)),
            pyfits.Column(name='smagf', format='E', array=np.array(np.where((np.array(magp2) != 'INDEF'),
                                                                            np.array(magp2), 9999), float)),
            pyfits.Column(name='smagerrf', format='E', array=np.array(np.where((np.array(merrp2) != 'INDEF'),
                                                                               np.array(merrp2), 9999), float)),

        ]))
        hdu = pyfits.PrimaryHDU(header=hdr)
        thdulist = pyfits.HDUList([hdu, tbhdu])
        agnkey.util.delete(img + '.sn2.fits')
        thdulist.writeto(img + '.sn2.fits')
        agnkey.util.updateheader(img + '.sn2.fits', 0,
                                 {'XDIM': [agnkey.util.readkey3(hdr, 'naxis1'), 'x number of pixels']})
        agnkey.util.updateheader(img + '.sn2.fits', 0,
                                 {'YDIM': [agnkey.util.readkey3(hdr, 'naxis2'), 'y number of pixels']})
        agnkey.util.updateheader(img + '.sn2.fits', 0,
                                 {'PSF_FWHM': [fwhm * scale, 'FWHM (arcsec) - computed with daophot']})
        os.chmod(img + '.sn2.fits', 0664)
        os.chmod(img + '.psf.fits', 0664)
        result = 1

    except:
        result = 0
        fwhm = 0.0
        traceback.print_exc()
    return result, fwhm * scale

###########################################################################
if __name__ == "__main__":
    start_time = time.time()
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-f", "--fwhm", dest="fwhm", default='', help='starting FWHM  \t\t\t %default')
    parser.add_option("-t", "--threshold", dest="threshold", default=10., type='float',
                      help='Source detection threshold \t\t\t %default')
    parser.add_option("-c", "--catalog", dest="catalog", default='', type='str',
                      help='use input catalog  \t\t %default')
    parser.add_option("-r", "--redo", action="store_true", dest='redo', default=False,
                      help='Re-do \t\t\t\t [%default]')
    parser.add_option("-i", "--interactive", action="store_true", dest='interactive', default=False,
                      help='Interactive \t\t\t [%default]')
    parser.add_option("--fix", action="store_true", dest='fixaperture', default=False,
                      help='fixaperture \t\t\t [%default]')
    parser.add_option("-s", "--show", dest="show", action='store_true', default=False,
                      help='Show PSF output \t\t [%default]')
    parser.add_option("-X", "--xwindow", action="store_true", dest='xwindow', default=False,
                      help='xwindow \t\t\t [%default]')

    option, args = parser.parse_args()
    if len(args) < 1: sys.argv.append('--help')
    option, args = parser.parse_args()
    imglist = agnkey.util.readlist(args[0])
    _xwindow = option.xwindow
    fixaperture = option.fixaperture
    _catalog = option.catalog
    option, args = parser.parse_args()

    if _xwindow:
        from stsci.tools import capable

        capable.OF_GRAPHICS = False

    for img in imglist:
        if '.fits' in img: img = img[:-5]
        if os.path.exists(img + '.sn2.fits') and not option.redo:
            print img + ': psf already calculated'
        else:
            ds9 = os.system("ps -U" + str(os.getuid()) + "|grep -v grep | grep ds9")
            if option.interactive and ds9 != 0:
                pid = subprocess.Popen(['ds9']).pid
                time.sleep(2)
                ds9 = 0

            result, fwhm = ecpsf(img, option.fwhm, option.threshold, option.interactive, ds9, fixaperture,_catalog)
            print '\n### ' + str(result)

            iraf.delete("tmp.*", verify="no")
            iraf.delete("_psf.*", verify="no")
            print  "********** Completed in ", int(time.time() - start_time), "sec"
            print result
            if option.show:
                agnkey.util.marksn2(img + '.fits', img + '.sn2.fits', 1, '')
            try:
                import string
                if result == 1:
                    agnkey.agnsqldef.updatevalue('dataredulco', 'fwhm', fwhm, string.split(img, '/')[-1] + '.fits')
                    agnkey.agnsqldef.updatevalue('dataredulco', 'mag', 9999, string.split(img, '/')[-1] + '.fits')
                    agnkey.agnsqldef.updatevalue('dataredulco', 'apmag', 9999, string.split(img, '/')[-1] + '.fits')
                    if os.path.isfile(img + '.diff.fits') and os.path.isfile(
                                    img + '.sn2.fits'):  # update diff info is file available
                        os.system('cp ' + img + '.sn2.fits ' + img + '.diff.sn2.fits')
                        agnkey.agnsqldef.updatevalue('dataredulco', 'fwhm', fwhm,
                                                     string.split(img, '/')[-1] + '.diff.fits')
                        agnkey.agnsqldef.updatevalue('dataredulco', 'mag', 9999,
                                                     string.split(img, '/')[-1] + '.diff.fits')
                        agnkey.agnsqldef.updatevalue('dataredulco', 'apmag', 9999,
                                                     string.split(img, '/')[-1] + '.diff.fits')
                else:
                    pass
            except:
                print 'module mysqldef not found'
