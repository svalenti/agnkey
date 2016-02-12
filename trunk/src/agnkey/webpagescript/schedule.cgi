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
form = cgi.FieldStorage()
name= cgi
_targid = form.getlist('targid')
if _targid:_targid=_targid[0]
else: 
    try:
        _targid=int(sys.argv[1])
    except:
        _targid=24

print "Content-Type: text/html\n\n"
print '''                                                                                                                                                        
<html> <head>        </head>'''
print '<body>'
#print '<div>'                                                                                                                                                                                                                        
fff0,fff1=agnkey.agndefin.obsin(_targid,30)        
if fff0:                                                                                                                                                                                                                            
    print '<h3> active triggers </3>'                                                                                                                
    print "<table BGCOLOR='CCFF66'  color='#FFFFFF'  border='1'  align='center'  height='10%' cellspacing='0' cellpadding='0' width=400 >"+fff0+'</table>'                                      
if fff1:                                                                                                                                                                                                           
    print '<h3> past triggers </3>'                                                                                                                                                                                 
    print "<table color='#GFFFFF' border='1'  align='center'  height='10%' cellspacing='0' cellpadding='0' width=400 >"+fff1+'</table>'                                                            
#    print '<br></br>'                                                                                                                       
#print '</div>'                

if not fff0 and not fff1:
    print '<h3> No triggers </3>'                  
print '</body>'
print '</html>'
