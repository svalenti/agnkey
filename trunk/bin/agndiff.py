#!/usr/bin/env python
description = ">> make different image using hotpants"
usage = "%prog imagein  imagetem [options] "
import os
import string
import re
import sys
import agnkey
import time
import pyfits
import numpy as np
from optparse import OptionParser, OptionGroup
import tempfile

def crossmatchtwofiles(img1, img2, radius=3,substamplist='substamplist'):
    ''' This module is crossmatch two images:
        It run sextractor transform the pixels position of the the sources in coordinates and crossmatch them  
        The output is a dictionary with the objects in common
    '''
    import agnkey
    import pywcs
    from numpy import array, argmin, min, sqrt

    hd1 = pyfits.getheader(img1)
    hd2 = pyfits.getheader(img2)
    wcs1 = pywcs.WCS(hd1)
    wcs2 = pywcs.WCS(hd2)

    xpix1, ypix1, fw1, cl1, cm1, ell1, bkg1, fl1 = agnkey.agnastrodef.sextractor(img1)
    xpix2, ypix2, fw2, cl2, cm2, ell2, bkg2, fl2 = agnkey.agnastrodef.sextractor(img2)
    xpix1, ypix1, xpix2, ypix2 = array(xpix1, float), array(ypix1, float), array(xpix2, float), array(ypix2, float)

    bb = wcs1.wcs_pix2sky(zip(xpix1, ypix1), 1)  # transform pixel in coordinate
    xra1, xdec1 = zip(*bb)
    bb = wcs2.wcs_pix2sky(zip(xpix2, ypix2), 1)  # transform pixel in coordinate
    xra2, xdec2 = zip(*bb)

    xra1, xdec1, xra2, xdec2 = array(xra1, float), array(xdec1, float), array(xra2, float), array(xdec2, float)
    distvec, pos1, pos2 = agnkey.agnastrodef.crossmatch(xra1, xdec1, xra2, xdec2, radius)
    # dict={}
    dict = {'ra1': xra1[pos1], 'dec1': xdec1[pos1], 'ra2': xra2[pos2], 'dec2': xdec2[pos2],
            'xpix1': xpix1[pos1], 'ypix1': ypix1[pos1], 'xpix2': xpix2[pos2], 'ypix2': ypix2[pos2]}
    np.savetxt(substamplist, zip(xpix1[pos1], ypix1[pos1]), fmt='%10.10s\t%10.10s')
    return substamplist, dict



