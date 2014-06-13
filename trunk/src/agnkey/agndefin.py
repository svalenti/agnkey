#!/usr/bin/env python
import sys,os,cgi,string,glob

#sys.path.append( '/Users/svalenti/Sites/lib/python2.7/site-packages')
##!/opt/epd/bin/python
#import sys,os,cgi,string,glob
#sys.path.append('/home/supernova/lib/python2.6/site-packages')

import ephem, datetime
import numpy as np
from matplotlib.dates import DateFormatter, MinuteLocator
from matplotlib.font_manager import FontProperties
import matplotlib.dates as mdates
import StringIO
import base64
import agnkey

#os.environ['HOME']='../tmp/'

####################################################################################
#    sss='<form style="background-color:orange" action="http://secure.lcogt.net/user/supernova/dev/cgi-bin/updatetable.py" enctype="multipart/form-data" method="post">'+\
def trigger(SN0,SN_RA,SN_DEC,_targid,_form,observations={},proposal=agnkey.util.readpass['proposal']):
    sss='<form style="background-color:orange" action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<p> <h3 style="background-color:orange"> TRIGER NEW OBSERVATION (use carefully)  <input type="submit" value="Send"> </h3></p>'+\
        '<input type="hidden" name="sn_name" value='+str(SN0)+'>'+\
        '<input type="hidden" name="SN_RA" value="'+str(SN_RA)+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(SN_DEC)+'">'+\
        '<input type="hidden" name="targid" value="'+str(_targid)+'">'
    for key in observations:
        if 'xxx' in key:
            sss=sss+'<input type="hidden" name="'+str(key)+'" value="'+str(observations[key])+'">'        
    sss=sss+'<input type="hidden" name="type" value="trigger">'+\
         '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
         '<table>'+\
         '<tr heigh=10><td> U </td><td> B </td><td> V </td><td> R </td><td> I </td><td> u </td><td> g </td><td> r </td><td> i </td><td> z </td></tr><tr>'
    for i in 'UBVRIugriz':
        if i in ['B','V','g','r','i']:
            sss=sss+'<td heigh=10> <input type="checkbox" name="'+str(i)+'" value="'+str(i)+'" checked></td>'
        else:
            sss=sss+'<td> <input type="checkbox" name="'+str(i)+'" value="'+str(i)+'" ></td>'
    sss=sss+'<td heigh=10 > select filters  </td></tr><tr>'
    for i in 'UBVRIugriz':
        sss=sss+ '<td heigh=10><select name="n'+str(i)+'">'
        sss=sss+ '<option value="2"> 2</option>  <option value="1">1</option> <option value="3">3</option><option value="5">5</option> <option value="10">10</option>'
        sss=sss+ '</select></td>'
    sss=sss+ '<td> number of exposure </td></tr><tr>'
    for i in 'UBVRIugriz':
        sss=sss+ '<td width=10><div class="styled-select"><select name="exp'+str(i)+'"  width:100px;>'+\
             '<option  width=10 value="120"> 120</option>'+\
             '<option value="15">15</option>'+\
             '<option value="30">30</option>'+\
             '<option value="45">45</option>'+\
             '<option value="60">60</option>'+\
             '<option value="90">90</option>'+\
             '<option value="120">120</option>'+\
             '<option value="150">150</option>'+\
             '<option value="180">180</option>'+\
             '<option value="200">200</option>'+\
             '<option value="240">240</option>'+\
             '<option value="300">300</option>'+\
             '<option value="360">360</option>'+\
             '<option value="400">400</option>'+\
             '<option value="600">600</option>'
        sss=sss+ '</select></div></td>'
    sss=sss+ '<td>exposure time </td>'+\
         '</tr>'+\
         '</table>'+\
         '<table>'+\
         '<tr><td> site: <select name="site">'+\
         '<option value="any"> any</option>  <option value="lsc">lsc</option>'+\
         '<option value="elp">elp</option>   <option value="coj">coj</option> <option value="cpt">cpt</option>'+\
         '</select></td></tr>'+\
         '<tr><td> number of triggers: </a> <select name="ntriggers">'+\
         '<option value="1"> 1 in the next 24h </option>  <option value="2"> 2 in the next 48h </option>'+\
         '<option value="3"> 2 in the next 24h</option>   <option value="4"> 4 in the next 48h </option>'+\
         '<option value="5"> 1 in the next 6 days</option>   <option value="6"> 2 in the next 6 days </option>'+\
         '<option value="7"> 3 in the next 6 days</option>   <option value="8"> 6 in the next 6 days </option>'+\
         '<option value="9"> 1 observation in the next 8h </option>   <option value="10">  3 observations in the next 12h </option>'+\
         '<option value="13"> 24 observation in the next 24 days </option>   <option value="14">  12 observations in the next 24 days </option>'+\
         '</select></td></tr>'+\
         '<tr><td> airmass limit: </a> <select name="airmass">'+\
         '<option value=2> 2 </option> '+\
         '<option value=2.5> 2.5 </option> '+\
         ' <option value=1.2> 1.2 </option>'+\
         '<option value=1.5> 1.5 </option>'+\
         ' <option value=3> 3 </option>'+\
         ' <option value=4> 4 </option>'+\
         '</select></td></tr>'+\
         '<tr><td> proposal: <select name="proposal">'
    for kk in proposal:
             sss=sss+'<option value="'+kk+'"> '+kk+' </option> '
    sss=sss+'</select></td></tr>'+\
         '<tr><td> instrument  <select name="instrument">'+\
         '<option value="sbig"> sbig </option>  <option value="sinistro">sinistro</option>'+\
         '<option value="spectral">spectral</option>'+\
         '<option value="ONEOF">ONEOF</option>'+\
         '</table>'+\
         '</form>'
    return sss

