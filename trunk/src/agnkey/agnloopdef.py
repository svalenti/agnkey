import agnkey

try:     from astropy.io import fits as pyfits
except:  import pyfits

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import string

def run_getmag(ll, _field, _output='', _interactive=False, _show=False, _bin=1e-10, magtype='mag',
               database='dataredulco',ra='',dec=''):
    import agnkey
    import datetime
    print magtype,ra,dec
    if magtype == 'mag':
        mtype = 'mag'
        mtypeerr = 'dmag'
    elif magtype == 'fit':
        mtype = 'psfmag'
        mtypeerr = 'psfdmag'
    elif magtype == 'ph':
        mtype = 'apmag'
        mtypeerr = 'psfdmag'
    elif magtype == 'appmagap1':
        mtype = 'appmagap1'
        mtypeerr = 'psfdmag'
    elif magtype == 'appmagap2':
        mtype = 'appmagap2'
        mtypeerr = 'psfdmag'
    elif magtype == 'appmagap3':
        mtype = 'appmagap3'
        mtypeerr = 'psfdmag'
    elif magtype == 'flux1':
        mtype = 'apflux1'
        mtypeerr = 'dapflux1'
    elif magtype == 'flux2':
        mtype = 'apflux2'
        mtypeerr = 'dapflux2'
    elif magtype == 'flux3':
        mtype = 'apflux3'
        mtypeerr = 'dapflux3'

    if _field == 'landolt':
        filters0 = ['U', 'B', 'V', 'R', 'I', 'Bessell-B', 'Bessell-V', 'Bessell-R',
                    'Bessell-I']  # to be raplace when more telescopes available with dictionary
    elif _field == 'sloan':
        filters0 = ['up', 'gp', 'rp', 'ip', 'zs', 'SDSS-G', 'SDSS-R', 'SDSS-I', 'Pan-Starrs-Z']
    elif _field == 'apass':
        filters0 = ['B', 'V', 'gp', 'rp', 'ip', 'Bessell-B', 'Bessell-V', 'SDSS-R', 'SDSS-I', 'Pan-Starrs-G']
    else:
        filters0 = ['up', 'gp', 'rp', 'ip', 'zs', 'SDSS-G', 'SDSS-R', 'SDSS-I', 'Pan-Starrs-Z']


    ww = np.where(ll[mtype])
    for key in ll.keys():
        ll[key] = ll[key][ww]

    mag=ll[mtype]
    dmag=ll[mtypeerr]
    hjd=ll['hjd']
    #namefile=ll['namefile']
    namefile = [k + v for k, v in zip(ll['wdirectory'], ll['namefile'])]
    filt=ll['filter']
    tel=ll['telescope']
    date=ll['dateobs']
    z1=ll['z1']
    z2=ll['z2']
    _magtype=ll['magtype']
    filetype = ll['filetype'][0]
    targid = ll['targid'][0]

    ll0 = ''
#    if mtype in ['apflux1','apflux2','apflux3']:
        #if filetype == 3:
        #    print 'add flux and zeropoint from reference'
        #    #######################################################
        #    command1=['select '+mtype+','+mtypeerr+\
        #              ',ZZ1, ZZ2, ZZ3, filter,instrument,namefile,wdirectory from dataredulco where targid='+\
        #              str(targid)+' and filetype=4']
        #    data1 = agnkey.agnsqldef.query(command1)
        #    ll0={'namefile':[]}
        #    for line in data1:
        #            ll0[line['namefile']] = {mtype:line[mtype], mtypeerr:line[mtypeerr]}
        #    #########################################
        #    mteplate = []
        #    mteplateerr = []
        #    for jj,_file in enumerate(namefile):
        #        hdr = pyfits.getheader(_file)
        #        if 'TEMPLATE' in hdr:
        #            # adding flux from reference image
        #            # since we scale all to temaplate the zero point is the same for all images
        #            # no need to apply zeropoint 
        #            if hdr['TEMPLATE'] in ll0:
        #                mteplate.append(ll0[hdr['TEMPLATE']][mtype])
        #                mteplateerr.append(ll0[hdr['TEMPLATE']][mtypeerr])
        #            else:
        #                mteplate.append(0)
        #                mteplateerr.append(0)
        #        else:
        #            mteplate.append(0)
        #            mteplateerr.append(0)
        #elif filetype == 1:
        #    ############################################################################
        #    #  NOT working 
        #    print 'add flux and zeropoint from each image'
        #    command1=['select '+mtype+','+mtypeerr+\
        #              ',ZZ1, ZZ2, ZZ3, ZZ1err,ZZ2err, ZZ3err, filter,instrument,namefile from dataredulco where targid='+\
        #              str(targid)+' and filetype=1 and quality!=1 and '+mtype+' is not NULL']
        #    data1 = agnkey.agnsqldef.query(command1)
        #    ll0={'namefile':[]}
        #    print mtype
        #    for line in data1:
        #        if '1' in mtype:
        #            ll0[line['namefile']] = {'ZZ':float(line['ZZ1'])-25, 'dZZ':line['ZZ1err']}
        #        elif '2' in mtype:
        #            ll0[line['namefile']] = {'ZZ':float(line['ZZ2'])-25, 'dZZ':line['ZZ2err']}
        #        elif '3' in mtype:
        #            ll0[line['namefile']] = {'ZZ':float(line['ZZ3'])-25, 'dZZ':line['ZZ3err']}
        #    mteplate = []
        #    mteplateerr = []
        #    for jj,_file in enumerate(namefile):
        #        mteplate.append(10**(-0.4*(ll0[os.path.basename(_file)]['ZZ'])))
#       #         mteplateerr.append(10**(0.4*ll0[_file]['dZZ']))
        #        mteplateerr.append(0)
        #    print mteplate
        #    ##########################################################################
#        else:
#            ll0 = ''
#            #######################################################
#    if ll0:
#        print 'add ZERO POINT TO FLUX for each night'
#        mag = np.array(mag,float) + np.array(mteplate,float)
#        dmag = np.array(dmag,float) + np.array(mteplateerr,float)

    setup={}
    setup['mtype']=mtype
    for _tel in set(tel):
        for _fil in set(filt):
            aaa=np.asarray((np.array(filt) == _fil) & (np.array(tel) == _tel))
            if len(aaa):
                if _tel not in setup:
                    setup[_tel]={}
                if _fil not in setup[_tel]:
                    setup[_tel][_fil]={}
                hjd00 = np.compress((np.array(filt) == _fil) & (np.array(tel) == _tel), np.array(hjd))
                mag00 = np.compress((np.array(filt) == _fil) & (np.array(tel) == _tel), np.array(mag))
                dmag00 = np.compress((np.array(filt) == _fil) & (np.array(tel) == _tel), np.array(dmag))
                date00 = np.compress((np.array(filt) == _fil) & (np.array(tel) == _tel), np.array(date))
                namefile00 = np.compress((np.array(filt) == _fil) & (np.array(tel) == _tel), np.array(namefile))
                z100 = np.compress((np.array(filt) == _fil) & (np.array(tel) == _tel), np.array(z1))
                z200 = np.compress((np.array(filt) == _fil) & (np.array(tel) == _tel), np.array(z2))
                magtype00 = np.compress((np.array(filt) == _fil) & (np.array(tel) == _tel), np.array(_magtype))

                ww = np.where((np.array(mag00) > -99999999)&(np.array(mag00) < 9999999))

                hjd0 = hjd00[ww]
                mag0 = mag00[ww]
                dmag0 = dmag00[ww]
                date0 = date00[ww]
                namefile0 = namefile00[ww]
                z10 = z100[ww]
                z20 = z200[ww]
                magtype0 = magtype00[ww]

                inds = np.argsort(hjd0)
                mag0 = np.take(mag0, inds)
                dmag0 = np.take(dmag0, inds)
                date0 = np.take(date0, inds)
                namefile0 = np.take(namefile0, inds)
                hjd0 = np.take(hjd0, inds)
                z10 = np.take(z10, inds)
                z20 = np.take(z20, inds)
                magtype0 = np.take(magtype0, inds)


                magtype1, mag1, dmag1, hjd1, date1, namefile1 = [], [], [], [], [], []
                done = []
                for i in range(0, len(hjd0)):
                    if i not in done:
                        ww = np.asarray([j for j in range(len(hjd0)) if
                                  (hjd0[j] - hjd0[i]) < _bin and (hjd0[j] - hjd0[i]) >= 0.0])  # abs(mjd0[j]-mjd0[i])<bin])
                        for jj in ww: done.append(jj)
                        if len(ww) >= 2:
                            hjd1.append(np.mean(hjd0[ww]))
                            if magtype == 'fit':
                                mag1.append(np.mean(mag0[ww]))
                            else:
                                mag1.append(np.mean(mag0[ww]))
                            try:
                                dmag1.append(np.std(mag0[ww]) / np.sqrt(len(ww)))
                            except:
                                dmag1.append(0.0)
                            magtype1.append(np.std(magtype0[ww]))
                            namefile1.append(namefile0[ww])
                            date1.append(date0[ww][0] + datetime.timedelta(np.mean(hjd0[ww]) - hjd0[ww][0]))
                        elif len(ww) == 1:
                            hjd1.append(hjd0[ww][0])
                            mag1.append(mag0[ww][0])
                            magtype1.append(magtype0[ww][0])
                            dmag1.append(dmag0[ww][0])
                            date1.append(date0[ww][0])
                            namefile1.append(namefile0[ww][0])
                setup[_tel][_fil]['mag'] = mag1
                setup[_tel][_fil]['magtype'] = magtype1
                setup[_tel][_fil]['dmag'] = dmag1
                setup[_tel][_fil]['hjd'] = list(np.array(hjd1))
                setup[_tel][_fil]['date'] = date1
                setup[_tel][_fil]['namefile'] = namefile1

    if _show:
        plotfast(setup)
        print setup['mtype']
        try:
            plotfast(setup)
        except:
            pass
    else:
        if _output:
            try:
                plotfast(setup, _output)
            except:
                pass

    keytelescope = {'1m0-03': '3', '1m0-04': '4', '1m0-05': '5', '1m0-06': '6', '1m0-07': '7', '1m0-08': '8',
                    '1m0-09': '9', '1m0-10': '10', '1m0-11': '11', '1m0-12': '12', '1m0-13': '13', 'fts': '14',
                    'ftn': '15', 'other': '20','2m0a':'14','2m0b':'15', '2m0-01':'14','2m0-02':'15'}
    if _tel not in keytelescope.keys():
        _tel = 'other'

    linetot = {}
    if _output: ff = open(_output, 'w')
    for _tel in setup:
      if  _tel!='mtype':
        filters = setup[_tel].keys()
        line0 = '# %10s\t%12s\t' % ('dateobs', 'hjd')
        for filt in filters0:
            if filt in filters and filt in setup[_tel].keys():
                line0 = line0 + '%12.12s\t%12.12s\t' % (str(filt), str(filt) + 'err')
        for _fil in setup[_tel]:
            for j in range(0, len(setup[_tel][_fil]['hjd'])):
                line = '  %10s\t%12s\t' % (str(setup[_tel][_fil]['date'][j]), str(setup[_tel][_fil]['hjd'][j]))
                for filt in filters0:
                    if filt in filters:
                        if filt == _fil:
                            line = line + '%12.10f\t%12.10f\t' % (
                            setup[_tel][_fil]['mag'][j], setup[_tel][_fil]['dmag'][j])
                        else:
                            if mtype not in ['apflux1','apflux2','apflux3']:
                                line = line + '%12.7s\t%12.6s\t' % ('9999', '0.0')
                            else:
                                line = line + '%12.7s\t%12.6s\t' % ('nan', 'nan')
                line = line + '%2s\t%6s\t\n' % (str(keytelescope[_tel]), str(_tel) + '_' + str(_fil))
                linetot[setup[_tel][_fil]['hjd'][j]] = line
    aaa = linetot.keys()
    if _output:
        for gg in np.sort(aaa):
            ff.write(linetot[gg])
    else:
        for gg in np.sort(aaa):
            print linetot[gg]
    if _output:
        ff.close()

    return setup


