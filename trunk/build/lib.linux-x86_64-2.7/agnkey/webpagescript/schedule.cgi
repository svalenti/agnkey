#!/usr/bin/env python 

import sys,os,cgi,string,glob
from socket import gethostname, gethostbyname,gethostname
ip = gethostbyname(gethostname())
import urllib,urllib2
hostname=gethostname()
os.environ['HOME']='../tmp/'

if hostname in ['engs-MacBook-Pro-4.local','valenti-macbook.physics.ucsb.edu','svalenti-lcogt.local','svalenti-lcogt.lco.gtn']:
    sys.path.append('/Users/svalenti/lib/python2.7/site-packages/')
else:
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')

import agnkey
form = cgi.FieldStorage()
name= cgi
_targid = form.getlist('targid')
if _targid:_targid=_targid[0]
else: _targid=23

print "Content-Type: text/html\n\n"
print '''                                                                                                                                                        
<html> <head>        </head>'''
print '<body>'
#print '<div>'                                                                                                                                                                                                                        
fff0,fff1=agnkey.agndefin.obsin(_targid)                                                                                                                                                                                             
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
