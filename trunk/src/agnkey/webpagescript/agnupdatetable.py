#!/dark/usr/anaconda/bin/python                                                                                                                               
#/usr/bin/env python                                                                                                                                          

import sys,os,cgi,string,glob,re
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
    location='SV'
else:
    location='deneb'
    sys.path.append('/home/cv21/lib/python2.7/site-packages/')

os.environ['HOME']='../tmp/'
import agnkey
from agnkey.agnsqldef import conn
import datetime,time,ephem

base_url = hostname
line00=''
####### user 
###### parameters
form = cgi.FieldStorage()
     ############ type   #########
_type = form.getlist('type')
if not _type:
    try: _type=sys.argv[1]
    except: pass
else: _type=_type[0]
    ##########   user  #########
if form.getlist('user'): _user=form.getlist('user')[0]
else:                    _user=''
if not _user: 
    _user=os.getenv("REMOTE_USER")
    if not _user: _user='SV'
    ##########   observations  #########
observations={}
for key in form:
    if 'xxx' in key:
        observations[key]=form.getlist(key)[0]    
    ##########   SN  #########
if form.getlist('sn_name'): SN=form.getlist('sn_name')[0]
else:                        SN=''
    ##########   SN_RA  #########
if form.getlist('SN_RA'): SN_RA=form.getlist('SN_RA')[0]
else:                      SN_RA=''
    ##########   SN_DEC  #########
if form.getlist('SN_DEC'): SN_DEC=form.getlist('SN_DEC')[0]
else:                       SN_DEC=''
    ##########   note  #########
if form.getlist('note'): _note=form.getlist('note')[0]
else:                        _note=''
    ##########   targid  #########
if form.getlist('targid'): _targid=form.getlist('targid')[0]
else:                        _targid=''
    ##########   id  #########
if form.getlist('id'): _id=form.getlist('id')[0]
else:                        _id=''
    ##########   site  #########
if form.getlist('site'): _site=form.getlist('site')[0]
else:                        _site=''
    ##########   vector  #########
if form.getlist('vector'): _vector=form.getlist('vector')[0]
else:                        _vector=''
    ##########   key  #########
if form.getlist('key'): _key=form.getlist('key')[0]
else:                        _key=''
    ##########   ntriggers  #########
if form.getlist('ntriggers'): _ntriggers=form.getlist('ntriggers')[0]
else:                        _ntriggers=''
    ##########   airmass  #########
if form.getlist('airmass'): _airmass=form.getlist('airmass')[0]
else:                        _airmass=''
    ##########   namefile  #########
if form.getlist('namefile'): _namefile=form.getlist('namefile')[0]
else:                        _namefile=''
    ##########   proposal  #########
if form.getlist('proposal'): _proposal=form.getlist('proposal')[0]
else:                        _proposal=''
    ##########   instrument  #########
if form.getlist('instrument'): _instrument=form.getlist('instrument')[0]
else:                        _instrument=''
    ##########   filetype  #########
if form.getlist('filetype'): _filetype=form.getlist('filetype')[0]
else:                        _filetype=''
    ##########   access  #########
if form.getlist('access'): _access=form.getlist('access')[0]
else:                        _access=''
    ##########   expfloyds  #########
if form.getlist('expfloyds'): _expfloyds=form.getlist('expfloyds')[0]
else:                        _expfloyds=''
    ##########   nexpfloyds  #########
if form.getlist('nexpfloyds'): _nexpfloyds = form.getlist('nexpfloyds')[0]
else:                        _nexpfloyds = 1
    ##########   slit  #########
if form.getlist('slit'): _slit=form.getlist('slit')[0]
else:                        _slit=''
    ##########   filt,exp,nexp  #########
filtvec=[]
expvec=[]
nexpvec=[]
for jj in 'UBVRIugriz':
    if form.getlist(jj):
        filtvec.append(form.getlist(jj)[0])
        expvec.append(form.getlist('exp'+str(jj))[0])
        nexpvec.append(form.getlist('n'+str(jj))[0])
    #########  output format  ############
if form.getlist('outputformat'): outputformat=form.getlist('outputformat')[0]
else:                             outputformat=''
###################################################
commandg=["select groupname from userstab where user='"+str(_user)+"'"]
gg=agnkey.agnsqldef.query(commandg)
datenow=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
_date=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec).date() 

