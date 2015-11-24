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

import agnkey
from numpy import argsort,take,abs
import datetime,pyfits,re
from numpy import sort,asarray,array,genfromtxt
import StringIO
import base64
#import agndefin
import ephem
try:
    _user=os.getenv("REMOTE_USER")
except:
    pass

#if not _user:  _user=os.environ['USER']
if not _user:  _user='SV'

page=''
_targid=''


hostname=gethostname()

base_url=hostname
#dhcp43019.physics.ucdavis.edu


try:
    txt = glob.glob('../tmp/*.txt')
    if len(txt):
        os.system('rm ../tmp/*.txt')
    png = glob.glob('../tmp/*.png')
    if len(png):
        os.system('rm ../tmp/*.png')
except: 
    pass

#############################################################

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

#################################################################
def JDnow(verbose=False):
    import datetime
    _MJD0=55927
    _MJDtoday=_MJD0+(datetime.datetime.now()-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
        (datetime.datetime.now()-datetime.datetime(2012, 01, 01,00,00,00)).days
    if verbose: print 'JD= '+str(_MJDtoday)
    return _MJDtoday

##############################################################################
def plotfast(setup,output='',logs=''):#,band,color,fissa=''):
    import matplotlib.pyplot as plt 
    from numpy import argmin,sqrt,mean,array,std,median,compress
    global idd,_jd,_mag,_setup,_namefile,shift
    if not output:   plt.ion()
    fig = plt.figure()
    plt.rcParams['figure.figsize'] =12, 7
    plt.axes([.1,.1,.65,.8])

    _symbol='sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*sdo+34<>^*'
    _color={'U':'b','B':'r','V':'g','R':'c','I':'m','up':'b','gp':'r','rp':'g','ip':'c','zs':'m',\
                 'Bessell-B':'r','Bessell-V':'g','Bessell-R':'c','Bessell-I':'m',\
                 'SDSS-G':'r','SDSS-R':'g','SDSS-I':'c','Pan-Starrs-Z':'m'}
    _shift={'U':-2,'B':-1,'V':0,'R':1,'I':2,'up':-2,'gp':-1,'rp':0,'ip':1,'zs':2,\
                 'Bessell-B':-1,'Bessell-V':0,'Bessell-R':1,'Bessell-I':2,\
                 'SDSS-G':-1,'SDSS-R':0,'SDSS-I':1,'Pan-Starrs-Z':2}
    _setup=setup
    ii=0
    mag,jd,namefile=[],[],[]
    for _tel in _setup:
        shift=0
        for _fil in _setup[_tel]:
            shift=_shift[_fil]
            col=_color[_fil]
            plt.plot(array(_setup[_tel][_fil]['jd']),array(_setup[_tel][_fil]['mag'])+shift,_symbol[ii],color=col,label=_tel+' '+_fil+' '+str(shift),markersize=5)
            mag=list(mag)+list(array(_setup[_tel][_fil]['mag'])+shift)
            jd=list(jd)+list(_setup[_tel][_fil]['jd'])
            namefile=list(namefile)+list(_setup[_tel][_fil]['namefile'])
            ii=ii+1

    _JDn=JDnow()
    if logs:
       sta=array(logs[0],float)-2400000.5
       sto=array(logs[1],float)-2400000.5
       sta=compress(sta>_JDn-10,sta)
       sto=compress(sto>_JDn-10,sto)
    else:
        sto=''
        sta=''

       
    if len(sta)>0:
        for dd in sta:
            plt.plot([dd,dd],[max(mag),min(mag)],'-g',label='')
        plt.plot([dd,dd],[max(mag),min(mag)],'-g',label='start window')
    if len(sto)>0:
        for dd in sto:
            plt.plot([dd,dd],[max(mag),min(mag)],':b',label='')
        plt.plot([dd,dd],[max(mag),min(mag)],':b',label='stop window')
       
    if float(_JDn)-float(max(jd))<50.:
       plt.plot([_JDn,_JDn],[max(mag),min(mag)],'-r',label='Today')

    plt.legend(numpoints=1,markerscale=.8,loc=(1,.0))
    plt.xlabel('JD')
    plt.ylabel('magnitude')
    plt.xlim(min(jd)-5,max(jd)+10)
    plt.ylim(max(mag)+.5,min(mag)-.5)
    leg = plt.gca().get_legend()
    yticklabels = plt.getp(plt.gca(),'yticklabels')
    xticklabels = plt.getp(plt.gca(),'xticklabels')
    plt.setp(xticklabels,fontsize='15')    
    plt.setp(yticklabels,fontsize='15')
    ltext = leg.get_texts()
    plt.setp(ltext,fontsize=15)
    _mag = mag[:]
    _jd  = jd[:]
    _namefile=namefile[:]
    _jd = array(_jd)
    _mag = array(_mag)
    idd = range(len(_jd))
    plt.plot(_jd,_mag,'ok',markersize=1)
    if not output:
         plt.draw()
         raw_input('press d to mark. Return to exit ...\n')
         plt.close()
         return ''
    else:
       pngplot = StringIO.StringIO()
       plt.savefig(pngplot,format='png')
       pngplot.seek(0)
       data_uri = pngplot.read().encode("base64").replace("\n", "")
       html = '<img width="500" height="300" alt="sample" src="data:image/png;base64,{0}">'.format(data_uri)
       return html
#    else:
#         plt.savefig(output+'.png', format='png')
#         os.system('chmod 777 '+output+'.png')


################################################################

def subset(xx,_avg=''):   # lista  jd
    from numpy import array
    diff = [xx[i+1]-xx[i] for i in range(len(xx)-1)]
    if _avg:  avg=float(_avg)
    else:
        avg = sum(diff) / len(diff)
        if avg>=1: avg=.5
        elif avg<=0.1: avg=.5
    i=1
    subset={}
    position={}
    subset[1]=[xx[0]]
    position[1]=[0]
    for j in range(0,len(diff)):
         if diff[j]> avg:   i=i+1
         if i not in subset:  subset[i]=[]
         if i not in position:  position[i]=[]
         subset[i].append(xx[j+1])
         position[i].append(j+1)
    return subset,position

###########################################################################################

def run_getmag(imglist,_field,_output='',_bin=1e-10,magtype='mag',_ft=1,logs=''):
     from numpy import array,compress,abs,mean,asarray,std,take,argsort,where
     import os,string,glob,re,sys
     direc=agnkey.__path__[0]
     if _field=='landolt': filters0=['U','B','V','R','I','Bessell-B','Bessell-V','Bessell-R','Bessell-I']        # to be raplace when more telescopes available with dictionary
     else:                 filters0=['up','gp','rp','ip','zs','SDSS-G','SDSS-R','SDSS-I','Pan-Starrs-Z']
     if magtype=='mag':
          mtype='mag'
          mtypeerr='dmag'
     elif magtype=='fit':
          mtype='psfmag' 
          mtypeerr='psfdmag'
     elif magtype=='ph':
          mtype='apmag' 
          mtypeerr='psfdmag'
     elif magtype=='ph1':
          mtype='appmagap1' 
          mtypeerr='dappmagap1' 
     elif magtype=='ph2':
          mtype='appmagap2' 
          mtypeerr='dappmagap2'
     elif magtype=='ph3':
          mtype='appmagap3'
          mtypeerr='dappmagap3'

     setup={}
     mag=imglist[mtype]
     dmag=imglist[mtypeerr]
     jd=imglist['jd']
     namefile=imglist['namefile']
     filt=imglist['filter']
     tel=imglist['telescope']
     date=imglist['dateobs']
     filetype=imglist['filetype']
     for _tel in list(set(tel)):
         if _tel not in setup: setup[_tel]={}

     for _tel in setup:
        _filt=set(compress((array(tel)==_tel),array(filt)))
        for filtro in _filt: setup[_tel][filtro]={}
        for _fil in setup[_tel]:
            jd00=compress((array(filt)==_fil)&(array(tel)==_tel)&(array(filetype)==_ft),array(jd))
            mag00=compress((array(filt)==_fil)&(array(tel)==_tel)&(array(filetype)==_ft),array(mag))
            dmag00=compress((array(filt)==_fil)&(array(tel)==_tel)&(array(filetype)==_ft),array(dmag))
            date00=compress((array(filt)==_fil)&(array(tel)==_tel)&(array(filetype)==_ft),array(date))
            namefile00=compress((array(filt)==_fil)&(array(tel)==_tel)&(array(filetype)==_ft),array(namefile))

            ww=where((array(mag00) > -99)&(array(mag00) < 99))
            jd0=jd00[ww]
            mag0=mag00[ww]
            dmag0=dmag00[ww]
            date0=date00[ww]
            namefile0=namefile00[ww]

            inds = argsort(jd0)
            mag0 = take(mag0, inds)
            dmag0 = take(dmag0, inds)
            date0 = take(date0, inds)
            namefile0 = take(namefile0, inds)
            jd0 = take(jd0, inds)

            mag1,dmag1,jd1,date1,namefile1=[],[],[],[],[]
            done=[]
            for i in range(0,len(jd0)):
                if i not in done:
                    ww=asarray([j for j in range(len(jd0)) if (jd0[j]-jd0[i])<_bin and (jd0[j]-jd0[i])>=0.0]) # abs(jd0[j]-jd0[i])<bin])
                    for jj in ww: done.append(jj)
                    if len(ww)>=2:
                        jd1.append(mean(jd0[ww]))
                        mag1.append(mean(mag0[ww]))
                        dmag1.append(std(dmag0[ww]))
                        namefile1.append(namefile0[ww])
                        date1.append(date0[ww][0]+datetime.timedelta(mean(jd0[ww])-jd0[ww][0]))
                    else:
                        jd1.append(jd0[ww][0])
                        mag1.append(mag0[ww][0])
                        dmag1.append(dmag0[ww][0])
                        date1.append(date0[ww][0])
                        namefile1.append(namefile0[ww][0])
            setup[_tel][_fil]['mag']=mag1
            setup[_tel][_fil]['dmag']=dmag1
            setup[_tel][_fil]['jd']=jd1
            setup[_tel][_fil]['date']=date1
            setup[_tel][_fil]['namefile']=namefile1

     #html=plotfast(setup,_output,bb)
     try:    html=plotfast(setup,_output,bb)
     except: html=''
     
     ff=open(_output+'.txt','w')
     for _tel in setup:
        filters=setup[_tel].keys()
        line0='# %10s\t%12s\t' % ('dateobs','jd')
        for filt in filters0:
             if filt in filters and filt in setup[_tel].keys():
                  line0=line0+'%7.7s\t%6.6s\t' %(str(filt),str(filt)+'err')
        ff.write(line0+'\n')
        for  _fil in setup[_tel]:
            for j in range(0,len(setup[_tel][_fil]['jd'])):
                line= '  %10s\t%12s\t' % (str(setup[_tel][_fil]['date'][j]),str(setup[_tel][_fil]['jd'][j]))
                for filt in filters0:
                  if filt in filters:
                    if filt==_fil:   line=line+'%7.7s\t%6.6s\t' %(str(setup[_tel][_fil]['mag'][j]),str(setup[_tel][_fil]['dmag'][j]))
                    else:            line=line+'%7.7s\t%6.6s\t' %('9999','0.0')
                line=line+'%2s\t%6s\t\n' % (str(_fil),str(_tel))
                ff.write(line)
     ff.close()     
     return html
  
########################################################################################

def ascifile(snfile,supernova,directory):
    pippo="""<form method="post" action="agntake_asci2.py" >
    <input type="hidden" name='nomespettro' value='"""+snfile+"""'><font color="#000000" size="1"></font>
    <input type="hidden" name='SN' value='"""+supernova+"""'><font color="#000000" size="1"></font>
    <input type="hidden" name='directory' value='"""+directory+"""'><font color="#000000" size="1"></font>
    <input type="submit" value="ascifile"></form>""" #"
    return pippo

def fastspec(snfile,supernova,directory):
    pippo="""<form method="post" action="agnfast_plot2.py" >
    <input type="hidden" name='nomespettro' value='"""+snfile+"""'><font color="#000000" size="1"></font>	
    <input type="hidden" name='SN' value='"""+supernova+"""'><font color="#000000" size="1"></font>
    <input type="hidden" name='directory' value='"""+directory+"""'><font color="#000000" size="1"></font>
    <input type="submit" value="preview"></form>"""  # "
    return pippo 

##########################################################################
# tit= open table
#

def tit(col1,col2,col3,col4,col5,col6):
    tit1="""<table border="0"  " height="10%" cellspacing='0' cellpadding='0' width="99%" >
	<tr>
		<td width="1000" height="20" class="ms-grid1-1101-top" align="center" style="background-color: #9A9A9A">
		<font face="Arial" color="#FFFFFF"><b>"""+col1+"""</b></font></td>
		<td width="1000" height="20" class="ms-grid1-1101-top" align="center" style="background-color: #9A9A9A" >
		<font face="Arial" color="#FFFFFF"><b>&nbsp; """+col2+"""&nbsp </b></font></td>
		<td width="1000" height="20" class="ms-grid1-1101-top" align="center" style="background-color: #9A9A9A" >
		<font face="Arial" color="#FFFFFF"><b>"""+col3+"""</b></font></td>
		<td width="1000" height="20" class="ms-grid1-1101-top" align="center" style="background-color: #9A9A9A" >
		<font face="Arial" color="#FFFFFF"><b>"""+col4+"""</b></font></td>
		<td width="1000" height="20" class="ms-grid1-1101-top" align="center" style="background-color: #9A9A9A" >
		<font face="Arial" color="#FFFFFF"><b>"""+col5+"""</b></font></td>
		<td width="1000" height="20" class="ms-grid1-1101-top" align="center" style="background-color: #9A9A9A" >
		<font face="Arial" color="#FFFFFF"><b>"""+col6+"""</b></font></td></tr> """  # "
    return tit1
 
tit2=""" </table>  """
tdopen=""" <td  class='ms-grid1-1100-even' margin='0' cellspacing='0' cellpadding='0' align='left' height='5%'>  """
tdopen2=""" <td cellspacing='0' cellpadding='0' class="ms-grid1-1100-even" align="left" height="5%" style="background-color: #9A9A9A">  """
tdclose=""" </td>  """ #"
#cellpadding="0" cellspacing="0"

#####################################################################
form = cgi.FieldStorage()
name= cgi

    ##########   SN  #########
if form.getlist('sn_name'):  
    SN0 = form.getlist('sn_name')[0]
else:                        
    SN0 = ''
    ##########   SN_RA  #########
if form.getlist('SN_RA'): 
    SN_RA = form.getlist('SN_RA')[0]
else:                      
    SN_RA = ''
    ##########   SN_DEC  #########
if form.getlist('SN_DEC'): 
    SN_DEC = form.getlist('SN_DEC')[0]
else:                       
    SN_DEC = ''

    ##########   targid  #########
if form.getlist('targid'): 
    _targid = form.getlist('targid')[0]
else:                        
    _targid = ''

#SN = form.getlist('sn_name')
#SN_RA = form.getlist('SN_RA')
#SN_DEC = form.getlist('SN_DEC')

d=(datetime.date.today()+datetime.timedelta(1)).strftime("%Y%m%d")
_JDn=JDnow()

##############################################################################
#if len(SN)>0:    SN0=re.sub(' ','',SN[0])
#else:            SN0=''
#if len(SN_RA)>0:    SN_RA=SN_RA[0]
#else:               SN_RA=''    #'95.410237499999994'
#if len(SN_DEC)>0:    SN_DEC=SN_DEC[0]
#else:                SN_DEC=''  #'-59.7140611111111'

if len(SN0)==0 and len(SN_RA)==0 and len(SN_DEC)==0:
  try: 
    SN_RA=sys.argv[1]
    SN_DEC=sys.argv[2]
  except: 
    try: SN0=sys.argv[1]
    except: pass

#commandg=["select groupname from userstab where user='"+str(_user)+"'"]
#gg=agnkey.agnsqldef.query(commandg)
#if len(gg)==0:
#    print "Content-Type: text/html\n"
#    print '<html><body>'
#    print '<h3> sorry user unknown, you dont have access to this page <h3>'
#    print '</body></html>'
#    sys.exit()

#####################################################
if not _targid:       #  try to get coordinate from NED
  if not SN_RA and not SN_DEC:     #  try to get coordinate from name
    if SN0:
        listac=agnkey.agnsqldef.getlike(agnkey.agnsqldef.conn, 'recobjects', 'name',SN0,'targid,name')
        allobj=''
        alltarg=[]
        for i in listac: 
            allobj=allobj+'\t'+i['name']
            alltarg.append(int(i['targid']))
            _targid=''
        if len(alltarg)==0:
            page='<h3> no objects with this name </h3>'
        elif  len(set(alltarg))>1:
            page='<h3> warning too many objects with these name </h3>'
            _targid=''
        else:
           lista2=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn,'lsc_sn_pos','targid',str(int(listac[0]['targid'])),'ra_sn,dec_sn,targid,name')
           _targid=listac[0]['targid']
           SN_RA=lista2[0]['ra_sn']
           SN_DEC=lista2[0]['dec_sn']
           SN0=lista2[0]['name']

