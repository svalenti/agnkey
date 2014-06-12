#!/System/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

import os,string,re,sys
import numpy as np
import agnkey
from agnkey.util import readkey3
import datetime
from optparse import OptionParser

def ingestfromipac(d0s,d1s,dataredutable,archa1,archa2,_force):
    filetype=1
    tfile='./tempdat_img.asc'  
    cols=['userid','propid','origname','FILEHAND'] 
    str0='wget --save-cookies=lcogt_img_cookies.txt'
    str0a='wget --load-cookies=lcogt_img_cookies.txt'
    str1=' --password='
    str2=' -O '
    str3=' "http://lcogtarchive.ipac.caltech.edu/cgi-bin/Gator/nph-query?'
    str4='outfmt=1&catalog=lco_img&mission=lcogt&'
    str5='spatial=NONE&'         # 1/2 deg square box
    str6='selcols='              # cols to return
    for i in range(0,len(cols)-2):        str6=str6+cols[i]+','
    str6=str6+cols[len(cols)-1]+'&'
    str7="constraints=date_obs+between+to_date('"+d0s+"','YYYY-MM-DD')+and+"+\
        "to_date('"+d1s+"','YYYY-MM-DD')"
    str10='/dev/null '
    str11='"http://irsa.ipac.caltech.edu/account/signon/login.do?'
    str12='"http://irsa.ipac.caltech.edu/account/signon/logout.do'
    str13='josso_cmd=login&'
    str14='josso_username='
    str15='josso_password='
    wget0=str0+str2+str10+str11+str13+str14+archa1+str15+archa2+'"'
    wget1=str0a+str2+tfile+str3+str4+str5+str6+str7+'"'
    wget2=str0+str2+str10+str12+'"'

    os.system(wget0)    #    download cookie from ipac
    os.system(wget1)    #    download list of images to ingest

