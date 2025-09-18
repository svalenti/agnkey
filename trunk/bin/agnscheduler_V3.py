#!/dark/usr/anaconda/bin/python

import agnkey
import numpy as np
import os,string,re
import datetime,time,ephem
import requests

def sendfloydstrigger_api3(_name,_exp,_ra,_dec,_utstart,_utend,username, token,proposal,_airmass=2.0, lunar=20,\
                          _site='', _slit=1.6, _calibration='after', nexp = 1, _type='wcs', mode='NORMAL'):
    ''' This definition will trigger new observations using the API Web Server
        - it takes most of the input by command line
        - some input have a default value (eg telclass,airmass,binx,biny
        - if site is specify will triger a specific telescope, otherwise will trigger on the full network
        - filters, number of exposure per filter, exposure time are vector of the same lenght
    '''
    import string
    from datetime import datetime

    def JDnow(datenow='',verbose=False):
        import datetime
        import time
        _JD0 = 2455927.5
        if not datenow:
            datenow = datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday,
                                        time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
        _JDtoday=_JD0+(datenow-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
                   (datenow-datetime.datetime(2012, 01, 01,00,00,00)).days
        if verbose: print 'JD= '+str(_JDtoday)
        return _JDtoday

    ######################3
    windows = [{
        'start': _utstart,
        'end': _utend
    }]
    #####################3

    if _site in ['ogg','coj']:
       location = {"telescope_class": "2m0", "site": _site}
    else:
       location = {"telescope_class": "2m0"}

       ######################
    if _type == 'wcs':
        acquisition_config = {
            "mode": "WCS",
            "extra_params": {
                "acquire_radius": 0.0 }}
    else:
        acquisition_config = {
            "mode": "BRIGHTEST",
            "extra_params": {
                "acquire_radius": 5.0}}    
       ######################

    guiding_config = {
        "mode":"ON",
        "optional": False,
        "exposure_time": 15.0,        
        "extra_params": {}}
       
    # Additional constraints to be added to this request 
    constraints = {
        'max_airmass': _airmass,
        'min_lunar_distrete  ance': lunar
    }

    #############################3
    target = {
        'name': _name,
        'type': 'ICRS',
        'ra': float(_ra),
        'dec': float(_dec),
        'epoch': 2000,
        "proper_motion_ra": 0.0,
        "proper_motion_dec": 0.0,
        "parallax": 0.0,
    }
    ###################################3
    slitvec={ '1.6': "slit_1.6as", '2.0': "slit_2.0as", '0.9': "slit_0.9as", '6.0': "slit_6.0as", '1.2': "slit_1.2as"}
    _slit = str(_slit)
    
    instrument_config_lamp = {
        "exposure_time": 20.0,
        "exposure_count": 1,
        "bin_x": 1,
        "bin_y": 1,
        "mode": "default",
        "rotator_mode": "VFLOAT",
        "optical_elements":{
            "slit": slitvec[_slit]
        },
        "extra_params": {
            "defocus": 0.0
        }
    }

    instrument_config_arc = {
        "exposure_time": 60.0,
        "exposure_count": 1,
        "bin_x": 1,
        "bin_y": 1,
        "mode": "default",
        "rotator_mode": "VFLOAT",
        "optical_elements":{
            "slit": slitvec[_slit]
        },
        "extra_params": {
            "defocus": 0.0
        }
    }

    instrument_config_spectrum = {
        "exposure_time": _exp,
        "exposure_count": nexp,
        "bin_x": 1,
        "bin_y": 1,
        "mode": "default",
        "rotator_mode": "VFLOAT",
        "optical_elements":{
            "slit": slitvec[_slit]
        },
        "extra_params": {
            "defocus": 0.0
        }
    }

    #############################
       
    configuration_lamp = {
        "type": "LAMP_FLAT",
        "instrument_type": "2M0-FLOYDS-SCICAM",
        "instrument_configs": [instrument_config_lamp],
        "acquisition_config": acquisition_config,
        "guiding_config": guiding_config,
        "constraints": constraints,
        "target": target
    }    

    configuration_arc = {
        "type": "ARC",
        "instrument_type": "2M0-FLOYDS-SCICAM",
        "instrument_configs": [instrument_config_arc],
        "acquisition_config": acquisition_config,
        "guiding_config": guiding_config,
        "constraints": constraints,
        "target": target
    }    

    configuration_spectrum = {
        "type": "SPECTRUM",
        "instrument_type": "2M0-FLOYDS-SCICAM",
        "instrument_configs": [instrument_config_spectrum],
        "acquisition_config": acquisition_config,
        "guiding_config": guiding_config,
        "constraints": constraints,
        "target": target
    }    

    

    if _calibration == 'all':
       configurations = [configuration_arc, configuration_lamp, configuration_spectrum, configuration_lamp, configuration_arc]
    elif _calibration =='after':
       configurations = [configuration_spectrum, configuration_lamp, configuration_arc]
    else:
       configurations = [configuration_spectrum]                            


       ############################################################################
    if mode not in ['NORMAL','TARGET_OF_OPPORTUNITY','normal','ToO']:
       mode='NORMAL'

    if mode in ['normal']:
           mode='NORMAL'
    elif mode in ['ToO']:
           mode='TARGET_OF_OPPORTUNITY'

    user_request = {
        'name': _name,  # The title
        'proposal': proposal,
        'ipp_value': 1.00,
        'operator': 'SINGLE',
        'observation_type': mode,
        'requests': [{
            'location': location,
            'configurations': configurations,
            'windows': windows
        }]
    }
    print '#'*20
    print user_request
    print '#'*20
    response = requests.post(
        'https://observe.lco.global/api/requestgroups/',
        headers={'Authorization': 'Token ' + token},
        json = user_request
    )

    ########################################################
    python_dict = response.json()
    try:
        if 'id' in python_dict:
           tracking_number=str(python_dict['id'])
        else:
           tracking_number=str('0')
        
        _start = datetime.strptime(string.split(str(_utstart),'.')[0],"20%y-%m-%d %H:%M:%S")
        _end = datetime.strptime(string.split(str(_utend),'.')[0],"20%y-%m-%d %H:%M:%S")
        input_datesub = JDnow(verbose=False)
        input_str_smjd = JDnow(_start,verbose=False)
        input_str_emjd = JDnow(_end,verbose=False)
        _seeing = 9999
        _sky = 9999
        _instrument = '2m0'
        priority = 1
        
        try:
           lineout = str(input_datesub)+' '+str(input_str_smjd)+' '+str(input_str_emjd)+'   '+str(_site)+' floyds '+\
                     str(_slit) + ' ' + str(_exp) + '   ' + str(_airmass) + '   ' + str(proposal) + ' '+str(username) + \
                     ' ' + str(_seeing) + ' ' + str(_sky) + ' ' + str(priority) + ' ' + str(tracking_number) + '  0'
        except:
           lineout = str(input_datesub) + ' ' + str(input_str_smjd) + ' '+str(input_str_emjd)+'   '+str(_site)+' floyds '+\
                     str(_slit) + ' '+str(_exp)+'   '+ str(_airmass)+'   ' + str(proposal) + ' ' + str(username) + ' ' + \
                     str(_seeing) + ' '+str(_sky) + ' ' + str(priority) + ' 0  0'
        return lineout, python_dict
    except:
       return '', python_dict


#####################################################################

def sendtrigger_api3(_name,_ra,_dec,expvec,nexpvec,filtervec,_utstart,_utend,username, token,proposal,camera='sbig',_airmass=2.0,lunar = 20, 
                     _site='', mode='NORMAL'):
    import string,re
    import numpy as np
    from datetime import datetime
    def JDnow(datenow='',verbose=False):
        import datetime
        import time
        _JD0=2455927.5
        if not datenow:
            datenow = datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday,
                                        time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
        _JDtoday=_JD0 + (datenow-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600. * 24)+\
                   (datenow - datetime.datetime(2012, 01, 01,00,00,00)).days
        if verbose: print 'JD= '+str(_JDtoday)
        return _JDtoday

    fildic={'1m0': {'U': 'U','B': 'B','V': 'V', 'R': 'R','I': 'I',
                    'u': 'up','g': 'gp', 'r': 'rp', 'i': 'ip', 'z': 'zs','Y':'Y',
                   'up': 'up', 'gp': 'gp', 'rp': 'rp', 'ip': 'ip', 'zs': 'zs'}}
    fildic['2m0'] = fildic['1m0']

    _inst={'sinistro': '1M0-SCICAM-SINISTRO','sbig': '1M0-SCICAM-SBIG',
           'spectral': '2M0-SCICAM-SPECTRAL','oneof': 'oneof'}
    binx={'sbig': 2,'sinistro': 1,'spectral': 2}

    insconfigmode={'sbig': "default", 'sinistro': "full_frame", 'spectral': "default"}
    
    if mode not in ['NORMAL','TARGET_OF_OPPORTUNITY','normal','ToO']:
       mode='NORMAL'

    if mode in ['normal']:
           mode='NORMAL'
    elif mode in ['ToO']:
           mode='TARGET_OF_OPPORTUNITY'

    if camera in ['sbig', 'sinistro']:
        telclass = '1m0'
    else:
        telclass = '2m0'

#################################### adding dither
    if camera in ['sinistro']:
       pixel = 10
       pixarc = 0.387 * 2.
       delta = pixel * pixarc / 3600. # 10 pixel in degree for sinisto camera
       scal = np.pi/180.
       _ra = float(_ra) + ( delta * np.cos(float(_dec) * scal) )
       _dec = float(_dec) + delta 

    ####################################

    windows = [{
        'start': _utstart,
        'end': _utend
    }]
       
    ####################################

    if _site in ['elp', 'cpt', 'ogg', 'lsc', 'coj']:
        location = { "telescope_class": telclass, 'site' : _site}
    else:
        location = { "telescope_class": telclass}


    acquisition_config = {
        "mode": "OFF",
        "exposure_time": None,
        "extra_params": {}}        

    guiding_config = {
        "mode":"ON",
        "optional": True,
        "exposure_time": None,
        "optical_elements": {},
        "extra_params": {}}

    # Additional constraints to be added to this request
    constraints = {
        'max_airmass': _airmass,
        'min_lunar_distance': lunar
    }

    submit = False
    if camera in ['sbig', 'sinistro', 'spectral']:
        #############################3
        target = {
            'name': _name,
            'type': 'ICRS',
            'ra': float(_ra),
            'dec': float(_dec),
            'epoch': 2000,
            "proper_motion_ra": 0.0,
            "proper_motion_dec": 0.0,
            "parallax": 0.0,
            "epoch":2000.0,
        }

        
        submit = True
        configurations=[]
        for i in range(0,len(filtervec)):


            instrument_config = {
                "exposure_time": float(expvec[i]),
                "exposure_count": int(nexpvec[i]),
                "bin_x": binx[camera],
                "bin_y": binx[camera],
                "mode": insconfigmode[camera],
                "rotator_mode": "",
                "optical_elements":{
                    "filter": fildic[telclass][filtervec[i]]
                },
                "extra_params": {}
            }
           
            configurations.append(
                {"constraints": constraints,
                 "instrument_configs": [instrument_config],
                 "acquisition_config": acquisition_config,
                 "guiding_config": guiding_config,
                 'target': target,
                 "instrument_type": _inst[camera],
                 "type": "EXPOSE",
                 "extra_params": {},
                 "priority": 1,
                }
            )

        user_request = {
            'name': _name,  # The title
            'proposal': proposal,
            'ipp_value': 1.00,
            'operator': 'SINGLE',
            'observation_type': mode,
            'requests': [{
                'location': location,
                'configurations': configurations,
                'windows': windows
            }]
        }
    else:
        print('warning: camera not defined')


    if submit is False:
        return '', {'error':'wrong camera'}
    else:
        response = requests.post(
            'https://observe.lco.global/api/requestgroups/',
            headers={'Authorization': 'Token ' + token},
            json = user_request
        )
    
        #################################################################
        python_dict = response.json()
        try:
           if 'id' in python_dict:
              tracking_number = str(python_dict['id'])
           else:
              tracking_number = str('0')
           _start = datetime.strptime(string.split(str(_utstart),'.')[0],"20%y-%m-%d %H:%M:%S")
           _end = datetime.strptime(string.split(str(_utend),'.')[0],"20%y-%m-%d %H:%M:%S")
           input_datesub = JDnow(verbose=False)
           input_str_smjd = JDnow(_start,verbose=False)
           input_str_emjd = JDnow(_end,verbose=False)
           _seeing = 9999
           _sky = 9999
           _instrument = telclass
           priority = 1
           try:
              lineout = str(input_datesub) + ' ' + str(input_str_smjd) + ' '+str(input_str_emjd) + '   ' + str(_site)+\
                        ' ' + ','.join(filtervec)+' ' + ','.join(nexpvec) + ' ' + ','.join(expvec) + '   ' + \
                        str(_airmass) + '   '+str(proposal) + ' ' + str(username) + ' '+str(_seeing) + ' ' + str(_sky) + \
                        ' '+str(_instrument) + ' '+str(priority) + ' '+str(tracking_number) + '  0'
           except:
              lineout = str(input_datesub) + ' ' + str(input_str_smjd) + ' ' + str(input_str_emjd) + '   ' + str(_site) + \
                        ' ' + ','.join(filtervec) + ' ' + ','.join(nexpvec) + ' ' + ','.join(expvec) + '   ' + \
                        str(_airmass) + '   '+str(proposal) + ' ' + str(username) + ' ' + str(_seeing) + ' ' + str(_sky) + \
                        ' ' + str(_instrument) + ' ' + str(priority) + ' 0  0'
           return lineout, python_dict
        except:
           return '', python_dict   



#####################################################################

def get_token(username,password):
    requests.post(
        'https://observe.lco.global/api/api-token-auth/',
        data = {
            'username': username,
            'password': password
        }
    ).json()
#    return requests


def getstatus_all(token,status,date,user='stefano_valenti1',proposal='KEY2020B-006'):
    req = 'https://observe.lco.global/api/requestgroups/' + '?limit=1000&'+\
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
# LOAD ALL TRIGGER OF THE LAST 15 DAYS
print('\n###################  LOAD ALL TRIGGER IN THE LAST 15 DAYS')
datenow = datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday)
date = (datenow+datetime.timedelta(-25)).strftime('%Y-%m-%d')
status = ''
token = agnkey.util.readpass['token']