############################################################################
if not _targid:       #  try to get coordinate from NED
    if SN0:
        root_url='http://nedwww.ipac.caltech.edu/cgi-bin/nph-objsearch'
        request_dict = {'extend':'no','of':'xml_all','objname':SN0}
        query_url = "%s?%s" % (root_url,urllib.urlencode(request_dict))
        U = urllib2.urlopen(query_url)
        R = U.read()
        U.close()
        xx=[]
        for i in range(0,len(string.split(R))):  
            if 'TABLEDATA' in string.split(R)[i]: xx.append(i)
        if len(xx)>0:
            cc=string.split(R)[xx[0]:xx[1]]
            ss=re.sub(',','',re.sub("'",'',re.sub("<TD>",'',str(cc))))
            SN0=re.sub(' ','',string.split(ss,'</TD>')[1])
            SN_RA=string.split(ss,'</TD>')[2]
            SN_DEC=string.split(ss,'</TD>')[3]
            page='<h2> object recognised by NED </h2>'
            SN0=''
###################################################################
if (SN_RA and SN_DEC) and not _targid:     #  try to get name from coordinate
    if SN_RA:
        if string.count(str(SN_RA),':'):
            r0,r1,r2=string.split(SN_RA,':')
            SN_RA=(float(r0)+(float(r1)/60.)+(float(r2)/3600.))*15
        else: SN_RA=float(SN_RA)
    if SN_DEC:
        if string.count(str(SN_DEC),':'):
            d0,d1,d2=string.split(SN_DEC,':')
            if '-' in d0:   SN_DEC=float(abs(float(d0)))+(float(d1)/60.)+(float(d2)/3600.)*(-1)
            else:           SN_DEC=float(abs(float(d0)))+(float(d1)/60.)+(float(d2)/3600.)
        else: SN_DEC=float(SN_DEC)
    aa=agnkey.agnsqldef.getfromcoordinate(agnkey.agnsqldef.conn, 'lsc_sn_pos', SN_RA, SN_DEC,.01)
    if len(aa)>=1:
        SN0,_targid=aa[0]['name'],aa[0]['targid']
    else:
        _SN,_targid='',''
        page='<h2> no object found at these coordinates </h2>'
        