###########################   need to start the page here 
print "Content-Type: text/html\n"
print '<html>'
print '<body>'
############################
#print SN_RA,SN_DEC,SN
if _type=='add':
    if not _note:
        print "Content-Type: text/html\n"
        print '<html>'
        print '<body>'
        print '<h3>warning: note is empty </h3>'
        print '</html>'
        print '</body>'
        sys.exit()
    else:
        _table='noteobjects'
        dictionary={'targid':int(_targid),'note':_note,'datenote':_date, 'user':_user}
        agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,_table,dictionary)

        dictionary1={'targid':int(_targid),'note':_note,'dateobs':_date, 'users':_user,'command':'add','tables':'noteobjects'}
        agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)
        
elif _type=='delete':
    if not _id:
        print "Content-Type: text/html\n"
        print '<html>'
        print '<body>'
        print '<h3>warning: note is empty </h3>'
        print '</html>'
        print '</body>'
        sys.exit()
    else:
        _table='noteobjects'
        agnkey.agnsqldef.deleteredufromarchive(_id,_table,'id')

        dictionary1={'targid':int(_targid),'note':_note,'dateobs':_date, 'users':_user,'command':'delete','tables':'noteobjects'}
        agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)
        
elif _type=='delspectrum':
     _table='dataspectraexternal'
     all1=agnkey.agnsqldef.getfromdataraw(agnkey.agnsqldef.conn, _table, 'id', _id,column2='*')
     if len(all1)==1:
         _file=re.sub(agnkey.util.workingdirectory,'../',all1[0]['directory']+all1[0]['namefile'])
         os.system('rm '+_file)
         agnkey.agnsqldef.deleteredufromarchive(_id,_table,'id')
         dictionary1={'targid':int(_targid),'note':_namefile,'dateobs':_date, 'users':_user,'command':'delete','tables':_table}
         agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)
         
elif _type=='newobject':
    if (int(gg[0]['groupname']) & 1023):
        if SN and SN_RA and SN_DEC:
            if SN_RA:
               if string.count(str(SN_RA),':'):
                    r0,r1,r2=string.split(SN_RA,':')
                    SN_RA=(float(r0)+(float(r1)/60.)+(float(r2)/3600.))*15
               else: SN_RA=float(SN_RA)
            if SN_DEC:
               if string.count(str(SN_DEC),':'):
                    d0,d1,d2=string.split(SN_DEC,':')
                    if '-' in d0:   SN_DEC=(float(abs(float(d0)))+(float(d1)/60.)+(float(d2)/3600.))*(-1)
                    else:           SN_DEC=float(abs(float(d0)))+(float(d1)/60.)+(float(d2)/3600.)
               else: SN_DEC=float(SN_DEC)
            _table='lsc_sn_pos'
            dictionary1={'name':SN,'ra_sn':float(SN_RA),'dec_sn':float(SN_DEC),'objtype':'agn'}
            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,_table,dictionary1)
            bb=agnkey.agnsqldef.getfromcoordinate(agnkey.agnsqldef.conn, 'lsc_sn_pos', SN_RA, SN_DEC,.01056)
            agnkey.agnsqldef.updatevalue('lsc_sn_pos','targid',bb[0]['id'],SN,connection='agnkey',namefile0='name')
            dictionary={'name':SN,'targid':bb[0]['id']}
            _JDn=ephem.julian_date()-2400000
            dictionary1={'targid':bb[0]['id'],'groupname':1023,'jd':_JDn}          
            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'recobjects',dictionary)
            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'permissionlog',dictionary1)

            dictionary2={'targid':int(bb[0]['id']),'note':SN,'dateobs':_date, 'users':_user,'command':'newobject','tables':'lsc_sn_pos'}
            agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary2)
            
        else:
            print "Content-Type: text/html\n"
            print '<html>'
            print '<body>'
            print '<h3>warning: NAME, RA and DEC should all be defined</h3>'
            print '</html>'
            print '</body>'
            sys.exit()
    else:
        print "Content-Type: text/html\n"
        print '<html>'
        print '<body>'
        print '<h3>warning: user '+str(_user)+' does not have permission to add new objects </h3>'
        print '</html>'
        print '</body>'
        sys.exit()