def run_cat(imglist, extlist, _interactive=False, mode=1, _type='fit', _fix=False, database='dataredulco',
            _field='slaon'):
    import agnkey
    import glob
    from numpy import where, array

    status = []
    if mode == 1:
        _mode = 'agncatalogue2.py'
        stat = 'abscat'
    elif mode == 2:
        _mode = 'agnmag.py'
        stat = 'mag'

    if len(extlist) > 0:
        for img in extlist:  
            status.append(checkstage(img, stat))
        extlist = extlist[where(array(status) > 0)]
        status = array(status)[where(array(status) > 0)]
        f = open('_tmpext.list', 'w')
        for img in extlist:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            f.write(_dir + re.sub('fits', 'sn2.fits', img) + '\n')
        f.close()
    else:
        for img in imglist:  
            status.append(checkstage(img, stat))
        imglist = imglist[where(array(status) > 0)]
        status = array(status)[where(array(status) > 0)]


    f = open('_tmp.list', 'w')
    for img in imglist:
        ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
        _dir = ggg[0]['wdirectory']
        f.write(_dir + re.sub('fits', 'sn2.fits', img) + '\n')
    f.close()
    if _interactive:
        ii = ' -i '
    else:
        ii = ''
    if _fix:
        ff = ' -c '
    else:
        ff = ''
    tt = ' -t ' + _type + ' '
    if _field:
        ss = ' -s ' + _field
    else:
        ss = ''
    # catalogue doesn't want to specify the system (sloan.landolt,apass)
    if mode == 1: ss = ''

    if len(extlist) > 0:
        command = _mode + ' _tmp.list -e _tmpext.list ' + ii + tt + ff + ss
    else:
        command = _mode + ' _tmp.list ' + ii + tt + ff + ss
    print command
    os.system(command)


def run_wcs(imglist, interactive=False, redo=False, _xshift=0, _yshift=0, catalogue='', database='dataredulco',mode='sv'):
    import agnkey
    import glob
    direc = ''
    for ggg in imglist:
        _dir,img = os.path.split(ggg)
        _dir = _dir+'/'
        status = checkstage(img, 'wcs')
        if status == -4 and redo:
            print 'wcs not good, try again'
            agnkey.agnsqldef.updatevalue(database, 'quality', 0, string.split(img, '/')[-1])
            status = checkstage(img, 'wcs')

        if status == 0: rr = '-r'
        if redo:
            rr = '-r'
        else:
            rr = ''
        if interactive:
            ii = '-i'
        else:
            ii = ''
        if catalogue:
            cc = ' -c ' + catalogue
        else:
            cc = ''
        if status >= -1:
            if not cc:
                ###########################################
                print _dir + img
                _ra0, _dec0, _SN0 = agnkey.util.checksnlist(_dir + img, 'supernovaelist.txt')
                if not _SN0:    
                    _ra0, _dec0, _SN0 = agnkey.util.checksnlist(_dir + img, 'standardlist.txt')
                if not _SN0:    
                    _ra0, _dec0, _SN0, _tt = agnkey.util.checksndb(_dir + img, 'lsc_sn_pos')
                print _ra0, _dec0, _SN0
                if _SN0:
                    _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/landolt/' + _SN0 + '*')
                    if len(_catalogue) == 0:
                        _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/sloan/' + _SN0 + '*')
                else:
                    _catalogue = []
                if len(_catalogue) > 0: cc = ' -c ' + re.sub(agnkey.__path__[0] + '/standard/cat/', '', _catalogue[0])
            #               ############################
            if mode =='sv':
                command = 'agnastro.py ' + _dir + img + ' ' + rr + ' ' + ii + ' -m  vizir --xshift ' + str(
                    _xshift) + ' --yshift ' + str(_yshift) + cc  #+' '+ff+' '+cc+' -t '+_type+' '+ss
                print command
                os.system(command)
            elif mode=='astrometry':
                agnkey.agnastrodef.run_astrometry(_dir + img, True,redo)
            else:
                print str(mode)+' not defined'

        elif status == 0:
            print 'status ' + str(status) + ': WCS stage not done'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'


def run_zero(imglist, _fix, _type, _field, _catalogue, _color='', interactive=False, redo=False, show=False, _cutmag=99,
             database='dataredulco', _calib=''):
    import agnkey
    import glob

    direc = agnkey.__path__[0]
    for img in imglist:
        if interactive:
            ii = ' -i '
        else:
            ii = ''
        if _fix:
            ff = ' -f '
        else:
            ff = ''
        if redo:
            rr = ' -r '
        else:
            rr = ''
        if _field:
            ss = ' -s ' + _field + ' '
        else:
            ss = ''
        if show:
            dd = ' --show '
        else:
            dd = ''
        if _calib:
            ll = '--calib ' + _calib
        else:
            ll = ''
        if _color:
            hh = ' -C ' + _color + ' '
        else:
            hh = ''
        status = checkstage(img, 'zcat')
        if status == 1: 
            rr = '-r'
        if status >= 1:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            if not _catalogue:
                _ra0, _dec0, _SN0 = agnkey.util.checksnlist(_dir + img, 'supernovaelist.txt')
                if not _SN0:    _ra0, _dec0, _SN0 = agnkey.util.checksnlist(_dir + img, 'standardlist.txt')
                if not _SN0:    _ra0, _dec0, _SN0, _tt = agnkey.util.checksndb(_dir + img, 'lsc_sn_pos')
                print _ra0, _dec0, _SN0
                if _SN0:
                    if not _calib:
                        _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/' + _field + '/' + _SN0 + '*')
                    elif _calib == 'natural':
                        _catalogue = glob.glob(
                            agnkey.__path__[0] + '/standard/cat/' + _field + 'natural/*' + _SN0 + '*')
                    elif _calib == 'sloanprime':
                        _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/sloanprime/' + _SN0 + '*')
                    elif _calib == 'apass':
                        _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/apass/' + _SN0 + '*')
                    else:
                        _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/' + _field + '/' + _SN0 + '*')
                if _catalogue: _catalogue = _catalogue[0]
            if _catalogue:
                cc = ' -c ' + _catalogue + ' '
            else:
                cc = ''
            command = 'agnabsphot.py ' + _dir + re.sub('fits', 'sn2.fits',img) + ' ' +\
                      ii + rr + ff + cc + ' -t ' + _type + ' ' + ss + dd + hh + ll +\
                      ' --cutmag ' + str(_cutmag)
            print command
            os.system(command)
        elif status == 0:
            print 'status ' + str(status) + ': WCS stage not done'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'


def run_apmag(imglist, database='dataredulco', _ra='', _dec='', _catalog='', verbose=False):
    import agnkey
    import glob

    for ggg in imglist:
            _dir,img1 = os.path.split(ggg)
            _dir = _dir+'/'
            if _ra and _dec:
                cord = ' --RA ' + str(_ra) + ' --DEC ' + str(_dec)
            else:
                cord = ''
            if _catalog:
                cc=' --catalog '+str(_catalog)+' '
            else:
                cc=' '
            if verbose:
                vv = ' -v '
            else:
                vv = ''
            print _dir + img1
            if os.path.isfile(_dir + img1):
                command = 'agnnewcalib.py ' + _dir + img1 + cord  + cc  + vv
                print command
                os.system(command)
            else:
                print img1, ' not found'


# ##################################################################

def run_cosmic(imglist, database='dataredulco', _sigclip=4.5, _sigfrac=0.2, _objlim=4, _force=False):
    import agnkey
    direc = agnkey.__path__[0]
    import glob

    for ggg in imglist:
            _dir,img = os.path.split(ggg)
            if _dir:
                _dir = _dir+'/'
            print _dir + img
            if os.path.isfile(_dir + img):
                if not os.path.isfile(re.sub('.fits', '.clean.fits', _dir + img)) or _force:
                    print _dir + img, _sigclip, _sigfrac, _objlim
                    output, mask, satu = agnkey.util.Docosmic(_dir + img, _sigclip, _sigfrac, _objlim)
                    agnkey.util.updateheader(output, 0, {'DOCOSMIC': [True, 'Cosmic rejection using LACosmic']})
                    print 'mv ' + output + ' ' + _dir
                    os.system('mv ' + output + ' ' + _dir)
                    os.system('mv ' + mask + ' ' + _dir)
                    os.system('mv ' + satu + ' ' + _dir)
                    print output, mask, satu
                else:
                    print 'cosmic rejection alread done'
            else:
                print img, ' not found'


###################################################################

def run_idlstart(imglist, database='dataredulco', _force=True):
    import agnkey
    import sys
    from pyraf import iraf

    iraf.imred(_doprint=0)
    iraf.specred(_doprint=0)
    direc = agnkey.__path__[0]
    import glob

    for ggg in imglist:
        _dir,img = os.path.split(ggg)
        if _dir:
            _dir = _dir+'/'
        print _dir + img                     
        if os.path.isfile(_dir + img):
            hdr = agnkey.util.readhdr(_dir + img)
            _telescope = agnkey.util.readkey3(hdr, 'telescop')
            _telid = agnkey.util.readkey3(hdr, 'telid')
            _site = agnkey.util.readkey3(hdr, 'SITEID')
            print _telescope, _telid,_site
            if _telescope in agnkey.util.telescope0['elp']:
                tel_tag = 'LCOGT-McDonald'
                _observatory = 'mcdonald'
            elif _telescope in agnkey.util.telescope0['cpt']:
                tel_tag = 'LCOGT-SAAO'
                _observatory = 'sso'
            elif _telescope in agnkey.util.telescope0['ogg']:
                _observatory = 'cfht'
                tel_tag = 'FTN'
            elif _telescope in agnkey.util.telescope0['lsc']:
                tel_tag = 'LCOGT-CTIO'
                _observatory = 'lco'
            elif _telescope in agnkey.util.telescope0['coj']:
                _observatory = 'sso'
                if _telid in ['1m0a', '1m0b', '1m0c']:
                    tel_tag = 'LCOGT-SSO'
                else:
                    tel_tag = 'FTS'
            elif _site in ['coj']:
                _observatory = 'sso'
                tel_tag = 'FTS'
            elif _site in ['ogg']:
                _observatory = 'cfht'
                tel_tag = 'FTN'
            else:
                print _telescope
                sys.exit('ERROR: site and telescope not correct')
            if 'HJD' not in hdr.keys() or _force:
                print _dir + img
                iraf.specred.setjd(_dir + img+'[0]', date='DATE-OBS', time='UTSTART', \
                                   exposure='EXPTIME', ra='ra', dec='dec', epoch='', observa=_observatory)
            else:
                print 'HJD already there'
            if 'TEL_TAG' not in hdr.keys() or _force:
                agnkey.util.updateheader(_dir + img, 0,
                                         {'tel_tag': [tel_tag, 'telescope identification for idl reduction']})
            else:
                print 'tel_tag already there'
        else:
            print img, ' not found'

def updatefromheader(imglist,imgheader='hjd',tablecolumn='hjd',database='dataredulco'):
    for img0 in imglist:
        _dir,img = os.path.split(img0)
        if _dir:
            _dir = _dir+'/'
        print _dir + img                     
        if os.path.isfile(_dir + img):
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            hdr = agnkey.util.readhdr(_dir + img)
            if len(ggg):
                if imgheader in hdr and tablecolumn in ggg[0]:
                    print img,hdr[imgheader],tablecolumn
                    agnkey.agnsqldef.updatevalue(database, tablecolumn, hdr[imgheader], img)
        


###################################################################