########################################################################
####################################################
print "Content-Type: text/html\n\n"
print '''
<html>
<head>
<title>AGNKEY</title>
<base href='%s'>
<link href='http://fonts.googleapis.com/css?family=Open+Sans:400,800,300,600,400italic,300italic' rel='stylesheet' type='text/css'>
<!--[if lte IE 8]><script language="javascript" type="text/javascript" src="../../flot/excanvas.min.js"></script><![endif]-->
<script language="javascript" type="text/javascript" src="../../flot/jquery.js"></script>
<script language="javascript" type="text/javascript" src="../../flot/jquery.flot.js"></script>
<script language="javascript" type="text/javascript" src="../../flot/jquery.flot.errorbars.js"></script>
<script language="javascript" type="text/javascript" src="../../flot/jquery.flot.selection.js"></script>
<script language="javascript" type="text/javascript" src="../../flot/jquery.flot.navigate.js"></script>
<script language="javascript" type="text/javascript">
  function loadIframe(obj) {
    document.getElementById('div_loadinggif').style.display = "none";
    document.getElementById('div_loadinggif').style.visibility = "hidden";
    obj.style.height = 1.2*obj.contentWindow.document.body.scrollHeight + 'px';
  }
</script>
<script language="javascript" type="text/javascript">
  function collapsetd() {
    if (window.innerWidth < 1640) {
        document.getElementById('td_collapsable1').style.width = '0px';
        document.getElementById('td_collapsable2').style.width = '0px';
    } else {
        document.getElementById('td_collapsable1').style.width = '20px';
        document.getElementById('td_collapsable2').style.width = '200px';
    }
  }
</script>''' % base_url