######################################################################################################
def triggerfloyds(SN0,SN_RA,SN_DEC,_targetid,_form,observations={},proposal=agnkey.util.readpass['proposal']):
    sss='<form style="background-color:#D8D8D8 " action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<p> <h3 style="background-color:#D8D8D8 "> TRIGER NEW OBSERVATION WITH FLOYDS(use carefully)  <input type="submit" value="Send"> </h3></p>'+\
        '<input type="hidden" name="sn_name" value='+str(SN0)+'>'+\
        '<input type="hidden" name="SN_RA" value="'+str(SN_RA)+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(SN_DEC)+'">'+\
        '<input type="hidden" name="targid" value="'+str(_targetid)+'">'
    for key in observations:
        if 'xxx' in key:
            sss=sss+'<input type="hidden" name="'+str(key)+'" value="'+str(observations[key])+'">'        
    sss=sss+'<input type="hidden" name="type" value="triggerfloyds">'+\
         '<input type="hidden" name="outputformat" value="'+str(_form)+'">'
    sss=sss+ '<td width=10> <div class="styled-select">exposure time: <select name="expfloyds'+'"  width:100px;>'+\
         '<option  width=10 value="300"> 300</option>'+\
         '<option value="600">600</option>'+\
         '<option value="900">900</option>'+\
         '<option value="1200">1200</option>'+\
         '<option value="1500">1500</option>'+\
         '<option value="1800">1800</option>'+\
         '<option value="2700">2700</option>'+\
         '<option value="3600">3600</option>'+\
         '<option value="60">60</option>'+\
         '<option value="30">30</option>'
    sss=sss+ '</select></div></td>'
    sss=sss+'</tr>'+\
         '</table>'+\
         '<table>'+\
         '<tr><td> site: <select name="site">'+\
         '<option value="any"> any</option>  <option value="ogg">FTN</option>'+\
         '<option value="coj">FTS</option>'+\
         '</select></td></tr>'+\
         '<tr><td> number of triggers: </a> <select name="ntriggers">'+\
         '<option value="1"> 1 in the next 24h </option>'+\
         '<option value="2"> 2 in the next 48h </option>'+\
         '<option value="3"> 2 in the next 24h</option> '+\
         '<option value="4"> 4 in the next 48h </option>'+\
         '<option value="5"> 1 in the next 6 days</option>'+\
         '<option value="6"> 2 in the next 6 days </option>'+\
         '<option value="7"> 3 in the next 6 days</option>'+\
         '<option value="8"> 6 in the next 6 days </option>'+\
         '<option value="9"> 1 observation in the next 8h </option>'+\
         '<option value="10"> 3 observations in the next 12h </option>'+\
         '<option value="11"> 1 observations in the next 1h </option>'+\
         '<option value="12"> 1 observations in the next 2h </option>'+\
         '</select></td></tr>'+\
         '<tr><td> airmass limit: </a> <select name="airmass">'+\
         '<option value=2> 2 </option>'+\
         '<option value=1.2> 1.2 </option>'+\
         '<option value=1.5> 1.5 </option>'+\
         '<option value=2.5> 2.5 </option>'+\
         ' <option value=3> 3 </option>'+\
         ' <option value=4> 4 </option>'+\
         '</select></td></tr>'+\
         '<tr><td> proposal: <select name="proposal">'
    for kk in proposal:
             sss=sss+'<option value="'+kk+'"> '+kk+' </option> '
    sss=sss+'</select></td></tr>'+\
         '</table>'+\
         '</form>'
    return sss         