def run_psf(imglist, treshold=5, interactive=False, _fwhm='', show=False, redo=False, xwindow='',
            fix=True, catalog='', database='dataredulco', datamax=''):
    import agnkey

    for img in imglist:
        if interactive:
            ii = '-i'
        else:
            ii = ''
        if show:
            ss = '-s'
        else:
            ss = ''
        if redo:
            rr = '-r'
        else:
            rr = ''
        if _fwhm:
            ff = '-f ' + str(_fwhm) + ' '
        else:
            ff = ''
        if fix:
            gg = ' '
        else:
            gg = ' --fix '
        if catalog:
            cc=' --catalog '+catalog+' '
        else:
            cc=' '

        if datamax:
            dd = ' --datamax '+str(datamax) + ' '
        else:
            dd = ' '

        status = checkstage(img, 'psf')
        print status
        if status == 1: rr = '-r'
        if status >= 1:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            if ggg[0]['filetype'] == 3:
                ##################################################################################
                print '\n### get parameters for difference image'
                _dir = ggg[0]['wdirectory']
                hdrdiff=agnkey.util.readhdr(_dir+img)
                if 'PSF' not in hdrdiff:
                    sys.exit('\n### warning PSF file not defined')
                else:
                    imgpsf=hdrdiff['PSF']
                    print '\n### psf file for difference image: '+imgpsf
                    statuspsf = checkstage(imgpsf, 'psf')
                    print statuspsf
                    if statuspsf == 2:
                        print 'psf file for difference image found'
                        gggpsf = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(imgpsf), '*')
                        _dirpsf = gggpsf[0]['wdirectory']
                        os.system('cp '+_dirpsf+re.sub('.fits', '.psf.fits', imgpsf)+' '+_dir+
                                  re.sub('.fits', '.psf.fits', img))
                        agnkey.agnsqldef.updatevalue('dataredulco', 'psf', re.sub('.fits', '.psf.fits', img),
                                             string.split(img, '/')[-1])
                        print '\n ### copy '+re.sub('.fits', '.psf.fits', imgpsf)+' in '+re.sub('.fits', '.psf.fits', img)
                    else:
                        print '\n### ERROR: PSF file not found \n please run psf file on image: '+imgpsf
                #####################################################################################
                if 'PHOTNORM' not in hdrdiff:
                    sys.exit('\n ### warning PHOTNORM file not defined')
                else:
                    photnorm=hdrdiff['PHOTNORM']
                    if photnorm=='t':
                        print '\n ### zero point done with template'
                        imgtable = hdrdiff['TEMPLATE']

                    elif photnorm=='i':
                        print '\n ### zero point done with target'
                        imgtable = hdrdiff['TARGET']

                    sntable = re.sub('.fits','.sn2.fits',imgtable)
                    gggtable = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(imgtable), '*')
                    dirtable = gggtable[0]['wdirectory']

                    if os.path.isfile(dirtable+sntable):
                        print '\n ### fits table found '
                        print 'cp ' + dirtable + sntable + ' ' + _dir + re.sub('.fits', '.sn2.fits', img)
                        os.system('cp ' + dirtable + sntable + ' ' + _dir + re.sub('.fits', '.sn2.fits', img))
                    else:
                        sys.exit('ERROR: fits table not there, run psf for ' + sntable)
#############################
            else:
                img0 = img
                command = 'agnpsf.py ' + _dir + img0 + ' ' + ii + ' ' + ss + ' ' + rr + ' ' + ff + ' ' + '-t ' + str(
                    treshold) + xwindow + gg + cc + dd
                print command
                os.system(command)
        elif status == 0:
            print 'status ' + str(status) + ': WCS stage not done'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'
    ##################################################################

###################################################################

def run_psf2(imglist, treshold=5, interactive=False, _fwhm='', show=False, redo=False, xwindow='',
            fix=True, catalog='',database='dataredulco',  datamax=''):
    import agnkey

    for img in imglist:
        if interactive:
            ii = '-i'
        else:
            ii = ''
        if show:
            ss = '-s'
        else:
            ss = ''
        if redo:
            rr = '-r'
        else:
            rr = ''
        if catalog:
            cc=' --catalog '+catalog+' '
        else:
            cc=' '
        if _fwhm:
            ff = '-f ' + str(_fwhm) + ' '
        else:
            ff = ''
        if fix:
            gg = ' '
        else:
            gg = ' --fix '
        if datamax:
            dd = ' --datamax '+str(datamax) + ' '
        else:
            dd = ' '

        status = checkstage(img, 'psf')
        print status
        if status == 1: rr = '-r'
        if status >= 1:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            if ggg[0]['filetype'] == 3:
                img0 = re.sub('.diff.fits', '.fits', img)
            else:
                img0 = img
            command = 'agnpsf2.py ' + _dir + img0 + ' ' + ii + ' ' + ss + ' ' + rr + ' ' + ff + ' ' + '-t ' + str(
                treshold) + xwindow + gg + cc + dd
            print command
            os.system(command)
        elif status == 0:
            print 'status ' + str(status) + ': WCS stage not done'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'
    ##################################################################

def run_fit(imglist, _ras='', _decs='', _xord=3, _yord=3, _bkg=4, _size=7, _recenter=False, _ref='', interactive=False,
            show=False, redo=False, dmax=51000, database='dataredulco'):
    import agnkey

    direc = agnkey.__path__[0]
    for img in imglist:
        status = checkstage(img, 'psfmag')
        print status
        if status >= 1:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            img0 = re.sub('.fits', '.sn2.fits', img)
            if interactive:
                ii = '-i'
            else:
                ii = ''
            if _recenter:
                cc = '-c'
            else:
                cc = ''
            if show:
                ss = '-s'
            else:
                ss = ''
            if redo:
                rr = '-r'
            else:
                rr = ''
            if dmax:
                dd = ' --datamax '+str(dmax)+' '
            else:
                dd = ' '
            if _ref:
                print img0, _ref, show
                _ras, _decs = agnkey.agnloopdef.getcoordfromref(img0, _ref, show)
            if _ras: _ras = '-R ' + str(_ras)
            if _decs: _decs = '-D ' + str(_decs)

            command = 'agnsn.py ' + _dir + img + ' ' + ii + ' ' + ss + ' ' + rr + ' -x ' + str(_xord) + ' -y ' + str(
                _yord) + ' ' + _ras + ' ' + _decs + ' ' + cc + ' -b ' + str(_bkg) + '  -z ' + str(
                _size) + dd

            if ggg[0]['filetype'] == 3:
                try:
                    img2 = pyfits.getheader(_dir + img)['PSF']
                    ggg2 = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img2), '*')
                    _dir2 = ggg2[0]['wdirectory']
                    pp = ' -p ' + _dir2 + re.sub('.fits', '.psf.fits', img2) + ' '
                    command = command + pp
                except:
                    command = ''
                    print 'PSF header not found in ' + str(img)
            print command
            os.system(command)
        elif status == 0:
            print 'status ' + str(status) + ': psf stage not done'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'
    ##################################################################


def checkstage(img, stage, database='dataredulco'):
    #  -4  bad quality
    #  -3  image not ingested in the dedu table
    #  -2  image not in the working directory
    #  -1  sn2 not in the working directory
    #   0  not done and previous stage not done
    #   1  not done and possible since previous stage done
    #   2  done and possible to do again
    #   3  local sequence catalogue available  
    import agnkey

    status = 0
    ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
    if not ggg:
        status = -3  # not in the redo table
    else:
        _dir = ggg[0]['wdirectory']
        if ggg[0]['quality'] == 1:
            status = -4  #  bad quality image
        else:
            if not os.path.isfile(_dir + img):
                status = -2  # fits image not in working dir
            elif not os.path.isfile(_dir + re.sub('fits', 'sn2.fits', img)):
                status = -1  # sn2 table not in working dir
    if stage == 'wcs' and status >= -1:
        if ggg[0]['wcs'] != 0:
            status = 1
        else:
            status = 2
    elif stage == 'psf' and status >= -1 and ggg[0]['wcs'] == 0:
        if ggg[0]['psf'] == 'X':
            status = 1
        else:
            status = 2
    elif stage == 'psfmag' and status >= 0 and ggg[0]['psf'] != 'X' and ggg[0]['wcs'] == 0:
        if ggg[0]['psfmag'] == 9999 or ggg[0]['psfmag'] == 9999:
            status = 1
        else:
            status = 2
    elif stage == 'zcat' and status >= 0 and ggg[0]['psf'] != 'X' and ggg[0]['wcs'] == 0:
        if ggg[0]['zcat'] == 'X':
            status = 1
        else:
            status = 2
    elif stage == 'mag' and status >= 0 and ggg[0]['zcat'] != 'X' and ggg[0]['psfmag'] != 9999:
        if ggg[0]['mag'] == 9999:
            status = 1
        else:
            status = 2
    elif stage == 'abscat' and status >= 0 and ggg[0]['zcat'] != 'X' and ggg[0]['psf'] != 'X':
        if ggg[0]['abscat'] == 'X':
            status = 1  # mag should be replaced with 'cat'
        else:
            status = 2
    elif stage == 'checkpsf' and status >= -1 and ggg[0]['wcs'] == 0:
        if ggg[0]['psf'] == 'X':
            status = 1
        else:
            status = 2
    elif stage == 'checkmag' and status >= 0 and ggg[0]['psf'] != 'X' and ggg[0]['wcs'] == 0:
        if ggg[0]['psfmag'] == 9999 or ggg[0]['psfmag'] == 9999:
            status = 1
        else:
            status = 2
    else:
        pass
    return status


####################################################################################
def getcoordfromref(img2, img1, _show, database='dataredulco'):  #img1.sn2  img2.sn2  import pyraf outside
    import agnkey
    from numpy import zeros, array, median, compress
    from pyraf import iraf

    iraf.digiphot(_doprint=0)
    iraf.daophot(_doprint=0)
    ggg1 = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile',
                                           re.sub('sn2.fits', 'fits', img1), '*')
    _dir1 = ggg1[0]['wdirectory']

    ggg2 = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile',
                                           re.sub('sn2.fits', 'fits', img2), '*')
    _dir2 = ggg2[0]['wdirectory']

    print _dir1, _dir2, img1, img2

    dicti1 = agnkey.agnabsphotdef.makecatalogue([_dir1 + img1])
    dicti2 = agnkey.agnabsphotdef.makecatalogue([_dir2 + img2])
    for i in dicti1.keys():
        for j in dicti1[i].keys():
            ra01 = dicti1[i][j]['ra0']
            dec01 = dicti1[i][j]['dec0']
    for i in dicti2.keys():
        for j in dicti2[i].keys():
            ra02 = dicti2[i][j]['ra0']
            dec02 = dicti2[i][j]['dec0']

    print _dir1 + img1
    t = pyfits.open(_dir1 + img1)
    tbdata = t[1].data
    hdr1 = t[0].header
    psfx1 = agnkey.util.readkey3(hdr1, 'PSFX1')
    psfy1 = agnkey.util.readkey3(hdr1, 'PSFY1')
    print psfx1, psfy1
    if psfx1 != None and psfy1 != None:
        lll = str(psfx1) + ' ' + str(psfy1)
        aaa = iraf.wcsctran('STDIN', 'STDOUT', _dir1 + img1, Stdin=[lll], inwcs='logical', units='degrees degrees',
                            outwcs='world', columns='1 2', formats='%10.5f %10.5f', Stdout=1)[3]
        rasn1, decsn1 = string.split(aaa)
        if _show:
            iraf.set(stdimage='imt8192')
            iraf.display(_dir1 + re.sub('sn2.fits', 'fits', img1), 1, fill=True, Stdout=1, zsc='yes',
                         zra='yes')  #,z1=0,z2=3000)
            iraf.tvmark(1, 'STDIN', Stdin=[lll], mark="cross", number='no', label='no', radii=5, nxoffse=5, nyoffse=5,
                        color=205, txsize=1)

        #    ra01,dec01,ra02,dec02=array(ra01,float),array(dec01,float),array(ra02,float),array(dec02,float)
    distvec, pos1, pos2 = agnkey.agnastrodef.crossmatch(list(ra01), list(dec01), list(ra02), list(dec02), 5)
    #    from pylab import ion,plot
    #    ion()
    #    plot(ra01,dec01,'or')
    #    plot(ra02,dec02,'xb',markersize=10)
    #    plot(array(ra01)[pos1],array(dec01)[pos1],'3g',markersize=20)
    #    plot(array(ra02)[pos2],array(dec02)[pos2],'*m',markersize=10)
    #    raw_input('ddd')
    rra = ra01[pos1] - ra02[pos2]
    ddec = dec01[pos1] - dec02[pos2]
    rracut = compress((abs(array(ra02[pos2]) - float(rasn1)) < .05) & (abs(array(dec02[pos2]) - float(decsn1)) < .05),
                      array(rra))
    ddeccut = compress((abs(array(ra02[pos2]) - float(rasn1)) < .05) & (abs(array(dec02[pos2]) - float(decsn1)) < .05),
                       array(ddec))

    if len(rracut) > 10:
        rasn2c = float(rasn1) - median(rracut)
        decsn2c = float(decsn1) - median(ddeccut)
    else:
        rasn2c = float(rasn1) - median(rra)
        decsn2c = float(decsn1) - median(ddec)

    if _show:
        print 'shift in arcsec (ra dec)'
        print len(pos1), len(ra01)
        print median(rra), median(ddec)
        print 'SN position on image 2 computed'
        print rasn2c, decsn2c
        iraf.display(_dir2 + re.sub('sn2.fits', 'fits', img2), 2, fill=True, Stdout=1, zsc='yes',
                     zra='yes')  #,z1=0,z2=3000)
        lll = str(rasn2c) + ' ' + str(decsn2c)
        bbb = iraf.wcsctran('STDIN', 'STDOUT', _dir2 + img2, Stdin=[lll], inwcs='world', units='degrees degrees',
                            outwcs='logical', columns='1 2', formats='%10.5f %10.5f', Stdout=1)[3]
        iraf.tvmark(2, 'STDIN', Stdin=[bbb], mark="cross", number='no', label='no', radii=5, nxoffse=5, nyoffse=5,
                    color=206, txsize=1)
        from pylab import ion, plot

        ion()
        plot(rra, ddec, 'or')
        plot(rracut, ddeccut, 'xb')

    return rasn2c, decsn2c


