#!/usr/bin/env python
description = ">> make catalogue from table"
usage = "%prog image [options] "

import os
import string
import numpy as np
from optparse import OptionParser
import time
import re
import agnkey

if __name__ == "__main__":
    start_time = time.time()
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-i", "--interactive", action="store_true", dest='interactive', default=False,
                      help='Interactive \t\t\t [%default]')
    parser.add_option("-e", "--exzp", dest="exzp", default='',
                      type='str', help='external zero point from different field \t\t %default')
    parser.add_option("-c", "--color", action="store_true", dest='color', default=False,
                      help='use specific color \t\t\t [%default]')
    parser.add_option("-t", "--typemag", dest="typemag", default='fit',
                      type='str', help='type of magnitude fit,ph \t\t %default')

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
    _exzp = option.exzp
    _interactive = option.interactive
    _color = option.color
    dicti = agnkey.util.makecatalogue2(lista)
    namemag = {'fit': ['smagf', 'smagerrf'], 'ph': ['magp3', 'merrp3']}
    allfilters = ''
    for fil in dicti:     
        allfilters = allfilters + filters1[fil]

    if _exzp:
        lista2 = agnkey.util.readlist(_exzp)
        dicti2 = agnkey.util.makecatalogue2(lista2)

    for _filter in dicti:
        for img in dicti[_filter]:
            print img,_filter
            if _exzp:
                zero = ''
                for _filter2 in dicti2:
                    if _filter2 ==_filter:
                        img2 = dicti2[_filter2].keys()[0]
                        print img2,_filter2
                        zero = dicti2[_filter2][img2]['ZZ2']
                        break
            else:
                zero = dicti[_filter][img]['ZZ2']

            if zero:
                print zero
                mag = dicti[_filter][img]['magp2']
                dmag = dicti[_filter][img]['merrp2']
                if dicti[_filter][img]['telescope'] in ['lsc', '1m0-04', '1m0-05', '1m0-06', '1m0-09']:
                    kk = agnkey.sites.extintion('ctio')
                elif dicti[_filter][img]['telescope'] in ['1m0-08', 'elp']:
                    kk = agnkey.sites.extintion('mcdonald')
                elif dicti[_filter][img]['telescope'] in ['1m0-10', '1m0-12', '1m0-13', 'cpt']:
                    kk = agnkey.sites.extintion('southafrica')
                elif dicti[_filter][img]['telescope'] in ['ftn']:
                    kk = agnkey.sites.extintion('mauna')
                elif dicti[_filter][img]['telescope'] in ['1m0-03','1m0-11', 'coj', 'fts']:
                    kk = agnkey.sites.extintion('siding')
                else:
                    print dicti[_filter][img]['telescope']
                    #sys.exit('problem with dicti 1')
                ra0 = dicti[_filter][img]['ra0']
                dec0 = dicti[_filter][img]['dec0']
                ra = dicti[_filter][img]['ra']
                dec = dicti[_filter][img]['dec']
                AP = zero + mag - kk[filters1[_filter]] * dicti[_filter][img]['airmass']
                DAP = dmag 

                output = re.sub('sn2.fits', 'cat', img)
                f = open(output, 'w')
                f.write('#daophot+standardfield\n#ra   dec   ' + filters1[_filter] + '   d' + filters1[_filter] + '\n')
                for i in range(0, len(ra0)):
                    if (float(AP[i])< 99) and (float(AP[i]) > 0):
                        f.write('%15s \t%15s \t%s\t%s\n' % (ra[i], dec[i], AP[i], DAP[i]))
                f.close()
                os.chmod(output, 0664)
                try:
                    if os.path.isfile(re.sub('sn2.fits', 'cat', img)):
                        agnkey.agnsqldef.updatevalue('dataredulco', 'abscat', string.split(output, '/')[-1],
                                                     re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                    else:
                        agnkey.agnsqldef.updatevalue('dataredulco', 'abscat', 'X',
                                                     re.sub('sn2.fits', 'fits', string.split(img, '/')[-1]))
                except:
                    print 'module mysqldef not found'
                    #print _filter, col, output
            else:
                print 'warning filter not found '+str(_filter)
#            raw_input('go on ')

