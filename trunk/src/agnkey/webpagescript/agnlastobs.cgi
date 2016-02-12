#!/dark/usr/anaconda/bin/python                                                                                                                               
#/usr/bin/env python                                                                                                                                          

import sys,os,cgi,string,glob
os.environ['HOME']='../tmp/'

from socket import gethostname, gethostbyname
ip = gethostbyname(gethostname())
import urllib,urllib2
hostname=gethostname()

if hostname in ['engs-MacBook-Pro-4.local','valenti-macbook.physics.ucsb.edu','valenti-mbp-2',\
                'svalenti-lcogt.local','svalenti-lcogt.lco.gtn','valenti-mbp-2.lco.gtn',\
                'valenti-mbp-2.attlocal.net','dhcp43168.physics.ucdavis.edu',\
                'valenti-MacBook-Pro-2.local']:
    sys.path.append('/Users/svalenti/lib/python2.7/site-packages/')
    location='SV'
elif hostname in ['dark']:
    sys.path.append('/dark/hal/lib/python2.7/site-packages/')
    location='dark'
else:
    location='deneb'
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')

os.environ['HOME']='../tmp/'
import agnkey
from numpy import argsort,take,abs
import datetime,pyfits,re

base_url=hostname
_user=os.getenv("REMOTE_USER")

def MJDnow(verbose=False):
    import datetime
    _MJD0=55927
    _MJDtoday=_MJD0+(datetime.datetime.now()-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
        (datetime.datetime.now()-datetime.datetime(2012, 01, 01,00,00,00)).days
    if verbose: print 'JD= '+str(_MJDtoday)
    return _MJDtoday

_MJDn = MJDnow()

##############################################################################

def searchobj1():
    search='''<form action="agnkeyview.cgi" method="post" style="width=150"> 
    <input width="100" name="sn_name" size="20" maxlength="30" type="text">
    <input width="100" value="search by name" type="submit"></form>'''
    return search

def searchobj2():
    search='''
    <form action="agnkeyview.cgi" method="post"> 
    <input  width="150" name="SN_RA" size="12" maxlength="12" type="text"  placeholder="00:00:00.000"/>
    <input  width="150" name="SN_DEC" size="13" maxlength="13" type="text" placeholder="+00:00:00.000"/>
    <input  width="150" value="search by coord" type="submit" /></form>'''
    return search

######################################
print "Content-Type: text/html\n"
print '<html>'
print '<head>'

print '<body topmargin="0" marginheight="0" leftmargin="0" marginwidth="0" rightmargin="0" bottommargin="0" bgcolor="#ececec" link="black" vlink="black" alink="black">'

print '''
<div id="container" style="width:1300px">
<div align="center"  leftmargin="10" id="header" style="background-color:#FFA500;">
<h1 style="margin-bottom:0;"> AGN AGENT </h1> '''
print '''<span style="font-family: 'Open Sans', sans-serif; font-weight:300; font-size:16"> user: &nbsp; %s</span>''' % (_user)
print '''</div>'''

print '''<div align="center"   id="menu" style="background-color:#FFD700;width:150px;float:left;position: fixed;">
<b>Menu</b>'''
print '<br></br>'
print searchobj1()
print '<br></br>'
print searchobj2()
print '<br></br>'
print agnkey.agndefin.addnewobject('agnkeyview.cgi')
print '<br></br>'
print '<a href="agnkeymain.cgi"> list of objects </a>'
print '<br></br>'
print '<a href="agncatalogue.cgi">  catalogue </a>'
print '<br></br>'
print '<a href="agnpermission.cgi"> permission </a>'
print '<br></br>'
print '<a href="agnupload.cgi"> upload spectrum  </a>'
print '<br></br>'
print '<a href="agnmissing.cgi"> Floyds inbox </a>'
print '<br></br>'
print '<a href="agnlastobs.cgi"> Last week </a>'
print '<br></br>'
print '''</div>'''
print '''<div  align="center"   id="content" style="margin-left:150px;background-color:FFFFEF;width:1150px;float:left;">'''

_user='SV'

command9=["select groupname from userstab where user='"+str(_user)+"'"]
bb=agnkey.agnsqldef.query(command9)
if len(bb)>0:
  if int(bb[0]['groupname'])==1:
################################################################################################
    command = ["select d.namefile,d.directory,d.targid,d.id,r.name  from datarawfloyds as d  join recobjects as r where d.mjd > "+str(_MJDn-7)+" and d.targid=r.targid and d.type='SPECTRUM' "]
    data = agnkey.agnsqldef.query(command)
    if data:
        ll={}
        for key in data[0]:
            ll[key] = []
        for jj in data:
            for key in jj:
                ll[key].append(jj[key])
    else:
        ll={'namefile':[]}
    print '<p> number of FLOYDS spectra in the last week %s </p>' %  str(len(ll['namefile']))
    print '<table  border="1">'
    for jj,spectrum in enumerate(ll['namefile']):
        line0=''
        nnn = '../../AGNKEY/'+re.sub(agnkey.util.workingdirectory,'',ll['directory'][jj])+str(re.sub(".fits",".png",spectrum))
        jjj=agnkey.agndefin.grafico1(nnn,'50','300')+'</p>'
        line0=line0+'<td>'+str(ll['name'][jj])+'</td>'
        line0=line0+'<td>'+str(spectrum)+'</td>'
        line0=line0+'<td>'+jjj+'</td>'
        line0=line0+'<td> '+ agnkey.agndefin.markasbad(str(ll['id'][jj]),str(ll['targid'][jj]),_user,'status','agnmissing.cgi')+'</td>'
        print '<tr>'+line0+'</tr>'
    print '</table>'
#################################################################################################
    command = ["select d.namefile,d.wdirectory,d.targid,d.id,r.name,d.filter,d.exptime  from dataredulco as d  join recobjects as r where d.jd > "+str(_MJDn-7)+" and d.targid=r.targid "]
    data = agnkey.agnsqldef.query(command)
    ll={}
    for key in data[0]:
        ll[key] = []
    for jj in data:
        for key in jj:
            ll[key].append(jj[key])
            
    print '<p> number of image  in the last week %s </p>' %  str(len(ll['namefile']))
    print '<table  border="1">'
    for jj,spectrum in enumerate(ll['namefile']):
        line0=''
        nnn = '../../AGNKEY/'+re.sub(agnkey.util.workingdirectory,'',ll['wdirectory'][jj])+str(re.sub(".fits",".png",spectrum))
        jjj=agnkey.agndefin.grafico1(nnn,'150','150')+'</p>'
        line0=line0+'<td>'+str(ll['name'][jj])+'</td>'
        line0=line0+'<td>'+str(ll['filter'][jj])+'</td>'
        line0=line0+'<td>'+str(ll['exptime'][jj])+'</td>'
        line0=line0+'<td>'+str(spectrum)+'</td>'
        line0=line0+'<td>'+jjj+'</td>'
#        line0=line0+'<td> '+ agnkey.agndefin.markasbad(str(ll['id'][jj]),str(ll['targid'][jj]),_user,'status','agnmissing.cgi')+'</td>'
        print '<tr>'+line0+'</tr>'
    print '</table>'
##################################################################################################
  else:
    print '<h3> sorry you dont have access to this page <h3>'
else:
    print '<h3> sorry user unknown, you dont have access to this page <h3>'





print '</head>'
print '</html>'
