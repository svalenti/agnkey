#!/usr/bin/env python
#/dark/usr/anaconda/bin/python

import sys,os,cgi,string,glob
os.environ['HOME']='../tmp/'

from socket import gethostname, gethostbyname
ip = gethostbyname(gethostname())
#import urllib,urllib2
hostname=gethostname()
#print(hostname)

import agn_function

if hostname in ['engs-MacBook-Pro-4.local','valenti-macbook.physics.ucsb.edu','valenti-mbp-2',\
                'svalenti-lcogt.local','svalenti-lcogt.lco.gtn','valenti-mbp-2.lco.gtn',\
                'valenti-mbp-2.attlocal.net','dhcp43168.physics.ucdavis.edu',\
                'valenti-MacBook-Pro-2.local']:
    sys.path.append('/Users/svalenti/lib/python2.7/site-packages/')
    location='SV'
elif hostname in ['phys-dark']:
    #sys.path.append('/dark/anaconda/anaconda27/envs/halenv/lib/python2.7/site-packages/')
    sys.path.append('/dark/anaconda/anaconda27/envs/dlt40/lib/python2.7/site-packages/')
    location='phys-dark'
else:
    location='deneb'
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')

os.environ['HOME']='../tmp/'
#import agnkey

from numpy import argsort,take,abs
import datetime,re
#from astropy.io import fits as pyfits

base_url=hostname

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

def expandpermissions(groupid):
    def bin(x, digits=0):
        oct2bin = ['000','001','010','011','100','101','110','111']
        binstring = [oct2bin[int(n)] for n in oct(x)]
        return ''.join(binstring).lstrip('0').zfill(digits)

    aa=agn_function.query(['select g.groups, g.groupid from groupstab as g order by g.groupid'])
    position={}
    for i in range(0,len(aa)): position[i+1]=aa[i]['groups']#,int(aa[i]['groupid'])]

    aaa=str(bin(int(groupid),32))
    stringa=''
    for i in position:
        if int(aaa[-1*i]):
            stringa=stringa+position[i]+'   |   '
    return stringa

def expandpermissions2(groupid):
    def bin(x, digits=0):
        oct2bin = ['000','001','010','011','100','101','110','111']
        binstring = [oct2bin[int(n)] for n in oct(x)]
        return ''.join(binstring).lstrip('0').zfill(digits)
    pos=32
    elements=[]
    for j in string.split(str(bin(int(groupid),32)),'1'):
        pos=pos-len(j)-1
        if pos>=0: elements.append(2**pos)
    return elements

####################################################
_user=os.getenv("REMOTE_USER")
if not _user:  _user='agnkey'

#print "Content-Type: text/html\n"
#print '<html><body>'
#print hostname
#print '<h3> objects visible for user '+str(_user)+'<h3>'
####################################################################################################
ddd = agn_function.addnewobject('agnkeyview.cgi')

###############################################
command9=["select groupname from userstab where user='"+str(_user)+"'"]
bb=agn_function.query(command9)
if len(bb)>0:
    num=int(bb[0]['groupname'])
else:
    num=0

##############################################################

print("Content-Type: text/html\n\n")
print('''
<html>
<head>
<title>AGNKEY</title>
<base href='%s'>
<link href='http://fonts.googleapis.com/css?family=Open+Sans:400,800,300,600,400italic,300italic' rel='stylesheet' type='text/css'>
<!--[if lte IE 8]><script language="javascript" type="text/javascript" src="flot/excanvas.min.js"></script><![endif]-->
</head>
''' %(base_url))

#<script language="javascript" type="text/javascript" src="http://secure.lcogt.net/user/supernova/dev/flot/jquery.js"></script>
#<script language="javascript" type="text/javascript" src="http://secure.lcogt.net/user/supernova/dev/flot/jquery.flot.js"></script>
#<script language="javascript" type="text/javascript" src="http://secure.lcogt.net/user/supernova/dev/flot/jquery.flot.errorbars.js"></script>
#<script language="javascript" type="text/javascript" src="http://secure.lcogt.net/user/supernova/dev/flot/jquery.flot.navigate.js"></script>