################################################################################
def visibility(_ra0,_dec0,_plot=True,xx='300',yy='200'):
#def visibility(_ra0,_dec0,_plot=True):
  from datetime import datetime, timedelta
  import matplotlib
  from matplotlib.dates import DateFormatter, MinuteLocator
  import string,ephem,datetime,sys
  import numpy as np
  import matplotlib.dates as mdates
  from matplotlib.ticker import MultipleLocator 
  #########################################################################
  site_ll = {
      'tst' : {'latitude' : '+34.433161', 'longitude' : '-119.8631' , 'color': 'k'},
      'sqa' : {'latitude' : '+34.6924533','longitude' : '-120.0422217' , 'color': 'c'},
      'ogg' : {'latitude' : '+20.706900', 'longitude' : '-156.25800', 'color': '#3366dd'},
      'bpl' : {'latitude' : '+34.433161', 'longitude' : '-119.8631',  'DOMA' : '01.08', 'color': 'g'},
      'elp' : {'latitude' : '+30.679833', 'longitude' : '-104.015173','DOMA' : '03.10','color': '#700000'},
      'lsc' : {'latitude' : '-30.167367', 'longitude' : '-70.8049',   'DOMA' : '05.02', 'DOMB' : '10.03', 'DOMC' : '11.04', 'color': 'm'},
      'cpt' : {'latitude' : '-32.3826',   'longitude' : '+20.8124',   'DOMA' : '06.05', 'DOMB' : '07.06', 'DOMC' : '08.10', 'color': '#004f00'},
      'coj' : {'latitude' : '-31.2733',   'longitude' : '+149.438',   'DOMA' : '14.12', 'DOMB' : '02.13', 'SPARE' : '09.00','color': '#fac900' }}

 ###########################################################################
  col='brgmc'
  sun = ephem.Sun()
  star = ephem.FixedBody()
  star._ra = str(float(_ra0)/15.)
  star._dec = str(float(_dec0))
  td = datetime.timedelta(minutes=10)
  obs = ephem.Observer()       #will contain ephemeris for start time
  utnow = obs.date.datetime()  #current utdate/time
  if _plot:
    import pylab as plt
    plt.figure(num=1, figsize=(10, 7))     
    plt.clf()
    ax=plt.axes([.1,.25,.6,.7])
#    plt.ion() 
#    fig, ax = plt.subplots() 
    ax.plot([utnow,utnow],[0.1,90],'r--',label='Now')

  ii=0
  dates1=[]
  for site in ['lsc','elp','cpt','coj','ogg']:
        obs = ephem.Observer()       #will contain ephemeris for start time
        moon = ephem.Moon()
        utdate = obs.date  #current utdate/time
        obs.date = utdate
        obs.lat = site_ll[site]['latitude']
        obs.long = site_ll[site]['longitude']
        sun.compute(obs)

        obs.horizon='-12'
        nextrise = obs.next_rising(sun,use_center=True)
        nextset = obs.next_setting(sun,use_center=True)

        nextriseutc= nextrise.datetime() 
        nextsetutc= nextset.datetime() 
        if nextsetutc > nextriseutc: 
            nextsetutc=nextsetutc+datetime.timedelta(days=-1)
        date = nextsetutc
        dates,dates2=[],[]
        altitude,distance=[],[]
        lha=[]
        HA=[]
        while date < nextriseutc:
            date += td
            dates.append(date)
            dates2.append(date.hour)
            obs.date = date
            moon.compute(obs)
            star.compute(obs)
            gg,tt,ll=string.split(str(ephem.separation((star.az, star.alt), (moon.az, moon.alt))),':')
            hh,mm,ss=string.split(str(star.alt),':')
            lha.append(abs((obs.sidereal_time()-star._ra)*24.0/(2.0*ephem.pi)))
##############################
            if '-' in hh:
                sign=-1
                de=0
            else:
                sign=1.
                de = (np.abs(float(hh))+(float(mm)/60.0 + float(ss)/3600.0))*sign
            altitude.append(de)
##############################
            if '-' in gg:
                sign=-1
                de1=0
            else:
                sign=1.
                de1 = (abs(float(gg))+(float(tt)/60.0 + float(ll)/3600.0))*sign
            distance.append(de1)
        dist= '%3.1f' % (np.mean(np.array(distance)))
        stringa=site+' '+str(dist)+" $^{o}$ "
        dates1=np.array(list(dates1)+list(dates))
        altitudegood=[altitude[x] if (lha[x] <= 4.8) else None for x in range(0,len(lha))]
        altitudebad=[altitude[x] if (lha[x] > 4.8) else None for x in range(0,len(lha))]
        if _plot:
            ax.plot(dates, altitudegood, '-', label=stringa, color=site_ll[site]['color'],linewidth=3)
            ax.plot(dates, altitudebad, ':', label='', color=site_ll[site]['color'])

        ii=ii+1
  if _plot:
    # Plot airmass limit line (airmass=2)
    ax.plot([min(dates1),max(dates1)],[30,30],'g-.',label='airmass limit')
    ax.set_xlabel('UT time (hours)',fontsize=18)
    ax.set_ylabel('altitude',fontsize=18)
    ax.set_ylim(0.,90)
    ax.legend(numpoints=1,markerscale=1.5,loc=(1.07,0.5),ncol=1)
    plt.xticks(rotation='vertical')
    ax2 = plt.twinx()

    ax.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%m-%dT%H'))
    ax2.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%m-%dT%H'))
    ax2.set_ylabel('airmass',fontsize=18)
    ax2.set_yticks([19.471,23.578,30,41.8,53.13,65.38,90])
    ax2.set_yticklabels(['3.0','2.5','2.0','1.5','1.25','1.1','1.0'])
    ax.format_xdata = matplotlib.dates.DateFormatter('%Y-%m-%d:%h')
    ax2.format_xdata = matplotlib.dates.DateFormatter('%Y-%m-%d:%h')
    ax.xaxis.set_major_locator(MultipleLocator(1./12.))
    ax.xaxis.set_minor_locator(MultipleLocator(1./120.))
    pngplot = StringIO.StringIO()
    plt.savefig(pngplot,format='png')
    pngplot.seek(0)
    data_uri = pngplot.read().encode("base64").replace("\n", "")
    html = '<img width="'+xx+'" height="'+yy+'" alt="sample" src="data:image/png;base64,{0}">'.format(data_uri)
    return html