print '''<script> $(function() {$("#includedContent").load("./schedule.cgi?targid=%s"); }); </script>''' % (_targid)
print ''' </head>'''

print ''''<body topmargin="0" marginheight="0" leftmargin="0" marginwidth="0" rightmargin="0" bottommargin="0" bgcolor="#ececec" link="black" vlink="black" alink="black"
onload="collapsetd();" onresize="collapsetd();"> '''
try:
    url=os.environ["REQUEST_URI"] 
except:
    url='http://deneb.st-and.ac.uk/agnecho/cgi-bin'

print '''
<div id="container" style="width:1300px">
<div align="center"  leftmargin="10" id="header" style="background-color:#FFA500;">
<h1 style="margin-bottom:0;"> AGN AGENT </h1> '''
print '''<span style="font-family: 'Open Sans', sans-serif; font-weight:300; font-size:16"> user: &nbsp; %s</span>''' % (_user)
print '''</div>'''

print '''<div align="center"   id="menu" style="background-color:#FFD700;width:150px;float:left; position:fixed;">
<b>Menu</b>'''
#print '<br></br>'
print searchobj1()
#print '<br></br>'
print searchobj2()
#print '<br></br>'
print agnkey.agndefin.addnewobject('agnkeyview.cgi')
print '<br></br>'
print '<a href="agnkeymain.cgi"> list of objects </a>'
print '<br></br>'
print '<a href="agncatalogue.cgi">  catalogue </a>'
print '<br></br>'
print '<a href="agnpermission.cgi"> permission  </a>'
print '<br></br>'
print '<a href="agnupload.cgi"> upload spectrum  </a>'
print '<br></br>'
print '<br></br>'
print '<a href="'+url+'#rawspectra"> raw spectra</a>'
print '<br></br>'
print '<a href="'+url+'#notes"> notes</a>'
print '<br></br>'
print '<a href="'+url+'#triggers"> trigger telescopes </a>'
print '<br></br>'
print '<a href="'+url+'#photometry"> photometry </a>'
print '<br></br>'
print '<a href="'+url+'#lightcurves" align="left"> light curves </a>'
print '''</div>'''

print '''<div  align="center"  id="content" style="background-color:FFFFEF; margin-left:150px; leftmargin="150px"; width:1150px;">'''
#print '<span style="margin-left:150px"></span>'

commandg=["select groupname from userstab where user='"+str(_user)+"'"]
gg=agnkey.agnsqldef.query(commandg)
if len(gg)==0:
    print '<h3> sorry user unknown, you dont have access to this page <h3>'
    print '''</div>'''
    print '</body>'
    print '</html>'
    sys.exit()

########################################################################

if _targid:
    num=int(gg[0]['groupname'])

########################    expand all groups user is part of  and allow user to see all objects belonging to each group
    ele=expandpermissions2(num)
    gg="( "
    for ii in ele:   gg=gg+" ((groupname & "+str(ii)+")="+str(ii)+") or "
    gg=gg[:-3]+')'
########################
    commandpermission=['select * from permissionlog where targid='+str(_targid)+' and '+str(gg)]

#    commandpermission=['select * from permissionlog where targid='+str(_targid)+' and (groupname & '+str(num)+')='+str(num)+'']
    listaper=agnkey.agnsqldef.query(commandpermission)
    if not listaper:
        print gg
        print '<h3> sorry you do not have access to this object <h3>'
        print '</body></html>'
        sys.exit()
#
######################################################################

if _targid:
    command9=["select * from dataredulco where targid="+str(_targid)]
    lista9=agnkey.agnsqldef.query(command9)