print('<body topmargin="0" marginheight="0" leftmargin="0" marginwidth="0" rightmargin="0" bottommargin="0" bgcolor="#ececec" link="black" vlink="black" alink="black">')

print('''
<div id="container" style="width:1300px">
<div align="center"  leftmargin="10" id="header" style="background-color:#FFA500;">
<h1 style="margin-bottom:0;"> AGN AGENT </h1> ''')
print('''<span style="font-family: 'Open Sans', sans-serif; font-weight:300; font-size:16"> user: &nbsp; %s</span>''' % (_user))
print('''</div>''')

print('''<div align="center"   id="menu" style="background-color:#FFD700;width:150px;float:left;"><b>Menu</b>''')
print('<br></br>')
print(searchobj1())
print('<br></br>')
print(searchobj2())
print('<br></br>')
print(agn_function.addnewobject('agnkeyview.cgi'))
print('<br></br>')
print('<a href="agnkeymain.cgi"> list of objects </a>')
print( '<br></br>')
print( '<a href="agnschedule.cgi">  schedule </a>')
print( '<br></br>')
print( '<a href="agncatalogue.cgi">  catalogue </a>')
print( '<br></br>')
print( '<a href="agnpermission.cgi"> permission </a>')
print( '<br></br>')
print( '<a href="agnupload.cgi"> upload spectrum  </a>')
print( '<br></br>')
print( '<a href="agnmissing.cgi"> Floyds inbox </a>')
print( '<br></br>')
print( '<a href="agnlastobs.cgi"> last week </a>')
print( '<br></br>')
print( '<br></br>')
print( '''</div>''')
print('''<div  align="center"   id="content" style="background-color:FFFFEF;width:1150px;float:left;">''')
#print(num)
if not num:
    print('<h3> sorry user unknown, you dont have access to this page <h3>')
else:
########################    expand all groups user is part of and allow user to see all objects belonging to each group
    ele=expandpermissions2(num)
    gg="( "
    for ii in ele:   gg=gg+" ((p.groupname & "+str(ii)+")="+str(ii)+") or "
    gg=gg[:-3]+')'
    print(gg)