#    plt.show()
#  return dates,altitude

################################################################################
def visibilityiair(_ra0,_dec0,_plot=True,xx='300',yy='200'):
  from datetime import datetime, timedelta
  import matplotlib
  from matplotlib.dates import DateFormatter, MinuteLocator
  import string,ephem,datetime,sys
  import numpy as np
  import matplotlib.dates as mdates
  from matplotlib.ticker import MultipleLocator 
  #########################################################################
  site_ll = {
      'tst' : {'latitude' : '+34.433161', 'longitude' : '-119.8631' , 'color': 'k'},
      'sqa' : {'latitude' : '+34.6924533','longitude' : '-120.0422217' , 'color': 'c'},
      'ogg' : {'latitude' : '+20.706900', 'longitude' : '-156.25800', 'color': '#3366dd'},
      'bpl' : {'latitude' : '+34.433161', 'longitude' : '-119.8631',  'DOMA' : '01.08', 'color': 'g'},
      'elp' : {'latitude' : '+30.679833', 'longitude' : '-104.015173','DOMA' : '03.10','color': '#700000'},
      'lsc' : {'latitude' : '-30.167367', 'longitude' : '-70.8049',   'DOMA' : '05.02', 'DOMB' : '10.03', 'DOMC' : '11.04', 'color': 'm'},
      'cpt' : {'latitude' : '-32.3826',   'longitude' : '+20.8124',   'DOMA' : '06.05', 'DOMB' : '07.06', 'DOMC' : '08.10', 'color': '#004f00'},
      'coj' : {'latitude' : '-31.2733',   'longitude' : '+149.438',   'DOMA' : '14.12', 'DOMB' : '02.13', 'SPARE' : '09.00','color': '#fac900' }}

 ###########################################################################
  col='brgmc'
  sun = ephem.Sun()
  star = ephem.FixedBody()
  star._ra = str(float(_ra0)/15.)
  star._dec = str(float(_dec0))
  td = datetime.timedelta(minutes=10)
  obs = ephem.Observer()       #will contain ephemeris for start time
  utnow = obs.date.datetime()  #current utdate/time
  if _plot:
    import pylab as plt
    plt.figure(num=1, figsize=(float(xx)/50, float(yy)/50))     
    plt.clf()
    ax=plt.axes([.1,.25,.6,.7])
#    plt.ion() 
#    fig, ax = plt.subplots() 
    ax.plot([utnow,utnow],[0.1,90],'r--',label='Now')

  ii=0
  dates1=[]
  for site in ['lsc','elp','cpt','coj','ogg']:
        obs = ephem.Observer()       #will contain ephemeris for start time
        moon = ephem.Moon()
        utdate = obs.date  #current utdate/time
        obs.date = utdate
        obs.lat = site_ll[site]['latitude']
        obs.long = site_ll[site]['longitude']
        sun.compute(obs)

        obs.horizon='-12'
        nextrise = obs.next_rising(sun,use_center=True)
        nextset = obs.next_setting(sun,use_center=True)

        nextriseutc= nextrise.datetime() 
        nextsetutc= nextset.datetime() 
        if nextsetutc > nextriseutc: 
            nextsetutc=nextsetutc+datetime.timedelta(days=-1)
        date = nextsetutc
        dates,dates2=[],[]
        altitude,distance=[],[]
        lha=[]
        HA=[]
        while date < nextriseutc:
            date += td
            dates.append(date)
            dates2.append(date.hour)
            obs.date = date
            moon.compute(obs)
            star.compute(obs)
            gg,tt,ll=string.split(str(ephem.separation((star.az, star.alt), (moon.az, moon.alt))),':')
            hh,mm,ss=string.split(str(star.alt),':')
            lha.append(abs((obs.sidereal_time()-star._ra)*24.0/(2.0*ephem.pi)))
##############################
            if '-' in hh:
                sign=-1
                de=0
            else:
                sign=1.
                de = (np.abs(float(hh))+(float(mm)/60.0 + float(ss)/3600.0))*sign
            altitude.append(de)