###################################################
if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-c", "--check", dest="check", action="store_true",
                      default=False, help=' check images registration \t\t\t [%default]')
    parser.add_option("-f", "--force", dest="force", action="store_true",
                      default=False, help=' force archiving \t\t\t [%default]')
    parser.add_option("--show", dest="show", action="store_true",
                      default=False, help=' show result  \t\t\t [%default]')
    parser.add_option("--verbose", dest="verbose", action="store_true",
                      default=False, help=' verbose result  \t\t\t [%default]')
    parser.add_option("--fixpix", dest="fixpix", action="store_true", default=False,
                      help='Run fixpix on the images before doing the subtraction')

    hotpants = OptionGroup(parser, "hotpants parameters")
    hotpants.add_option("--nrxy", dest="nrxy", default='1,1',
                        help='Number of image region in x y directions \t [%default]')
    hotpants.add_option("--nsxy", dest="nsxy", default='8,8',
                        help="Number of region's stamps in x y directions\t [%default]")
    hotpants.add_option("--ko", dest="ko", default='2',
                        help='spatial order of kernel variation within region\t [%default]')
    hotpants.add_option("--bgo", dest="bgo", default='2',
                        help='spatial order of background variation within region \t [%default]')
    hotpants.add_option("--afssc", dest="afssc", default=False,
                        action="store_true", help='use selected stamps \t\t\t [%default]')
    hotpants.add_option("--normalize", dest="normalize", default='i',
                        help='normalize zero point to image [i] or template [t] \t [%default]')
    hotpants.add_option("--convolve", dest="convolve", default='',
                        help='convolve direction to image [i] or template [t] \t [%default]')
    hotpants.add_option("--interpolation", dest="interpolation", default='drizzle',
                        help='interpolation algorithm  [drizzle,nearest,linear,poly3,poly5,spline3]\t [%default]')
    parser.add_option_group(hotpants)
    option, args = parser.parse_args()
    _normalize = option.normalize
    _convolve0 = option.convolve
    _interpolation = option.interpolation
    if _convolve0 not in ['i','t','']:
        sys.argv.append('--help')
    if _normalize not in ['i', 't']:
        sys.argv.append('--help')
    if _interpolation not in ['drizzle', 'nearest', 'linear', 'poly3', 'poly5', 'spline3']:
        sys.argv.append('--help')
    if len(args) < 2:
        sys.argv.append('--help')
    option, args = parser.parse_args()
    imglisttar = agnkey.util.readlist(args[0])
    imglisttemp = agnkey.util.readlist(args[1])
    from numpy import where, mean, savetxt

    _checkast = option.check
    _force = option.force
    _show = option.show
    _verbose = option.verbose
    _fixpix = option.fixpix

    #     saturation=40000
    nrxy = option.nrxy
    nsxy = option.nsxy
    ko = option.ko
    bgo = option.bgo
    afssc = option.afssc

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

    from pyraf import iraf
    from iraf import images
    from iraf import immatch

    for f in listatar:
        for o in listatar[f]:
            if f in listatemp:
                if o in listatemp[f]:
                    imglist1 = listatar[f][o]
                    imglist2 = listatemp[f][o]
                    for imgtarg_path in imglist1:
                        _dir, imgtarg0 = os.path.split(imgtarg_path)
                        if _dir: _dir += '/'
                        imgtemp_path = imglist2[0]
                        _dirtemp, imgtemp0 = os.path.split(imgtemp_path)
                        if _dirtemp: _dirtemp += '/'
                        imgout0 = re.sub('.fits', '.diff.fits', imgtarg0)
                        if os.path.isfile(_dir + imgout0) and not _force:
                            print 'file', imgout0, 'already there'
                            continue
                        targmask0 = re.sub('.fits', '.mask.fits', imgtarg0)
                        if not os.path.isfile(_dir + targmask0):
                            print "no cosmic ray mask for target image, run 'agnkeyloop.py -s cosmic' first"
                            continue
                        tempmask0 = re.sub('.fits', '.mask.fits', imgtemp0)
                        if not os.path.isfile(_dirtemp + tempmask0):
                            print "no cosmic ray mask for template image, run 'agnkeyloop.py -s cosmic' first"
                            continue
                        outmask0 = re.sub('.fits', '.mask.fits', imgout0)
                        artar, hdtar = pyfits.getdata(_dir+imgtarg0, header=True)

                        if os.path.isfile(_dirtemp+re.sub('.fits', '.sn2.fits', imgtemp0)):
                            hdtempsn = pyfits.getheader(_dirtemp+re.sub('.fits', '.sn2.fits', imgtemp0))
                        else:
                            hdtempsn = {}

                        ##########################################################
                        temp_file1 = next(tempfile._get_candidate_names())
                        temp_file2 = next(tempfile._get_candidate_names())
                        temp_file3 = next(tempfile._get_candidate_names())
                        temp_file0 = next(tempfile._get_candidate_names())

                        temp_file1, dict = crossmatchtwofiles(_dir + imgtarg0, _dirtemp + imgtemp0, 4,temp_file1)
                        xra1, xdec1, xra2, xdec2, xpix1, ypix1, xpix2, ypix2 = dict['ra1'], dict['dec1'], dict['ra2'], \
                                                                               dict['dec2'], dict['xpix1'], \
                                                                               dict['ypix1'], dict['xpix2'], \
                                                                               dict['ypix2']

                        vector4 = [str(k) + ' ' + str(v) + ' ' + str(j) + ' ' + str(l) for k, v, j, l in
                                   zip(xpix1, ypix1, xpix2, ypix2)]
                        if len(vector4) >= 12:
                            num = 3
                        else:
                            num = 2
                        np.savetxt(temp_file0+'_tmpcoo', vector4, fmt='%1s')
                        iraf.immatch.geomap(temp_file0+'_tmpcoo', "tmp$db"+temp_file0, 1, hdtar['NAXIS1'], 1, hdtar['NAXIS2'],
                                            fitgeom="general", functio="legendre", xxor=num, xyor=num, xxterms="half",
                                            yxor=num, yyor=num, yxterms="half", calctype="real", inter='No',verbose='no')

                        imgtemp = temp_file0+'_temp.fits'
                        imgtarg = temp_file0+'_targ.fits'
                        imgout = temp_file0+'_out.fits'
                        tempmask = temp_file0+'_tempmask.fits'
                        targmask = temp_file0+'_targmask.fits'
                        agnkey.util.delete(imgtemp)
                        agnkey.util.delete(imgtarg)
                        agnkey.util.delete(imgout)
                        agnkey.util.delete(tempmask)
                        agnkey.util.delete(targmask)
                        agnkey.util.delete(temp_file0+'_tempmask3.fits')
                        if os.path.isfile(re.sub('.fits','.clean.fits',_dir+imgtarg0)):
                            print 'use clean'
                            iraf.imcopy(re.sub('.fits','.clean.fits', _dir+imgtarg0), imgtarg, verbose='yes')
                        else:
                            iraf.imcopy(_dir + imgtarg0, imgtarg, verbose='no')

                        iraf.imcopy(_dir + targmask0, targmask, verbose='no')