def filtralist(ll2, _filter, _id, _name, _ra, _dec, _bad, _filetype=1):
    from numpy import array, asarray
    import sys
    import agnkey

    ll1 = {}
    for key in ll2.keys():  ll1[key] = ll2[key][:]

    if _filetype:
        if _filetype in [1, 2, 3, 4]:
            ww = asarray([i for i in range(len(ll1['filetype'])) if ((ll1['filetype'][i] == _filetype))])
            if len(ww) > 0:
                for jj in ll1.keys(): ll1[jj] = array(ll1[jj])[ww]
            else:
                for jj in ll1.keys(): ll1[jj] = []
    if _bad and _bad == 'quality':
        pass
    else:
        ww = asarray([i for i in range(len(ll1['quality'])) if ((ll1['quality'][i] != 1))])
        if len(ww) > 0:
            for jj in ll1.keys(): ll1[jj] = array(ll1[jj])[ww]
        else:
            for jj in ll1.keys(): ll1[jj] = []

    if _filter:  #filter 
        if _filter == 'sloan':
            ww = asarray([i for i in range(len(ll1['filter'])) if (
            (ll1['filter'][i] in ['zs', 'up', 'gp', 'ip', 'rp', 'SDSS-G', 'SDSS-R', 'SDSS-I', 'Pan-Starrs-Z']))])
        elif _filter == 'landolt':
            ww = asarray([i for i in range(len(ll1['filter'])) if (
            (ll1['filter'][i] in ['U', 'B', 'V', 'R', 'I', 'Bessell-B', 'Bessell-V', 'Bessell-R', 'Bessell-I']))])
        elif _filter == 'apass':
            ww = asarray([i for i in range(len(ll1['filter'])) if ((ll1['filter'][i] in ['B', 'V', 'Bessell-B',
                                                                                         'Bessell-V', 'gp', 'ip', 'rp',
                                                                                         'SDSS-G', 'SDSS-R',
                                                                                         'SDSS-I']))])
        elif _filter in ['zs', 'up', 'gp', 'ip', 'rp', 'U', 'B', 'V', 'R', 'I', 'SDSS-G', 'SDSS-R', 'SDSS-I',
                         'Pan-Starrs-Z', 'Bessell-B', 'Bessell-V', 'Bessell-R', 'Bessell-I']:
            ww = asarray([i for i in range(len(ll1['filter'])) if ((ll1['filter'][i] in [_filter]))])
        else:
            lista = []
            for fil in _filter:
                try:
                    lista.append(agnkey.sites.filterst('lsc')[fil])
                except:
                    try:
                        lista.append(agnkey.sites.filterst('fts')[fil])
                    except:
                        pass
            ww = asarray([i for i in range(len(ll1['filter'])) if ((ll1['filter'][i] in lista))])
        if len(ww) > 0:
            for jj in ll1.keys(): ll1[jj] = array(ll1[jj])[ww]
        else:
            for jj in ll1.keys(): ll1[jj] = []
    if _id:  # ID
        try:
            xx = '0000'[len(_id):] + _id
            ww = asarray([i for i in range(len(ll1['filter'])) if ((_id in string.split(ll1['namefile'][i], '-')[3]))])
        except:
            ww = asarray([i for i in range(len(ll1['filter'])) if (_id in ll1['namefile'][i])])
        if len(ww) > 0:
            for jj in ll1.keys(): ll1[jj] = array(ll1[jj])[ww]
        else:
            for jj in ll1.keys(): ll1[jj] = []
    if _name:  # name
        ww = asarray([i for i in range(len(ll1['filter'])) if ((_name in ll1['objname'][i]))])
        if len(ww) > 0:
            for jj in ll1.keys(): ll1[jj] = array(ll1[jj])[ww]
        else:
            for jj in ll1.keys(): ll1[jj] = []
    if _ra and _dec:
        from numpy import abs

        ww = asarray([i for i in range(len(ll1['ra0'])) if (
        abs(float(ll1['ra0'][i]) - float(_ra)) < .5 and abs(float(ll1['dec0'][i]) - float(_dec)) < .5 )])
        if len(ww) > 0:
            for jj in ll1.keys(): ll1[jj] = array(ll1[jj])[ww]
        else:
            for jj in ll1.keys(): ll1[jj] = []

    if _bad:
        if _bad == 'wcs':
            ww = asarray([i for i in range(len(ll1[_bad])) if (ll1[_bad][i] != 0)])
        elif _bad == 'zcat' or _bad == 'abscat':
            ww = asarray([i for i in range(len(ll1[_bad])) if (ll1[_bad][i] == 'X' )])
        elif _bad == 'goodcat':
            ww = asarray([i for i in range(len(ll1['abscat'])) if (ll1['abscat'][i] != 'X' )])
        elif _bad == 'apmag':
            ww = asarray([i for i in range(len(ll1['appmagap1'])) if (ll1['appmagap1'][i] is None )])
        elif _bad == 'psf':
            ww = asarray([i for i in range(len(ll1['psf'])) if (ll1['psf'][i] == 'X' )])
        elif _bad == 'quality':
            ww = asarray([i for i in range(len(ll1['quality'])) if ((ll1['quality'][i] == 1))])
        elif _bad == 'diff':
            maskexists = [os.path.isfile(filepath+filename.replace('.fits', '.diff.fits'))
                            for filepath, filename in zip(ll1['wdirectory'], ll1['namefile'])]
            ww = np.flatnonzero(np.logical_not(np.array(maskexists)))
        else:
            ww = asarray([i for i in range(len(ll1[_bad])) if (ll1[_bad][i] == 9999 )])
        if len(ww) > 0:
            for jj in ll1.keys(): ll1[jj] = array(ll1[jj])[ww]
        else:
            for jj in ll1.keys(): ll1[jj] = []

        if _bad == 'psfmag':  # do not consider standard field as bad psfmag files
            ww = asarray([i for i in range(len(ll1['objname'])) if (
            (ll1['objname'][i]) not in ['L104', 'L105', 'L95', 'L92', 'L106', 'L113', 'L101', 'L107', 'L110', 'MarkA',
                                        's82_00420020', 's82_01030111', 'Ru152'])])
            if len(ww) > 0:
                for jj in ll1.keys(): ll1[jj] = array(ll1[jj])[ww]
            else:
                for jj in ll1.keys(): ll1[jj] = []
            #          if _bad in ['goodcat']:
            #          else:
            #               ww=asarray([i for i in range(len(ll1[_bad])) if ((ll1['quality'][i]!=1))])
            #          if len(ww)>0:
            #               for jj in ll1.keys(): ll1[jj]=array(ll1[jj])[ww]
            #          else:  
            #               for jj in ll1.keys(): ll1[jj]=[]
    return ll1


#########################################################################

def run_local(imglist, _field, _interactive=False, database='dataredulco'):
    import agnkey
    import glob

    #direc = agnkey.__path__[0]

    ff = open('_tmpcat.list', 'w')
    for img in imglist:
        ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
        if ggg:
            _dir = ggg[0]['wdirectory']
            if ggg[0]['abscat'] != 'X':
                ff.write(_dir + re.sub('.fits', '.cat', img) + '\n')
    ff.close()
    if _interactive:
        ii = ' -i '
    else:
        ii = ''
    if _field:
        _field = ' -f ' + _field
    else:
        _field = ''
    command = 'agnmaglocal.py _tmpcat.list ' + ii + ' ' + _field
    print command
    os.system(command)


##########################################################################
def position(imglist, ra1, dec1, show=False):
    import agnkey
    from pyraf import iraf
    from numpy import array, zeros, median, argmin, cos, abs, pi, mean

    iraf.imcoords(_doprint=0)
    ra, dec = [], []
    if not ra1 and not dec1:
        for img in imglist:
            t = pyfits.open(img)
            tbdata = t[1].data
            hdr1 = t[0].header
            psfx = agnkey.util.readkey3(hdr1, 'PSFX1')
            psfy = agnkey.util.readkey3(hdr1, 'PSFY1')
            if psfx != None and psfy != None:
                lll = str(psfx) + ' ' + str(psfy)
                aaa = iraf.wcsctran('STDIN', 'STDOUT', img, Stdin=[lll], inwcs='logical', units='degrees degrees',
                                    outwcs='world', columns='1 2', formats='%10.5f %10.5f', Stdout=1)[3]
                try:
                    ra.append(float(string.split(aaa)[0]))
                    dec.append(float(string.split(aaa)[1]))
                except:
                    pass
    else:
        for img in imglist:
            dicti = agnkey.util.makecatalogue2([img])
            for i in dicti.keys():
                for j in dicti[i].keys():
                    ra0 = dicti[i][j]['ra']
                    dec0 = dicti[i][j]['dec']
                    ra00 = zeros(len(ra0))
                    dec00 = zeros(len(ra0))
                    for i in range(0, len(ra0)):
                        ra00[i] = float(iraf.real(ra0[i])) * 15
                        dec00[i] = float(iraf.real(dec0[i]))
                    distvec, pos0, pos1 = agnkey.agnastrodef.crossmatch(array([float(ra1)]), array([float(dec1)]),
                                                                        array(ra00, float), array(dec00, float), 5)
                    if len(pos1) >= 1:
                        ra.append(ra00[pos1[argmin(distvec)]])
                        dec.append(dec00[pos1[argmin(distvec)]])
                        print i, j, ra00[pos1[argmin(distvec)]], dec00[pos1[argmin(distvec)]]
                    #                        iraf.display(re.sub('.sn2.','.',j),1,fill=True,Stdout=1)
                    #                        lll=str(ra00[pos1[argmin(distvec)]])+' '+str(dec00[pos1[argmin(distvec)]])
                    #                        aaa=iraf.wcsctran('STDIN','STDOUT',j,Stdin=[lll],inwcs='world',units='degrees degrees',outwcs='logical',columns='1 2',formats='%10.5f %10.5f',Stdout=1)[3]
                    #                        iraf.tvmark(1,'STDIN',Stdin=list([aaa]),mark="circle",number='yes',label='no',radii=20,nxoffse=5,nyoffse=5,color=205,txsize=2)
                    #                        raw_input('ddd')
    if show:
        from pylab import ion, plot, xlim, ylim, xlabel, ylabel, getp, setp, legend, gca

        ion()
        xlabel('ra (arcsec)')
        ylabel('dec (arcsec)')
        yticklabels = getp(gca(), 'yticklabels')
        xticklabels = getp(gca(), 'xticklabels')
        setp(xticklabels, fontsize='20')
        setp(yticklabels, fontsize='20')
        legend(numpoints=1, markerscale=1.5)
        print median(dec)
        plot(((ra - median(ra)) * 3600) * cos(median(dec) * pi / 180.), (dec - median(dec)) * 3600, 'or',
             label='position')
    try:
        ra, dec = mean(ra), mean(dec)
    except:
        ra = ''
        dec = ''
    return ra, dec