elif _type=='permission':
     aa=agnkey.agnsqldef.query(['select groups,groupid from groupstab order by groupid'])
     position2={}
     for i in range(0,len(aa)): position2[aa[i]['groups']]=int(aa[i]['groupid'])
     aaa=0
     if 'public' in form.keys():
         aaa=position2['public']
     else:
         for i in position2.keys(): 
             if i in form.keys():
                 if i !='public':
                     aaa=aaa+position2[i]     
     agnkey.agnsqldef.updatevalue('permissionlog','groupname',int(aaa),_id,connection='agnkey',namefile0='id')

     dictionary1={'targid':int(_targid),'note':str(aaa),'dateobs':_date, 'users':_user,'command':'update','tables':'permissionlog'}
     agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)
     
elif _type=='catalogue':
    agnkey.agnsqldef.updatevalue('lsc_sn_pos',_key,_note,_id,connection='agnkey',namefile0='id')

    dictionary1={'targid':int(_targid),'note':str(_key)+' '+str(_note),'dateobs':_date, 'users':_user,'command':'update','tables':'lsc_sn_pos'}
    agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)

elif _type=='markasbad':
    agnkey.agnsqldef.updatevalue('datarawfloyds',_key,_note,_id,connection='agnkey',namefile0='id')
    print _date,_note,_key,_user,_targid
    dictionary1={'targid':int(_targid),'note':str(_key)+' '+str(_note),'dateobs':_date, 'users':_user,'command':'update','tables':'lsc_sn_pos'}
    agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)

    
elif _type=='catalogue2':
    agnkey.agnsqldef.updatevalue('lsc_sn_pos',_key,_note,_id,connection='agnkey',namefile0='id')

    dictionary1={'targid':int(_targid),'note':str(_key)+' '+str(_note),'dateobs':_date, 'users':_user,'command':'update','tables':'lsc_sn_pos'}
    agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)
    
elif _type=='recinfo':
    _table='recobjects'
    dictionary={'targid':int(_targid),'name':_note}
    agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,_table,dictionary)

    dictionary1={'targid':int(_targid),'note':str(_note),'dateobs':_date, 'users':_user,'command':'add','tables':'recobjects'}
    agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)
    
elif _type=='download':
     _JDn=ephem.julian_date()-2400000
     f=open('../tmp/download_'+str(_JDn)+'_'+_user+'.sh','w')
     f.write(re.sub('xxxx',_note,_vector))
     f.close()
     print "Content-Type: text/html\n"
     print '<html>'
     print '<body>'
     print '<h4> <a href="../tmp/download_'+str(_JDn)+'_'+_user+'.sh"><b>&bull;</b> source file to downoad data </a></h4>'
     print '</body>'
     print '</html>'
     dictionary1={'targid':int(_targid),'note':'download_'+str(_JDn)+'_'+_user+'.sh','dateobs':_date, 'users':_user,'command':'download','tables':'dataredulco'}
     agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'userslog',dictionary1)
     sys.exit()

     
