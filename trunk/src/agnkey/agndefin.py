#!/dark/usr/anaconda2/bin/python
#/usr/bin/env python
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
         '<option value="7"> 3 in the next 6 days</option>   <option value="8"> 7 in the next 7 days </option>'+\
         '<option value="9"> 1 observation in the next 8h </option>   <option value="10">  3 observations in the next 12h </option>'+\
         '<option value="13"> 24 observations in the next 24 days </option>   <option value="14">  12 observations in the next 24 days </option>'+\
         '<option value="15"> 21 observations in the next 7 days </option>'+\
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
    sss=sss+'<td width=10> <div class="styled-select"> number of spectra : <select name="nexpfloyds'+'"  width:100px;>'+\
         '<option  width=10 value="1"> 1</option>'+\
         '<option  width=10 value="2"> 2</option>'+\
         '<option  width=10 value="3"> 3</option>'+\
         '<option  width=10 value="4"> 4</option>'+ '</select></div></td>'
    sss=sss+'</tr>'+\
         '</table>'+\
         '<table>'+\
         '<tr><td> site: <select name="site">'+\
         '<option value="any"> any</option>'+\
         '<option value="ogg">FTN</option>'+\
         '<option value="coj">FTS</option>'+\
         '</select></td></tr>'+\
         '<tr><td> slit: <select name="slit">'+\
         '<option value="default">default </option>'+\
         '<option value="1.2">1.2</option>'+\
         '<option value="1.6">1.6</option>'+\
         '<option value="2.0">2.0</option>'+\
         '<option value="6.0">6.0</option>'+\
         '</select></td></tr>'+\
         '<tr><td> number of triggers: </a> <select name="ntriggers">'+\
         '<option value="1"> 1 in the next 24h </option>'+\
         '<option value="2"> 2 in the next 48h </option>'+\
         '<option value="3"> 2 in the next 24h</option> '+\
         '<option value="4"> 4 in the next 48h </option>'+\
         '<option value="5"> 1 in the next 6 days</option>'+\
         '<option value="6"> 2 in the next 6 days </option>'+\
         '<option value="7"> 3 in the next 6 days</option>'+\
         '<option value="8"> 7 in the next 7 days </option>'+\
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

        lha=[abs(i) if abs(i)<=12 else abs(i-24) for i in lha]

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



##############################
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
        '</form>'  # 
    return ddd

##############################################

def markasbad(_id,_targid,_user,_key,_form):
    line='<form action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<input type="hidden" name="id" value="'+str(_id)+'">'+\
        '<input type="hidden" name="key" value="'+str(_key)+'">'+\
        '<input type="hidden" name="note" value="bad">'+\
        '<input type="hidden" name="targid" value="'+str(_targid)+'">'+\
        '<input type="hidden" name="user" value="'+str(_user)+'">'+\
        '<input type="hidden" name="type" value="markasbad">'+\
        '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
        '<input type="submit" value="mark as bad"></form>'
    return line


def stopobservation(_id,_targid,_user,_key,_form):
    line='<form action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<input type="hidden" name="id" value="'+str(_id)+'">'+\
        '<input type="hidden" name="key" value="'+str(_key)+'">'+\
        '<input type="hidden" name="note" value="0">'+\
        '<input type="hidden" name="targid" value="'+str(_targid)+'">'+\
        '<input type="hidden" name="user" value="'+str(_user)+'">'+\
        '<input type="hidden" name="type" value="stopobservation">'+\
        '<input type="hidden" name="outputformat" value="'+str(_form)+'">'+\
        '<input type="submit" value="stop observations"></form>'
    return line

