#!/usr/bin/env  python 

import sys,os,cgi,string,glob
from socket import gethostname, gethostbyname,gethostname
ip = gethostbyname(gethostname())
import urllib,urllib2
hostname=gethostname()

if hostname in ['engs-MacBook-Pro-4.local','valenti-macbook.physics.ucsb.edu','svalenti-lcogt.local']:
    sys.path.append('/Users/svalenti/lib/python2.7/site-packages/')
else:
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')

import agnkey
os.environ['HOME']='../tmp/'
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

_user=os.getenv("REMOTE_USER")

def bin(x, digits=0):
  oct2bin = ['000','001','010','011','100','101','110','111']
  binstring = [oct2bin[int(n)] for n in oct(x)]
  return ''.join(binstring).lstrip('0').zfill(digits)

aa=agnkey.agnsqldef.query(['select groups,groupid from groupstab order by groupid'])
position={}
for i in range(0,len(aa)): position[i+1]=aa[i]['groups']#,int(aa[i]['groupid'])]

def groupcheck(position,aaa,_id,_targid,_form):
    line='<form action="agnupdatetable.py" method="post">'
    line=line+'<input type="hidden" name="id" value="'+str(_id)+'">'
    line=line+'<input type="hidden" name="type" value="permission">'
    for i in position:
        if int(aaa[-1*i]):
            line=line+'<td><input type="checkbox" name="'+str(position[i])+'" value="'+position[i]+\
                  '" checked> '+position[i]+'</td>'
        else:
            line=line+'<td><input type="checkbox" name="'+str(position[i])+'" value="'+position[i]+\
                  '"> '+position[i]+'</td>'
    line=line+'<input type="hidden" name="targid" value="'+str(_targid)+'">'
    line=line+'<input type="hidden" name="outputformat" value="'+str(_form)+'">'
    line=line+'<td><input value="update" type="submit"/></td> </form>'
    return line

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

print '''<div align="center"   id="menu" style="background-color:#FFD700;width:150px;float:left;position: fixed; ">
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

print '''<div  align="center"   id="content" style="margin-left:150px;background-color:FFFFEF;width:1050px;float:left;">'''

command9=["select groupname from userstab where user='"+str(_user)+"'"]
gg=agnkey.agnsqldef.query(command9)
if len(gg)>0:
  if int(gg[0]['groupname'])==1:
    command99=["select * from lsc_sn_pos where objtype!='STD' and objtype!='nosn'"]
    aa=agnkey.agnsqldef.query(command99)
    ll0={}
    for jj in aa[0].keys(): ll0[jj]=[]
    for i in range(0,len(aa)):
      for jj in aa[0].keys(): ll0[jj].append(aa[i][jj])
    print '<table  border="1">'
    for i in range(0,len(ll0['name'])):
      bb=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'permissionlog','targid',str(ll0['targid'][i]),'*')
      if bb:
        ll1={}
        for jj in bb[0].keys(): ll1[jj]=[]
        for k in range(0,len(bb)):
            for jj in bb[0].keys(): ll1[jj].append(bb[k][jj])    
        aaa=str(bin(int(ll1['groupname'][0]),32))
        line=groupcheck(position,aaa,ll1['id'][0],ll1['targid'][0],'agnpermission.cgi')
        print '<tr><td>'+ll0['name'][i]+'</td><td>'+line+'</tr>'
    print '</table>'
  else:
    print '<h3> sorry you dont have access to this page </h3>'
else:
  print '<h3> sorry user unknown, you dont have access to this page </h3>'

print '<br></br>'
if len(gg)>0:
  if int(gg[0]['groupname'])==1:
    command99=["select * from lsc_sn_pos where objtype='test'"]
    aa=agnkey.agnsqldef.query(command99)
    ll0={}
    for jj in aa[0].keys(): ll0[jj]=[]
    for i in range(0,len(aa)):
      for jj in aa[0].keys(): ll0[jj].append(aa[i][jj])
    print '<table  border="1">'
    for i in range(0,len(ll0['name'])):
      bb=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, 'permissionlog','targid',str(ll0['targid'][i]),'*')
      if bb:
        ll1={}
        for jj in bb[0].keys(): ll1[jj]=[]
        for k in range(0,len(bb)):
            for jj in bb[0].keys(): ll1[jj].append(bb[k][jj])    
        aaa=str(bin(int(ll1['groupname'][0]),32))
        line=groupcheck(position,aaa,ll1['id'][0],ll1['targid'][0],'agnpermission.cgi')
        print '<tr><td>'+ll0['name'][i]+'</td><td>'+line+'</tr>'
    print '</table>'
#  else:
#    print '<h3> sorry you are not an LCOGT user, you dont have access to this page <h3>'
#else:
#  print '<h3> sorry user unknown, you dont have access to this page <h3>'

print '</head>'
print '</html>'