elif _type=='trigger':
    print "Content-Type: text/html\n"
    print '<html>'
    print '<body>'
    print _ntriggers
    print _instrument
    print _proposal

    print '</body>'
    print '</html>'
    if _ntriggers=='1':
        utstart=[datenow]
        utend=[datenow+datetime.timedelta(1)]
    elif _ntriggers=='2':
        utstart=[datenow,datenow+datetime.timedelta(1)]
        utend=[datenow+datetime.timedelta(1),datenow+datetime.timedelta(2)]
    elif _ntriggers=='3':
        utstart=[datenow,datenow+datetime.timedelta(.5)]
        utend=[datenow+datetime.timedelta(.5),datenow+datetime.timedelta(1)]
    elif _ntriggers=='4':
        utstart=[datenow,datenow+datetime.timedelta(.5),\
                 datenow+datetime.timedelta(1),datenow+datetime.timedelta(1.5)]
        utend=[datenow+datetime.timedelta(.5),datenow+datetime.timedelta(1),\
               datenow+datetime.timedelta(1.5),datenow+datetime.timedelta(2)]
    elif _ntriggers=='5':
        utstart=[datenow]
        utend=[datenow+datetime.timedelta(6)]
    elif _ntriggers=='6':
        utstart=[datenow,datenow+datetime.timedelta(3)]
        utend=[datenow+datetime.timedelta(3),datenow+datetime.timedelta(6)]
    elif _ntriggers=='7':
        utstart=[datenow,datenow+datetime.timedelta(2), datenow+datetime.timedelta(4)]
        utend=[datenow+datetime.timedelta(2),datenow+datetime.timedelta(4), datenow+datetime.timedelta(6)]
    elif _ntriggers=='8':
        utstart=[datenow,datenow+datetime.timedelta(1),\
                 datenow+datetime.timedelta(2),datenow+datetime.timedelta(3),\
                 datenow+datetime.timedelta(4),datenow+datetime.timedelta(5),\
                 datenow+datetime.timedelta(6)]
        utend=[datenow+datetime.timedelta(1),datenow+datetime.timedelta(2),\
               datenow+datetime.timedelta(3),datenow+datetime.timedelta(4),\
               datenow+datetime.timedelta(5),datenow+datetime.timedelta(6),\
               datenow+datetime.timedelta(7)]
    elif _ntriggers=='9':
        utstart=[datenow]
        utend=[datenow+datetime.timedelta(.3333)]
    elif _ntriggers=='10':
        utstart=[datenow,datenow+datetime.timedelta(.1666),datenow+datetime.timedelta(.33333)]
        utend=[datenow+datetime.timedelta(.1666),datenow+datetime.timedelta(.33333),datenow+datetime.timedelta(.5)]
    elif _ntriggers=='13':
        utstart=[datenow,datenow+datetime.timedelta(1),\
                 datenow+datetime.timedelta(2),datenow+datetime.timedelta(3),\
                 datenow+datetime.timedelta(4),datenow+datetime.timedelta(5),\
                 datenow+datetime.timedelta(6),datenow+datetime.timedelta(7),\
                 datenow+datetime.timedelta(8),datenow+datetime.timedelta(9),\
                 datenow+datetime.timedelta(10),datenow+datetime.timedelta(11),\
                 datenow+datetime.timedelta(12),datenow+datetime.timedelta(13),\
                 datenow+datetime.timedelta(14),datenow+datetime.timedelta(15),\
                 datenow+datetime.timedelta(16),datenow+datetime.timedelta(17),\
                 datenow+datetime.timedelta(18),datenow+datetime.timedelta(19),\
                 datenow+datetime.timedelta(20),datenow+datetime.timedelta(21),\
                 datenow+datetime.timedelta(22),datenow+datetime.timedelta(23)]
        utend=[datenow+datetime.timedelta(1),datenow+datetime.timedelta(2),\
               datenow+datetime.timedelta(3),datenow+datetime.timedelta(4),\
               datenow+datetime.timedelta(5),datenow+datetime.timedelta(6),\
               datenow+datetime.timedelta(7),datenow+datetime.timedelta(8),\
               datenow+datetime.timedelta(9),datenow+datetime.timedelta(10),\
               datenow+datetime.timedelta(11),datenow+datetime.timedelta(12),\
               datenow+datetime.timedelta(13),datenow+datetime.timedelta(14),\
               datenow+datetime.timedelta(15),datenow+datetime.timedelta(16),\
               datenow+datetime.timedelta(17),datenow+datetime.timedelta(18),\
               datenow+datetime.timedelta(19),datenow+datetime.timedelta(20),\
               datenow+datetime.timedelta(21),datenow+datetime.timedelta(22),\
               datenow+datetime.timedelta(23),datenow+datetime.timedelta(24)]
    elif _ntriggers=='14':
        utstart=[datenow,datenow+datetime.timedelta(2),\
                 datenow+datetime.timedelta(4),datenow+datetime.timedelta(6),\
                 datenow+datetime.timedelta(8),datenow+datetime.timedelta(10),\
                 datenow+datetime.timedelta(12),datenow+datetime.timedelta(14),\
                 datenow+datetime.timedelta(16),datenow+datetime.timedelta(18),\
                 datenow+datetime.timedelta(20),datenow+datetime.timedelta(22)]
        utend=[datenow+datetime.timedelta(2),datenow+datetime.timedelta(4),\
               datenow+datetime.timedelta(6),datenow+datetime.timedelta(8),\
               datenow+datetime.timedelta(10),datenow+datetime.timedelta(12),\
               datenow+datetime.timedelta(14),datenow+datetime.timedelta(16),\
               datenow+datetime.timedelta(18),datenow+datetime.timedelta(20),\
               datenow+datetime.timedelta(22),datenow+datetime.timedelta(24)]
    elif _ntriggers=='15':
        delta = .33333333
        utstart = [datenow]
        utend   = [datenow+datetime.timedelta(delta)]
        for kk in range(1,21):
            utstart.append(datenow+datetime.timedelta(delta*kk))
            utend.append(datenow+datetime.timedelta(delta*(kk+1)))

    proposals=agnkey.util.readpass['proposal']
    users=agnkey.util.readpass['users']
    if not _proposal:   
        _proposal=proposals[0]
        _user0=users[0]
    else:
        _user0=users[proposals.index(_proposal)]
    passwd=agnkey.util.readpass['odinpasswd']
    print utstart[0],utend[0]
    for mm in range(0,len(utstart)):
        print str(SN),str(SN_RA),str(SN_DEC),expvec,nexpvec,filtvec,str(utstart[mm]),str(utend[mm]),_user0,_proposal,_airmass,_site,_instrument
        logfile=agnkey.util.sendtrigger2(str(SN),str(SN_RA),str(SN_DEC),expvec,nexpvec,filtvec,str(utstart[mm]),str(utend[mm]),_user0,passwd,_proposal,_instrument,_airmass,_site)

        line00= line00+'<p> '+logfile+' '+str(_targid)+' </p>'
        input_datesub,input_str_smjd,input_str_emjd,_site2,_filters2,_nexp2,_exp2,_airmass2,_prop2,_user2,_seeing2,_sky2,_instrument2,_priority2,tracknum,reqnum=string.split(logfile)
        dictionary={'user':_user,'targid':int(_targid),'triggerjd':float(input_datesub),'windowstart':float(input_str_smjd),\
                    'windowend':float(input_str_emjd),'filters':_filters2,'exptime':_exp2,'numexp':_nexp2,'proposal':_prop2,\
                    'site':_site2,'instrument':_instrument2,'sky':float(_sky2),'seeing':float(_seeing2),\
                    'airmass':float(_airmass2),'reqnumber':int(reqnum),'tracknumber':int(tracknum)}
        agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'obslog',dictionary)