else:
    if SN_RA and SN_DEC:       # raw data
        distance=1
        command9=["set @sc = pi()/180"," set @ra = "+str(SN_RA),"set @dec = "+str(SN_DEC),"set @distance = "+str(distance),"SELECT *,abs(2*asin( sqrt( sin((a.dec0-@dec)*@sc/2)*sin((a.dec0-@dec)*@sc/2) + cos(a.dec0*@sc)*cos(@dec*@sc)*sin((a.ra0-@ra)*@sc/2)*sin((a.ra0-@ra)*@sc/2.0) )))*180/pi() as hsine FROM dataredulco as a HAVING hsine<@distance order by a.dateobs desc"]
        lista9=agnkey.agnsqldef.query(command9)
    else:
        if SN0:
            command9=["select * from dataredulco as a where a.dateobs <="+"'"+d+"' and a.dateobs >="+"'20120909' and a.objname like '%"+SN0+"%' order by a.dateobs desc "]
            lista9=agnkey.agnsqldef.query(command9)
        else:
            lista9=''
if len(lista9):
    ll9={}
    for jj in lista9[0].keys(): ll9[jj]=[]
    for i in range(0,len(lista9)):
        for jj in lista9[0].keys(): ll9[jj].append(lista9[i][jj])
else: ll9=''

#######################################################################
if _targid:
    command=["select * from dataredulco as a where a.targid="+str(_targid)+" order by a.dateobs desc"]
    lista=agnkey.agnsqldef.query(command)
else:
    if SN_RA and SN_DEC:       # photometry 
        distance=1
        command=["set @sc = pi()/180"," set @ra = "+str(SN_RA),"set @dec = "+str(SN_DEC),"set @distance = "+str(distance),"SELECT *,abs(2*asin( sqrt( sin((a.dec0-@dec)*@sc/2)*sin((a.dec0-@dec)*@sc/2) + cos(a.dec0*@sc)*cos(@dec*@sc)*sin((a.ra0-@ra)*@sc/2)*sin((a.ra0-@ra)*@sc/2.0) )))*180/pi() as hsine FROM dataredulco as a HAVING hsine<@distance order by a.dateobs desc"]
        lista=agnkey.agnsqldef.query(command)
    elif  SN0:
        command=["select * from dataredulco as a where a.dateobs <="+"'"+d+"' and a.dateobs >="+"'20120909' and a.objname like '%"+SN0+"%'  order by a.dateobs desc "]
        lista=agnkey.agnsqldef.query(command)
    else:
        lista=''
if len(lista):
    ll0={}
    for jj in lista[0].keys(): ll0[jj]=[]
    for i in range(0,len(lista)):
        for jj in lista[0].keys(): ll0[jj].append(lista[i][jj])
    wwsloan=asarray([i for i in range(0,len(ll0['filter'])) if (ll0['filter'][i] in ['gp','rp','ip','zs','up','SDSS-G','SDSS-R','SDSS-I','Pan-Starrs-Z'])])
    wwlandolt=asarray([i for i in range(0,len(ll0['filter'])) if (ll0['filter'][i] in ['U','B','V','R','I','Bessell-B','Bessell-V','Bessell-R','Bessell-I'])])
    wwimages=asarray([j for j in range(len(ll0['jd'])) if (float(_JDn)-ll0['jd'][j]< 7)])
else:
    wwsloan=[]
    wwlandolt=[]
    wwimages=[]

#############################  png files
#print agnkey.util.workingdirectory,ll0['namefile'][0],ll0['wdirectory'][0],base_url,hostname
#print re.sub(agnkey.util.workingdirectory,'',ll0['wdirectory'][0])+re.sub('.fits','.png',ll0['namefile'][0])
if len(wwimages)>0:
   listpng=array(['../../AGNKEY/'+re.sub(agnkey.util.workingdirectory,'',k)+re.sub('.fits','.png',v) for k,v in  zip(ll0['wdirectory'],ll0['namefile'])])[wwimages]
else:  listpng=[]

if len(lista):
    llimage=['wget --user='+str(_user)+' --password=xxxx '+'http://dark.physics.ucdavis.edu/~valenti/AGNKEY/'+re.sub(agnkey.util.workingdirectory,'',k)+v for k,v in  zip(ll0['wdirectory'],ll0['namefile'])]
else: llimage=[]

webp=''
if ll9:
    riga={}
    coordinate={}
    for i in range(0,len(ll9['objname'])):
        obj=ll9['objname'][i]
        dat=ll9['dateobs'][i]
        tel=ll9['telescope'][i]
        filt=ll9['filter'][i]
        if obj not in riga:
            riga[obj]={}
            coordinate[obj]=str(ll9['ra0'][i])+' '+str(ll9['dec0'][i])
        if dat not in riga[obj]:   riga[obj][dat]={}
        if tel not in riga[obj][dat]: 
            riga[obj][dat][tel]={}
        if filt not in  riga[obj][dat][tel]:
            riga[obj][dat][tel][filt]=[]
            #riga[obj][dat][tel]['exptime']=[]
        
        riga[obj][dat][tel][filt].append(str(int(ll9['exptime'][i])))
        #riga[obj][dat][tel]['exptime'].append(ll9['exptime'][i])

#    riga[obj][dat][tel]=list(set(riga[obj][dat][tel]))
    for obj in riga.keys():
        fff=sort(list(riga[obj].keys()))
        for dat in fff:
            for tel in riga[obj][dat].keys():
                dd=''
                mm=''
                for filt in riga[obj][dat][tel].keys():
                    dd=dd+filt+'-'
                    
                    for jj in set(riga[obj][dat][tel][filt]):
                         mm=mm+str(jj)+' '
                    mm=mm[:-1]+'-'
                dd=dd[:-1]
                mm=mm[:-1]
#                    for kk in list((riga[obj][dat][tel][filt])): 
#                for jj in list((riga[obj][dat][tel]['exptime'])): mm=mm+str(int(jj))+' '
                webp=webp+'<p align="left">'+' &nbsp; &nbsp; '+str(obj)+' &nbsp; &nbsp; '+str(coordinate[obj])+' &nbsp;  &nbsp;   '+str(dat)+' &nbsp;  &nbsp;   '+str(tel)+' &nbsp;   &nbsp;  '+str(dd)+' &nbsp;   &nbsp;  '+str(mm)+'</p>'

