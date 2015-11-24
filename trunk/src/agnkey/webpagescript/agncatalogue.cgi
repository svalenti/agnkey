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
    sys.path.append('/home/valenti/lib/python2.7/site-packages/')
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
print '''</div>'''
print '''<div  align="center"   id="content" style="margin-left:150px;background-color:FFFFEF;width:1150px;float:left;">'''

command9=["select groupname from userstab where user='"+str(_user)+"'"]
bb=agnkey.agnsqldef.query(command9)
if len(bb)>0:
  if int(bb[0]['groupname'])==1:
    command9=["select * from lsc_sn_pos where objtype!='STD' and objtype!='test'"]
    aa=agnkey.agnsqldef.query(command9)
    print '<table  border="1">'
    line0=''
    for key in ['name','redshift','ra','dec','type','targid']:
      line0=line0+'<td>'+str(key)+'</td>'
    print '<tr>'+line0+'</tr>'
    for i in range(0,len(aa)):
      line=''
      for key in ['redshift','ra_sn','dec_sn','objtype','targid']:
        line= line+'<td>'+str(aa[i][key])+'<br>'+agnkey.agndefin.objectinfo(aa[i],_user,key,'agncatalogue.cgi')+'</td>'
      print '<tr><td>'+aa[i]['name']+'</td>'+line+'</tr>'
    print '</table>'

    command9=["select * from lsc_sn_pos where objtype='test'"]
    aa=agnkey.agnsqldef.query(command9)
    print '<table  border="1">'
    line0=''
    for key in ['name','redshift','ra','dec','type','targid']:
      line0=line0+'<td>'+str(key)+'</td>'
    print '<tr>'+line0+'</tr>'
    for i in range(0,len(aa)):
      line=''
      for key in ['redshift','ra_sn','dec_sn','objtype','targid']:
        line= line+'<td>'+str(aa[i][key])+'<br>'+agnkey.agndefin.objectinfo(aa[i],_user,key,'agncatalogue.cgi')+'</td>'
      print '<tr><td>'+aa[i]['name']+'</td>'+line+'</tr>'
    print '</table>'
  else:
    print '<h3> sorry you dont have access to this page <h3>'
else:
    print '<h3> sorry user unknown, you dont have access to this page <h3>'
print '</head>'
print '</html>'