########################
#    command8=["select r.name,a.ra_sn,a.dec_sn, a.targid, p.groupname, a.redshift, count(distinct(d.dateobs)) as numero ,max(d.dateobs) as last, a.objtype from lsc_sn_pos as a join recobjects as r join dataredulco as d join permissionlog as p where a.targid=r.targid and d.targid=a.targid  and p.targid=a.targid and "+str(gg)+" and a.objtype!='test1' group by r.targid order by p.groupname  desc"]
#########
#    command8=["select r.name,a.ra_sn,a.dec_sn, a.targid, p.groupname, a.redshift, count(distinct(d.dateobs)) as numero ,max(d.dateobs) as last, a.objtype from lsc_sn_pos as a join recobjects as r join dataredulco as d join permissionlog as p where a.targid=r.targid and p.targid=a.targid and "+str(gg)+" and a.objtype!='test1' group by r.targid order by p.groupname  desc"]
########
#    command8=["select r.name,a.ra_sn,a.dec_sn, a.targid, p.groupname, a.redshift, d.filetype as numero ,max(d.dateobs) as last, a.objtype from lsc_sn_pos as a join recobjects as r join dataredulco as d join permissionlog as p where a.targid=r.targid and p.targid=a.targid and "+str(gg)+" and a.objtype!='test1' group by r.targid order by p.groupname  desc"]
    command8=["select r.name, a.ra_sn,a.dec_sn, a.targid, p.groupname, a.redshift, d.filetype as numero , max(d.dateobs) as last, a.objtype from lsc_sn_pos as a join dataredulco as d join recobjects as r join permissionlog as p where a.id = d.targid and a.id=r.targid and a.id = p.targid and a.objtype!='test1' and "+str(gg)+" group by a.id order by p.groupname desc"]
    lista8 = agn_function.query(command8)
    print('here')
    print('''</table></br></br>''')
    print('''<table class="fixed" border="1" style='table-layout:fixed'><tr align="center"> <td  height= 40  length=30 width=200> <b> AGN name </b></td> <td> <b> RA  </b></td><td>  <b>DEC</b>  </td> <td> <b> Type  </b> </td> <td> <b> Redshift </b> </td> <td> <B> N nights </b> </td> <td  width=100  align="center"> <b> last obs. </b> </td> <td> <b>  groups </b>  </td></tr>''')
    mm=0
    for i in range(0,len(lista8)):
      if lista8[i]['objtype']!='STD' and lista8[i]['objtype']!='test':
          mm=mm+1
          if mm % 2: ccc='BGCOLOR="#F5F5DC"'
          else:      ccc=''
          commnew=["select count(distinct(d.dateobs)) as dd ,max(d.dateobs) as cc from dataredulco as d where targid="+str(lista8[i]['targid'])]
          lista99=agn_function.query(commnew)
          if len(lista99):          
              num=lista99[0]['dd']
              last=lista99[0]['cc']
          else: 
              num=0
              last=0
          oblink='<a href="agnkeyview.cgi?sn_name='+re.sub('\+','%2B',lista8[i]['name'])+'"> '+lista8[i]['name']+' </a> '
          print('<tr '+ccc+' align="center"><td align="left" length=30 ><b>'+oblink+'</b></td> <td align="left" width=100>'+\
              str(lista8[i]['ra_sn'])+'</td> <td align="left" width=100>'+str(lista8[i]['dec_sn'])+\
              '</td> <td>'+str(lista8[i]['objtype'])+'</td> <td>'+str(lista8[i]['redshift'])+'</td> <td>'+str(num)+\
              '</td> <td>'+str(last)+'</td> <td align="left" width=400>'+expandpermissions(lista8[i]['groupname'])+'</tr>')
#              '</td> <td>'+str(lista8[i]['last'])+'</td> <td align="left" width=400>'+expandpermissions(lista8[i]['groupname'])+'</tr>'
#              '</td> <td>'+str(lista8[i]['objtype'])+'</td> <td>'+str(lista8[i]['redshift'])+'</td> <td>'+str(lista8[i]['numero'])+\
          command88=["select name from recobjects where targid="+str(lista8[i]['targid'])]
          lista88=agn_function.query(command88)
          if len(lista88)>1:
              fff=''
              for j in lista88: fff=fff+' '+j['name']
              print('<tr '+ccc+' ><td length=30 >'+fff+'</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>')
    print('</table></br></br>')
    print('''</table></br></br>''')
    print('''<table class="fixed" border="2" style='table-layout:fixed'><tr align='center'> <td width=200 align="left"> STD name  </td> <td> RA  </td><td>  DEC  </td> <td>  N nights  </td> <td>  last obs  </td></tr>''')
    for i in range(0,len(lista8)):
      if lista8[i]['objtype']=='test':
          oblink='<a href="agnkeyview.cgi?sn_name='+lista8[i]['name']+'"> '+lista8[i]['name']+' </a> '
          print('<tr align="center"><td align="left">'+oblink+'</td> <td width=150 align="left">'+str(lista8[i]['ra_sn'])+'</td> <td width=150 align="left">'+str(lista8[i]['dec_sn'])+\
                '</td> <td>'+str(lista8[i]['numero'])+'</td> <td width=200>'+str(lista8[i]['last'])+'</tr>')
    print('</table></br></br>')
#else:
#    print '<h3> sorry user unknown, you dont have access to this page <h3>'
print('</body></html>')
