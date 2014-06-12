#!/System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

import agnkey
import os,glob,shutil,sys

if len(sys.argv)<=1:
     listfits=glob.glob('*fits')
     for img in listfits:
          print img
     img=raw_input('Which image do you want to test ['+str(listfits[0])+'] ? ')
     if not img: img=listfits[0]
else:
     img=sys.argv[1]

hdr=agnkey.util.readhdr(img)
     
_imagetype=agnkey.util.readkey3(hdr,'type')
_object=agnkey.util.readkey3(hdr,'object')
_JD=agnkey.util.readkey3(hdr,'JD')
_airmass=agnkey.util.readkey3(hdr,'airmass')
_filter=agnkey.util.readkey3(hdr,'filter')
_grism=agnkey.util.readkey3(hdr,'grism')
_exptime=agnkey.util.readkey3(hdr,'exptime')
_date=agnkey.util.readkey3(hdr,'date-obs')
_gain=agnkey.util.readkey3(hdr,'gain')
_ron=agnkey.util.readkey3(hdr,'ron')
_lampid=agnkey.util.readkey3(hdr,'lampid')
_RA=agnkey.util.readkey3(hdr,'RA')
_DEC=agnkey.util.readkey3(hdr,'DEC')
_ccdmax=agnkey.util.readkey3(hdr,'datamax')
_ccdmin=agnkey.util.readkey3(hdr,'datamin')
_cenwav=agnkey.util.readkey3(hdr,'cenw')
_slitw=agnkey.util.readkey3(hdr,'slit')
_UT=agnkey.util.readkey3(hdr,'ut')
_xdimen=agnkey.util.readkey3(hdr,'NAXIS1')
_ydimen=agnkey.util.readkey3(hdr,'NAXIS2')
_instrument=agnkey.util.readkey3(hdr,'instrume')
_obsmode=agnkey.util.readkey3(hdr,'obsmode')

if not _gain: _gain='########'
if not _ron: _ron='########'
if not _instrument: _instrument=='########'
if not _ydimen: _ydimen='########'
if not _xdimen: _xdimen='########'
if not _filter: _filter='########'
if not _RA: _RA='########'
if not _grism: _grism='########'
if not _slitw: _slitw='########'
if not _lampid: _lampid='#######'
if not _date: _date='#######'
if not _cenwav: _cenwav='#######'
if not _UT: _UT='#######'
if not _ccdmin:_ccdmin='#######'
if not _ccdmax:_ccdmax='#######'
if not _obsmode:_obsmode='#######'
if not _object:_object='#######'
_system='#######'


print '####################################################################'
print 'IMG                OBJECT  IMAGETYPE    EXPTIME    FILTER        GRISM      '
print str(img)+'\t'+str(_object)+'\t'+str(_imagetype)+'\t'+str(_exptime)+'\t'+str(_filter)+'\t'+str(_grism)
print '####################################################################'
print 'AIRMASS             JD             DATE          XDIM   YDIM    GAIN   RON '
print str(_airmass)+'\t'+str(_JD)+'\t'+str(_date)+'\t'+str(_xdimen)+'\t'+str(_ydimen)+'\t'+str(_gain)+'\t'+str(_ron)
print '####################################################################'
print 'LAMP_ID     slitw         RA          DEC     CCDMIN    CCDMAX   CENWAV '
print str(_lampid)+'\t'+str(_slitw)+'\t'+str(_RA)+'\t'+str(_DEC)+'\t'+str(_ccdmin)+'\t'+str(_ccdmax)+'\t'+str(_cenwav)
print '####################################################################'
print ' UT     xdimension    ydimension        instrument      SYSTEM   OBSMODE '
print str(_UT)+'\t'+str(_xdimen)+'\t'+str(_ydimen)+'\t'+str(_instrument)+'\t'+str(_system)+'\t'+str(_obsmode)
print '####################################################################'

