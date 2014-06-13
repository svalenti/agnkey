#!/usr/bin/env python
import cgi,os,string,glob,sys
from socket import gethostname, gethostbyname,gethostname
ip = gethostbyname(gethostname()) 
import urllib,urllib2
hostname=gethostname()

if hostname in ['engs-MacBook-Pro-4.local','valenti-macbook.physics.ucsb.edu','svalenti-lcogt.local']:
    sys.path.append('/Users/svalenti/lib/python2.7/site-packages/')
else:
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')


os.environ['HOME']='../tmp/'
from numpy import argsort,take,abs,sort,asarray,array
import datetime,re,pyfits
import agnkey
_user=os.getenv("REMOTE_USER")
if not _user: _user='SV'
form = cgi.FieldStorage()

if form.getlist('note'): _note=form.getlist('note')[0]
else:                        _note=''

if form.getlist('namefile'): _namefile=form.getlist('namefile')[0]
else:                        _namefile=''

if form.getlist('access'):   _access=form.getlist('access')[0]
else:                        _access=''

base_url=hostname

#if hostname=='engs-MacBook-Pro-4.local':
#    base_url = "http://localhost/~svalenti/cgi-bin/" 
#else:
#    base_url = "http://secure.lcogt.net/user/supernova/dev/cgi-bin/"

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


commandg=["select groupname from userstab where user='"+str(_user)+"'"]
gg=agnkey.agnsqldef.query(commandg)
if gg:
    access=str(gg[0]['groupname'])
else:
    access=0

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
print '''<div align="center"   id="menu" style="background-color:#FFD700;width:150px;float:left;position: fixed;"><b>Menu</b>'''
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

if access==0:
    print '<h3>Error: user '+str(_user)+' do not have access to this page <h3>'
else:
    if int(access)!=1 and int(access)!=32768:  private=1+32768+int(access)
    else:
        if int(access)==1:        private=32768+int(access)
        elif int(access)==32768:  private=1+int(access)
    public=68719476735 

    lll='<center><fieldset style="text-align:left; border:2px solid black; width: 50em; background-color:#AABADD;">'+\
        '<legend style="border:2px solid black; padding: 2px 6px; background-color:#FFFDDA;"><font size="+2"><b>Upload spectrum</b></font></legend>'+\
        '<form action="./agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<p>Please only fits file (with keyword IDENT):<input id="uploadName" name="file" type="file"></p>'+\
        '<input type="hidden" name="type" value="spectrum">'+\
        '<select name= "access" >'+\
        '<option  width=10 value="'+str(public)+'"> public  </option>'+\
        '<option  width=10 value="'+str(private)+'"> private </option>'+\
        '</select> <h3>Fits file should have (at least) in the header the following keywords: <br></br> RA, DEC, DATE-OBS, OBJECT </h3>'+\
        '<input type="submit" value="Submit">'+\
        '</form></center>'

    ddd='<center><fieldset style="text-align:left; border:2px solid black; width: 50em; background-color:#FFFFFF;">'+\
        '<p>'+_note+'</p>'+'</center>'

    print lll
    print ddd
    print '</body></html>'