elif _type=='triggerfloyds':
    print _ntriggers
    print _instrument
    print _proposal

    if _ntriggers=='1':
        utstart=[datenow]
        utend=[datenow+datetime.timedelta(1)]
    elif _ntriggers=='2':
        utstart=[datenow,datenow+datetime.timedelta(1)]
        utend=[datenow+datetime.timedelta(1),datenow+datetime.timedelta(2)]
    elif _ntriggers=='3':
        utstart=[datenow,datenow+datetime.timedelta(.5)]
        utend=[datenow+datetime.timedelta(.5),datenow+datetime.timedelta(1)]
    elif _ntriggers=='4':
        utstart=[datenow,datenow+datetime.timedelta(.5),\
                 datenow+datetime.timedelta(1),datenow+datetime.timedelta(1.5)]
        utend=[datenow+datetime.timedelta(.5),datenow+datetime.timedelta(1),\
               datenow+datetime.timedelta(1.5),datenow+datetime.timedelta(2)]
    elif _ntriggers=='5':
        utstart=[datenow]
        utend=[datenow+datetime.timedelta(6)]
    elif _ntriggers=='6':
        utstart=[datenow,datenow+datetime.timedelta(3)]
        utend=[datenow+datetime.timedelta(3),datenow+datetime.timedelta(6)]
    elif _ntriggers=='7':
        utstart=[datenow,datenow+datetime.timedelta(2), datenow+datetime.timedelta(4)]
        utend=[datenow+datetime.timedelta(2),datenow+datetime.timedelta(4), datenow+datetime.timedelta(6)]
    elif _ntriggers=='8':
        utstart=[datenow,datenow+datetime.timedelta(1),\
                 datenow+datetime.timedelta(2),datenow+datetime.timedelta(3),\
                 datenow+datetime.timedelta(4),datenow+datetime.timedelta(5)]
        utend=[datenow+datetime.timedelta(1),datenow+datetime.timedelta(2),\
               datenow+datetime.timedelta(3),datenow+datetime.timedelta(4),\
               datenow+datetime.timedelta(5),datenow+datetime.timedelta(6)]
    elif _ntriggers=='9':
        utstart=[datenow]
        utend=[datenow+datetime.timedelta(.3333)]
    elif _ntriggers=='10':
        utstart=[datenow,datenow+datetime.timedelta(.1666),datenow+datetime.timedelta(.33333)]
        utend=[datenow+datetime.timedelta(.1666),datenow+datetime.timedelta(.33333),datenow+datetime.timedelta(.5)]
    elif _ntriggers=='11':
        utstart=[datenow]
        utend=[datenow+datetime.timedelta(0.041666)]
    elif _ntriggers=='12':
        utstart=[datenow]
        utend=[datenow+datetime.timedelta(0.083333333)]

