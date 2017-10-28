#!/dark/usr/anaconda/bin/python

import agnkey
import numpy as np
import os,string,re
import datetime,time,ephem
import requests


def getstatus_all(token,status,date,user='stefano_valenti1',proposal='KEY2014A-002'):
    req = 'https://observe.lco.global/api/userrequests/' + '?limit=1000&'+\
          'proposal=' + proposal + '&'+\
          'created_after=' + date + '&'+\
          'user=' + user
    if status:
        req = req + '&state=' + status
    print req
    ss = requests.get(req, headers={'Authorization': 'Token ' + token})
    return ss.json()


def updatetriggerslog(ll0):
    username, passwd = agnkey.util.readpass['odinuser'], agnkey.util.readpass['odinpasswd']
    token = agnkey.util.readpass['token']
    track = ll0['tracknumber']
    _status = ''
    if track!=0:
        _dict = agnkey.util.getstatus_new(token,str(track).zfill(10))
    else:
        print ll0
        print 'warning track number 0'
        _dict={}

    #################   update status
    if 'state' in _dict.keys():
        _status=_dict['state']
        if ll0['status']!=_status:
            agnkey.agnsqldef.updatevalue('triggerslog', 'status', _status, track,
                                         connection='agnkey',namefile0='tracknumber')
    else:
        _status = 'NULL'

    
    #################   update reqnumber
    if 'requests' in _dict.keys():
        _reqnumber = _dict['requests'][0]['id']
        if str(ll0['reqnumber']).zfill(10)!= _reqnumber:
            agnkey.agnsqldef.updatevalue('triggerslog', 'reqnumber', _reqnumber, track,
                                         connection='agnkey',namefile0='tracknumber')
    else:
       _reqnumber = ''

    return _status
        
############################################################################
# LOAD ALL TRIGGER OF THE LAST 7 DAYS
datenow = datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday)
date = (datenow+datetime.timedelta(-15)).strftime('%Y-%m-%d')
status = ''
token = agnkey.util.readpass['token']
all = getstatus_all(token,status,date)
result = {}
for line in all['results']:
    if line['requests']:
        result[line['id']] = [line['state'],line['requests'][-1]['id']]
    else:
        result[line['id']] = [line['state'], 0 ]

#   UPDATE STATUS 
command1 = ['select t.*,d.filters,d.mode from triggerslog as t join triggers as d where t.status is NULL and d.id = t.triggerid']
data11 = agnkey.agnsqldef.query(command1)
if len(data11):
    try:
        for data2 in data11:
          track = data2['tracknumber']
          if track!=0:
            if track in result:
                _status = result[track][0]
                _reqnumber = result[track][1]
                agnkey.agnsqldef.updatevalue('triggerslog', 'status', _status, track,
                                           connection='agnkey',namefile0='tracknumber')
                if _reqnumber:
                    agnkey.agnsqldef.updatevalue('triggerslog', 'reqnumber', _reqnumber, track,
                                               connection='agnkey',namefile0='tracknumber')
            else:
                #
                #  replace quering one by one with a single query
                #
                print 'warning problems here '+str(track)
                _status = 'COMPLETED'
                #_status = updatetriggerslog(data2)
            print _status
          else:
              print 'warning track number = 0 '
    except:
        pass

_lunar = 20
_jd = ephem.julian_date()

command2 = ['select t.*,d.filters,d.mode,d.instrument from triggerslog as t join triggers as d where t.status = "PENDING" and d.id = t.triggerid']  
data3 = agnkey.agnsqldef.query(command2)
if len(data3):
    print  'ID    JD_NOW        STATUS      END_WINDOW'
    for data2 in data3:
        track = data2['tracknumber']
        if track in result:
            _status = result[track][0]
            _reqnumber = result[track][1]
            agnkey.agnsqldef.updatevalue('triggerslog', 'status', _status, track,
                                         connection='agnkey',namefile0='tracknumber')
            if _reqnumber:
                agnkey.agnsqldef.updatevalue('triggerslog', 'reqnumber', _reqnumber, track,
                                             connection='agnkey',namefile0='tracknumber')
            else:
                #  replace old method
                _status = 'COMPLETED'
                #_status = updatetriggerslog(data2)

        print data2['id'], _jd , _status, data2['windowend']
        if _status == 'PENDING' and _jd - data2['windowend'] > 0.9:
                print 'warning this observation is still PENDING but window is over'
                agnkey.agnsqldef.updatevalue('triggerslog', 'status', 'UNSCHEDULABLE', data2['id'],
                                             connection='agnkey',namefile0='id')

command3 = ['select t.*,l.name,l.ra_sn,l.dec_sn from triggers as t join lsc_sn_pos as l where active = 1 and l.id = t.targid']
data = agnkey.agnsqldef.query(command3)