##############################
            if '-' in gg:
                sign=-1
                de1=0
            else:
                sign=1.
                de1 = (abs(float(gg))+(float(tt)/60.0 + float(ll)/3600.0))*sign
            distance.append(de1)
        dist= '%3.1f' % (np.mean(np.array(distance)))
        stringa=site.upper()+' (Moon dist: '+str(dist)+"$^{o}$)"
        dates1=np.array(list(dates1)+list(dates))
        altitudegood=[altitude[x] if (lha[x] <= 4.8) else None for x in range(0,len(lha))]
        altitudebad=[altitude[x] if (lha[x] > 4.8) else None for x in range(0,len(lha))]
        if _plot:
            ax.plot(dates, altitudegood, '-', label=stringa, color=site_ll[site]['color'],linewidth=3)
            ax.plot(dates, altitudebad, ':', label='', color=site_ll[site]['color'])

        ii=ii+1
  if _plot:
    # Plot airmass limit line (airmass=2)
    ax.plot([min(dates1),max(dates1)],[30,30],'g-.',label='Airmass limit')

    titlefont = FontProperties()
    titlefont.set_size(18)
    titlefont.set_family('sans-serif')
    titlefont.set_style('normal')
    
    ax.set_xlabel('UT',fontproperties=titlefont)
    ax.set_ylabel('Altitude',fontproperties=titlefont)
    ax.set_ylim(0.,90)
    leg=ax.legend(numpoints=1,markerscale=1.5,loc=(1.1,0.5),ncol=1,fancybox=True)
    leg.get_frame().set_alpha(0)
    for label in leg.get_texts():
        label.set_fontsize(16)
    plt.xticks(rotation='vertical')
    ax2 = plt.twinx()

    ax.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%m-%dT%H'))
    ax2.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%m-%dT%H'))
    ax2.set_ylabel('Airmass',fontproperties=titlefont)
    ax2.set_yticks([19.471,23.578,30,41.8,53.13,65.38,90])
    ax2.set_yticklabels(['3.0','2.5','2.0','1.5','1.25','1.1','1.0'])
    ax.format_xdata = matplotlib.dates.DateFormatter('%Y-%m-%d:%h')
    ax2.format_xdata = matplotlib.dates.DateFormatter('%Y-%m-%d:%h')
    ax.xaxis.set_major_locator(MultipleLocator(1./12.))
    ax.xaxis.set_minor_locator(MultipleLocator(1./120.))
    pngplot = StringIO.StringIO()
    plt.savefig(pngplot,format='png',transparent=True)
    pngplot.seek(0)
    data_uri = pngplot.read().encode("base64").replace("\n", "")
    html = '<img width="'+xx+'" height="'+yy+'" alt="sample" src="data:image/png;base64,{0}">'.format(data_uri)
    return html

#    plt.show()
#  return dates,altitude


##############################
#ddd='<form action="http://secure.lcogt.net/user/supernova/dev/cgi-bin/updatetable.py" enctype="multipart/form-data" method="post">'+\
def addnewobject(_form):
    ddd='<form action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<input type="hidden" name="targid" value="">'+\
         '<input name="sn_name" size="30" maxlength="30" type="text" />'+\
         '<input name="SN_RA" size="12" maxlength="12" type="text"  placeholder="00:00:00.000"/>'+\
         '<input name="SN_DEC" size="13" maxlength="13" type="text" placeholder="+00:00:00.000"/>'+\
         '<input type="hidden" name="type" value="newobject">'+\
         '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
         '<input type="submit" value="add new object"></p>'+\
         '</form>'
    return ddd
###########################################################

def grafico(filename,hh='50',vv='50'):
    if filename:
        ggg='''<td class="ms-grid1-1101-even" width="'''+vv+'''" height="'''+hh+'''" align="center" ">'''+filename+"</td>"
    else:
       ggg='''<td class="ms-grid1-1101-even" width="'''+vv+'''" height="'''+hh+'''"  align="center" "></td>'''
    return ggg

##############################################################
def grafico1(filename,hh='150',vv='180'):
     ggg='''<td class="ms-grid1-1101-even" align="center" height="80%">
                <a href="'''+filename+'''">
                <img border="2" src="'''+filename+'''" xthumbnail-orig-image="'''+filename+'''" width="'''+vv+'''" height="'''+hh+'''"></a></td>'''
     return ggg

##########################################################################
def addnote(_targid,SN0,SN_RA,SN_DEC,_user,_form):
    ddd='<form action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<p>Add note : <textarea rows="1" cols="100" wrap="physical" name="note"></textarea>'+\
        '<input type="hidden" name="targid" value="'+str(_targid)+'">'+\
        '<input type="hidden" name="sn_name" value='+str(SN0)+'>'+\
        '<input type="hidden" name="SN_RA" value="'+str(SN_RA)+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(SN_DEC)+'">'+\
        '<input type="hidden" name="user" value="'+str(_user)+'">'+\
        '<input type="hidden" name="type" value="add">'+\
        '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
        '<input type="submit" value="Send"></p>'+\
        '</form>'  # lcogtlog2.cgi
    return ddd

##############################################

def objectinfo(obj,_user,_key,_form):
    line='<form action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<input type="hidden" name="id" value="'+str(obj['id'])+'">'+\
        '<input type="hidden" name="key" value="'+str(_key)+'">'+\
        '<input type="hidden" name="targid" value="'+str(obj['targid'])+'">'+\
        '<input type="hidden" name="sn_name" value='+str(obj['name'])+'>'+\
        '<input type="hidden" name="SN_RA" value="'+str(obj['ra_sn'])+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(obj['dec_sn'])+'">'+\
        '<input type="hidden" name="user" value="'+str(_user)+'">'+\
        '<input type="hidden" name="type" value="catalogue2">'+\
        '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
        '<p><textarea rows="1" cols="10" wrap="physical" name="note"></textarea></p>'+\
        '<input value="update" type="submit"/> </form>'
    return line

######################################