#                        try:
                        iraf.immatch.gregister(_dirtemp + imgtemp0, imgtemp, "tmp$db"+temp_file0, temp_file0+"_tmpcoo", geometr="geometric",
                                               interpo=_interpolation, boundar='constant', constan=0, flux='yes', verbose='no')
                        try:
                            iraf.immatch.gregister(_dirtemp + tempmask0, tempmask, "tmp$db"+temp_file0, temp_file0+"_tmpcoo", geometr="geometric",
                                               interpo=_interpolation, boundar='constant', constan=0, flux='yes', verbose='no')
                        except:
                            # this is strange, sometime the registration of the msk fail the first time, but not the second time
                            iraf.immatch.gregister(_dirtemp + tempmask0, tempmask, "tmp$db"+temp_file0, temp_file0+"_tmpcoo", geometr="geometric",
                                               interpo=_interpolation, boundar='constant', constan=0, flux='yes', verbose='no')

                        if os.path.isfile(_dirtemp +re.sub('.fits','.var.fits',imgtemp0)):
                            if _verbose:  print 'variance image already there, do not create noise image'
                            iraf.immatch.gregister(_dirtemp + re.sub('.fits','.var.fits',imgtemp0), 
                                                   temp_file0+'_tempnoise3.fits', "tmp$db"+temp_file0, temp_file0+"_tmpcoo", geometr="geometric", 
                                                   interpo=_interpolation, boundar='constant', constan=0, flux='yes', verbose='no')


                        if _show:
                            iraf.display(imgtemp, frame=4, fill='yes')
                            iraf.display(_dirtemp + imgtemp0, frame=3, fill='yes')
                            iraf.display(imgtarg, frame=2, fill='yes')
                            iraf.display(_dir + imgtarg0, frame=1, fill='yes')

                        ###########################################################

                        data_targ, head_targ = pyfits.getdata(imgtarg, header=True)
                        exp_targ  = agnkey.util.readkey3(head_targ, 'exptime')
                        sat_targ = agnkey.util.readkey3(head_targ, 'saturate')
                        gain_targ = agnkey.util.readkey3(head_targ, 'gain')
                        rn_targ = agnkey.util.readkey3(head_targ,'ron')

                        data_temp, head_temp = pyfits.getdata(imgtemp, header=True)
                        exp_temp = agnkey.util.readkey3(head_temp, 'exptime')
                        sat_temp = agnkey.util.readkey3(head_temp, 'saturate')
                        gain_temp = agnkey.util.readkey3(head_temp, 'gain')

                        if 'rdnoise' in head_temp:
                            rn_temp   = head_temp['rdnoise']
                        else:
                            rn_temp   = 1

                        if 'L1FWHM' in head_targ: 
                            max_fwhm = head_targ['L1FWHM']  # to be check
                        else:                     
                            max_fwhm = 3.0

                        targmask_data = pyfits.getdata(targmask)

                        # round all values in template mask up to 1 (unless they are 0)
                        tempmask_data, tempmask_header = pyfits.getdata(tempmask, header=True)
                        tempmask_int = (tempmask_data > 0).astype('uint8')
                        tempmask_fits = pyfits.PrimaryHDU(header=tempmask_header, data=tempmask_int)
                        tempmask_fits.writeto(tempmask, clobber=True, output_verify='fix')

                        # create the noise images
                        median = np.median(data_targ)
                        noise = 1.4826*np.median(np.abs(data_targ - median))
                        pssl_targ = gain_targ*noise**2 - rn_targ**2/gain_targ - median
                        #noiseimg = (data_targ - median)**2
                        noiseimg = data_targ + pssl_targ + rn_targ**2
                        noiseimg[targmask_data > 0] = sat_targ
                        pyfits.writeto(temp_file0+'_targnoise3.fits', noiseimg, output_verify='fix', clobber=True)

                        #print 'variance image already there, do not create noise image'
                        if not os.path.isfile(_dirtemp +re.sub('.fits','.var.fits',imgtemp0)):                            
                            median = np.median(data_temp)
                            noise = 1.4826*np.median(np.abs(data_temp - median))
                            pssl_temp = gain_temp*noise**2 - rn_temp**2/gain_temp - median
                            #noiseimg = (data_temp - median)**2
                            noiseimg = data_temp + pssl_temp + rn_temp**2
                            noiseimg[tempmask_data > 0] = sat_temp
                            pyfits.writeto(temp_file0+'_tempnoise3.fits', noiseimg, output_verify='fix', clobber=True)
                        else:
                            pssl_temp = 0
                            print 'variance image already there, do not create noise image'

                        #  if skylevel is in the header, swarp with bkg subtraction has been applyed
                        if 'SKYLEVEL' in head_temp:
                            pssl_temp = head_temp['SKYLEVEL']

                        # create mask image for template
                        data_temp, head_temp
                        mask = np.abs(data_temp) < 1e-6
                        pyfits.writeto(temp_file0+'_tempmask3.fits',mask.astype('i'))

                        if _fixpix:
                            iraf.flpr(); iraf.flpr()
                            iraf.unlearn(iraf.fixpix)
                            iraf.fixpix('./'+imgtarg, './'+targmask, verbose='no')
                            iraf.flpr(); iraf.flpr()
                            iraf.unlearn(iraf.fixpix)
                            iraf.fixpix('./'+imgtemp, './'+tempmask, verbose='no')
                            iraf.flpr(); iraf.flpr()
                            iraf.unlearn(iraf.fixpix)
                        # hotpants parameters
                        iuthresh = str(sat_targ)                        # upper valid data count, image
                        iucthresh = str(0.95*sat_targ)                   # upper valid data count for kernel, image
                        tuthresh = str(sat_temp)                        # upper valid data count, template
                        tucthresh = str(0.95*sat_temp)                   # upper valid data count for kernel, template
                        rkernel = str(np.median([10, 2.*max_fwhm, 20])) # convolution kernel half width
                        radius = str(np.median([15, 3.0*max_fwhm, 25])) # HW substamp to extract around each centroid
                        sconv = '-sconv'                                # all regions convolved in same direction (0)

                        normalize = _normalize  #normalize to (t)emplate, (i)mage, or (u)nconvolved (t)

                        if _convolve0 in ['t','i']:
                            _convolve=' -c '+_convolve0+' '
                        else:
                            _convolve=''

                        if afssc:
                            temp_file2, xpix1, ypix1, xpix2, ypix2 = crossmatchtwofiles(imgtarg, imgtemp,3, temp_file2)
                            _afssc = ' -cmp ' + str(temp_file2) + ' -afssc 1 '
                        else:
                            _afssc = ''
                        line = ('hotpants -inim ' + imgtarg + ' -tmplim ' + imgtemp + ' -outim ' + imgout +
                                ' -tu ' + tuthresh + ' -tuk ' + tucthresh +
                                ' -tl ' + str(min(-pssl_temp,0)) + ' -tg ' + str(gain_temp) +
                                ' -tr ' + str(rn_temp) + ' -tp ' + str(min(-pssl_temp,0)) +
                                ' -tni '+ temp_file0+'_tempnoise3.fits ' +
                                ' -iu ' + str(iuthresh) + ' -iuk ' + str(iucthresh) + 
                                ' -il ' + str(min(-pssl_targ,0)) + ' -ig ' + str(gain_targ) +
                                ' -ir ' + str(rn_targ) + ' -ip ' + str(min(-pssl_targ,0)) +
                                ' -ini '+ temp_file0 + '_targnoise3.fits ' +
                                ' -r ' + str(rkernel) +
                                ' -nrx ' + nrxy.split(',')[0] + ' -nry ' + nrxy.split(',')[1] +
                                ' -nsx ' + nsxy.split(',')[0] + ' -nsy ' + nsxy.split(',')[1] +
                                _afssc + ' -rss ' + str(radius) +
                                _convolve + ' -n ' + normalize + ' ' + sconv +
                                ' -ko ' + ko + ' -bgo ' + bgo+' -tmi ' +
                                temp_file0 + '_tempmask3.fits  -okn -ng 4 9 0.70 6 1.50 4 3.00 2 5 ')


                        if _verbose:  
                            line = line + '-v 1'
                            os.system(line)
                        else:                        
                            line = line + '-v 0'
                            aa = os.popen(line).read()
                        print line    

                        # delete temporary files
                        if os.path.isfile(re.sub('.fits', '.conv.fits', imgout)):
                            os.system('rm ' + re.sub('.fits', '.conv.fits', imgout))
                        if os.path.isfile(re.sub('.fits', 'xy', imgout)):
                            os.system('rm ' + re.sub('.fits', 'xy', imgout))
                        if os.path.isfile(re.sub('.fits', 'xy.skipped', imgout)):
                            os.system('rm ' + re.sub('.fits', 'xy.skipped', imgout))
                        if os.path.isfile(re.sub('.fits', 'xy.all', imgout)):
                            os.system('rm ' + re.sub('.fits', 'xy.all', imgout))

                        hd = pyfits.getheader(imgout)
                        agnkey.util.updateheader(imgout, 0,
                                              {'template': [imgtemp0, 'template image'],
                                               'exptemp': [exp_temp,'exposure time template'],
                                               'target': [imgtarg0, 'target image'],
                                               'DIFFIM': [imgout0,'HOTPanTS : Difference Image'],
                                               'exptarg': [exp_targ,'exposure time target']})

                        if normalize == 't':
                            agnkey.util.updateheader(imgout, 0, {'EXPTIME': [exp_temp, '[s] Exposure length']})

                        if hd['CONVOL00'] == 'TEMPLATE':
                            if _verbose: print '\n ### image to compute  psf: '+imgtarg0
                            agnkey.util.updateheader(imgout, 0, {'PSF': [imgtarg0, 'image to compute  psf']})
                        else:
                            if _verbose:  print '\n ### image to compute  psf: '+imgtemp0
                            agnkey.util.updateheader(imgout, 0, {'PSF': [imgtemp0, 'image to compute  psf']})

                            #                    copy all information from target
                        hd = pyfits.getheader(imgout)
                        dictionary = {}
                        try:
                            ggg0 = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'dataredulco', 'namefile', imgtarg0, '*')
                            for voce in ggg0[0].keys():
                                if voce not in ['id','appmagap1','appmagap2','appmagap3','instmagap1',
                                                'apflux1','apflux2','apflux3','dapflux1','dapflux2','dapflux3',
                                                'instmagap2','instmagap3','dappmagap1','dappmagap2','dappmagap3']:
                                    dictionary[voce] = ggg0[0][voce]
                        except:
                            dictionary = {'dateobs': agnkey.util.readkey3(hd, 'date-obs'),
                                          'exptime': agnkey.util.readkey3(hd, 'exptime'),
                                          'dayobs': agnkey.util.readkey3(hd, 'day-obs'),
                                          'filter': agnkey.util.readkey3(hd, 'filter'),
                                          'telescope': agnkey.util.readkey3(hd, 'telescop'),
                                          'airmass': agnkey.util.readkey3(hd, 'airmass'),
                                          'objname': agnkey.util.readkey3(hd, 'object'),
                                          'wcs': agnkey.util.readkey3(hd, 'wcserr'), 
                                          'ut': agnkey.util.readkey3(hd, 'ut'),
                                          'mjd': agnkey.util.readkey3(hd, 'mjd'),
                                          'instrument': agnkey.util.readkey3(hd, 'instrume'),
                                          'ra0': agnkey.util.readkey3(hd, 'RA'), 
                                          'dec0': agnkey.util.readkey3(hd, 'DEC')}

                        dictionary['exptime'] =  agnkey.util.readkey3(hd, 'exptime')
                        dictionary['mag'] = 9999
                        dictionary['psfmag'] = 9999
                        dictionary['apmag'] = 9999
                        dictionary['z1'] = 9999
                        dictionary['z2'] = 9999
                        dictionary['c1'] = 9999
                        dictionary['c2'] = 9999
                        dictionary['psf']='X'
                        dictionary['namefile'] = imgout0
                        dictionary['wdirectory'] = _dir
                        dictionary['filetype'] = 3
                        if dictionary['wdirectory']:
                            if not os.path.isdir(dictionary['wdirectory']):
                                os.mkdir(dictionary['wdirectory'])
                            if not os.path.isfile(dictionary['wdirectory'] + imgout) or _force in ['yes', True]:
                                if _verbose:  print 'mv ' + imgout + ' ' + dictionary['wdirectory'] + imgout0
                                os.system('mv ' + imgout + ' ' + dictionary['wdirectory'] + imgout0)
                                os.system('mv ' + imgtemp + ' ' + dictionary['wdirectory'] + re.sub('.diff.', '.ref.', imgout0))
                        #  remove temp files

                        agnkey.util.delete(temp_file1)
                        agnkey.util.delete(temp_file2)
                        agnkey.util.delete(temp_file0)
                        agnkey.util.delete(temp_file0+'*')
                        ###########################################################################################################
                        #                           choose sn2 file depending on
                        #                           normalization parameter
                        #
                        ##########################################################################################################
                        if normalize == 'i':
                            if _verbose:  print '\n ### scale to target'
                            imgscale = imgtarg0
                            pathscale = _dir
                        elif normalize == 't':
                            if _verbose:  print '\n ### scale to reference'
                            imgscale = imgtemp0
                            pathscale = _dirtemp

                        if os.path.isfile(pathscale + re.sub('.fits', '.sn2.fits', imgscale)):
                            line = ('cp ' + pathscale + re.sub('.fits', '.sn2.fits', imgscale) + ' ' +
                                    dictionary['wdirectory'] + re.sub('.fits', '.sn2.fits', imgout0))
                            os.system(line)
                            if _verbose: print line
                            agnkey.util.updateheader(
                                dictionary['wdirectory'] + re.sub('.fits', '.sn2.fits', imgout0),
                                0, {'mag': [9999., 'apparent'], 'psfmag': [9999., 'inst mag'],
                                    'apmag': [9999., 'aperture mag']})
                            #
                            # this is to keep track on the zeropoint and the flux measurement on the template image 
                            # in the difference image. the final flux is the sum of the flux in the difference image 
                            # + the flux on the reference image 
                            # -2.5 * log10( Ft/ exp_t ) = -2.5 log10 (Delta /exp_t + Fr/exp_r  * 10**(Zr - Zt)/(-2.5)) 
                            #
                            #  Ft  flux target
                            #  Fr flux reference
                            #  Zr zeropoint rerefence
                            #  Zt zeropoint target        
                            #  Delta   flux on difference image
                            #
                            if 'ZPN' in hdtempsn:
                                agnkey.util.updateheader(dictionary['wdirectory'] + \
                                                         re.sub('.fits', '.sn2.fits', imgout0), 0,
                                                         {'ZPNref': [hdtempsn['ZPN'],
                                                                     'ZPN reference image']})
                            else:
                                if _verbose: print 'not ZN'
                                pass


                            if 'apflux1' in hdtempsn:
                                agnkey.util.updateheader(dictionary['wdirectory'] + \
                                                         re.sub('.fits', '.sn2.fits', imgout0), 0, {
                                                             'apfl1re': [hdtempsn['apflux1'], 'flux reference image'],
                                                             'dapfl1re': [hdtempsn['dapflux1'], 'error flux reference image']})
                            else:
                                if _verbose: print 'not apflux'
                                pass

                        else:
                            print 'fits table not found ' + str(dictionary['wdirectory'] + \
                                                                re.sub('.fits', '.sn2.fits',
                                                                       string.split(imgscale, '/')[-1]))

                        if agnkey.agnsqldef.conn:
                            ###################    insert in dataredulco
                            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'dataredulco',
                                                                  'namefile', string.split(imgout0, '/')[-1], '*')
                            if ggg and _force:   
                                agnkey.agnsqldef.deleteredufromarchive(string.split(imgout0, '/')[-1],
                                                                       'dataredulco', 'namefile')
                            if not ggg or _force:
                                if _verbose:
                                    print 'insert'
                                    print dictionary
                                agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn, 'dataredulco', dictionary)
                            else:
                                for voce in ggg[0].keys():
                                    if voce not in ['id','']:
                                        agnkey.agnsqldef.updatevalue('dataredulco', voce,
                                                                     dictionary[voce], string.split(imgout0, '/')[-1])
                            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'inoutredu',
                                                                  'nameout', string.split(imgout0, '/')[-1], '*')
                            if ggg:
                                agnkey.agnsqldef.deleteredufromarchive(string.split(imgout0, '/')[-1],
                                                                       'inoutredu', 'nameout')
                            dictionary = {'namein': string.split(imgtarg0, '/')[-1],
                                          'nameout': string.split(imgout0, '/')[-1],
                                          'nametemp': string.split(imgtemp0, '/')[-1], 'tablein': 'dataredulco',
                                          'tableout': 'dataredulco', 'tabletemp': 'dataredulco'}
                            if _verbose:
                                print 'insert in out'
                                print dictionary
                            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn, 'inoutredu', dictionary)
                        else:
                            print 'file ' + imgout0 + '  already there '