#########################################################################
def checkcat(imglist, database='dataredulco'):
    import agnkey

    for img in imglist:
        status = checkstage(img, 'checkpsf')
        #print img,status
        if status >= 1:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            print _dir, img
            if os.path.isfile(_dir + re.sub('.fits', '.cat', img)):
                aa = raw_input('>>>good catalogue [[y]/n] or [b] bad quality ? ')
                if not aa: aa = 'y'
                if aa in ['n', 'N', 'No', 'NO', 'bad', 'b', 'B']:
                    print 'updatestatus bad catalogue'
                    agnkey.agnsqldef.updatevalue(database, 'abscat', 'X', string.split(img, '/')[-1])
                    agnkey.util.delete(_dir + re.sub('.fits', '.cat', img))
                    if aa in ['bad', 'b', 'B']:
                        print 'updatestatus bad quality'
                        agnkey.agnsqldef.updatevalue(database, 'quality', 1, string.split(img, '/')[-1])
                        agnkey.util.delete(_dir + re.sub('.fits', '.cat', img))
            else:
                agnkey.agnsqldef.updatevalue(database, 'abscat', 'X', string.split(img, '/')[-1])
        elif status == 0:
            print 'status ' + str(status) + ': WCS stage not done'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'


def checkpsf(imglist, database='dataredulco'):
    import agnkey

    direc = agnkey.__path__[0]
    from pyraf import iraf

    iraf.digiphot(_doprint=0)
    iraf.daophot(_doprint=0)
    for img in imglist:
        status = checkstage(img, 'checkpsf')
        print img, status
        if status >= 1:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            iraf.delete('_psf.psf.fits', verify=False)
            if os.path.isfile(_dir + re.sub('.fits', '.psf.fits', img)):
                print img
                agnkey.util.marksn2(_dir + img, _dir + re.sub('fits', 'sn2.fits', img), 1, '', True)
                iraf.seepsf(_dir + re.sub('.fits', '.psf.fits', img), '_psf.psf')
                iraf.surface('_psf.psf')
                aa = raw_input('>>>good psf [[y]/n] or [b] bad quality ? ')
                if not aa: aa = 'y'
                if aa in ['n', 'N', 'No', 'NO', 'bad', 'b', 'B']:
                    print 'updatestatus bad'
                    agnkey.agnsqldef.updatevalue(database, 'psf', 'X', string.split(img, '/')[-1])
                    agnkey.agnsqldef.updatevalue(database, 'psfmag', 9999, string.split(img, '/')[-1])
                    if os.path.isfile(_dir + re.sub('.fits', '.psf.fits', img)):
                        print 'rm ' + _dir + re.sub('.fits', '.psf.fits', img)
                        os.system('rm ' + _dir + re.sub('.fits', '.psf.fits', img))
                    if os.path.isfile(_dir + re.sub('.fits', '.sn2.fits', img)):
                        print 'rm ' + _dir + re.sub('.fits', '.sn2.fits', img)
                        os.system('rm ' + _dir + re.sub('.fits', '.sn2.fits', img))
                    if aa in ['bad', 'b', 'B']:
                        print 'updatestatus bad quality'
                        agnkey.agnsqldef.updatevalue(database, 'quality', 1, string.split(img, '/')[-1])
        elif status == 0:
            print 'status ' + str(status) + ': WCS stage not done'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'

    #############################################################################


def checkwcs(imglist, force=True, database='dataredulco', _z1='', _z2=''):
    import agnkey
    import glob

    direc = agnkey.__path__[0]
    from pyraf import iraf

    iraf.digiphot(_doprint=0)
    iraf.daophot(_doprint=0)
    print force
    print _z1, _z2
    for img in imglist:
        status = checkstage(img, 'wcs')
        if status >= 0 or force == False:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            _filter = ggg[0]['filter']
            _exptime = ggg[0]['exptime']
            iraf.set(stdimage='imt8192')
            if _z1 != None and _z2 != None:
                iraf.display(_dir + img, 1, fill=True, Stdout=1, zscale='no', zrange='no', z1=_z1, z2=_z2)
            else:
                iraf.display(_dir + img, 1, fill=True, Stdout=1)
                ###########################################
            _ra0, _dec0, _SN0 = agnkey.util.checksnlist(_dir + img, 'supernovaelist.txt')
            if not _SN0:    _ra0, _dec0, _SN0 = agnkey.util.checksnlist(_dir + img, 'standardlist.txt')
            if not _SN0:    _ra0, _dec0, _SN0, _tt = agnkey.util.checksndb(_dir + img, 'lsc_sn_pos')
            print _ra0, _dec0, _SN0, img, _filter, _exptime
            if _SN0:
                ccc = iraf.wcsctran('STDIN', 'STDOUT', _dir + img, Stdin=[str(_ra0) + ' ' + str(_dec0)], inwcs='world',
                                    units='degrees degrees', outwcs='logical',
                                    columns='1 2', formats='%10.5f %10.5f', Stdout=1)
                iraf.tvmark(1, 'STDIN', Stdin=list(ccc), mark="circle", number='yes', label='no', radii=15, nxoffse=5,
                            nyoffse=5, color=206, txsize=3)

                _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/landolt/' + _SN0 + '*')
                if not _catalogue:
                    _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/sloan/' + _SN0 + '*')
                if not _catalogue:
                    _catalogue = glob.glob(agnkey.__path__[0] + '/standard/cat/apass/' + _SN0 + '*')
            else:
                _catalogue = ''
            if len(_catalogue) >= 1:
                catvec = agnkey.agnastrodef.readtxt(_catalogue[0])
                bbb = []
                for i in range(0, len(catvec['ra'])):
                    bbb.append(catvec['ra'][i] + ' ' + catvec['dec'][i])
                aaa = iraf.wcsctran('STDIN', 'STDOUT', _dir + img, Stdin=list(bbb), inwcs='world',
                                    units='degrees degrees', outwcs='logical', columns='1 2', formats='%10.5f %10.5f',
                                    Stdout=1)
                iraf.tvmark(1, 'STDIN', Stdin=list(aaa), mark="cross", number='yes', label='no', radii=1, nxoffse=5,
                            nyoffse=5, color=204, txsize=1)

            else:
                catvec = agnkey.agnastrodef.querycatalogue('usnoa2', _dir + img, 'vizir')
                apix1 = catvec['pix']
                iraf.tvmark(1, 'STDIN', Stdin=list(apix1), mark="circle", number='yes', label='no', radii=20, nxoffse=5,
                            nyoffse=5, color=205, txsize=2)
            aa = raw_input('>>>good wcs [[y]/n] or [b] bad quality ? ')
            if not aa: aa = 'y'
            if aa in ['n', 'N', 'No', 'NO', 'bad', 'b', 'B']:
                print 'updatestatus bad'
                agnkey.agnsqldef.updatevalue(database, 'wcs', 9999, string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'psf', 'X', string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'psfmag', 9999, string.split(img, '/')[-1])
                if os.path.isfile(_dir + re.sub('.fits', '.psf.fits', img)):
                    print 'rm ' + _dir + re.sub('.fits', '.psf.fits', img)
                    os.system('rm ' + _dir + re.sub('.fits', '.psf.fits', img))
                if os.path.isfile(_dir + re.sub('.fits', '.sn2.fits', img)):
                    print 'rm ' + _dir + re.sub('.fits', '.sn2.fits', img)
                    os.system('rm ' + _dir + re.sub('.fits', '.sn2.fits', img))
                if aa in ['bad', 'b', 'B']:
                    print 'updatestatus bad quality'
                    agnkey.agnsqldef.updatevalue(database, 'quality', 1, string.split(img, '/')[-1])
            elif aa in ['c', 'C', 'cancel']:
                print 'remove from database'
                os.system('rm ' + _dir + img)
                agnkey.agnsqldef.deleteredufromarchive(string.split(img, '/')[-1], 'dataredulco', 'namefile')
                agnkey.agnsqldef.deleteredufromarchive(string.split(img, '/')[-1], 'inoutredu', 'nameout')
            #          elif status==0: print 'status '+str(status)+': WCS stage not done' 
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'

    ##################################################################


#############################################################################

def makestamp(imglist, database='dataredulco', _z1='', _z2='', _interactive=True, redo=False, _output=''):
    import agnkey
    import numpy as np
    import pylab as plt
    import pywcs
    import time

    for ggg in imglist:
        _dir,img = os.path.split(ggg)
        if _dir:
            _dir = _dir+'/'
        print _dir + img
        status = agnkey.agnloopdef.checkstage(img, 'wcs')
        if status >= 0:  # or force==False:
            _output = re.sub('.fits', '.png', _dir + img)
            if os.path.isfile(_output):
                if redo:
                    os.remove(_output)
                else:
                    status = -5
        if status >= 0:  # or force==False:
            hdr = pyfits.open(_dir + img)
            X = hdr[0].data
            header = hdr[0].header
            wcs = pywcs.WCS(header)
            _ra0, _dec0, _SN0, _tt = agnkey.util.checksndb(_dir + img, 'lsc_sn_pos')
            if _SN0:
                [[xPix, yPix]] = wcs.wcs_sky2pix([(_ra0, _dec0)], 1)
                if (xPix > 0 and xPix <= header.get('NAXIS1')) and (yPix <= header.get('NAXIS2') and yPix > 0):
                    xmin, xmax = xPix - 300, xPix + 300
                    ymin, ymax = yPix - 300, yPix + 300
                else:
                    try:
                        xmin, xmax = 0, header.get('NAXIS1')
                        ymin, ymax = 0, header.get('NAXIS2')
                    except:
                        xmin, xmax = 0, 1000
                        ymin, ymax = 0, 1000
                _sky, _sig = agnkey.agnloopdef.getsky(X[xmin:xmax, ymin:ymax])
                _z1 = _sky - _sig
                _z2 = _sky + _sig * 5
                plt.clf()
                try:
                    im = plt.imshow(X, cmap='gray', norm=None, aspect=None, interpolation='nearest', alpha=None,
                                    vmin=float(_z1), vmax=float(_z2), origin='upper', extent=None)
                except:
                    im = plt.imshow(X, cmap='gray', norm=None, aspect=None, interpolation='nearest', alpha=None, vmin=0,
                                    vmax=1000, origin='upper', extent=None)
                plt.xlim(float(xPix) - 200, float(xPix) + 200)
                plt.ylim(float(yPix) + 200, float(yPix) - 200)
                plt.plot([float(xPix)], [float(yPix)], marker='o', mfc='none', markersize=25, markeredgewidth=2,
                         markeredgecolor='r', label=str(_SN0))
                if _interactive:
                    plt.show()
                else:
                    print _output
                    agnkey.util.delete(_output)
                    plt.savefig(_output)
            else:
                print 'SN not found'

        elif status == -1:
            time.sleep(.1)
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            time.sleep(.1)
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            time.sleep(.1)
            print 'status ' + str(status) + ': bad quality image'
        elif status == -5:
            time.sleep(.1)
            print 'status ' + str(status) + ': png already done'
        else:
            time.sleep(.1)
            print 'status ' + str(status) + ': unknown status'