#################  exstract images path to download ############
    f=open('tempdat_img.asc','r')
    ss=f.readlines()
    f.close()
    lista=[]
    for i in ss:
        if i[0] not in ['|','\\']:  
            if string.split(i)[-2] in agnkey.util.proposal:
                lista.append(string.split(i)[-1])


    for img in lista:
        output=string.split(img,'/')[-1]
        downloadimage='wget --load-cookies=lcogt_img_cookies.txt -O '+str(output)+' "http://lcogtarchive.ipac.caltech.edu/cgi-bin/LCODownload/nph-lcoDownload?&file='+img+'"'
        exist=agnkey.agnsqldef.getfromdataraw(agnkey.util.conn,dataredutable,'namefile', string.split(output,'/')[-1],column2='namefile')
        if not exist or _force in ['update','yes']:
            if not os.path.isfile(output): 
                os.system(downloadimage)
            hdr=agnkey.util.readhdr(output)
            _targid=agnkey.agnsqldef.targimg(output)
            _telescope=readkey3(hdr,'telescop')
            _instrument=readkey3(hdr,'instrume')
            if  _telescope in ['all','lsc','elp','cpt','coj','1m0-03','1m0-04','1m0-05','1m0-08','1m0-09','1m0-10','1m0-11','1m0-12','1m0-13','tar']:
                if _instrument in ['kb05','kb70','kb71','kb73','kb74','kb75','kb76','kb77','kb78','kb79',\
                                   'fl02','fl03','fl04','fl05','fl06','fl07','fl08','fl09','fl10']:
                    print '1m telescope'
                    dictionary={'dateobs':readkey3(hdr,'date-obs'),'exptime':readkey3(hdr,'exptime'), 'filter':readkey3(hdr,'filter'),'jd':readkey3(hdr,'JD'),\
                                'telescope':readkey3(hdr,'telescop'),'airmass':readkey3(hdr,'airmass'),'objname':readkey3(hdr,'object'),'ut':readkey3(hdr,'ut'),\
                                'wcs':readkey3(hdr,'wcserr'),'instrument':readkey3(hdr,'instrume'),'ra0':readkey3(hdr,'RA'),'dec0':readkey3(hdr,'DEC'),\
                                'observer':readkey3(hdr,'OBSERVER'),'propid':readkey3(hdr,'PROPID'),\
                                'USERID':readkey3(hdr,'USERID'),'temperature':readkey3(hdr,'CCDATEMP'),'dateobs2':readkey3(hdr,'DATE-OBS')}
                    dictionary['namefile']=string.split(output,'/')[-1]
                    dictionary['wdirectory']=agnkey.util.workingdirectory+'1mtel/'+readkey3(hdr,'date-night')+'/'
                    dictionary['filetype']=filetype
                    dictionary['targid']=_targid
                    print 'insert reduced'
                else: dictionary=''
            elif _telescope in ['ftn','fts']:
                print '2m telescope'
                print '1m telescope'
                dictionary={'dateobs':readkey3(hdr,'date-obs'),'exptime':readkey3(hdr,'exptime'), 'filter':readkey3(hdr,'filter'),'jd':readkey3(hdr,'JD'),\
                            'telescope':readkey3(hdr,'telescop'),'airmass':readkey3(hdr,'airmass'),'objname':readkey3(hdr,'object'),'ut':readkey3(hdr,'ut'),\
                            'wcs':readkey3(hdr,'wcserr'),'instrument':readkey3(hdr,'instrume'),'ra0':readkey3(hdr,'RA'),'dec0':readkey3(hdr,'DEC'),\
                            'observer':readkey3(hdr,'OBSERVER'),'propid':readkey3(hdr,'PROPID'),\
                            'USERID':readkey3(hdr,'USERID'),'temperature':readkey3(hdr,'CCDATEMP'),'dateobs2':readkey3(hdr,'DATE-OBS')}
                dictionary['namefile']=string.split(output,'/')[-1]
                dictionary['wdirectory']=agnkey.util.workingdirectoy+'1mtel/'+readkey3(hdr,'date-night')+'/'
                dictionary['filetype']=filetype
                dictionary['targid']=_targid
                print 'insert reduced'
            else: dictionary=''
            
            if dictionary:
                if not exist:
                    print 'insert values'
                    agnkey.agnsqldef.insert_values(agnkey.util.conn,dataredutable,dictionary)
                else:
                    print dataredutable
                    print 'update values'
                    for voce in dictionary:
                        print voce
                        for voce in ['wdirectory','filetype','ra0','dec0','jd','exptime','filter']:
                            agnkey.agnsqldef.updatevalue(dataredutable,voce,dictionary[voce],string.split(output,'/')[-1])
                            ######################################
                if not os.path.isdir(dictionary['wdirectory']): 
                    os.mkdir(dictionary['wdirectory'])
                if not os.path.isfile(dictionary['wdirectory']+output) or _force=='yes': 
                    print 'mv '+output+' '+dictionary['wdirectory']+output
                    os.system('mv '+output+' '+dictionary['wdirectory']+output)
                    os.chmod(dictionary['wdirectory']+output,0664)
            else: 
                print 'dictionary empty'
        else:
            print '\n### file already there '+output
    os.system(wget2)        # close connection for download
############################################################################################################
description="> ingest 1m and 2m  data  " 
usage= "%prog  -e epoch [-s stage -n name -f filter -d idnumber]\n available stages [wcs,psf,psfmag,zcat,abscat,mag,local,getmag]\n"

if __name__ == "__main__":
    parser = OptionParser(usage=usage,description=description, version="%prog 1.0")
    parser.add_option("-e", "--epoch",dest="epoch",default='20121212',type="str",
                      help='epoch to reduce  \t [%default]')
    parser.add_option("-f", "--force",dest="force",default='no',type="str",
                  help='force ingestion \t [no/yes/update] \n')
    option,args = parser.parse_args()
    if option.force not in ['no','yes','update']:      sys.argv.append('--help')
    option,args = parser.parse_args()
    epoch=option.epoch
    _force=option.force

    if '-' not in str(epoch): 
        epoch1=datetime.date(int(epoch[0:4]),int(epoch[4:6]),int(epoch[6:8]))
        epoch2=datetime.date(int(epoch[0:4]),int(epoch[4:6]),int(epoch[6:8]))
    else:
        epoch1,epoch2=string.split(epoch,'-')
        start=datetime.date(int(epoch1[0:4]),int(epoch1[4:6]),int(epoch1[6:8]))
        stop=datetime.date(int(epoch2[0:4]),int(epoch2[4:6]),int(epoch2[6:8]))
        
    archa1=agnkey.util.ipacuser+'&'
    archa2=agnkey.util.ipacpasswd
    dataredutable='dataredulco'
    print epoch1,epoch2
    print _force
    ingestfromipac(str(epoch1),str(epoch2),dataredutable,archa1,archa2,_force)