#
#   result includes all trigger in the last 15 days
#
all = getstatus_all(token,status,date)
result = {}
for line in all['results']:
    if line['requests']:
        result[line['id']] = [line['state'],line['requests'][-1]['id']]
    else:
        result[line['id']] = [line['state'], 0 ]


#        
#   UPDATE STATUS OF ALL TRIGGER WITH STATUS NULL IN THE TABLE
#
#
print('\n#################### UPDATE STATUS OF TRIGGERS WITH STATUS EQUAL TO NULL')
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
                print('warning problems here '+str(track))
                _status = 'UNSCHEDULABLE'
                #_status = updatetriggerslog(data2)
            print _status
          else:
              print 'warning track number = 0 '
    except:
        pass

_lunar = 20
_jd = ephem.julian_date()

print('\n#################### UPDATE STATUS FOR PENDING REQUESTS INCLUDING EXPIRED REQUESTES')
#
#  UPDATE STATS FOR PENDING REQUESTS INCLUDING EXPIRED REQUESTES
#
command2 = ['select t.*,d.filters,d.mode,d.instrument from triggerslog as t join triggers as d where t.status = "PENDING" and d.id = t.triggerid']  
data3 = agnkey.agnsqldef.query(command2)
if len(data3):
    print  'ID    JD_NOW        STATUS      END_WINDOW'
    for data2 in data3:
        track = data2['tracknumber']
        _reqnumber = None
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
                print('Warning: request number not defined')
                _status = 'COMPLETED'
                #_status = updatetriggerslog(data2)
        else:
            print('Warning: track not in result')

        print data2['id'], _jd , _status, 
        print _jd - data2['windowend']
        if _status == 'PENDING' and _jd - data2['windowend'] > 0.1:
                print 'warning this observation is still PENDING but window is over'
                agnkey.agnsqldef.updatevalue('triggerslog', 'status', 'UNSCHEDULABLE', data2['id'],
                                             connection='agnkey',namefile0='id')