def checkclean(imglist, force=True, database='dataredulco'):
    import agnkey
    import time
    plt.ion()

    imglist2=[]
    date = []
    for img in imglist:
        status = checkstage(img, 'wcs')
        if status >= 0 or force == False:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            imglist2.append(ggg[0]['wdirectory']+img)
            date.append(str(ggg[0]['dateobs']))

    X, hdr = pyfits.getdata(imglist2[0], header=True)
    _z1,_z2 = agnkey.zscale.zscale(X) 

    fig = plt.figure()
    ax = fig.add_axes([0.1,0.1,0.85,0.85])
    image = ax.imshow(X,interpolation='nearest', origin='upper', cmap='gray_r', vmin=_z1, vmax=_z2)

    for kk,img in enumerate(imglist2):
            print date[kk],img
            img0 = string.split(img, '/')[-1]
            X, hdr = pyfits.getdata(img, header=True)
            aa=time.time()
            _z1,_z2 = agnkey.zscale.zscale(X)    
            print time.time()-aa
            image.set_data(X)
            image.set_clim(vmin=_z1,vmax=_z2)
            fig.canvas.draw()
            fig.canvas.flush_events()
            ###########################################
#    for img in imglist:
#        ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
#        _dir = ggg[0]['wdirectory']
##        iraf.set(stdimage='imt8192')
#        imgclean = re.sub('.fits', '.clean.fits', img)
#        if os.path.isfile(_dir + imgclean):
#            iraf.display(_dir + img, 1, fill=True, Stdout=1)
#            iraf.display(_dir + imgclean, 2, fill=True, Stdout=1)
            ###########################################
            aa = raw_input('>>>good or bad quality [[g]/b]? ')
            if not aa: aa = 'g'
            if aa in ['bad', 'b', 'B']:
                agnkey.agnsqldef.updatevalue(database, 'wcs', 9999, string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'psf', 'X', string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'psfmag', 9999, string.split(img, '/')[-1])
                if os.path.isfile(_dir + re.sub('.fits', '.psf.fits', img)):
                    print 'rm ' + _dir + re.sub('.fits', '.psf.fits', img)
                    os.system('rm ' + _dir + re.sub('.fits', '.psf.fits', img))
                if os.path.isfile(_dir + re.sub('.fits', '.sn2.fits', img)):
                    print 'rm ' + _dir + re.sub('.fits', '.sn2.fits', img)
                    os.system('rm ' + _dir + re.sub('.fits', '.sn2.fits', img))
                print 'updatestatus bad quality'
                agnkey.agnsqldef.updatevalue(database, 'quality', 1, string.split(img, '/')[-1])
            else:
                print 'updatestatus quality good'
                agnkey.agnsqldef.updatevalue(database, 'quality', 127, string.split(img, '/')[-1])
#        else:
#            print 'clean image not found'

    ##################################################################


def checkfast(imglist, force=True, database='dataredulco'):
    import agnkey
    import time
    plt.ion()

    imglist2=[]
    date = []
    for img in imglist:
        status = checkstage(img, 'wcs')
        if status >= 0 or force == False:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            imglist2.append(ggg[0]['wdirectory']+img)
            date.append(str(ggg[0]['dateobs']))

    if len(imglist2):
      X, hdr = pyfits.getdata(imglist2[0], header=True)
      _z1,_z2 = agnkey.zscale.zscale(X) 
      fig = plt.figure()
      ax = fig.add_axes([0.1,0.1,0.85,0.85])
      image = ax.imshow(X,interpolation='nearest', origin='upper', cmap='gray_r', vmin=_z1, vmax=_z2)
      for kk,img in enumerate(imglist2):
            print date[kk],img
            _dir,img0 = os.path.split(img)
            #img0 = string.split(img, '/')[-1]
            X, hdr = pyfits.getdata(img, header=True)
            aa=time.time()
            _z1,_z2 = agnkey.zscale.zscale(X)    
            print time.time()-aa
            image.set_data(X)
            image.set_clim(vmin=_z1,vmax=_z2)
            fig.canvas.draw()
            fig.canvas.flush_events()
            ###########################################
            aa = raw_input('>>>good or bad quality [[g]/b]? ')
            if not aa: aa = 'g'
            if aa in ['bad', 'b', 'B']:
                agnkey.agnsqldef.updatevalue(database, 'wcs', 9999, string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'psf', 'X', string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'psfmag', 9999, string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'appmagap1', 9999, string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'appmagap2', 9999, string.split(img, '/')[-1])
                agnkey.agnsqldef.updatevalue(database, 'appmagap3', 9999, string.split(img, '/')[-1])
                if os.path.isfile(_dir + re.sub('.fits', '.psf.fits', img)):
                    print 'rm ' + _dir + re.sub('.fits', '.psf.fits', img)
                    os.system('rm ' + _dir + re.sub('.fits', '.psf.fits', img))
                if os.path.isfile(_dir + re.sub('.fits', '.sn2.fits', img)):
                    print 'rm ' + _dir + re.sub('.fits', '.sn2.fits', img)
                    os.system('rm ' + _dir + re.sub('.fits', '.sn2.fits', img))
                print 'updatestatus bad quality'
                agnkey.agnsqldef.updatevalue(database, 'quality', 1, string.split(img, '/')[-1])
            else:
                print 'updatestatus quality good'
                agnkey.agnsqldef.updatevalue(database, 'quality', 127, string.split(img, '/')[-1])
            #          elif status==0: print 'status '+str(status)+': WCS stage not done' 
#        elif status == -1:
#            print 'status ' + str(status) + ': sn2.fits file not found'
#        elif status == -2:
#            print 'status ' + str(status) + ': .fits file not found'
#        elif status == -4:
#            print 'status ' + str(status) + ': bad quality image'
#        else:
#            print 'status ' + str(status) + ': unknown status'


    ##################################################################


def checkmag(imglist, database='dataredulco'):
    import agnkey
    direc = agnkey.__path__[0]
    from pyraf import iraf

    iraf.digiphot(_doprint=0)
    iraf.daophot(_doprint=0)
    for img in imglist:
        status = checkstage(img, 'checkmag')
        if status >= 1:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            if os.path.isfile(_dir + re.sub('.fits', '.og.fits', img)) and os.path.isfile(
                            _dir + re.sub('.fits', '.rs.fits', img)):
                aaa = iraf.display(_dir + re.sub('.fits', '.og.fits', img), 1, fill=True, Stdout=1)
                print aaa
                iraf.display(_dir + re.sub('.fits', '.rs.fits', img), 2, fill=True, Stdout=1)
                aa = raw_input('>>>good mag [[y]/n] or [b] bad quality ? ')
                if not aa: aa = 'y'
                if aa in ['n', 'N', 'No', 'NO', 'bad', 'b', 'B']:
                    print 'updatestatus bad'
                    agnkey.agnsqldef.updatevalue(database, 'psfmag', 9999, string.split(img, '/')[-1])
                    agnkey.agnsqldef.updatevalue(database, 'appmagap1', 9999, string.split(img, '/')[-1])
                    agnkey.agnsqldef.updatevalue(database, 'appmagap2', 9999, string.split(img, '/')[-1])
                    agnkey.agnsqldef.updatevalue(database, 'appmagap3', 9999, string.split(img, '/')[-1])
                    if os.path.isfile(_dir + re.sub('.fits', '.og.fits', img)):
                        print 'rm ' + _dir + re.sub('.fits', '.og.fits', img)
                        os.system('rm ' + _dir + re.sub('.fits', '.og.fits', img))
                    if os.path.isfile(_dir + re.sub('.fits', '.rs.fits', img)):
                        print 'rm ' + _dir + re.sub('.fits', '.rs.fits', img)
                        os.system('rm ' + _dir + re.sub('.fits', '.rs.fits', img))
                if aa in ['bad', 'b', 'B']:
                    print 'updatestatus bad quality'
                    agnkey.agnsqldef.updatevalue(database, 'quality', 1, string.split(img, '/')[-1])
        elif status == 0:
            print 'status ' + str(status) + ': WCS stage not done'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'


def checkpos(imglist, _ra, _dec, database='dataredulco'):
    import agnkey
    #     import  mysqldef #import updatevalue
    imglist2 = []
    for img in imglist:
        status = checkstage(img, 'checkmag')
        if status >= 1:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            _dir = ggg[0]['wdirectory']
            if os.path.isfile(_dir + re.sub('fits', 'sn2.fits', img)):  imglist2.append(
                _dir + re.sub('fits', 'sn2.fits', img))
    print imglist2, _ra, _dec
    ra, dec = agnkey.agnloopdef.position(imglist2, _ra, _dec, show=True)
    print '######## mean ra and dec position  ############'
    print 'ra= ' + str(ra)
    print 'dec= ' + str(dec)
    print '#############'


def checkquality(imglist, database='dataredulco'):
    import agnkey

    direc = agnkey.__path__[0]
    from pyraf import iraf

    iraf.digiphot(_doprint=0)
    iraf.daophot(_doprint=0)
    for img in imglist:
        status = checkstage(img, 'checkquality')
        if status == -4:
            ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(img), '*')
            if not ggg:
                status = -3  # not in the redo table
            else:
                _dir = ggg[0]['wdirectory']
                if os.path.isfile(_dir + img):
                    iraf.set(stdimage='imt8192')
                    iraf.display(_dir + img, 1, fill=True, Stdout=1)
                    aa = raw_input('>>>good image [y/[n]] ? ')
                    if not aa: aa = 'n'
                    if aa in ['n', 'N', 'No', 'NO']:
                        print 'status bad'
                    else:
                        print 'updatestatus good'
                        agnkey.agnsqldef.updatevalue(database, 'quality', 127, string.split(img, '/')[-1])
                        #updatevalue('dataredulco','psfmag',9999,string.split(img,'/')[-1])
                        #if os.path.isfile(_dir+re.sub('.fits','.psf.fits',img)):
                        #print 'rm '+_dir+re.sub('.fits','.psf.fits',img)
                        #os.system('rm '+_dir+re.sub('.fits','.psf.fits',img))
                        #if os.path.isfile(_dir+re.sub('.fits','.sn2.fits',img)):
                        #print 'rm '+_dir+re.sub('.fits','.sn2.fits',img)
                        #os.system('rm '+_dir+re.sub('.fits','.sn2.fits',img))
                        #else: print 'status: quality good '


##################################################################