def recinfo(obj,_user,_form):
  line='<form action="agnupdatetable.py" method="post">'+\
        '<input type="hidden" name="targid" value="'+str(obj['targid'])+'">'+\
        '<input type="hidden" name="sn_name" value='+str(obj['name'])+'>'+\
        '<input type="hidden" name="SN_RA" value="'+str(obj['ra_sn'])+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(obj['dec_sn'])+'">'+\
        '<input type="hidden" name="user" value="'+str(_user)+'">'+\
        '<input type="hidden" name="type" value="recinfo">'+\
        '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
        '<p><textarea rows="1" cols="10" wrap="physical" name="note"></textarea></p>'+\
        '<input value="update" type="submit"/> </form>'
  return line

######################################

def delspectrum(SN,SN_RA,SN_DEC,_targid,_id,_namefile,_user,_form):
    ddd='<form action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<input type="hidden" name="targid" value="'+str(_targid)+'">'+\
        '<input type="hidden" name="id" value="'+str(_id)+'">'+\
        '<input type="hidden" name="sn_name" value='+str(SN)+'>'+\
        '<input type="hidden" name="SN_RA" value="'+str(SN_RA)+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(SN_DEC)+'">'+\
        '<input type="hidden" name="namefile" value="'+str(_namefile)+'">'+\
        '<input type="hidden" name="user" value="'+str(_user)+'">'+\
        '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
        '<input type="hidden" name="type" value="delspectrum">'+\
        '<input type="submit" value="delete"></form>'
    return ddd

######################################

def delfromdb(SN,SN_RA,SN_DEC,_targid,ii,_user,_form):
   ddd='<form action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
      '<input type="hidden" name="targid" value="'+str(_targid)+'">'+\
      '<input type="hidden" name="id" value="'+str(ii['id'])+'">'+\
      '<input type="hidden" name="note" value="'+str(ii['note'])+'">'+\
      '<input type="hidden" name="sn_name" value='+str(SN)+'>'+\
      '<input type="hidden" name="SN_RA" value="'+str(SN_RA)+'">'+\
      '<input type="hidden" name="SN_DEC" value="'+str(SN_DEC)+'">'+\
      '<input type="hidden" name="user" value="'+str(_user)+'">'+\
      '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
      '<input type="hidden" name="type" value="delete">'+\
      '<input type="submit" value="delete"></form>'
   return ddd

###################################################################################3
###################################################################################3