###################################################################################3

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
    from astropy.io import fits as pyfits
    import agnkey

    hdr = pyfits.getheader(img)
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
    elif 'UT' in hdr: 
        _ut=hdr.get('UT')
    elif 'UTC-OBS' in hdr: 
        _ut=hdr.get('UTC-OBS')
    elif 'DATE-OBS' in hdr:   
        _ut=hdr.get('DATE-OBS')
    else: 
        _ut=''
    if 'T' in _ut:    _ut=string.split(_ut,'T')[1]

    # ra and  dec
    if 'RA' in hdr:    _ra=hdr.get('RA')
    else: _ra=''
    if 'DEC' in hdr:    _dec=hdr.get('DEC')
    else: _dec=''

    if ':' in str(_ra):      _ra,_dec=deg2HMS(_ra,_dec)

    # JD
    if 'MJD' in hdr: _mjd=hdr.get('MJD')
    elif 'MJD-OBS' in hdr: _mjd=hdr.get('MJD-OBS')
    elif 'JD' in hdr: _mjd=hdr.get('JD') - 2400000.5
    elif 'DATE-OBS' in hdr: 
        dd=''
        try:
            dd=datetime.datetime.strptime(hdr.get('DATE-OBS')[0:-6],'%Y-%m-%dT%H:%M:%S')
        except:
            try:
                dd=datetime.datetime.strptime(hdr.get('DATE-OBS')[0:-6],'%Y-%m-%dT%H:%M')
            except: pass
        if dd:     _mjd=agnkey.agnsqldef.JDnow(dd,False)  - 2400000.5
        else:      _mjd=''
    else:    _mjd=''

    
    if 'GRISM' in hdr:
        _grism=re.sub('/','_',hdr.get('GRISM'))
    elif 'GRATING' in hdr:
        _grism=hdr.get('GRATING')
    else:
        _grism='grism'

    if _telescope in ['fts','ftn']:
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'mjd':float(hdr.get('MJD-OBS')),\
                    'telescope':_telescope,'airmass':hdr.get('airmass'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('instrume'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('APERWID'),\
                    'targid':_targid,'grism':_grism, 'original':hdr.get('arcfile'),'PROPID':hdr.get('PROPID'),\
                    'dateobs2':hdr.get('DATE-OBS')}

    elif 'gemini' in _telescope.lower():
        if 'south' in _telescope.lower(): _telescope='gs'
        else: _telescope='gn'
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'mjd':_mjd,\
                    'telescope':_telescope,'airmass':hdr.get('AIRMASS'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('INSTRUME'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('slit'),'targid':_targid,'grism':_grism,\
                    'original':hdr.get('arcfile')}

    else:
        dictionary={'dateobs':_dateobs,'exptime':hdr.get('exptime'), 'filter':hdr.get('filter'),'mjd':_mjd,\
                    'telescope':_telescope,'airmass':hdr.get('airmass'),'objname':_object,'ut':_ut,\
                    'instrument':hdr.get('instrume'),'ra0':_ra,'dec0':_dec,'slit':hdr.get('slit'),'targid':_targid,'grism':_grism,\
                    'original':hdr.get('arcfile'),'observer':hdr.get('observer')}
        dictionary['namefile']=string.split(img,'/')[-1]

    dictionary['namefile']=string.split(img,'/')[-1]
    _dir=re.sub(string.split(img,'/')[-1],'',img)
    dictionary['directory']=_dir
    return dictionary

########################################

def uploadspectrum(img,_output,_force,_permission,_filetype='fits'):
    from astropy.io import fits as pyfits
    import agnkey
    import numpy as np
    import re,string,sys,os
    import tarfile
    if _filetype=='tar':
        os.system('tar -xf ../tmp/'+img)
        tar=tarfile.open(img)
        imglist=tarfile.TarFile.getnames(tar)
        tar.close()
    else:
        imglist = [img]
    note = ''
    for img in imglist:
          note= note + 'input= '+img+'\n'
          try:
              hdr=pyfits.open(img)[0].header
          except:
              return 'problem '+img+'  reading file. Check that it is in a fits format  '
          if 'TELID' in hdr:  _tel=hdr.get('TELID')
          elif 'TELESCOP' in hdr:    _tel=hdr.get('TELESCOP')
          else:                    _tel='other'
          if not _tel: _tel='other'
          _tel = re.sub(' ','',_tel)
          note = note + 'telescope= ' + _tel + '\n'
          ###################################### # gemini files in jerord format needs some trick
          if 'gemini' in _tel.lower():
              data,hdr0 = pyfits.getdata(img, 'sci', header=True)
              try:        hdr0.__delitem__('AIRMASS')
              except:     hdr0.remove('AIRMASS')
              hed=['TELESCOP','OBSERVAT','RA','DEC','UT','ST','EXPTIME','MASKNAME',\
                   'GRATING','CENTWAVE','OBSMODE','GAIN','RDNOISE','MJD-OBS',\
                   'PIXSCALE','DATE-OBS','AIRMASS']
              for jj in hed:
                  hdr0.update(jj,hdr[jj])
              if 'south' in _tel.lower(): _tel='gs'
              else: _tel='gn'
              pyfits.writeto(re.sub('.fits','0.fits',img), np.float32(data), hdr0)
              img=re.sub('.fits','0.fits',img)
          dictionary=archivereducedspectrum(img)
          _grism=dictionary['grism']
          _date=dictionary['dateobs']
          _date=re.sub('-','',_date)
          if 'T' in _date: string.split(_date,'T')[0]
          _ut=dictionary['ut']
          _object=dictionary['objname']
          if not _output:
                  _output=str(_object)+'_'+str(_date)+'_'+str(_grism)+'_'+re.sub(':','',str(_ut))+'.fits'
          _output=re.sub('/','_',_output)

          if agnkey.util.host=='SVMAC':
              directory='/Users/svalenti/redu2/AGNKEY/spectra/'+_date+'_'+_tel
              directory1=re.sub('/Users/svalenti/redu2/','../',directory)
          elif agnkey.util.host=='deneb':
              directory='/home/cv21/ANKEY_www/AGNKEY/spectra/'+_date+'_'+_tel
              directory1=re.sub('/home/cv21/AGNKEY_www/','../',directory)
          elif agnkey.util.host=='dark':
              directory='/dark/hal/AGNKEY/spectra/'+_date+'_'+_tel
              directory1=re.sub('/dark/hal/','../../',directory)


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
              if os.path.isdir(directory1):
                  print('directory there')
              else:
                  os.system('mkdir '+directory1)
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
    return note

########################################################################################
def obsin(targid,_days=7):
    import agnkey
    import datetime
    import time
    import re
    def JDnow(datenow='',verbose=False):
        _JD0=2455927.5
        if not datenow:
            datenow=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
        _JDtoday=_JD0+(datenow-datetime.datetime(2012, 1, 1, 0, 0, 0)).seconds/(3600.*24)+\
            (datenow-datetime.datetime(2012, 1, 1, 0, 0, 0)).days
        if verbose:
            print('JD= '+str(_JDtoday))
        return _JDtoday


    _JDn=JDnow()

    command='select l.name,l.targid,l.ra_sn,l.dec_sn,o.filters,o.exptime,o.windowstart,o.windowend,o.tracknumber, o.reqnumber, o.tarfile, o.status from obslog as o join lsc_sn_pos as l where windowend > '+str(_JDn)+' and l.targid=o.targid and l.targid="'+str(targid)+'"'
    command1='select l.name,l.targid,l.ra_sn,l.dec_sn, o.filters,o.exptime,o.windowstart,o.windowend,o.tracknumber, o.reqnumber, o.tarfile, o.status from obslog as o join lsc_sn_pos as l where windowend > '+str(_JDn-float(_days))+'and windowend < '\
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

    readpass=agnkey.util.readpasswd(agnkey.util.workingdirectory,agnkey.util.realpass)
    username,passwd=readpass['odinuser'],readpass['odinpasswd']
    lll0=''
    lll1=''
    if ll0:
        ccc='BGCOLOR="#CCFF66"'
        for i in range(0,len(ll0['name'])):
            if float(ll0['tracknumber'][i])>1:
                if ll0['status'][i]:  
                    _status=ll0['status'][i]
                else:
                    _status=''
#                if _status=='PENDING': _status=''
                _date1 = agnkey.util.jd2date(ll0['windowend'][i])
                _date0 = agnkey.util.jd2date(ll0['windowstart'][i])
                if ll0['tarfile'][i]:  
                    _tarfile=ll0['tarfile'][i]
                else:
                    _tarfile=''
                if ll0['reqnumber'][i]:  
                    _reqnumber=ll0['reqnumber'][i]
                else:
                    _reqnumber=''
                if 'floyds' in ll0['filters'][i]:
                  if _reqnumber:
                    if not _tarfile:
                        try:
                            _date=re.sub('-','',_dict['requests'][ll0['tracknumber'][i]]['schedule'][0]['frames'][0]['day_obs'])
                            _tarfile=_reqnumber+'_'+str(_date)+'.tar.gz'
                            agnkey.agnsqldef.updatevalue('obslog','tarfile',_tarfile,str(ll0['tracknumber'][i]),connection='agnkey',namefile0='tracknumber')
                        except:
                            _tarfile=''
                    if _tarfile:
                        lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+\
                              str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+\
                              str(ll0['tracknumber'][i])+'</td><td>'+str(_status)+\
                              '</td><td>'+'<a href="../../AGNKEY/floydsraw/'+str(_tarfile)+'"> download tar '+'</td></tr>'

                    else:
                        lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+\
                              str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+\
                              str(ll0['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
#                            str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+'</td><td>'+'</td><td>'+str(_date0)+'</td><td>'+\

                  else:
                      lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+\
                            str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+\
                            str(ll0['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
#                            str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+'</td><td>'+'</td><td>'+str(_date0)+'</td><td>'+\
                else:
                    lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+\
                          str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+\
                          str(ll0['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
#                        str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+\


    if ll1:
        for i in range(0,len(ll1['name'])):
            if float(ll1['tracknumber'][i])>1:
                _date1 = agnkey.util.jd2date(ll1['windowend'][i])
                _date0 = agnkey.util.jd2date(ll1['windowstart'][i])
                if ll1['status'][i]:  
                    _status=ll1['status'][i]
                else:
                    _status=''
                if ll1['tarfile'][i]:  
                    _tarfile=ll1['tarfile'][i]
                else:
                    _tarfile=''
                if ll1['reqnumber'][i]:  
                    _reqnumber=ll1['reqnumber'][i]
                else:
                    _reqnumber=''
                if 'floyds' in ll1['filters'][i]:
                   if _reqnumber:
                            if _tarfile:
                                agnkey.agnsqldef.updatevalue('obslog','tarfile',_tarfile,str(ll1['tracknumber'][i]),connection='agnkey',namefile0='tracknumber')
                                lll1=lll1+'<tr><td>'+str(ll1['name'][i])+'</td><td>'+str(ll1['filters'][i])+'</td><td>'+str(ll1['exptime'][i])+'</td><td>'+\
                                      str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+\
                                      str(ll1['tracknumber'][i])+'</td><td>'+str(_status)+\
                                      '</td><td>'+'<a href="../../AGNKEY/floydsraw/'+str(_tarfile)+'"> download tar '+'</td></tr>'
                                      #str(ll1['windowstart'][i])+'</td><td>'+str(ll1['windowend'][i])+'</td><td>'+

                            else:
                                lll1=lll1+'<tr><td>'+str(ll1['name'][i])+'</td><td>'+str(ll1['filters'][i])+'</td><td>'+str(ll1['exptime'][i])+'</td><td>'+\
                                      str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+\
                                      str(ll1['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
                                      #str(ll1['windowstart'][i])+'</td><td>'+str(ll1['windowend'][i])+'</td><td>'+
                   else:
                       pass
                else:
                    lll1=lll1+'<tr><td>'+str(ll1['name'][i])+'</td><td>'+str(ll1['filters'][i])+'</td><td>'+str(ll1['exptime'][i])+'</td><td>'+\
                          str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+\
                          str(ll1['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
                    #str(ll1['windowstart'][i])+'</td><td>'+str(ll1['windowend'][i])+'</td><td>'+\
    return lll0,lll1

##########################################################################################

########################################################################################
def obsin2(targid,_days=7):
    import agnkey
    import datetime
    import time
    import re
    def JDnow(datenow='',verbose=False):
        _JD0=2455927.5
        if not datenow:
            datenow=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
        _JDtoday=_JD0+(datenow-datetime.datetime(2012,  1,  1, 0, 0, 0)).seconds/(3600.*24)+\
            (datenow-datetime.datetime(2012,  1,  1, 0, 0, 0)).days
        if verbose:
            print('JD= '+str(_JDtoday))
        return _JDtoday


    _JDn=JDnow()

    command='select l.name, l.targid, l.ra_sn, l.dec_sn, o.filters, o.exptime, o.mode, g.windowstart, g.windowend, g.tracknumber, '+\
        'g.reqnumber, g.tarfile, g.status from triggers as o join triggerslog as g join lsc_sn_pos as l '+\
        'where o.id = g.triggerid and g.windowend > '+str(_JDn)+' and l.targid=o.targid and l.targid="'+str(targid)+'"'
    command1='select l.name,l.targid, l.ra_sn, l.dec_sn, o.filters, o.exptime, o.mode, g.windowstart, g.windowend, g.tracknumber, '+\
        'g.reqnumber, g.tarfile, g.status from triggers as o join triggerslog as g join lsc_sn_pos as l '+\
        'where o.id = g.triggerid and g.windowend > '+str(_JDn-float(_days))+'and g.windowend < '+\
        str(_JDn)+' and l.targid=o.targid and l.targid="'+str(targid)+'"'

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

    readpass=agnkey.util.readpasswd(agnkey.util.workingdirectory,agnkey.util.realpass)
    username,passwd=readpass['odinuser'],readpass['odinpasswd']
    lll0=''
    lll1=''
    if ll0:
        ccc='BGCOLOR="#CCFF66"'
        for i in range(0,len(ll0['name'])):
            if float(ll0['tracknumber'][i])>=0:
                _date1 = agnkey.util.jd2date(ll0['windowend'][i])
                _date0 = agnkey.util.jd2date(ll0['windowstart'][i])
                if ll0['status'][i]:  
                    _status=ll0['status'][i]
                else:
                    _status=''
#                if _status=='PENDING': _status=''
                if ll0['tarfile'][i]:  
                    _tarfile=ll0['tarfile'][i]
                else:
                    _tarfile=''
                if ll0['reqnumber'][i]:  
                    _reqnumber=ll0['reqnumber'][i]
                else:
                    _reqnumber=''
                if 'floyds' in ll0['filters'][i]:
                  if _reqnumber:
                    if not _tarfile:
                        try:
                            _date=re.sub('-','',_dict['requests'][ll0['tracknumber'][i]]['schedule'][0]['frames'][0]['day_obs'])
                            _tarfile=_reqnumber+'_'+str(_date)+'.tar.gz'
                            agnkey.agnsqldef.updatevalue('triggerslog','tarfile',_tarfile,str(ll0['tracknumber'][i]),connection='agnkey',namefile0='tracknumber')
                        except:
                            _tarfile=''
                    if _tarfile:
                        lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+\
                              str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+str(ll0['mode'][i])+'</td><td>'+\
                              str(ll0['tracknumber'][i])+'</td><td>'+str(_status)+\
                              '</td><td>'+'<a href="../../AGNKEY/floydsraw/'+str(_tarfile)+'"> download tar '+'</td></tr>'
                              #str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+'</td><td>'+\
                    else:
                        lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+\
                              str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+str(ll0['mode'][i])+'</td><td>'+\
                              str(ll0['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
#                              str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+'</td><td>'+\
                  else:
                      lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+\
                            str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+str(ll0['mode'][i])+'</td><td>'+\
                            str(ll0['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
                            #str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+'</td><td>'+\
                else:
                    lll0=lll0+'<tr><td>'+str(ll0['name'][i])+'</td><td>'+str(ll0['filters'][i])+'</td><td>'+str(ll0['exptime'][i])+'</td><td>'+\
                          str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+str(ll0['mode'][i])+'</td><td>'+\
                          str(ll0['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
                          #str(ll0['windowstart'][i])+'</td><td>'+str(ll0['windowend'][i])+'</td><td>'+\

    if ll1:
        for i in range(0,len(ll1['name'])):
            if float(ll1['tracknumber'][i])>=0:
                _date1 = agnkey.util.jd2date(ll1['windowend'][i])
                _date0 = agnkey.util.jd2date(ll1['windowstart'][i])
                if ll1['status'][i]:  
                    _status=ll1['status'][i]
                else:
                    _status=''
                if ll1['tarfile'][i]:  
                    _tarfile=ll1['tarfile'][i]
                else:
                    _tarfile=''
                if ll1['reqnumber'][i]:  
                    _reqnumber=ll1['reqnumber'][i]
                else:
                    _reqnumber=''
                if 'floyds' in ll1['filters'][i]:
                   if _reqnumber:
                            if _tarfile:
                                agnkey.agnsqldef.updatevalue('triggerslog','tarfile',_tarfile,str(ll1['tracknumber'][i]),connection='agnkey',namefile0='tracknumber')
                                lll1=lll1+'<tr><td>'+str(ll1['name'][i])+'</td><td>'+str(ll1['filters'][i])+'</td><td>'+str(ll1['exptime'][i])+'</td><td>'+\
                                      str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+str(ll1['mode'][i])+'</td><td>'+\
                                      str(ll1['tracknumber'][i])+'</td><td>'+str(_status)+\
                                      '</td><td>'+'<a href="../../AGNKEY/floydsraw/'+str(_tarfile)+'"> download tar '+'</td></tr>'
                                #str(ll1['windowstart'][i])+'</td><td>'+str(ll1['windowend'][i])+'</td><td>'+\
                            else:
                                lll1=lll1+'<tr><td>'+str(ll1['name'][i])+'</td><td>'+str(ll1['filters'][i])+'</td><td>'+str(ll1['exptime'][i])+'</td><td>'+\
                                      str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+str(ll1['mode'][i])+'</td><td>'+\
                                      str(ll1['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
                                      #str(ll1['windowstart'][i])+'</td><td>'+str(ll1['windowend'][i])+'</td><td>'+\
                   else:
                       pass
                else:
                    lll1=lll1+'<tr><td>'+str(ll1['name'][i])+'</td><td>'+str(ll1['filters'][i])+'</td><td>'+str(ll1['exptime'][i])+'</td><td>'+\
                          str(_date0)+'</td><td>'+str(_date1)+'</td><td>'+str(ll1['mode'][i])+'</td><td>'+\
                          str(ll1['tracknumber'][i])+'</td><td>'+str(_status)+'</td></tr>'
                    #str(ll1['windowstart'][i])+'</td><td>'+str(ll1['windowend'][i])+\
    return lll0,lll1

##########################################################################################

def get_filtclr():
 filtclr={}
 filtclr['U']='purple'
 filtclr['B']='blue'
 filtclr['V']='#00bc00'
 filtclr['R']='red'
 filtclr['I']= '#CCCC33'
 filtclr['Bessell-B']='blue'
 filtclr['Bessell-V']='#00bc00'
 filtclr['Bessell-R']='red'
 filtclr['Bessell-I']='#CCCC33'
 filtclr['up']='purple'
 filtclr['gp']='green'
 filtclr['rp']='red'
 filtclr['ip']='#CCCC33'
 filtclr['zs']='black'
 filtclr['w']='#a883b8'
 filtclr['SDSS-U']='purple'
 filtclr['SDSS-G']='green'
 filtclr['SDSS-R']='red'
 filtclr['SDSS-I']='black'  
 filtclr['Pan-Starrs-Z']='black'
 filtclr['H-Alpha']='grey'
 return filtclr

##############################################################################

def sqlquery(db,command):
   import MySQLdb,os,string
   lista=''
   try:
       cursor = db.cursor(MySQLdb.cursors.DictCursor)
       cursor.execute(command)
       lista = cursor.fetchall()
       if cursor.rowcount == 0:
           pass
       cursor.close()
   except MySQLdb.Error, e: 
       lista = "Error %d: %s" % (e.args[0], e.args[1])
       print(lista)
   return lista

#################################################################

# lcdata='[ {label: "COJ B",  points: {show: true, fill: true, fillColor: "blue", type: "o", radius: 2, errorbars: "y", yerr: {show:true, upperCap: "-", lowerCap: "-", radius: 2} },  color: "blue",  data: [ [-17.2193814586, 4.426, 0.161], [-17.2162217363, 0.322, 0.469], [-9.20783068286, 2.1532, 0.155], [-9.2047520373, 1.238, 0.264] ] },{}]'
# mint, maxt, minmag, maxmag=-18.85779960560616, 0.8032181585673273, -0.5191500000005, 6.7708166666705

def plot_phot(db,targid, width=450, height=250, plottype='flot', magtype='psfmag'):
 import random
 # Get the data string:
 lcdata, mint, maxt, minmag, maxmag = load_lc_data(db,targid,plottype,magtype)

 if lcdata == '':
     print('''<span style="font-family: 'Open Sans', sans-serif; font-weight:400; font-size:14; color:black;">No photometry to display</span>''')
     return ''
 # Make the flot plot:
 r = random.randrange(0, 10001)
 print('''<div id="lcplot%s%s%s" style="width:%spx;height:%spx"></div>''' %(targid, magtype, str(r), str(width), str(height)))

 print('''<script id="source_phot" language="javascript" type="text/javascript">''')
 print('''function negformat(val, axis) {
            return val.toFixed(axis.tickDecimals);
          };''')

# dm=True
# if dm:
#     print '''function absmag(val, axis) {
#                return (-val-%s).toFixed(axis.tickDecimals);
#              };''' %dm



 print('''$(function () {
          var lcplot = $("#lcplot%s%s%s");
          var xlabel = '<div style="position:absolute;left:%spx;bottom:5px;color:#666;font-family: \\'Open Sans\\', sans-serif; font-weight:400; font-size:12">Days Ago</div>';
          var options = {
                 series: { 
                    lines: { show: false },
                    shadowSize: 0 
                 }, 
                 legend: { show: false }, 
                 xaxis: {
                    font: {size: 12, weight: "400", family: "'Open Sans', sans-serif"},
                    color: '#666',
                    tickColor: '#DCDCDC',
                    tickFormatter:negformat,
                    autoscaleMargin: 0.02,
                    reversed: true ,
	            labelHeight: 35,
                    min: %s,
                    max: %s
                 }, 
                 yaxis: {
                    font: {size: 12, weight: "400", family: "'Open Sans', sans-serif"},
                    color: '#666',
                    tickColor: '#DCDCDC',
		    tickFormatter:negformat,
                    transform: function (v) { return -v; },  
                    inverseTransform: function (v) { return -v; },
                    reversed: true ,
                    min: %s,
                    max: %s,
                    position: "left"
                 }, 
                 selection: { mode: "xy" },
                 grid: { hoverable: true, borderWidth: 1 }
                }; 
          ''' % (targid, magtype, r, width/2-20,str(mint), str(maxt), str(minmag), str(maxmag)))

 print('''function plotSelected() {
          var data = %s;
          var plot = $.plot(lcplot, data,
                     $.extend(true, {}, options, {})
                     )
  	  lcplot.append(xlabel);
	  return plot;
          }   
          var plot = plotSelected();
      ''' %lcdata)

 print(''' // tooltips
          function showChartTooltip(x, y, contents) {
              $('<div id="charttooltip%s%s%s">' + contents + '</div>').css( {
                  position: 'absolute',
                  display: 'None',
                  top: y + 5,
                  left: x + 5,
                  border: '1px solid #fdd',
                  padding: '2px',
                  'background-color': '#fee',
                  opacity: 0.8
              }).appendTo("body").fadeIn(200);
          }
          var previousPoint = null;
          $("#lcplot%s%s%s").bind("plothover", function (event, pos, item) {
              $("#x").text(pos.x.toFixed(2));
              $("#y").text(pos.y.toFixed(2));
              if (item) {
                  if (previousPoint != item.datapoint) {
                      previousPoint = item.datapoint;
                      $("#charttooltip%s%s%s").remove();
                      var x = item.datapoint[0].toFixed(2),
                          y = item.datapoint[1].toFixed(2);
                      showChartTooltip(item.pageX, item.pageY, "<span style=\\"font-family: 'Open Sans', sans-serif; font-weight:400; font-size:12; color:black;\\"> mag: " + y + " (" + -x + " days ago) <br> " + item.series.label + "</span>");
                  }
              } 
              else {
                  $("#charttooltip%s%s%s").remove();
                  previousPoint = null;
              }
          });''' %(targid, magtype, r, targid, magtype, r, targid, magtype, r, targid, magtype, r))

 print('''
       // zooming
       lcplot.bind("plotselected", function (event, ranges) {
           var data = %s;
           plot = $.plot(lcplot, data,
                  $.extend(true, {}, options, {
                        xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
			yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
      			})
           )
           lcplot.append(xlabel);
           // zooming reset button:
           $("<div style='right:10px; top:7px; font-family:\\"Open Sans\\",sans-serif; font-weight:400; font-size:12; color:black; position:absolute; cursor:pointer'>[reset]</div>")
           .appendTo(lcplot)
           .click(function () { 
              plot.getOptions().xaxes[0].min = %s;
              plot.getOptions().xaxes[0].max = %s;
              plot.getOptions().yaxes[0].min = %s;
              plot.getOptions().yaxes[0].max = %s;
              plot.setupGrid();
              plot.draw();  
           });
       });
 ''' % (lcdata,mint, maxt, minmag, maxmag))

 print('''
       // zooming reset button       
       $("<div style='right:10px; top:7px; font-family:\\"Open Sans\\",sans-serif; font-weight:400; font-size:12; color:black; position:absolute; cursor:pointer'>[reset]</div>")
           .appendTo(lcplot)
           .click(function () { 
              plot.getOptions().xaxes[0].min = %s;
              plot.getOptions().xaxes[0].max = %s;
              plot.getOptions().yaxes[0].min = %s;
              plot.getOptions().yaxes[0].max = %s;
              plot.setupGrid();
              plot.draw();  
           });
       ''' %(mint, maxt, minmag, maxmag))
 print('''}); ''')
 print('''</script> ''')
 return ''

#################################################################################

def load_lc_data(db,targid,plottype='flot',magtype='psfmag',_ft=1):
 filtclr=get_filtclr()
 if magtype in  ['psfmag','apmag','appmagap1','appmagap2','appmagap3','mag']: 
     if magtype=='psfmag':
      dmagtype='psfdmag'
     elif magtype=='apmag':
      dmagtype='psfdmag'
     elif magtype=='appmagap1':
      dmagtype='dappmagap1'
     elif magtype=='appmagap2':
      dmagtype='dappmagap2'
     elif magtype=='appmagap3':
      dmagtype='dappmagap3'
     elif magtype=='mag':
      dmagtype='dmag'

     invert=False
     query = '''SELECT %s, ((mjd+2400000.5)-(to_days(now())+1721059.5+hour(curtime())/24+minute(curtime())/60/24)) as daysago ''' % magtype
     query += '''FROM dataredulco '''
     query += '''WHERE %s is not null and targid=%s ''' % (magtype,targid)
     query += ''' and %s !=  9999   ''' % magtype
     query += '''ORDER BY daysago desc'''
     cursor = sqlquery(db,query)
     if len(cursor) == 0:
         if magtype=='mag':
             magtype='psfmag'
             dmagtype='psfdmag'
             query = '''SELECT %s, ((mjd+2400000.5)-(to_days(now())+1721059.5+hour(curtime())/24+minute(curtime())/60/24)) as daysago ''' % magtype
             query += '''FROM dataredulco '''
             query += '''WHERE %s is not null and targid=%s ''' % (magtype,targid)
             query += ''' and %s !=  9999   ''' % magtype
             query += '''ORDER BY daysago desc'''
             cursor = sqlquery(db,query)
             if len(cursor) == 0:
                 return ('', 0, 0, 0, 0)
             else:
                invert=True
         else:
             return ('', 0, 0, 0, 0)

     days,psfmag=zip(*[[i['daysago'],i[magtype]] for i in cursor])
     maxt=max(days)
     mint=min(days)
     interval = maxt-mint
     mint = mint-0.1*interval
     maxt = maxt+0.1*interval

     minmag = min(psfmag)
     maxmag = max(psfmag)

     query  = '''SELECT distinct p.filter, p.telescope, p.instrument '''
     query += '''FROM dataredulco as p '''
     query += '''WHERE p.%s is not null ''' % magtype
     query += ''' and p.filetype = %s ''' % str(_ft)
     query += ''' and %s !=  9999   '''  %  magtype
     query += '''AND p.targid=%s ''' % targid

     cursor = sqlquery(db,query)
     if len(cursor)>=1:
         if plottype == 'flot':
             lcdata = '[ '
             for row in cursor:
                 lcdata += '''{label: "%s %s", ''' %(row['telescope'],row['filter'])
                 if row['filter'] in filtclr:
                     clr = filtclr[row['filter']]
                 else:
                     clr = 'black' 
                 lcdata += ''' points: {show: true, fill: true, fillColor: "%s", type: "o", radius: 2, errorbars: "y", yerr: {show:true, upperCap: "-", lowerCap: "-", radius: 2} }, ''' %clr
                 lcdata += ''' color: "%s", ''' %clr
                 lcdata += ''' data: [ ''' 
                 query =  '''SELECT ((p.mjd+2400000.5)-(to_days(now())+1721059.5+hour(curtime())/24+minute(curtime())/60/24)) as daysago, '''
                 query += '''p.%s, p.%s  ''' % (magtype,dmagtype)
                 query += '''FROM dataredulco as p '''
                 query += '''WHERE p.%s is not null ''' % magtype
                 query += ''' and p.filetype = %s ''' % str(_ft)
                 query += ''' and p.%s !=  9999   '''  % magtype
                 query += '''AND p.targid=%s ''' %targid
                 query += '''AND p.filter='%s' ''' %row['filter']
                 datacursor = sqlquery(db,query)
                 for datarow in datacursor:
                     if datarow[dmagtype] == 9999: #HACK, need to find out why this happens (not null mag but 9999 emag)
                         datarow[dmagtype] = 0 
                     lcdata += '''[%s, %s, %s], ''' %(datarow['daysago'], datarow[magtype], datarow[dmagtype])
                 if lcdata[-2:] == ', ':
                     lcdata = lcdata[:-2] # remove last apostrophe
                 lcdata += ''' ] }, '''
             lcdata = lcdata[:-2] # remove last apostrophe
             lcdata += ''' ]''' 
    
         elif plottype == 'google':
             lcdata  = '''['Days Ago','Mag','MagLow','MagHigh',],'''             
         else:
             lcdata = '[]'   
     else:
         lcdata = '[]'
 else:
     lcdata = []
     mint = 0
     maxt = 0
     minmag = 0
     maxmag = 0
 return (lcdata, mint, maxt, minmag, maxmag)


########################################################################################################################
def triggercadence(SN0,SN_RA,SN_DEC,_targid,_form,observations={},proposal=agnkey.util.readpass['proposal']):
    sss='<form style="background-color:#F5F5DC" action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<p> <h3 style="background-color:#F5F5DC"> TRIGER NEW OBSERVATION  <input type="submit" value="Send"> </h3></p>'+\
        '<input type="hidden" name="sn_name" value='+str(SN0)+'>'+\
        '<input type="hidden" name="SN_RA" value="'+str(SN_RA)+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(SN_DEC)+'">'+\
        '<input type="hidden" name="targid" value="'+str(_targid)+'">'
    for key in observations:
        if 'xxx' in key:
            sss=sss+'<input type="hidden" name="'+str(key)+'" value="'+str(observations[key])+'">'        
    sss=sss+'<input type="hidden" name="type" value="triggercadence">'+\
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
         '<tr><td> cadence [days]: </a>'+\
         '<input name="cadence" size="4" maxlength="4" type="text" /></td></tr>'+\
         '<tr><td> airmass limit: </a>'+\
         '<input name="airmass" size="4" maxlength="4" default="1.6" type="text" /></td></tr>'+\
         '<tr><td> obs mode: </a> <select name="obsmode">'+\
         '<option value="normal"> normal </option> '+\
         '<option value="ToO"> too </option> '+\
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

#################################
######################################################################################################
def triggerfloydscadence(SN0,SN_RA,SN_DEC,_targetid,_form,observations={},proposal=agnkey.util.readpass['proposal']):
    sss='<form style="background-color:#F5F5DC " action="agnupdatetable.py" enctype="multipart/form-data" method="post">'+\
        '<p> <h3 style="background-color:#F5F5DC "> TRIGER NEW OBSERVATION   <input type="submit" value="Send"> </h3></p>'+\
        '<input type="hidden" name="sn_name" value='+str(SN0)+'>'+\
        '<input type="hidden" name="SN_RA" value="'+str(SN_RA)+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(SN_DEC)+'">'+\
        '<input type="hidden" name="targid" value="'+str(_targetid)+'">'
    for key in observations:
        if 'xxx' in key:
            sss=sss+'<input type="hidden" name="'+str(key)+'" value="'+str(observations[key])+'">'        
    sss=sss+'<input type="hidden" name="type" value="triggerfloydscadence">'+\
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
    sss=sss+'<td width=10> <div class="styled-select"> number of spectra : <select name="nexpfloyds'+'"  width:100px;>'+\
         '<option  width=10 value="1"> 1</option>'+\
         '<option  width=10 value="2"> 2</option>'+\
         '<option  width=10 value="3"> 3</option>'+\
         '<option  width=10 value="4"> 4</option>'+ '</select></div></td>'
    sss=sss+'</tr>'+\
         '</table>'+\
         '<table>'+\
         '<tr><td> site: <select name="site">'+\
         '<option value="any"> any</option>'+\
         '<option value="ogg">FTN</option>'+\
         '<option value="coj">FTS</option>'+\
         '</select></td></tr>'+\
         '<tr><td> slit: <select name="slit">'+\
         '<option value="default">default </option>'+\
         '<option value="1.2">1.2</option>'+\
         '<option value="1.6">1.6</option>'+\
         '<option value="2.0">2.0</option>'+\
         '<option value="6.0">6.0</option>'+\
         '</select></td></tr>'+\
         '<tr><td> cadence [days]: </a>'+\
         '<input name="cadence" size="4" maxlength="4" type="text" /></td></tr>'+\
         '<tr><td> airmass limit: </a>'+\
         '<input name="airmass" size="4" maxlength="4" default="1.6" type="text" /></td></tr>'+\
         '<tr><td> obs mode: </a> <select name="obsmode">'+\
         '<option value="normal"> normal </option> '+\
         '<option value="ToO"> too </option> '+\
         '</select></td></tr>'+\
         '<tr><td> mode: </a> <select name="acmode">'+\
         '<option value="wcs" > wcs </option>'+\
         ' <option value="brightest" > brightest </option>'+\
         '</select></td></tr>'+\
         '<tr><td> proposal: <select name="proposal">'
    for kk in proposal:
             sss=sss+'<option value="'+kk+'"> '+kk+' </option> '
    sss=sss+'</select></td></tr>'+\
         '</table>'+\
         '</form>'
    return sss         

################################################################################