def onkeypress2(event):
    import matplotlib.pyplot as plt
    from numpy import argmin, sqrt, mean, array, std, median
    import agnkey

    global idd, _hjd, _mag, _setup, _namefile, shift, _database
    xdata, ydata = event.xdata, event.ydata

    
    if xdata:
      dist = sqrt((xdata - _hjd) ** 2 + (ydata - _mag) ** 2)
      ii = argmin(dist)
      if ii in idd: 
          idd.remove(ii)
      print _namefile[ii]
      print _mag[ii]
      _dir= os.path.dirname(_namefile[ii])+'/'
      filename = os.path.basename(_namefile[ii])
      if _dir:
          if 'diff' in filename:
              if os.path.isfile(_dir + filename) and os.path.isfile(_dir + re.sub('diff.fits', 'ref.fits', filename)):
                  from pyraf import iraf
                  iraf.digiphot(_doprint=0)
                  iraf.daophot(_doprint=0)
                  iraf.display(_dir + filename, 1, fill=True, Stdout=1)
                  iraf.display(_dir + re.sub('diff.fits', 'fits', filename), 2, fill=True, Stdout=1)
          else:
              if os.path.isfile(_dir + re.sub('.fits', '.og.fits', filename)) and os.path.isfile(
                      _dir + re.sub('.fits', '.rs.fits', filename)):
                  from pyraf import iraf
                  iraf.digiphot(_doprint=0)
                  iraf.daophot(_doprint=0)
                  iraf.display(_dir + re.sub('.fits', '.og.fits', filename), 1, fill=True, Stdout=1)
                  iraf.display(_dir + re.sub('.fits', '.rs.fits', filename), 2, fill=True, Stdout=1)

    if event.key in ['d']:
        if _setup['mtype'] in ['apflux1','apflux2','apflux3']:
            print 'flux to null'
            agnkey.agnsqldef.updatevalue(_database, 'apflux1', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'apflux2', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'apflux3', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'dapflux1', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'dapflux2', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'dapflux3', 'NULL', filename)
        else:
            print 'mag to null'
            agnkey.agnsqldef.updatevalue(_database, 'mag', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'psfmag', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'apmag', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'appmagap1', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'appmagap2', 'NULL', filename)
            agnkey.agnsqldef.updatevalue(_database, 'appmagap3', 'NULL', filename)
            if _dir:
                agnkey.util.updateheader(_dir + re.sub('.fits', '.sn2.fits', filename), 0,
                                         {'PSFMAG1': [9999, 'psf magnitude']})
                agnkey.util.updateheader(_dir + re.sub('.fits', '.sn2.fits', filename), 0,
                                         {'APMAG1': [9999, 'ap magnitude']})
    elif event.key in ['u']:
        agnkey.agnsqldef.updatevalue(_database, 'magtype', -1, filename)
        print '\n### set as a limit'
    elif event.key in ['b']:
        agnkey.agnsqldef.updatevalue(_database, 'quality', 1, filename)
        agnkey.agnsqldef.updatevalue(_database, 'mag', 'NULL', filename)
        agnkey.agnsqldef.updatevalue(_database, 'psfmag', 'NULL', filename)
        agnkey.agnsqldef.updatevalue(_database, 'apmag', 'NULL', filename)
        agnkey.agnsqldef.updatevalue(_database, 'appmagap1', 'NULL', filename)
        agnkey.agnsqldef.updatevalue(_database, 'appmagap2', 'NULL', filename)
        agnkey.agnsqldef.updatevalue(_database, 'appmagap3', 'NULL', filename)
        agnkey.agnsqldef.updatevalue(_database, 'apflux1', 'NULL', filename)
        agnkey.agnsqldef.updatevalue(_database, 'apflux2', 'NULL', filename)
        agnkey.agnsqldef.updatevalue(_database, 'apflux3', 'NULL', filename)
        print '\n### set bad quality'
    print '\n### press:\n d to cancel value,\n c to check one point\n u to set the upper limit\n b to set bad quality.\n Return to exit ...'

    nonincl = []
    for i in range(len(_hjd)):
        if i not in idd: nonincl.append(i)
    _symbol = 'sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*'
    _color = {'U': 'b', 'B': 'r', 'V': 'g', 'R': 'c', 'I': 'm', 'up': 'b', 'gp': 'r', 'rp': 'g', 'ip': 'c', 'zs': 'm', \
              'Bessell-B': 'r', 'Bessell-V': 'g', 'Bessell-R': 'c', 'Bessell-I': 'm', \
              'SDSS-G': 'r', 'SDSS-R': 'g', 'SDSS-I': 'c', 'Pan-Starrs-Z': 'm'}
    _shift = {'U': -2, 'B': -1, 'V': 0, 'R': 1, 'I': 2, 'up': -2, 'gp': -1, 'rp': 0, 'ip': 1, 'zs': 2, \
              'Bessell-B': -1, 'Bessell-V': 0, 'Bessell-R': 1, 'Bessell-I': 2, \
              'SDSS-G': -1, 'SDSS-R': 0, 'SDSS-I': 1, 'Pan-Starrs-Z': 2}

    if 'mtype' in _setup.keys():
        if _setup['mtype'] in ['apflux1','apflux2','apflux3']:            
            _shift = {'U': 0, 'B': 0, 'V': 0, 'R': 0, 'I': 0, 'up': 0, 'gp': 0, 'rp': 0, 'ip': 0, 'zs': 0, \
                      'Bessell-B': 0, 'Bessell-V': 0, 'Bessell-R': 0, 'Bessell-I': 0, \
                      'SDSS-G': 0, 'SDSS-R': 0, 'SDSS-I': 0, 'Pan-Starrs-Z': 0}

    ii = 0
    mag, hjd = [], []
    for _tel in _setup:
      if _tel!='mtype':
        shift = 0
        for _fil in _setup[_tel]:
            shift = _shift[_fil]
            col = _color[_fil]
            plt.plot(array(_setup[_tel][_fil]['hjd']), array(_setup[_tel][_fil]['mag']) + shift, _symbol[ii], color=col,
                     markersize=5)
            mag = list(mag) + list(array(_setup[_tel][_fil]['mag']) + shift)
            hjd = list(hjd) + list(_setup[_tel][_fil]['hjd'])
            ii = ii + 1

    plt.xlabel('HJD')
    plt.ylabel('magnitude')
    _mag = mag[:]
    _hjd = hjd[:]
    _hjd = array(_hjd)
    _mag = array(_mag)
    idd = range(len(_hjd))

    yticklabels = plt.getp(plt.gca(), 'yticklabels')
    xticklabels = plt.getp(plt.gca(), 'xticklabels')
    plt.setp(xticklabels, fontsize='10')
    plt.setp(yticklabels, fontsize='10')
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0., markerscale=.8, numpoints=1)
    #    plt.legend(numpoints=1,markerscale=.8)
    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize=10)
    plt.plot(_hjd, _mag, 'ok', markersize=1)
    plt.plot(_hjd[nonincl], _mag[nonincl], 'ow')


##############################################################################
def plotfast(setup, output='', database='dataredulco'):  #,band,color,fissa=''):
    import matplotlib.pyplot as plt
    from numpy import argmin, sqrt, mean, array, std, median, compress

    global idd, _hjd, _mag, _setup, _namefile, shift, _database  #,testo,lines,pol,sss,f,fixcol,sigmaa,sigmab,aa,bb
    if not output:   
        plt.ion()

    _setup = setup
    _database = database

    plt.rcParams['figure.figsize'] = 9, 5
    fig = plt.figure()
    plt.axes([.15, .05, .65, .85])
    

    _symbol = 'sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*'
    _color = {'U': 'b', 'B': 'r', 'V': 'g', 'R': 'c', 'I': 'm', 'up': 'b', 'gp': 'r', 'rp': 'g', 'ip': 'c', 'zs': 'm', \
              'Bessell-B': 'r', 'Bessell-V': 'g', 'Bessell-R': 'c', 'Bessell-I': 'm', \
              'SDSS-G': 'r', 'SDSS-R': 'g', 'SDSS-I': 'c', 'Pan-Starrs-Z': 'm'}
    _shift = {'U': -2, 'B': -1, 'V': 0, 'R': 1, 'I': 2, 'up': -2, 'gp': -1, 'rp': 0, 'ip': 1, 'zs': 2, \
              'Bessell-B': -1, 'Bessell-V': 0, 'Bessell-R': 1, 'Bessell-I': 2, \
              'SDSS-G': -1, 'SDSS-R': 0, 'SDSS-I': 1, 'Pan-Starrs-Z': 2}

    if 'mtype' in _setup.keys():
        if _setup['mtype'] in ['apflux1','apflux2','apflux3']:            
            _shift = {'U': 0, 'B': 0, 'V': 0, 'R': 0, 'I': 0, 'up': 0, 'gp': 0, 'rp': 0, 'ip': 0, 'zs': 0, \
                      'Bessell-B': 0, 'Bessell-V': 0, 'Bessell-R': 0, 'Bessell-I': 0, \
                      'SDSS-G': 0, 'SDSS-R': 0, 'SDSS-I': 0, 'Pan-Starrs-Z': 0}

    ii = 0
    mag, hjd, namefile = [], [], []
    for _tel in _setup:
      if _tel!='mtype':
        shift = 0
        for _fil in _setup[_tel]:
            shift = _shift[_fil]
            col = _color[_fil]
            print _tel, _fil
            jj = array(_setup[_tel][_fil][
                'hjd'])  #compress(array(_setup[_tel][_fil]['magtype'])>=1,array(_setup[_tel][_fil]['mjd']))
            mm = array(_setup[_tel][_fil][
                'mag'])  #compress(array(_setup[_tel][_fil]['magtype'])>=1,array(_setup[_tel][_fil]['mag']))
            plt.plot(jj, mm + shift, _symbol[ii], color=col, label=str(_tel) + ' ' + str(_fil) + ' ' + str(shift), markersize=5)

            jj1 = compress(array(_setup[_tel][_fil]['magtype']) < 0, array(_setup[_tel][_fil]['hjd']))
            mm1 = compress(array(_setup[_tel][_fil]['magtype']) < 0, array(_setup[_tel][_fil]['mag']))
            if len(mm1) > 0:
                plt.errorbar(jj1, mm1, mm1 / 100, lolims=True, fmt=None, ecolor='k')

            mag = list(mag) + list(array(_setup[_tel][_fil]['mag']) + _shift[_fil])
            hjd = list(hjd) + list(_setup[_tel][_fil]['hjd'])
            namefile = list(namefile) + list(_setup[_tel][_fil]['namefile'])
            ii = ii + 1

    plt.xlabel('HJD')
    plt.ylabel('magnitude')
    plt.xlim(min(hjd) - 5, max(hjd) + 5)
    yticklabels = plt.getp(plt.gca(), 'yticklabels')
    xticklabels = plt.getp(plt.gca(), 'xticklabels')
    plt.setp(xticklabels, fontsize='10')
    plt.setp(yticklabels, fontsize='10')
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0., markerscale=.8, numpoints=1)
    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize=10)
    _mag = mag[:]
    _hjd = hjd[:]
    _namefile = namefile[:]
    _hjd = array(_hjd)
    _mag = array(_mag)
    idd = range(len(_hjd))
    plt.plot(_hjd, _mag, 'ok', markersize=1)
    kid = fig.canvas.mpl_connect('key_press_event', onkeypress2)
    if not output:
        plt.draw()
        raw_input('press d to mark. Return to exit ...\n')
        plt.close()
    else:
        plt.savefig(output + '.png', format='png')
        os.system('chmod 777 ' + output + '.png')


################################################################

def subset(xx, _avg=''):  # lista  jd
    from numpy import array

    diff = [xx[i + 1] - xx[i] for i in range(len(xx) - 1)]
    if _avg:
        avg = float(_avg)
    else:
        avg = sum(diff) / len(diff)
        if avg >= 1:
            avg = .5
        elif avg <= 0.1:
            avg = .5
    i = 1
    subset = {}
    position = {}
    subset[1] = [xx[0]]
    position[1] = [0]
    for j in range(0, len(diff)):
        if diff[j] > avg:   i = i + 1
        if i not in subset:  subset[i] = []
        if i not in position:  position[i] = []
        subset[i].append(xx[j + 1])
        position[i].append(j + 1)
    return subset, position


##########################################################

def chosecolor(allfilter, usegood=False, _field=''):
    goodcol = {'B': 'BV', 'V': 'VR', 'R': 'VR', 'I': 'RI', 'U': 'UB', 'u': 'ug', 'g': 'gr', 'r': 'ri', 'i': 'ri',
               'z': 'iz'}
    if not _field:
        if allfilter[0] in 'UBVRI':
            tot, tot2 = 'UBVRI', 'IRVBU'
        else:
            tot, tot2 = 'ugriz', 'zirgu'
    else:
        if _field == 'landolt':
            tot, tot2 = 'UBVRI', 'IRVBU'
        elif _field == 'sloan':
            tot, tot2 = 'ugriz', 'zirgu'
        elif _field == 'apass':
            tot, tot2 = 'BVgri', 'irgVB'

    color = {}
    for filt in allfilter:
        if tot.index(filt) == 0:
            for _fil in tot[1:]:
                if _fil in allfilter:
                    if _fil not in color: color[_fil] = []
                    color[_fil].append(filt + _fil)
                    break
        elif tot.index(filt) == len(tot):
            for _fil in tot2[1:]:
                if _fil in allfilter:
                    if _fil not in color: color[_fil] = []
                    color[_fil].append(_fil + filt)
                    break
        else:
            for _fil in tot[tot.index(filt) + 1:]:
                if _fil in allfilter:
                    if _fil not in color: color[_fil] = []
                    color[_fil].append(filt + _fil)
                    break
            for _fil in tot2[tot2.index(filt) + 1:]:
                if _fil in allfilter:
                    if _fil not in color: color[_fil] = []
                    color[_fil].append(_fil + filt)
                    break
    if usegood:
        for i in color:
            if goodcol[i] in color[i]: color[i] = [goodcol[i]]
    return color