def archivereducedspectrum(img):
    import string,re
    import pyfits
    hdr = pyfits.getheader(img)
    import agnkey
    from agnkey.agnabsphotdef import deg2HMS
    try:     _targid=agnkey.agnsqldef.targimg(img)
    except:  _targid=''

    if 'TELID' in hdr:           _telescope=hdr.get('TELID')
    elif 'TELESCOPE' in hdr:     _telescope=hdr.get('TELESCOP')
    else:                        _telescope='other'

    #    object
    _object=hdr.get('object')
    if not _object: _object='spectrum'
    _object=re.sub('\}','', _object)
    _object=re.sub('\{','', _object)
    _object=re.sub('\[','', _object)
    _object=re.sub('\]','', _object)
    _object=re.sub('\(','', _object)
    _object=re.sub('\)','', _object)
    _object=re.sub('-','', _object)
    _object=re.sub(' ','', _object)
    #    dateobs
    if 'DATE-OBS' in hdr:  
        _dateobs=hdr.get('DATE-OBS')
        if 'T' in _dateobs: _dateobs=string.split(_dateobs,'T')[0]
    else:     _dateobs=''
    #   UT
    if 'UTSTART' in hdr:  _ut=hdr.get('UTSTART')
    elif 'UT' in hdr: _ut=hdr.get('UT')
    elif 'DATE-OBS' in hdr:   _ut=hdr.get('DATE-OBS')
    else: _ut=''
    if 'T' in _ut:    _ut=string.split(_ut,'T')[1]

    # ra and  dec
    if 'RA' in hdr:    _ra=hdr.get('RA')
    else: _ra=''
    if 'DEC' in hdr:    _dec=hdr.get('DEC')
    else: _dec=''

    if ':' in str(_ra):      _ra,_dec=deg2HMS(_ra,_dec)

    # JD
    if 'MJD' in hdr: _jd=hdr.get('MJD')+0.5
    elif 'MJD-OBS' in hdr: _jd=hdr.get('MJD-OBS')+0.5
    elif 'JD' in hdr: _jd=hdr.get('JD')
    elif 'DATE-OBS' in hdr: 
        dd=''
        try:
            dd=datetime.datetime.strptime(hdr.get('DATE-OBS')[0:-6],'%Y-%m-%dT%H:%M:%S')
        except:
            try:
                dd=datetime.datetime.strptime(hdr.get('DATE-OBS')[0:-6],'%Y-%m-%dT%H:%M')
            except: pass
        if dd:     _jd=agnkey.agnsqldef.JDnow(dd,False)
        else:      _jd=''
    else:    _jd=''

    if _telescope in ['fts','ftn']:
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'jd':float(hdr.get('MJD'))+0.5,\
                    'telescope':_telescope,'airmass':hdr.get('airmass'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('instrume'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('APERWID'),\
                    'targid':_targid,'grism':re.sub('/','_',hdr.get('GRISM')), 'original':hdr.get('arcfile'),'PROPID':hdr.get('PROPID'),\
                    'dateobs2':hdr.get('DATE-OBS')}

    elif 'gemini' in _telescope.lower():
        if 'south' in _telescope.lower(): _telescope='gs'
        else: _telescope='gn'
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'jd':_jd,\
                    'telescope':_telescope,'airmass':hdr.get('AIRMASS'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('INSTRUME'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('slit'),'targid':_targid,'grism':hdr.get('GRATING'),\
                    'original':hdr.get('arcfile')}

    else:
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'jd':_jd,\
                    'telescope':_telescope,'airmass':hdr.get('airmass'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('instrume'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('slit'),'targid':_targid,'grism':hdr.get('GRISM'),\
                    'original':hdr.get('arcfile'),'observer':hdr.get('observer')}
        dictionary['namefile']=string.split(img,'/')[-1]

    dictionary['namefile']=string.split(img,'/')[-1]
    _dir=re.sub(string.split(img,'/')[-1],'',img)
    dictionary['directory']=_dir
    return dictionary

########################################

def uploadspectrum(img,_output,_force,_permission):
    import pyfits
    import agnkey
    import re,string,sys,os
    

    note='input= '+img+'\n'
    try:
        hdr=pyfits.open(img)[0].header
    except:      return 'problem reading file. Check that it is in a fits format  '
    if 'TELID' in hdr:  _tel=hdr.get('TELID')
    elif 'TELESCOP' in hdr:    _tel=hdr.get('TELESCOP')
    else:                    _tel='other'
    if not _tel: _tel='other'
    _tel=re.sub(' ','',_tel)
    note=note+'telescope= '+_tel+'\n'
###################################### # gemini files in jerord format needs some trick
    if 'gemini' in _tel.lower():      
        data,hdr0 = pyfits.getdata(img, 'sci', header=True)
        try:        hdr0.__delitem__('AIRMASS')
        except:     hdr0.remove('AIRMASS') 
        hed=['TELESCOP','OBSERVAT','RA','DEC','UT','ST','EXPTIME','MASKNAME','GRATING','CENTWAVE','OBSMODE','GAIN','RDNOISE','MJD-OBS',\
                 'PIXSCALE','DATE-OBS','AIRMASS']
        for jj in hed:
            hdr0.update(jj,hdr[jj])
        if 'south' in _tel.lower(): _tel='gs'
        else: _tel='gn'
        pyfits.writeto(re.sub('.fits','0.fits',img), float32(data), hdr0)
        img=re.sub('.fits','0.fits',img)
############################################# 

    dictionary=archivereducedspectrum(img)
    _grism=dictionary['grism']
    _date=dictionary['dateobs']
    _date=re.sub('-','',_date)
    if 'T' in _date: string.split(_date,'T')[0]
    _ut=dictionary['ut']
    _object=dictionary['objname']
    if not _output:
            _output=str(_object)+'_'+str(_date)+'_'+str(_grism)+'_'+re.sub(':','',str(_ut))+'.fits'
    

    directory='/home/cv21/AGNKEY_www/AGNKEY/spectra/'+_date+'_'+_tel
    directory1=re.sub('/home/cv21/AGNKEY_www/','../',directory)
    dictionary['directory']=directory+'/'
    dictionary['namefile']=_output

    note=note+'output= '+_output+'\n'
    if not dictionary['objname']: note=note+'ERROR= OBJECT not defined '
    else:                         note=note+'objname= '+str(dictionary['objname'])+'\n'
    if not dictionary['directory']: note=note+'ERROR= directory not defined '
    else:                         note=note+'directory= '+str(dictionary['directory'])+'\n'
    if not dictionary['ra0']:     note=note+'ERROR= RA not defined \n'
    else:                         note=note+'ra= '+str(dictionary['ra0'])+'\n'
    if not dictionary['dec0']:    note=note+'ERROR= DEC not defined \n'
    else:                         note=note+'dec= '+str(dictionary['dec0'])+'\n'
    if not dictionary['targid']:  note=note+'ERROR= TARGID not defined (it will be automatic generated when RA,DEC and OBJECT are defined)\n'
    else:                         note=note+'targid= '+str(dictionary['targid'])+'\n'
    if not dictionary['dateobs']: note=note+'ERROR= DATE-OBS not defined \n'
    else:                         note=note+'dateobs= '+str(dictionary['dateobs'])+'\n'

    if 'ERROR' in note: 
        return note
    else:
        if os.path.isdir(directory1): print 'directory there'
        else:                        os.system('mkdir '+directory1)
        if os.path.isfile(directory1+'/'+_output): 
            note=note+'file already there'+'\n'
            if _force=='force':
                note=note+'replace file'+'\n'
                os.system('rm '+directory1+'/'+_output)
                os.system('cp '+img+' '+directory1+'/'+_output)
        else:
            os.system('cp '+img+' '+directory1+'/'+_output)
        #if _tel in ['ftn','fts']:
        #    datarawtable='datareduspectra'
        #else:

        datarawtable='dataspectraexternal'
        if datarawtable=='dataspectraexternal':
            dictionary['access']=_permission
            note=note+'acces= '+str(dictionary['access'])+'\n'

        note=note+'database= '+datarawtable+'\n'
        if not agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn,datarawtable,'namefile', string.split(_output,'/')[-1],column2='namefile'):
            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,datarawtable,dictionary)
        else:
            if _force=='update':
                note=note+'update database'+'\n'
                for voce in dictionary:
                    if voce!='id' and voce!='namefile':
                        agnkey.agnsqldef.updatevalue(datarawtable,voce,dictionary[voce],string.split(_output,'/')[-1])
            elif _force=='force':
                note=note+'replace line in the database'+'\n'
                agnkey.agnsqldef.deleteredufromarchive(string.split(_output,'/')[-1],datarawtable,'namefile')
                agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,datarawtable,dictionary)
            else: note=note+'database not changed'+'\n'