Warningdictionary={}
if len(data):
    ll = {}
    for jj in data[0].keys(): 
        ll[jj] = []
    for i in range(0,len(data)):
        for jj in data[0].keys(): 
            ll[jj].append(data[i][jj])

    for jj,activeid in enumerate(ll['id']):
#      if activeid in [265]:# 93:# [61,66,67]: 
#      if activeid in [243]:# 93:# [61,66,67]: 
        _jd = ephem.julian_date()
        print '\n'
        print '### id = ' + str(ll['id'][jj])
        print '### name = ' + ll['name'][jj]
        print '### filters = '+str(ll['filters'][jj])
        print '### cadence = '+str(ll['cadence'][jj])
        print '### mode = '  + str(ll['mode'][jj])
        print '### instrument = '  + str(ll['instrument'][jj])
        print '### trigger = '+ str(activeid)
        print '\n'
        command1 = ['select t.*,d.filters from triggerslog as t join triggers as d where t.triggerid = '+str(activeid)+' and d.id = t.triggerid order by windowend desc limit 3'] # and t.status="PENDING"']
        data1 = agnkey.agnsqldef.query(command1)
        trigger = False
        if len(data1):
            jd0 = 0
            for data2 in data1:
                track = data2['tracknumber']
                if track in result:
                    _status = result[track][0]
                    _reqnumber = result[track][1]
                    agnkey.agnsqldef.updatevalue('triggerslog', 'status', _status, track,
                                                 connection='agnkey', namefile0='tracknumber')
                    if _reqnumber:
                        agnkey.agnsqldef.updatevalue('triggerslog', 'reqnumber', _reqnumber, track,
                                                     connection='agnkey', namefile0='tracknumber')
                else:
                    print 'Warning: trigger not found'
                    #_status = updatetriggerslog(data2)
                    _status = 'COMPLETED'

                if _status == 'PENDING':
                    jd0 = _jd              
                elif _status == 'COMPLETED':
                    jd0 = max(jd0,data2['windowend'])
                elif _status in ['UNSCHEDULABLE','CANCELED','WINDOW_EXPIRED']:
                    pass
                else:
                    print 'status not recognized '+str(_status)
            if jd0==0:
                print 'no observation completed'
                trigger=True
            else:
                print 'last observation '+str(float(_jd)-float(jd0))+' days ago'
                print 'cadence '+str(ll['cadence'][jj])   # .1 to take in account the trigger time
                if float(ll['cadence'][jj]) <= 1:
                    if float(_jd)-float(jd0) > .001:
                        print 'cadence less or equal to one day'
                        print 'last window ended, trigger'
                        trigger=True
                elif 1 < float(ll['cadence'][jj]) <= 2:
                    print 'cadence between 1 and 2 days'
                    print 'trigger if it is cadence-.3 days from end of the window'
                    if float(ll['cadence'][jj])-.3 <= float(_jd)-float(jd0):
                        trigger=True
                else: 
                    print 'trigger if it is cadence-.3 days from end of the window'
                    if float(ll['cadence'][jj])-.3 <= float(_jd)-float(jd0):
                        print 'trigger new observation'
                        trigger=True
                    else:
                        print 'last observation less than '+str(ll['cadence'][jj])+' days ago, do not trigger'
        else:
            print 'no trigger for this '+str(activeid)
            trigger = True


        if trigger:
            SN_RA = ll['ra_sn'][jj]
            SN_DEC = ll['dec_sn'][jj]
            NAME = ll['name'][jj]
            _airmass = ll['airmass'][jj]
            _proposal = ll['proposal'][jj]
            _site = ll['site'][jj]
            _targid = ll['targid'][jj]
            _mode   = ll['mode'][jj]
            proposals = agnkey.util.readpass['proposal']
            users = agnkey.util.readpass['users']
            token = agnkey.util.readpass['token']
            if not _proposal:   
                _proposal=proposals[0]
                _user0=users[0]
            else:
                _user0=users[proposals.index(_proposal)]
                passwd=agnkey.util.readpass['odinpasswd']

            datenow = datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday,\
                                        time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)

            datenow = datenow + datetime.timedelta(2./1440.)

            if float(ll['cadence'][jj])<1:
                print 'cadence less than 24h'
                dd1 = datenow + datetime.timedelta(float(ll['cadence'][jj]))
                dd2 = datenow + datetime.timedelta(float(ll['cadence'][jj]))*2 
                dd3 = datenow + datetime.timedelta(float(ll['cadence'][jj]))*3
                utstart = [datenow,dd1,dd2]
                utend = [dd1,dd2,dd3]
            else:
                utstart = [datenow]
                utend = [datenow + datetime.timedelta(1)]

            ################# loop on triggers
            for mm,nn in enumerate(utstart): 
                 if ll['filters'][jj] == 'floyds':
                     expvec = ll['exptime'][jj]
                     nexpvec = ll['numexp'][jj]
                     _slit = str(ll['slit'][jj])
                     _acmode = str(ll['acqmode'][jj])
                     if _acmode != 'brightest':
                         _acmode ='wcs'

                     print 'trigger floyds observations'
                     print str(NAME),expvec,str(SN_RA),str(SN_DEC),str(utstart[mm]),str(utend[mm]),_user0,token,\
                         _proposal,str(_airmass),_site,_slit,'after', nexpvec 
                     logfile,pp = agnkey.util.sendfloydstrigger_new(str(NAME),expvec,str(SN_RA),str(SN_DEC),\
                                                             str(utstart[mm]),str(utend[mm]),_user0, token,
                                                             _proposal,_lunar,str(_airmass),_site,_slit,'after',\
                                                             nexpvec, _acmode, mode= _mode )
                     print logfile
                     try:
                         input_datesub, input_str_smjd, input_str_emjd, _site2, _instrument2, _nexp2, _exp2, _airmass2,\
                             _prop2, _user2, _seeing2, _sky2, _priority2, tracknum, reqnum = string.split(logfile)
                         dictionary={'targid':int(_targid), 'triggerjd':float(input_datesub),'windowstart':float(input_str_smjd),\
                                     'windowend':float(input_str_emjd), 'reqnumber':int(reqnum),'tracknumber':int(tracknum),\
                                     'triggerid':activeid}
                         agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'triggerslog',dictionary) 
                     except:
                         Warningdictionary[str(ll['id'][jj])]=''+\
                             '\n### id = ' + str(ll['id'][jj])+\
                             '\n### name = ' + ll['name'][jj]+\
                             '\n### filters = '+str(ll['filters'][jj])+\
                             '\n### instrument = '+str(ll['instrument'][jj])+\
                             '\n### cadence = '+str(ll['cadence'][jj])+\
                             '\n### trigger = '+ str(activeid)+'\n\n'+str(pp)
                 else:
                     filtvec = string.split(ll['filters'][jj],',')
                     nexpvec = string.split(ll['numexp'][jj],',')
                     expvec = string.split(ll['exptime'][jj],',')
                     _instrument = ll['instrument'][jj]
                     print 'trigger photometric observations'
                     print str(NAME),str(SN_RA),str(SN_DEC),expvec,nexpvec,filtvec,str(utstart[mm]),str(utend[mm]),\
                         _user0,token,_proposal,_instrument,_airmass,_site,_mode
                     logfile,python_dict = agnkey.util.sendtrigger2_new(str(NAME),str(SN_RA),str(SN_DEC),\
                                                                                                 expvec,nexpvec, filtvec,str(utstart[mm]),\
                                                                                                 str(utend[mm]),_user0, token, _proposal,\
                                                                                                 _instrument,_airmass, _lunar, _site, mode= _mode )

                     print logfile
                     print python_dict
                     good = False
                     if logfile:
                         input_datesub, input_str_smjd, input_str_emjd, _site2, _filters2, _nexp2, _exp2, _airmass2,\
                             _prop2, _user2, _seeing2, _sky2, _instrument2, _priority2, tracknum, reqnum = string.split(logfile)
                         if int(tracknum) !=0:
                             print logfile
                             good =True

                     if good:
                         dictionary={'targid':int(_targid),'triggerjd':float(input_datesub),'windowstart':float(input_str_smjd),\
                                     'windowend':float(input_str_emjd),'reqnumber':int(reqnum),'tracknumber':int(tracknum),\
                                     'triggerid':activeid}                         
                         agnkey.agnsqldef.insert_values(agnkey.agnsqldef.conn,'triggerslog', dictionary)
                     else:
                         Warningdictionary[str(ll['id'][jj])]=''+\
                             '\n### id = ' + str(ll['id'][jj])+\
                             '\n### name = ' + ll['name'][jj]+\
                             '\n### filters = '+str(ll['filters'][jj])+\
                             '\n### instrument = '+str(ll['instrument'][jj])+\
                             '\n### cadence = '+str(ll['cadence'][jj])+\
                             '\n### mode    = '+str(ll['mode'][jj])+\
                             '\n### trigger = '+ str(activeid)+\
                             '\n### log = '+str(logfile)+\
                             '\n### python_dict = '+str(python_dict)+\
                             '\n\n'                             
else:
    print 'no active objects'

print Warningdictionary
if len(Warningdictionary):
    _from = 'stfn.valenti@gmail.com'
    _to1  = 'stfn.valenti@gmail.com'
    _subject = 'agnkey warning '
    text = ''
    for jj in Warningdictionary:
        text = text + Warningdictionary[jj]

    agnkey.util.sendemail(_from,_to1,_subject,text)