###########################################################################
def get_list(epoch, _telescope='all', _filter='', _bad='', _name='', _id='', _ra='', _dec='', database='dataredulco',
             filetype=1):
    from numpy import argsort, take
    import sys
    import agnkey
    #     from agnkey.mysqldef import getlistfromraw
    import datetime

    if '-' not in str(epoch):
        epoch0 = datetime.date(int(epoch[0:4]), int(epoch[4:6]), int(epoch[6:8]))
        lista = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, database, 'dateobs', str(epoch0), '', '*',
                                                _telescope)
    else:
        epoch1, epoch2 = string.split(epoch, '-')
        start = datetime.date(int(epoch1[0:4]), int(epoch1[4:6]), int(epoch1[6:8]))
        stop = datetime.date(int(epoch2[0:4]), int(epoch2[4:6]), int(epoch2[6:8]))
        lista = agnkey.agnsqldef.getlistfromraw(agnkey.agnsqldef.conn, database, 'dateobs', str(start), str(stop), '*',
                                                _telescope)
    if lista:
        ll0 = {}
        for jj in lista[0].keys(): ll0[jj] = []
        for i in range(0, len(lista)):
            for jj in lista[0].keys(): ll0[jj].append(lista[i][jj])

        inds = argsort(ll0['hjd'])  #  sort by mjd
        for i in ll0.keys():
            ll0[i] = take(ll0[i], inds)

        ll0['ra'] = []
        ll0['dec'] = []
        if 'ra0' not in ll0.keys():
            for i in ll0['namefile']:
                ggg = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'datarawlco', 'namefile', i, '*')
                ll0['ra'].append(ggg[0]['ra0'])
                ll0['dec'].append(ggg[0]['dec0'])
        else:
            ll0['ra'] = ll0['ra0']
            ll0['dec'] = ll0['dec0']
        ll = agnkey.agnloopdef.filtralist(ll0, _filter, _id, _name, _ra, _dec, _bad)
    else:
        ll = ''
    return ll


######

def check_missing(lista, database='dataredulco'):
    import agnkey
    from numpy import argsort, take
    import sys
    import datetime

    if len(lista) > 0:
        for i in lista:
            xx = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'datarawlco', 'namefile', str(i),
                                                 column2='directory')
            yy = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', str(i),
                                                 column2='wdirectory')
            xx, yy = xx[0]['directory'], yy[0]['wdirectory']
            if not os.path.isfile(yy + i):
                os.system('cp ' + xx + i + ' ' + yy + i)
                print xx, str(i), yy + i


def checkfilevsdatabase(lista, database='dataredulco'):
    import agnkey
    import sys

    if lista:
        if len(lista['namefile']) > 0:
            for i in range(0, len(lista['namefile'])):
                imgsn = re.sub('.fits', '.sn2.fits', lista['wdirectory'][i] + lista['namefile'][i])
                if os.path.isfile(imgsn):
                    hdr1 = agnkey.util.readhdr(imgsn)
                    _filter = agnkey.util.readkey3(hdr1, 'filter')
                    _exptime = agnkey.util.readkey3(hdr1, 'exptime')
                    _airmass = agnkey.util.readkey3(hdr1, 'airmass')
                    _telescope = agnkey.util.readkey3(hdr1, 'telescop')
                    _psfmag = agnkey.util.readkey3(hdr1, 'PSFMAG1')
                    _psfdmag1 = agnkey.util.readkey3(hdr1, 'PSFDMAG1')
                    _apmag = agnkey.util.readkey3(hdr1, 'APMAG1')
                    _mag = agnkey.util.readkey3(hdr1, 'MAG')
                    if not _mag:  #  mag
                        if lista['mag'][i] != 9999.0:
                            print lista['namefile'][i], _mag, lista['mag'][i], 'mag'
                            agnkey.agnsqldef.updatevalue(database, 'mag', 9999.0, lista['namefile'][i])
                    else:
                        if _mag == 9999.0:
                            if lista['mag'][i] != 9999.0:
                                print lista['namefile'][i], _mag, lista['mag'][i], 'mag'
                                agnkey.agnsqldef.updatevalue(database, 'mag', 9999.0, lista['namefile'][i])
                        elif _mag != 9999.0:
                            if round(lista['mag'][i], 4) != round(float(_mag), 4):
                                print lista['namefile'][i], _mag, lista['mag'][i], 'mag'
                                agnkey.agnsqldef.updatevalue(database, 'mag', _mag, lista['namefile'][i])

                    if not _psfmag:  #  psfmag
                        if lista['psfmag'][i] != 9999.0:
                            print lista['namefile'][i], _mag, lista['psfmag'][i], 'psfmag'
                            agnkey.agnsqldef.updatevalue(database, 'psfmag', 9999.0, lista['namefile'][i])
                    else:
                        if _psfmag == 9999.0:
                            if lista['psfmag'][i] != 9999.0:
                                print lista['namefile'][i], _psfmag, lista['psfmag'][i], 'psfmag'
                                agnkey.agnsqldef.updatevalue(database, 'psfmag', 9999.0, lista['namefile'][i])
                        elif _psfmag != 9999.0:
                            if round(lista['psfmag'][i], 4) != round(float(_psfmag), 4):
                                print lista['namefile'][i], _psfmag, lista['psfmag'][i], 'psfmag'
                                agnkey.agnsqldef.updatevalue(database, 'psfmag', _psfmag, lista['namefile'][i])

                    if not _apmag:  #  apmag
                        if lista['mag'][i] != 9999.0:
                            print lista['namefile'][i], _mag, lista['mag'][i], 'apmag'
                            agnkey.agnsqldef.updatevalue(database, 'apmag', 9999.0, lista['namefile'][i])
                    else:
                        if _apmag == 9999.0:
                            if lista['apmag'][i] != 9999.0:
                                print lista['namefile'][i], _apmag, lista['apmag'][i], 'apmag'
                                agnkey.agnsqldef.updatevalue(database, 'apmag', 9999.0, lista['namefile'][i])
                        elif _apmag != 9999.0:
                            if round(lista['apmag'][i], 4) != round(float(_apmag), 4):
                                print lista['namefile'][i], _apmag, lista['apmag'][i], 'apmag'
                                agnkey.agnsqldef.updatevalue(database, 'apmag', _apmag, lista['namefile'][i])


#########################################################################################
def run_merge(imglist, _redu=False):
    import agnkey
    direc = agnkey.__path__[0]
    from numpy import where, array
    import agnsqldef
    import glob

    status = []
    stat = 'psf'
    for img in imglist:
        status.append(checkstage(string.split(img, '/')[-1], stat))
    print imglist
    print status
    imglist = imglist[where(array(status) > 0)]
    status = array(status)[where(array(status) > 0)]

    f = open('_tmp.list', 'w')
    for jj in range(0, len(imglist)):
        f.write(imglist[jj] + '\n')
    f.close()
    if _redu:
        ii = ' -f '
    else:
        ii = ''
    #     if _fix: ff=' -c '
    #     else:    ff=''
    #     tt=' -t '+_type+' '
    command = 'agnmerge.py _tmp.list ' + ii  #+tt+ff
    print command
    os.system(command)


#####################################################################
def run_diff(listtar, listtemp, _show=False, _force=False, _normalize='i'):
    import agnkey

    direc = agnkey.__path__[0]
    from numpy import where, array
    import agnsqldef
    import glob 

    status = []
    stat = 'psf'
    for img in listtar:  status.append(checkstage(string.split(img, '/')[-1], stat))
    listtar = listtar[where(array(status) > 0)]
    status = array(status)[where(array(status) > 0)]

    imglisttar = ','.join(listtar)
    imglisttemp = ','.join(listtemp)
    if _show:
        ii = ' --show '
    else:
        ii = ''
    if _force:
        ff = ' -f '
    else:
        ff = ' '
    command = 'agndiff.py '+imglisttar+' '+imglisttemp+' ' + ii + ff + '--normalize ' + _normalize
    #print command
    os.system(command)


######################################################################3
def run_template(listtemp, show=False, _force=False, _interactive=False, 
                 _ra=None, _dec=None, _psf=None, _mag=0, _clean=True, 
                 _subtract_mag_from_header=False):
    import agnkey
    direc = agnkey.__path__[0]
    from numpy import where, array
    import glob

    status = []
    stat = 'psf'
    for img in listtemp:  
        status.append(checkstage(string.split(img, '/')[-1], stat))
    listtemp = listtemp[where(array(status) > 0)]
    status = array(status)[where(array(status) > 0)]

    f = open('_temp.list', 'w')
    for jj in range(0, len(listtemp)):
        f.write(listtemp[jj] + '\n')
    f.close()
    command = 'agnmaketempl.py _temp.list'
    if show:
        command += ' --show'
    if _force:
        command += ' -f'
    if _interactive:
        command += ' -i'
    if _ra:
        command += ' -R ' + str(_ra)
    if _dec:
        command += ' -D ' + str(_dec)
    if _psf:
        command += ' -p ' + _psf
    if _mag:
        command += ' --mag ' + str(_mag)
    if not _clean:
        command += ' --uncleaned'
    if _subtract_mag_from_header:
        command += ' --subtract-mag-from-header'
    print command
    os.system(command)


#########################################

def getsky(data):
    """
  Determine the sky parameters for a FITS data extension. 

  data -- array holding the image data
  """
    from numpy import random
    # maximum number of interations for mean,std loop
    maxiter = 30

    # maximum number of data points to sample
    maxsample = 10000

    # size of the array
    ny, nx = data.shape

    # how many sampels should we take?
    if data.size > maxsample:
        nsample = maxsample
    else:
        nsample = data.size

    # create sample indicies
    xs = random.uniform(low=0, high=nx, size=nsample).astype('L')
    ys = random.uniform(low=0, high=ny, size=nsample).astype('L')

    # sample the data
    sample = data[ys, xs].copy()
    sample = sample.reshape(nsample)

    # determine the clipped mean and standard deviation
    mean = sample.mean()
    std = sample.std()
    oldsize = 0
    niter = 0
    while oldsize != sample.size and niter < maxiter:
        niter += 1
        oldsize = sample.size
        wok = (sample < mean + 3 * std)
        sample = sample[wok]
        wok = (sample > mean - 3 * std)
        sample = sample[wok]
        mean = sample.mean()
        std = sample.std()

    return mean, std

#####################################################################

def checkdiff(imglist, database='dataredulco'):
    import agnkey 
    from pyraf import iraf
    iraf.digiphot(_doprint=0)
    iraf.daophot(_doprint=0)
    for img in imglist:
        status = checkstage(img, 'wcs')
        if status >= 0:
            photlcodict = agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, database, 'namefile', img, '*')
            _dir = photlcodict[0]['wdirectory']
            diffimg = _dir + img
            origimg = diffimg.replace('.diff', '')
            tempimg = origimg.replace('.fits', '.ref.fits')
            if os.path.isfile(diffimg) and os.path.isfile(origimg) and os.path.isfile(tempimg):
                print img, photlcodict[0]['filter']
                iraf.display(origimg, 1, fill=True, Stdout=1)
                iraf.display(tempimg, 2, fill=True, Stdout=1)
                iraf.display(diffimg, 3, fill=True, Stdout=1)
                ans = raw_input('>>> good difference [[y]/n] or [b]ad quality (original image)? ')
                if ans in ['n', 'N', 'No', 'NO', 'bad', 'b', 'B']:
                    print 'updatestatus bad'
                    print 'rm', diffimg.replace('.fits', '*')
                    os.system('rm ' + diffimg.replace('.fits', '*'))
                    print 'rm', tempimg
                    os.system('rm ' + tempimg)
                    print 'delete', img, 'from database'
                    agnkey.agnsqldef.deleteredufromarchive(img, 'dataredulco', 'namefile')
                if ans in ['bad', 'b', 'B']:
                    print 'updatestatus bad quality'
                    agnsql.agnsqldef.updatevalue(database, 'quality', 1, os.path.basename(origimg))
            else:
                for f in [origimg, tempimg, diffimg]:
                    if not os.path.isfile(f): print f, 'not found'
        elif status == -1:
            print 'status ' + str(status) + ': sn2.fits file not found'
        elif status == -2:
            print 'status ' + str(status) + ': .fits file not found'
        elif status == -4:
            print 'status ' + str(status) + ': bad quality image'
        else:
            print 'status ' + str(status) + ': unknown status'


#############################################################