#        note=note+str(dictionary)
        return note

########################################################################################
def obsin(targid):
    import agnkey
    import datetime
    import time
    def JDnow(datenow='',verbose=False):
        _JD0=2455927.5
        if not datenow:
            datenow=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
        _JDtoday=_JD0+(datenow-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
            (datenow-datetime.datetime(2012, 01, 01,00,00,00)).days
        if verbose: print 'JD= '+str(_JDtoday)
        return _JDtoday

    _JDn=JDnow()
    command='select l.name,l.targid,l.ra_sn,l.dec_sn,o.filters,o.exptime,o.windowstart,o.windowend,o.tracknumber from obslog as o join lsc_sn_pos as l where windowend > '+str(_JDn)+' and l.targid=o.targi\
d and l.targid="'+str(targid)+'"'
    command1='select l.name,l.targid,l.ra_sn,l.dec_sn, o.filters,o.exptime,o.windowstart,o.windowend,o.tracknumber from obslog as o join lsc_sn_pos as l where windowend > '+str(_JDn-7)+'and windowend < '\
+str(_JDn)+' and l.targid=o.targid and l.targid="'+str(targid)+'"'

    aa=agnkey.agnsqldef.query([command])
    cc=agnkey.agnsqldef.query([command1])
    ll0={}
    if aa:
        for i in aa[0].keys(): ll0[i]=[]
        for jj in range(0,len(aa)):
            for kk in aa[0].keys():
                ll0[kk].append(aa[jj][kk])
    ll1={}
    if cc:
        for i in cc[0].keys(): ll1[i]=[]
        for jj in range(0,len(cc)):
            for kk in cc[0].keys():
                ll1[kk].append(cc[jj][kk])

    username,passwd='svalenti@lcogt.net','eIgheeK_'
    lll0=''
    lll1=''
    if ll0:
        ccc='BGCOLOR="#CCFF66"'
        for i in range(0,len(ll0['name'])):
            if float(ll0['tracknumber'][i])>1:
                _dict=agnkey.util.getstatus(username,passwd,str(ll0['tracknumber'][i]).zfill(10))
                if 'state' in _dict.keys(): _status=_dict['state']
                else:  _status='xxxx'
                if 'requests' in _dict.keys(): _request_number=_dict['requests']
                else: _request_number=[]
            else:
                _status='xxx'
                _request_number=[]
            if 'floyds' in ll0['filters'][i] and _request_number:
                for jj in _request_number: 
                    data='../AGNKEY/floydsraw/'+jj+'.tar.gz'
                    lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+'</td><td>'+str(ll0['tracknumber'][i])+'</td><td>'+_status+'</td><td>'+'<a href="'+data+'"> download tar '+'</td></tr>'
            else:
                lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+'</td><td>'+str(ll0['tracknumber'][i])+'</td><td>'+_status+'</td></tr>'
    if ll1:
        for i in range(0,len(ll1['name'])):
            if float(ll1['tracknumber'][i])>1:
                _dict=agnkey.util.getstatus(username,passwd,str(ll1['tracknumber'][i]).zfill(10))
                if 'state' in _dict.keys(): _status=_dict['state']
                else:  _status='xxxx'
                if 'requests' in _dict.keys(): _request_number=_dict['requests']
                else: _request_number=[]
            else:
                _status='xxx'
                _request_number=[]
            if 'floyds' in ll1['filters'][i] and _request_number:
                for jj in _request_number: 
                    data='../AGNKEY/floydsraw/'+jj+'.tar.gz'
                    data='http://data.lcogt.net/download/package/spectroscopy/request/'+_request_number+'.tar.gz'
                    lll1=lll1+'<tr><td>'+str(ll1['name'][i])+'</td><td>'+str(ll1['filters'][i])+'</td><td>'+str(ll1['exptime'][i])+'</td><td>'+str(ll1['windowstart'][i])+'</td><td>'+str(ll1['windowend'][i])+'</td><td>'+str(ll1['tracknumber'][i])+'</td><td>'+_status+'</td><td>'+'<a href="'+data+'"> download tar '+'</td></tr>'
            else:
                lll1=lll1+'<tr><td>'+str(ll1['name'][i])+'</td><td>'+str(ll1['filters'][i])+'</td><td>'+str(ll1['exptime'][i])+'</td><td>'+str(ll1['windowstart'][i])+'</td><td>'+str(ll1['windowend'][i])+'</td><td>'+str(ll1['tracknumber'][i])+'</td><td>'+_status+'</td></tr>'
    return lll0,lll1

##########################################################################################