##########################################################################################
if not SN_RA and not SN_DEC:
    if len(ll9)>0:
        SN_RA,SN_DEC=float(ll9['ra0'][0]),float(ll9['dec0'][0])
################################################33
#  spectra  archive
if _targid:
    command1e=["select * from dataspectraexternal as a where targid="+str(_targid)+" order by a.dateobs desc "]
    lista33e=agnkey.agnsqldef.query(command1e)
else:
    if SN_RA and SN_DEC:       # spectra
        distance=1
        command1e=["set @sc = pi()/180"," set @ra = "+str(SN_RA),"set @dec = "+str(SN_DEC),"set @distance = "+str(distance),"SELECT *,abs(2*asin( sqrt( sin((a.dec0-@dec)*@sc/2)*sin((a.dec0-@dec)*@sc/2) + cos(a.dec0*@sc)*cos(@dec*@sc)*sin((a.ra0-@ra)*@sc/2)*sin((a.ra0-@ra)*@sc/2.0) )))*180/pi() as hsine FROM dataspectraexternal HAVING hsine<@distance order by a.dateobs desc"]
        lista33e=agnkey.agnsqldef.query(command1e)
    else:
        if SN0:
            command1e=["select * from dataspectraexternal as a where a.dateobs <="+"'"+d+"' and a.dateobs >="+"'20120909' and a.objname like '%"+SN0+"%' order by a.dateobs desc "]
            lista33e=agnkey.agnsqldef.query(command1e)
        else:
            lista33e=''

ll22e={}
if len(lista33e):
    for jj in lista33e[0].keys(): ll22e[jj]=[]
    for i in range(0,len(lista33e)):
        for jj in lista33e[0].keys(): ll22e[jj].append(lista33e[i][jj])

if len(ll22e)==0:    ll22e=''

webs=''


if ll22e:
   for i in range(0,len(ll22e['objname'])):
      _object0=ll22e['objname'][i]
      name=ll22e['namefile'][i]
      if location=='deneb':
          directory=re.sub(agnkey.util.workingdirectory,'http://'+base_url+'/AGNKEY/',ll22e['directory'][i])
          directory2='../AGNKEY/'+re.sub('/home/cv21/AGNKEY_www/AGNKEY/','',ll22e['directory'][i])
      elif location=='dark':
          directory=re.sub(agnkey.util.workingdirectory,'http://dark.physics.ucdavis.edu/~valenti/AGNKEY/',ll22e['directory'][i])
          directory2='../../AGNKEY/'+re.sub(agnkey.util.workingdirectory,'',ll22e['directory'][i])
      else:
          directory='../AGNKEY/'+re.sub('/Users/svalenti/redu2/AGNKEY/','',ll22e['directory'][i])
          directory2='../AGNKEY/'+re.sub('/Users/svalenti/redu2/AGNKEY/','',ll22e['directory'][i])

      date=ll22e['dateobs'][i]
      fspec=fastspec(name,name,directory)
      fitsfile='<a href="'+directory2+ll22e['namefile'][i]+'"> fitsfile</a>'
      ascifil=ascifile(name,name,directory)
      if _user in agnkey.util.readpass['superusers']:
         deletespectrum=agnkey.agndefin.delspectrum(SN0,SN_RA,SN_DEC,_targid,ll22e['id'][i],ll22e['namefile'][i],_user,'agnkeyview.cgi')
      else:
         deletespectrum=''
      webs=webs+'<tr  style="margin:0; padding:0;">'+tdopen+str(name)+tdclose+tdopen+str(date)+tdclose+\
            tdopen+str(fspec)+tdclose+tdopen+str(ascifil)+tdclose+tdopen+str(deletespectrum)+tdclose+tdopen+str(fitsfile)+tdclose+'</tr>'      

###############################################################################################################################
#  FLOYDS   raw

if _targid:
    command1=["select * from datarawfloyds as a where targid="+str(_targid)+" and a.type='SPECTRUM' order by a.dateobs desc "]
    lista3=agnkey.agnsqldef.query(command1)
else:
    if SN_RA and SN_DEC:       # spectra
        distance=1
        command1=["set @sc = pi()/180"," set @ra = "+str(SN_RA),"set @dec = "+str(SN_DEC),"set @distance = "+str(distance),"SELECT *,abs(2*asin( sqrt( sin((a.dec0-@dec)*@sc/2)*sin((a.dec0-@dec)*@sc/2) + cos(a.dec0*@sc)*cos(@dec*@sc)*sin((a.ra0-@ra)*@sc/2)*sin((a.ra0-@ra)*@sc/2.0) )))*180/pi() as hsine FROM datarawfloyds as a where a.type='SPECTRUM' HAVING hsine<@distance order by a.dateobs desc"]
        lista3=agnkey.agnsqldef.query(command1)
    else:
        if SN0:
            command1=["select * from datarawfloyds as a where a.dateobs <="+"'"+d+"' and a.dateobs >="+"'20120909' and a.type='SPECTRUM' and a.objname like '%"+SN0+"%' order by a.dateobs desc "]
            lista3=agnkey.agnsqldef.query(command1)
        else:
            lista3=''

if len(lista3):
    ll2={}
    for jj in lista3[0].keys(): ll2[jj]=[]
    for i in range(0,len(lista3)):
        for jj in lista3[0].keys(): ll2[jj].append(lista3[i][jj])
else:
    ll2=''