#
#   select all active trigger in data
#
print('\n######################  SELECT ALL ACTIVE TRIGGER')
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

    print('\n#################  FOR EACH ACTIVE REQUEST, CHECK LAST OBSERVATION AND DECIDE TO TRIGGER OR NOT')         
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
                    if _status!='UNSCHEDULABLE':
                        agnkey.agnsqldef.updatevalue('triggerslog', 'status', _status, track,
                                                     connection='agnkey', namefile0='tracknumber')
                    if _reqnumber:
                        agnkey.agnsqldef.updatevalue('triggerslog', 'reqnumber', _reqnumber, track,
                                                     connection='agnkey', namefile0='tracknumber')

                else:
                    print 'Warning: trigger not found ' + str(track)
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
                if float(ll['cadence'][jj]) <= 2:
                    if float(_jd)-float(jd0) > .001:
                        print 'cadence less or equal to one day'
                        print 'last window ended, trigger'
                        trigger=True
#                elif 1 < float(ll['cadence'][jj]) <= 2:
#                    print 'cadence between 1 and 2 days'
#                    print 'trigger if it is cadence-.3 days from end of the window'
#                    if float(ll['cadence'][jj])-.3 <= float(_jd)-float(jd0):
#                        trigger=True
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
                     logfile,pp = sendfloydstrigger_api3(str(NAME),expvec,str(SN_RA),str(SN_DEC),\
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
                     logfile,python_dict = sendtrigger_api3(str(NAME),str(SN_RA),str(SN_DEC),\
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

    