####################   chose proposal  ######################
    proposals=agnkey.util.readpass['proposal']
    users=agnkey.util.readpass['users']
    if not _proposal:
        _proposal=proposals[0]
        _user0=users[0]
    else:
        _user0=users[proposals.index(_proposal)]
    priority=1
    telclass='2m0'
    passwd=agnkey.util.readpass['odinpasswd']
    if _slit=='default':
        if _site=='coj':
            _slit='2.0'
        elif _site=='ogg':
            _slit='1.6'
        else:
            _slit='2.0'
############################################################
#
    for mm in range(0,len(utstart)):
        logfile=agnkey.util.sendfloydstrigger(str(SN),_expfloyds,str(SN_RA),str(SN_DEC),str(utstart[mm]),str(utend[mm]),_user0,passwd,_proposal,str(_airmass),_site,_slit,'after', _nexpfloyds )
#
        line00= line00+'<p> '+logfile+' '+str(_targid)+' </p>'
        _nexp2='1'
        input_datesub,input_str_smjd,input_str_emjd,_site2,_instrument2,_nexp2,_exp2,_airmass2,_prop2,_user2,_seeing2,_sky2,_priority2,tracknum,reqnum=string.split(logfile)
        _filters2='floyds'
        _instrument2='2m0'
        dictionary={'user':_user,'targid':int(_targid),'triggerjd':float(input_datesub),'windowstart':float(input_str_smjd),\
                    'windowend':float(input_str_emjd),'filters':_filters2,'exptime':_exp2,'numexp':_nexp2,'proposal':_prop2,\
                    'site':_site2,'instrument':_instrument2,'sky':float(_sky2),'seeing':float(_seeing2),\
                    'airmass':float(_airmass2),'reqnumber':int(reqnum),'tracknumber':int(tracknum)}
        agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'obslog',dictionary)    


elif _type=='spectrum':
    outputformat='agnupload.cgi'
    _force='force'
    _output=''
    fileitem = form['file']
    if fileitem.filename:
            open('../tmp/'+fileitem.filename, 'wb').write(fileitem.file.read())
            print _output,_force,_access,_note,fileitem.filename,_filetype
            _note=agnkey.agndefin.uploadspectrum('../tmp/'+fileitem.filename,_output,_force,_access,_filetype)
            print _note
            _note=re.sub('\n','<br><br>',_note)
    else:  
        _note='no spectrum uploded'

###############################################
if outputformat=='agnpermission.cgi':
    line ='<form id="myForm" action="agnpermission.cgi" method="post"></form>'
elif outputformat=='agncatalogue.cgi':
    line='<form id="myForm" action="agncatalogue.cgi" method="post"></form>'
elif outputformat=='agnmissing.cgi':
    line='<form id="myForm" action="agnmissing.cgi" method="post"></form>'
elif outputformat=='agnkeyview.cgi':
    line='<form id="myForm" action="agnkeyview.cgi" method="post">'+\
        '<input type="hidden" name="SN_RA" value="'+str(SN_RA)+'">'+\
        '<input type="hidden" name="SN_DEC" value="'+str(SN_DEC)+'">'+\
        '<input type="hidden" name="targid" value="'+str(_targid)+'">'+\
        '<input type="hidden" name="sn_name" value='+str(SN)+'></form>'
    line00=str(line00)+' '+str(SN_RA)+' '+str(SN_DEC)+' '+str(SN)+' '+str(_targid)

elif outputformat=='agnschedule.cgi':
    line ='<form id="myForm" action="agnschedule.cgi" method="post">'
    for key in observations:
        line=line+'<input type="hidden" name="'+str(key)+'" value="'+str(observations[key])+'">'
    '</form>'
elif outputformat=='agnupload.cgi':
    line='<form id="myForm" action="agnupload.cgi" method="post">'+\
        '<input type="hidden" name="note" value="'+str(_note)+'">'+\
        '<input type="hidden" name="access" value='+str(_access)+'></form>'    
else:  
    line = '<h3>outputformat not defined</h3>'
###############################################
print line
print str(line00)
print '<h3> updating database ......  </h3>'
print '<script>'
print "document.getElementById('myForm').submit();"
print '</script>'
print '</body>'
print '</html>'