webs2=''
if ll2:
    riga={}
    ddat={}
    coordinate={}
    note={}
    imm={}
    for i in range(0,len(ll2['objname'])):
        obj=ll2['objname'][i]
        tel=ll2['telescope'][i]
        jjd=ll2['jd'][i]
        ddat[jjd]=ll2['dateobs'][i]
        note[jjd]=ll2['note'][i]
        imm[jjd]='http://'+base_url+'/AGNKEY/'+re.sub(agnkey.util.workingdirectory,'',ll2['directory'][i])+'/'+ll2['namefile'][i]

        if jjd not in riga:
            riga[jjd]={}
            coordinate[jjd]=str(ll2['ra0'][i])+' '+str(ll2['dec0'][i])
        if obj not in riga[jjd]:   riga[jjd][obj]={}
        if tel not in riga[jjd][obj]: riga[jjd][obj][tel]=[]
        riga[jjd][obj][tel].append(ll2['exptime'][i])
    riga[jjd][obj][tel]=list(set(riga[jjd][obj][tel]))

    for jjd in sort(riga.keys()):
      #if os.path.isfile(str(re.sub('.fits','.png',imm[jjd]))):
      nnn= str(re.sub('.fits','.png',imm[jjd]))
      jjj=agnkey.agndefin.grafico1(nnn,'25','150')+'</p>'
      #else:
      #    jjj='</p>'
      fff=sort(list(riga[jjd].keys()))
      for obj in fff:
            for tel in riga[jjd][obj].keys():
                dd=''
                for kk in list(set(riga[jjd][obj][tel])): dd=dd+str(kk)+' '
                webs2=webs2+'<p style="margin:0; padding:0;">'+str(obj)+' &nbsp; &nbsp; '+str(coordinate[jjd])+' &nbsp;  &nbsp;   '+str(ddat[jjd])+' &nbsp;  &nbsp;   '+str(tel)+' &nbsp;   &nbsp;  '+str(note[jjd])+' &nbsp;   &nbsp;  '+str(dd)+' &nbsp;   &nbsp;'+jjj
                #+grafico1(jjj,'50','150')+'</p>'
                #str(imm[jjd])+'</p>'
########################################################################3
     
log1=[]
ss,dd=[],[]
bb=''
if _targid:
    lista2=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn,'obslog','targid',str(_targid),'windowstart,windowend')
    if len(lista2)>0:
        log1={}
        for jj in lista2[0].keys(): log1[jj]=[]
        for i in range(0,len(lista2)):
            for jj in lista2[0].keys(): log1[jj].append(lista2[i][jj])
        bb=[log1['windowstart'],log1['windowend']]

if len(wwsloan)>0:
    ll1={}
    for key in ll0:
        ll1[key]=list(array(ll0[key])[wwsloan])
    html=run_getmag(ll1,'sloan','../tmp/xxx',1e-10,'ph1',1,bb)
    html=run_getmag(ll1,'sloan','../tmp/'+SN0+'_sloan1_'+_user,1e-10,'ph1')
    if html:
       nameimage=html
    else:
       nameimage=''
    graph1=agnkey.agndefin.grafico(nameimage,'30','30')
else: graph1=agnkey.agndefin.grafico('')


if len(wwsloan)>0:
    ll1={}
    for key in ll0:
        ll1[key]=list(array(ll0[key])[wwsloan])        
    html=run_getmag(ll1,'sloan','../tmp/'+SN0+'_sloan2_'+_user,1e-10,'ph2',1,bb)
    if html:
       nameimage=html
    else:
       nameimage=''
    graph11=agnkey.agndefin.grafico(nameimage)
else: graph11=agnkey.agndefin.grafico('')


if len(wwsloan)>0:
    ll2={}
    for key in ll0:
        ll2[key]=list(array(ll0[key])[wwsloan])
    html=run_getmag(ll2,'sloan','../tmp/'+SN0+'_sloan3_'+_user,1e-10,'ph3',1,bb)
    if html:
       nameimage=html
    else:
       nameimage=''
    graph2=agnkey.agndefin.grafico(nameimage)
else: graph2=agnkey.agndefin.grafico('')

if len(wwsloan)>0:
    ll2={}
    for key in ll0:
        ll2[key]=list(array(ll0[key])[wwsloan])
    html=run_getmag(ll2,'sloan','../tmp/'+SN0+'_sloan0_'+_user,1e-10,'fit',1,bb)
    if html:
       nameimage=html
    else:
       nameimage=''
    graph22=agnkey.agndefin.grafico(nameimage)
else: graph22=agnkey.agndefin.grafico('')


##################################
if _targid:
    command1=["select * from noteobjects where targid="+str(_targid)+" order by id "]
    lista44=agnkey.agnsqldef.query(command1)
else: lista44=''

note=''
if len(lista44):
   for ii in lista44:
      note=note+str(ii['datenote'])+'&#09;'+'&bull;'+'&#09;'+str(ii['user'])+'&#09;'+'&bull;'+'&#09;'+str(ii['note'])+agnkey.agndefin.delfromdb(SN0,SN_RA,SN_DEC,_targid,ii,_user,'agnkeyview.cgi')

#################################################

pngfiles=''
if len(listpng)>0:
   for img in listpng:
      graph=agnkey.agndefin.grafico1(img)
      pngfiles=pngfiles+'<tr>'+tdopen+graph+tdclose+'</tr>'

if (SN_RA and SN_DEC):
    html2=agnkey.agndefin.visibility(SN_RA,SN_DEC,True,'500','300')
    graph10=agnkey.agndefin.grafico(html2,'100','100')
else:
  graph10=''
#############################################################      
aka=''
if _targid:
  commandr=["select name from recobjects where targid="+str(_targid)]
  listar=agnkey.agnsqldef.query(commandr)
  if len(listar)>1:
    for hh in listar:
      aka=aka+str(hh['name'])+' <br></br>'

if _targid:
  commandr1=["select * from lsc_sn_pos where targid="+str(_targid)]
  listar1=agnkey.agnsqldef.query(commandr1)
else:
  listar1=''

print '<a id="info"></a>'

tit1=tit('Supernova','spectrum','epoch','plot','note','refer.')
print """<table border="0" style='table-layout:fixed'   class='fixed'  height='10%' cellspacing='0' cellpadding='0' width='60%' >"""
print '<tr align="center" BGCOLOR="#CCFF66"> <td width=100 > <h3> '+str('AGN NAME')+'  </h3></td><td width=100> <h3> Redshift </h3></td>'+\
      '<td width=100> <h3> RA </h3></td>'+\
      '<td width=100> <h3> DEC  </h3></td>'+\
      '<td width=100> <h3>type </h3></td>'+\
      ' <td  align="center" width=100 > <h3>     aka </h3></td> </tr>'
if listar1:
  if _user in agnkey.util.readpass['superusers']:
    print '<tr BGCOLOR="#CCFF66" align="center"><td > <h3>'+str(SN0)+ '</h3> </td> <td width=300> <h3>'+str(listar1[0]['redshift'])+'</h3> </td>'+\
          ' <td align="center" width=100><h3>'+str(listar1[0]['ra_sn'])[0:9]+'</h3></td>'+\
          ' <td align="center" width=100><h3>'+str(listar1[0]['dec_sn'])[0:9]+'</h3></td>'+\
          ' <td align="center" width=100><h3>'+str(listar1[0]['objtype'])+'</h3></td>'+\
          ' <td align="center" width=100> <h3> '+aka+' </h3> </td></tr>'
    print '<tr BGCOLOR="#CCFF66" align="center"><td >'+'</td> <td width=300>'+agnkey.agndefin.objectinfo(listar1[0],_user,'redshift','agnkeyview.cgi')+\
          '</td> <td width=300>'+agnkey.agndefin.objectinfo(listar1[0],_user,'ra_sn','agnkeyview.cgi')+\
          '</td> <td width=300>'+agnkey.agndefin.objectinfo(listar1[0],_user,'dec_sn','agnkeyview.cgi')+\
          '</td> <td width=300>'+agnkey.agndefin.objectinfo(listar1[0],_user,'objtype','agnkeyview.cgi')+\
          '</td> <td width=300>'+agnkey.agndefin.recinfo(listar1[0],_user,'agnkeyview.cgi')+'</td>'+\
          '</tr>'
  else:
    print '<tr BGCOLOR="#CCFF66" align="center"><td > <h3>'+str(SN0)+ '</h3> </td> <td width=100> <h3>'+str(listar1[0]['redshift'])+'</h3> </td>'+\
          ' <td align="center" width=100><h3>'+str(listar1[0]['ra_sn'])[0:9]+'</h3></td>'+\
          ' <td align="center" width=100><h3>'+str(listar1[0]['dec_sn'])[0:9]+'</h3></td>'+\
          ' <td width=100><h3>'+str(listar1[0]['objtype'])+'</h3></td>'+\
          ' <td width=100 ><h3>'+str(_user)+'</h3></td width=300> <td> <h3> '+aka+' </h3> </td></tr>'   
print """</table>"""

#################################################################################
##############################
print '</td>'+'<td width=50>'
print graph10
print '</td>'
print '</td>'+'<td width=50>'
if listar1:
    print '<td width="200">'+'''<IMG SRC="http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx?ra='''+str(listar1[0]['ra_sn'])+'''&dec='''+str(listar1[0]['dec_sn'])+'''&scale=0.79224   &width=350&height=350&opt=GST&query=SR(10,20)">'''+'</td>'
print '</td>'+'</tr>'
print """</table>"""
#print '<br></br>'

print '<a id="notes"></a>'
print """<table class='fixed' style='table-layout:fixed'  border='0' BGCOLOR='#CCFFFF'  height='10%' cellspacing='0' cellpadding='0' width='800' >"""
print " <td align='center' width='700'> <h3> notes </h3> <td>"""
if note:   print "<tr><td width='800'>"+note+"</td></tr>"
else:      print "<tr><td width='800%'></td></tr>"
print """</table>"""
print '<br></br>'
_note=agnkey.agndefin.addnote(_targid,SN0,SN_RA,SN_DEC,_user,'agnkeyview.cgi')
print _note

if page: print page

print '<br></br>'
if pngfiles:
  print pngfiles
print '<br></br>'
if webs:
  print '<br> ____________________________________________________________________________________ </br>'
  print '<h4>  SPECTRA </h4>'
  print tit('file','date','plot','asci','note','refer')
  print webs
  print tit2
print '<br></br>'
if webs2:
  print '<a id="rawspectra"></a>'
  print '<br> ____________________________________________________________________________________ </br>'
  print '<h4>  SPECTRA (RAW DATA) </h4>'
  print webs2
  print '<br></br>'
if webp:
  print '<a id="photometry"></a>'
  print '<br> ____________________________________________________________________________________ </br>'
  print '<h4>  PHOTOMETRY </h4>'
  print webp
  print '<br></br>'
  line=''
  for ll in llimage: line=line+ll+' \n '
#  print '<form action="updatetable.py" enctype="multipart/form-data" method="post">'
  print '<form action="agnupdatetable.py" enctype="multipart/form-data" method="post">'
  print '<p>enter password to download raw data: <textarea rows="1" cols="20" wrap="physical" name="note"></textarea>'
  print '<input type="hidden" name="type" value="download">'
  print '<input type="hidden" name="targid" value="'+str(_targid)+'">'
  print '<input type="hidden" name="vector" value="'+str(line)+'">'
  print '<input type="submit" value="Send"></p>'
  print '</form>'

print '<a id="triggers"></a>'
#if _user in agnkey.util.superusers and _targid:
print '<br> ____________________________________________________________________________________ </br>'
print agnkey.agndefin.trigger(str(SN0),str(SN_RA),str(SN_DEC),str(_targid),'agnkeyview.cgi',{},agnkey.util.readpass['proposal'])
print '<br> ____________________________________________________________________________________ </br>'
print agnkey.agndefin.triggerfloyds(str(SN0),str(SN_RA),str(SN_DEC),str(_targid),'agnkeyview.cgi',{},agnkey.util.readpass['proposal'])
print '<br> ____________________________________________________________________________________ </br>'
print '<br></br>'

print '<a id="lightcurves"></a>'
print """<table border='0'> """  #align='center'  height='10%' cellspacing='0' cellpadding='0' width=400 >
print '<tr align="center" > <td> psf mag  ',agnkey.agndefin.plot_phot(agnkey.agnsqldef.conn,_targid, width=400, height=250, plottype='flot',magtype='mag'),\
    '</td><td> aperture mag 1 ', agnkey.agndefin.plot_phot(agnkey.agnsqldef.conn,_targid, width=400, height=250, plottype='flot',magtype='appmagap1'),'</td> </tr>'
print '<tr align="center" ><td>  aperture mag2 ',agnkey.agndefin.plot_phot(agnkey.agnsqldef.conn,_targid, width=400, height=250, plottype='flot',magtype='appmagap2'),\
    ' </td><td> aperture mag 3', agnkey.agndefin.plot_phot(agnkey.agnsqldef.conn,_targid, width=400, height=250, plottype='flot',magtype='appmagap3'),'</td></tr>'
print '</table>'

print '<div id="includedContent"></div></div>'

print '</body></html>'
