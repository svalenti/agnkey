import numpy as np

####################################################

def getconnection(site):
   import  agnkey

   connection={#        CHANGE THIS LINE WITH THE INFO ON THE NEW DATABASE
               'agnkey':{}}
   connection[site]['database']=agnkey.util.readpass['database']
   connection[site]['hostname']=agnkey.util.readpass['hostname']
   connection[site]['username']=agnkey.util.readpass['mysqluser']
   connection[site]['passwd']=agnkey.util.readpass['mysqlpasswd']
   return  connection[site]['hostname'],connection[site]['username'],connection[site]['passwd'],connection[site]['database']

def dbConnect(lhost, luser, lpasswd, ldb):
   import sys
   import MySQLdb,os,string
   try:
      conn = MySQLdb.connect (host = lhost,
                              user = luser,
                            passwd = lpasswd,
                                db = ldb)
   except MySQLdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit (1)
   return conn

try:
   hostname, username, passwd, database=getconnection('agnkey')
   conn = dbConnect(hostname, username, passwd, database)
except:
   conn=''
   print '\### warning: problem with the database'

########################################################################

def getmissing(conn, epoch0, epoch2,telescope,datatable='dataredulco'):
   import sys
   import MySQLdb,os,string
   print epoch0, epoch2,telescope
   try:
      cursor = conn.cursor (MySQLdb.cursors.DictCursor)
      if telescope =='all':
         if epoch2:
            cursor.execute ("select raw.namefile from datarawlco raw where "+\
                               " raw.dateobs < "+str(epoch2)+" and raw.dateobs >= "+str(epoch0)+\
                               " and NOT EXISTS(select * from "+str(datatable)+" redu where raw.namefile = redu.namefile)")
         else:
            cursor.execute ("select raw.namefile from datarawlco raw where "+\
                               " raw.dateobs = "+str(epoch0)+\
                               " and NOT EXISTS(select * from "+str(datatable)+" redu where raw.namefile = redu.namefile)")
      elif telescope in ['elp','lsc','cpt','coj','1m0','kb','fl']:
         if epoch2:  
            print "select raw.namefile from datarawlco raw where raw.namefile like '%"+telescope+"%'"+\
                               " and raw.dateobs < "+str(epoch2)+" and raw.dateobs >= "+str(epoch0)+\
                               " and NOT EXISTS(select * from "+str(datatable)+" redu where raw.namefile = redu.namefile)"
            cursor.execute ("select raw.namefile from datarawlco raw where raw.namefile like '%"+telescope+"%'"+\
                               " and raw.dateobs < "+str(epoch2)+" and raw.dateobs >= "+str(epoch0)+\
                               " and NOT EXISTS(select * from "+str(datatable)+" redu where raw.namefile = redu.namefile)")
         else:
            cursor.execute ("select raw.namefile from datarawlco raw where raw.namefile like '%"+telescope+"%'"+\
                               " and raw.dateobs = "+str(epoch0)+\
                               " and NOT EXISTS(select * from "+str(datatable)+" redu where raw.namefile = redu.namefile)")
      else:
         if epoch2:
            cursor.execute ("select raw.namefile from datarawlco raw where raw.telescope = '"+str(telescope)+\
                               "' and raw.dateobs < "+str(epoch2)+" and raw.dateobs >= "+str(epoch0)+\
                               " and NOT EXISTS(select * from "+str(datatable)+" redu where raw.namefile = redu.namefile)")
         else:
            cursor.execute ("select raw.namefile from datarawlco raw where raw.telescope = '"+str(telescope)+\
                               "' and raw.dateobs = "+str(epoch0)+\
                               " and NOT EXISTS(select * from "+str(datatable)+" redu where raw.namefile = redu.namefile)")
      resultSet = cursor.fetchall ()
      if cursor.rowcount == 0:
         pass
      cursor.close ()
   except MySQLdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit (1)
   return resultSet

def getfromdataraw(conn, table, column, value,column2='*'):
   import sys
   import MySQLdb,os,string
   try:
      cursor = conn.cursor (MySQLdb.cursors.DictCursor)
      cursor.execute ("select "+column2+" from "+str(table)+" where "+column+"="+"'"+value+"'")
      resultSet = cursor.fetchall ()
      if cursor.rowcount == 0:
         pass
      cursor.close ()
   except MySQLdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit (1)
   return resultSet


def getlistfromraw(conn, table, column, value1,value2,column2='*',telescope='all'):
   import sys
   import MySQLdb,os,string
   try:
      cursor = conn.cursor (MySQLdb.cursors.DictCursor)
      if telescope=='all':
         if value2:
            cursor.execute ("select "+column2+" from "+str(table)+" where "+column+"<="+"'"+value2+"' and "+column+">="+"'"+value1+"'")
         else:
            cursor.execute ("select "+column2+" from "+str(table)+" where "+column+"="+"'"+value1+"'")
      elif telescope in ['lsc','elp','cpt','coj','1m0','kb','fts','ftn','fl']:
         if value2:
            cursor.execute ("select "+column2+" from "+str(table)+" where "+column+"<="+"'"+value2+"' and "+column+">="+"'"+value1+"' and namefile like '%"+telescope+"%'")
         else:
            cursor.execute ("select "+column2+" from "+str(table)+" where "+column+"="+"'"+value1+"' and namefile like '%"+telescope+"%'")
      else:
         if value2:
            cursor.execute ("select "+column2+" from "+str(table)+" where "+column+"<="+"'"+value2+"' and "+column+">="+"'"+value1+"' and telescope='"+telescope+"'")
         else:
            cursor.execute ("select "+column2+" from "+str(table)+" where "+column+"="+"'"+value1+"' and  telescope='"+telescope+"'")
      resultSet = cursor.fetchall ()
      if cursor.rowcount == 0:
         pass
      cursor.close ()
   except MySQLdb.Error, e: 
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit (1)
   return resultSet

###########################################################################

def updatevalue(table,column,value,namefile,connection='agnkey',namefile0='namefile'):
   import sys
   import MySQLdb,os,string
   import agnkey

   hostname, username, passwd, database=agnkey.agnsqldef.getconnection(connection)
   conn = agnkey.agnsqldef.dbConnect(hostname, username, passwd, database)

   try:
      cursor = conn.cursor (MySQLdb.cursors.DictCursor)
      if value in [True,False]:
         cursor.execute ("UPDATE "+str(table)+" set "+column+"="+str(value)+" where "+str(namefile0)+"= "+"'"+str(namefile)+"'"+"   ")
      else:
         cursor.execute ("UPDATE "+str(table)+" set "+column+"="+"'"+str(value)+"'"+" where "+str(namefile0)+"= "+"'"+str(namefile)+"'"+"   ")
      resultSet = cursor.fetchall ()
      if cursor.rowcount == 0:
         pass
      cursor.close ()
   except MySQLdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
#      sys.exit (1)

###########################################################################

def insert_values(conn,table,values):
    import sys,string,os,re
    import MySQLdb,os,string
    def dictValuePad(key):
        return '%(' + str(key) + ')s'

    def insertFromDict(table, dict):
        """Take dictionary object dict and produce sql for 
        inserting it into the named table"""
        sql = 'INSERT INTO ' + table
        sql += ' ('
        sql += ', '.join(dict)
        sql += ') VALUES ('
        sql += ', '.join(map(dictValuePad, dict))
        sql += ');'
        return sql

    sql = insertFromDict(table, values)
    try:
        cursor = conn.cursor (MySQLdb.cursors.DictCursor)
        cursor.execute(sql, values)
        resultSet = cursor.fetchall ()
        if cursor.rowcount == 0:
            pass
        cursor.close ()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
#        sys.exit (1)

########################################################################
#  dataraw
#create table dataraw (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, namefile VARCHAR(50) UNIQUE KEY, directory VARCHAR(100), objname VARCHAR(50), jd FLOAT, dateobs DATE, exptime FLOAT, filter VARCHAR(20), grism VARCHAR(20), telescope VARCHAR(20), instrument VARCHAR(20), type VARCHAR(20), category VARCHAR(20) , tech VARCHAR(20) , airmass FLOAT, ut TIME, slit VARCHAR(20), lamp VARCHAR(20), status VARCHAR(50), input VARCHAR(50), note VARCHAR(100), ra0 FLOAT, dec0 FLOAT, OBID INT, temperature FLOAT, observer VARCHAR(30) );

# dataredu
#create table dataredu (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, namefile VARCHAR(50) UNIQUE KEY, directory VARCHAR(100), objname VARCHAR(50), jd FLOAT, dateobs DATE, exptime FLOAT, filter VARCHAR(20), grism VARCHAR(20), telescope VARCHAR(20), instrument VARCHAR(20), type VARCHAR(20), category VARCHAR(20) , tech VARCHAR(20) , airmass FLOAT, ut TIME, slit VARCHAR(20), lamp VARCHAR(20), status VARCHAR(50), input VARCHAR(50), note VARCHAR(100), ra0 FLOAT, dec0 FLOAT, OBID INT, temperature FLOAT, observer VARCHAR(30) );

#reducomputed
#create table redulog (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, namefile VARCHAR(50) UNIQUE KEY, directory VARCHAR(100), bias  VARCHAR(50), flat VARCHAR(50), dark VARCHAR(50), illcorr VARCHAR(50), crosstalk VARCHAR(50), arc VARCHAR(50), skysub VARCHAR(50), mask  VARCHAR(50), fringing VARCHAR(50), astrometry  BOOL, zeropoint  VARCHAR(30), sensitivity VARCHAR(50), telluric  VARCHAR(50) );

#(val BOOL, true INT DEFAULT 1, false INT DEFAULT 0)
###############################
#create table datarawlco (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, namefile VARCHAR(50) UNIQUE KEY, directory VARCHAR(100), objname VARCHAR(50), jd DOUBLE, dateobs DATE, exptime FLOAT, filter VARCHAR(20), grism VARCHAR(20), telescope VARCHAR(20), instrument VARCHAR(20), type VARCHAR(20), category VARCHAR(20) , tech VARCHAR(20) , airmass FLOAT, ut TIME, slit VARCHAR(20), lamp VARCHAR(20), status VARCHAR(50), input VARCHAR(50), note VARCHAR(100), ra0 FLOAT, dec0 FLOAT,  fwhm FLOAT DEFAULT 9999, OBID INT, temperature FLOAT, PROPID VARCHAR(30), rotskypa FLOAT, observer VARCHAR(30), USERID VARCHAR(30), dateobs2  VARCHAR(23)) ;


#create table datarawfloyds (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, namefile VARCHAR(50) UNIQUE KEY, directory VARCHAR(100), objname VARCHAR(50), jd DOUBLE, dateobs DATE, exptime FLOAT, filter VARCHAR(20), grism VARCHAR(20), telescope VARCHAR(20), instrument VARCHAR(20), type VARCHAR(20), category VARCHAR(20) , tech VARCHAR(20) , airmass FLOAT, ut TIME, slit VARCHAR(20), lamp VARCHAR(20), status VARCHAR(50), input VARCHAR(50), note VARCHAR(100), ra0 FLOAT, dec0 FLOAT,  fwhm FLOAT DEFAULT 9999, OBID INT, temperature FLOAT, PROPID VARCHAR(30), rotskypa FLOAT, observer VARCHAR(30), USERID VARCHAR(30), dateobs2  VARCHAR(23)) ;

#create table dataredulco (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, namefile VARCHAR(50) UNIQUE KEY, wdirectory VARCHAR(100), objname VARCHAR(50), jd DOUBLE, dateobs DATE, exptime FLOAT, filter VARCHAR(20), telescope VARCHAR(20), instrument VARCHAR(20), airmass FLOAT, ut TIME, wcs FLOAT DEFAULT 9999, psf FLOAT DEFAULT 9999, apmag FLOAT, psfx FLOAT, psfy FLOAT, psfmag FLOAT DEFAULT 9999, psfdmag FLOAT, z1 FLOAT DEFAULT 9999, z2 FLOAT DEFAULT 9999, c1 FLOAT DEFAULT 9999, c2 FLOAT DEFAULT 9999, dz1 FLOAT DEFAULT 9999, dz2 FLOAT DEFAULT 9999, dc1 FLOAT DEFAULT 9999, dc2 FLOAT DEFAULT 9999 , zcol1 VARCHAR(2), zcol2 VARCHAR(2) , mag FLOAT DEFAULT 9999, dmag FLOAT, quality BOOL, zcat varchar(50) DEFAULT 'X', abscat varchar(50) DEFAULT 'X');

#create table inoutredu (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, namein VARCHAR(100), tablein VARCHAR(20), nameout VARCHAR(100), tableout VARCHAR(20) );

#create table lsc_sn_pos (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), ra DOUBLE, dec DOUBLE, redshift DOUBLE, psf_string VARCHAR(20), sloan_cat, landolt_cat );

# create table groupstab (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, group  VARCHAR(20) , groupid INT); 

# create table changelog  (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, user VARCHAR(20), targid BIGINT, date DATE, note  VARCHAR(200));

# create table obslog  (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, user VARCHAR(20), targid BIGINT, triggerjd DOUBLE, windowstart DOUBLE, windowend  DOUBLE, filters  VARCHAR(30), exptime VARCHAR(30), numexp VARCHAR(30), proposal VARCHAR(30), site VARCHAR(10), instrument VARCHAR(30), sky FLOAT DEFAULT 9999, seeing FLOAT DEFAULT 9999, airmass FLOAT DEFAULT 9999, slit FLOAT DEFAULT 9999, acqmode VARCHAR(20), priority FLOAT DEFAULT 9999);

#select raw.namefile,raw.directory from datarawlco raw where raw.telescope = '1m0a' and raw.dateobs = 20121105 and NOT EXISTS(select * from dataredulco redu where raw.namefile = redu.namefile);

# delete from dataraw where namefile='test';
#######################################

def ingestdata(telescope,instrument,listepoch,_force):
   import glob,string,os,re
   import agnkey
   from agnsqldef import dbConnect
   from agnsqldef import insert_values
   from agnsqldef import getfromdataraw
   from agnsqldef import updatevalue
   
   if telescope in ['fts','ftn','1m0-03','1m0-04','1m0-05','1m0-08','1m0-09','1m0-10','1m0-11','1m0-12','1m0-13','lsc','elp','cpt','all','coj','tar']:
      hostname, username, passwd, database=agnkey.agnsqldef.getconnection('agnkey')
   else:
      hostname, username, passwd, database=agnkey.agnsqldef.getconnection('lcogt')

   conn = agnkey.agnsqldef.dbConnect(hostname, username, passwd, database)
   print instrument
   if telescope=='all': tellist=['elp','lsc','cpt','coj']
   elif telescope in ['1m0-08']: tellist=['elp']
   elif telescope in ['1m0-05','1m0-04','1m0-09']: tellist=['lsc']
   elif telescope in ['1m0-13','1m0-10','1m0-12']: tellist=['cpt']
   elif telescope in ['1m0-11','1m0-03']: tellist=['coj']
   elif telescope =='elp': tellist=['elp']
   elif telescope =='lsc': tellist=['lsc']
   elif telescope =='cpt': tellist=['cpt']
   elif telescope =='coj': tellist=['coj']
   elif telescope =='fts': tellist=['coj']
   elif telescope =='ftn': tellist=['ogg']

   if not instrument:
      if telescope in ['1m0-03','1m0-04','1m0-05','1m0-08','1m0-09','1m0-10','1m0-11','1m0-12','1m0-13','lsc','elp','cpt','all','coj']:
                               instrumentlist = ['kb05','kb70','kb71','kb73','kb74','kb75','kb76','kb77','kb78','kb79',\
                                                 'fl02','fl03','fl04','fl05','fl06','fl07','fl08','fl09','fl10']
      elif ['fts','ftn']:      instrumentlist = ['fs01','fs02','fs03','em01','em03']
   else:                       instrumentlist = [instrument]

   for epoch in listepoch:
    print epoch
    if telescope in ['fts']:
       imglist=''
       print '\n###  warning ingestion raw data FTN and FTS data should be done from web site and not from /archive/data1/'
    elif telescope in ['ftn']:
       imglist=''
       print '\n###  warning ingestion raw data FTN and FTS data should be done from web site and not from /archive/data1/'
    elif telescope in ['1m0-03','1m0-04','1m0-05','1m0-08','1m0-09','1m0-10','1m0-11','1m0-12','1m0-13','lsc','elp','cpt','all','coj']:
       print 'force ingestion'
       import agnkey
       from agnkey.util import readkey3,readhdr
       imglist=[]
       print tellist,instrumentlist
       for tel in tellist:
          for instrument in instrumentlist:
             directory=agnkey.util.rawdata+tel+'/'+instrument+'/'+str(epoch)+'/oracproc/'
             print directory
             imglist=imglist+glob.glob(directory+'*0.fits')
    elif telescope in ['tar']:
       import agnkey
       from agnkey.util import readkey3,readhdr
       imglist0=glob.glob('*fits')
       imglist=[]
       instrumentlist=[]
       tellist=[]
       for img in imglist0:
          img=os.getcwd()+'/'+img
          answ=raw_input('do you want to ingest this files '+str(img)+' [[y]/n]?')
          if not answ: answ='y'
          if answ in ['yes','y','Y','YES','Yes']:
             hdr=readhdr(img)
             if readkey3(hdr,'instrume') not in instrumentlist:
                instrumentlist=instrumentlist+[readkey3(hdr,'instrume')]
             if readkey3(hdr,'TELESCOP') not in tellist:             
                tellist=tellist+[readkey3(hdr,'TELESCOP')]
             imglist=imglist+[img]
       print tellist,instrumentlist
       print imglist
    else:      imglist=[]
    datarawtable='datarawlco'
    for img in imglist:
      if not agnkey.agnsqldef.getfromdataraw(conn,datarawtable,'namefile', string.split(img,'/')[-1],column2='namefile') or _force:
         if telescope in ['fts','ftn']:
               if instrument in ['fs01']:
                  hdr=readhdr(img)
                  _tech=None
                  dictionary={ 'lamp':readkey3(hdr,'lamp'), 'grism':readkey3(hdr,'grism'),'telescope':readkey3(hdr,'TELID'),\
                           'instrument':readkey3(hdr,'instrume'),'dec0':readkey3(hdr,'DEC'),'ra0':readkey3(hdr,'RA'),'ut':readkey3(hdr,'ut'),\
                           'dateobs':readkey3(hdr,'date-obs'),'exptime':readkey3(hdr,'exptime'), 'filter':readkey3(hdr,'filter'),'jd':readkey3(hdr,'JD'),\
                           'slit':readkey3(hdr,'slit'),'airmass':readkey3(hdr,'airmass'),'objname':readkey3(hdr,'object'),'type':readkey3(hdr,'type'),\
                           'category':readkey3(hdr,'catg'),'tech':_tech,'observer':readkey3(hdr,'OBSERVER'),'propid':readkey3(hdr,'PROPID'),\
                           'OBID':readkey3(hdr,'GROUPID'),'USERID':readkey3(hdr,'USERID'),'temperature':readkey3(hdr,'CCDATEMP'),'dateobs2':readkey3(hdr,'DATE-OBS')}
               dictionary['namefile']=string.split(img,'/')[-1]
               dictionary['directory']=re.sub(dictionary['namefile'],'',img) 
         elif  telescope in ['all','lsc','elp','cpt','coj','1m0-03','1m0-04','1m0-05','1m0-08','1m0-09','1m0-10','1m0-11','1m0-12','1m0-13','tar']:
               if instrument in ['kb05','kb70','kb71','kb73','kb74','kb75','kb76','kb77','kb78','kb79',\
                                 'fl02','fl03','fl04','fl05','fl06','fl07','fl08','fl09','fl10']:
                  hdr=readhdr(img)
#                  if readkey3(hdr,'PROPID') in ['LCOELP-001','LCONET-001','DDTLCO-008'] or readkey3(hdr,'object') in ['2012cg','LSQ12cpf','2012da','PTF12fuu','PTF12grk','PTF12gzk']:
                  if readkey3(hdr,'PROPID') in ['LCOELP-001','LCONET-001','DDTLCO-009'] or readkey3(hdr,'object') in ['PSN09554214','2012cg','LSQ12cpf','2012da','PTF12fuu','PTF12grk','PTF12gzk','PTF13dzb']:
                     print readkey3(hdr,'PROPID'),readkey3(hdr,'USERID'),readkey3(hdr,'object')
                     _tech=None
                     dictionary={ 'lamp':readkey3(hdr,'lamp'), 'grism':readkey3(hdr,'grism'),'telescope':readkey3(hdr,'telescop'),'fwhm':readkey3(hdr,'L1FWHM'),\
                           'instrument':readkey3(hdr,'instrume'),'dec0':readkey3(hdr,'DEC'),'ra0':readkey3(hdr,'RA'),'ut':readkey3(hdr,'ut'),\
                           'dateobs':readkey3(hdr,'date-obs'),'exptime':readkey3(hdr,'exptime'), 'filter':readkey3(hdr,'filter'),'jd':readkey3(hdr,'JD'),\
                           'slit':readkey3(hdr,'slit'),'airmass':readkey3(hdr,'airmass'),'objname':readkey3(hdr,'object'),'type':readkey3(hdr,'type'),\
                           'category':readkey3(hdr,'catg'),'tech':_tech,'observer':readkey3(hdr,'OBSERVER'),'propid':readkey3(hdr,'PROPID'),\
                            'OBID':readkey3(hdr,'GROUPID'),'USERID':readkey3(hdr,'USERID'),'temperature':readkey3(hdr,'CCDATEMP'),'dateobs2':readkey3(hdr,'DATE-OBS')}
                     dictionary['namefile']=string.split(img,'/')[-1]
                     dictionary['directory']=re.sub(dictionary['namefile'],'',img) 
                  else: dictionary={}
         if telescope in ['fts','ftn']:
               if instrument in ['fs01']:
                  if not agnkey.agnsqldef.getfromdataraw(conn,datarawtable,'namefile', string.split(img,'/')[-1],column2='namefile'):
                     agnkey.agnsqldef.insert_values(conn,datarawtable,dictionary)
                  elif _force:
                     for voce in dictionary:
                        if voce!='id' and voce!='namefile':
                           agnkey.agnsqldef.updatevalue(datarawtable,voce,dictionary[voce],string.split(img,'/')[-1])
         elif  telescope in ['all','1m0-03','1m0-04','1m0-05','1m0-08','1m0-09','1m0-10','1m0-11','1m0-12','1m0-13','lsc','elp','cpt','coj','tar']:
            if dictionary:
               if instrument in ['kb05','kb70','kb71','kb73','kb74','kb75','kb76','kb77','kb78','kb79',\
                                 'fl02','fl03','fl04','fl05','fl06','fl07','fl08','fl09','fl10']:
                  if not agnkey.agnsqldef.getfromdataraw(conn,datarawtable,'namefile', string.split(img,'/')[-1],column2='namefile'):
                     agnkey.agnsqldef.insert_values(conn,datarawtable,dictionary)
                     print 'insert '+img
                  elif _force:
                     for voce in dictionary:
                        if voce!='id' and voce!='namefile':
                           agnkey.agnsqldef.updatevalue(datarawtable,voce,dictionary[voce],string.split(img,'/')[-1])
         else:
              raw_input('go on ? ')
#      else:
#         print img+' already ingested'
###############################################################################################################################################

def ingestredu(_telescope,_instrument,imglist,force='no',datatable='dataredulco'):
   import string,re,os,sys
   import agnkey
   print 'here'
   #os.umask(000)   # permission to supernova user and group 

   hostname, username, passwd, database=agnkey.agnsqldef.getconnection('agnkey')
   conn = agnkey.agnsqldef.dbConnect(hostname, username, passwd, database)
   dataredutable=datatable
   _type=''
   if not _instrument:
      if _telescope in ['1m0-03','1m0-04','1m0-05','1m0-08','1m0-09','1m0-10','1m0-11','1m0-12','1m0-13','lsc','elp','cpt','coj','all']:   _type='1m'
      elif _telescope in ['ftn','fts']: _type='2m'
      else: sys.exit('instrument not defined, telescopen not in the list')
   else:
      if _instrument in ['kb05','kb70','kb71','kb73','kb74','kb75','kb76','kb77','kb78','kb79']:  _type='1m'
      elif _instrument in ['fl02','fl03','fl04','fl05','fl06','fl07','fl08','fl09','fl10']:       _type='1m'
      elif _instrument in ['fs01','fs02','fs03','em03','em01']:                                   _type='2m'
      elif _instrument in ['en05','en06']:                                                        _type='floyds'
      else: sys.exit('instrument or telescope not recognised')

   for img in imglist:
      exist=agnkey.agnsqldef.getfromdataraw(conn,dataredutable,'namefile', string.split(img,'/')[-1],column2='namefile')
      if exist:
         if force=='yes':
            print img,database
            agnkey.agnsqldef.deleteredufromarchive(string.split(img,'/')[-1],dataredutable)
            print 'delete line from '+str(database)
            exist=agnkey.agnsqldef.getfromdataraw(conn,dataredutable,'namefile', string.split(img,'/')[-1],column2='namefile')

      if not exist or force =='update':
         _dir=agnkey.agnsqldef.getfromdataraw(conn,'datarawlco','namefile', string.split(img,'/')[-1],column2='directory')[0]['directory']
         if _dir:                                                      filetype=1  #   data in raw table, the image is a single image
         else:
            if 'diff' in string.split(img,'/')[-1][0:4]=='diff':       filetype=3  #   difference image
            else:                                                      filetype=2  #   merge image
         print filetype
         if img[0]=='/':
            _dir=re.sub(string.split(img,'/')[-1],'',img)
            img=string.split(img,'/')[-1]
         else:
            if not _dir: sys.exit('warning: '+str(img)+' not in raw table and full path missing')

         if _type=='1m':
            import agnkey
            from agnkey.util import readkey3,readhdr
            hdr=readhdr(_dir+img)
            if 'WCSERR' in hdr:
               wcs='WCSERR'
            elif 'WCS_ERR' in hdr:
               wcs='WCS_ERR'
            else:
               wcs='WCSERR'
            _targid=agnkey.agnsqldef.targimg(_dir+img)
            dictionary={'dateobs':readkey3(hdr,'date-obs'),'exptime':readkey3(hdr,'exptime'), 'filter':readkey3(hdr,'filter'),'jd':readkey3(hdr,'JD'),\
                           'telescope':readkey3(hdr,'telescop'),'airmass':readkey3(hdr,'airmass'),'objname':readkey3(hdr,'object'),'ut':readkey3(hdr,'ut'),\
                           'wcs':readkey3(hdr,wcs),'instrument':readkey3(hdr,'instrume'),'ra0':readkey3(hdr,'RA'),'dec0':readkey3(hdr,'DEC')}
            dictionary['namefile']=string.split(img,'/')[-1]
            #dictionary['wdirectory']='/science/supernova/data/lsc/'+readkey3(hdr,'date-night')+'/'
            dictionary['wdirectory']=agnkey.util.workingdirectoy+'lsc/'+readkey3(hdr,'date-night')+'/'
            dictionary['filetype']=filetype
            dictionary['targid']=_targid

            print img
            print dictionary
            print 'insert reduced'
            print database
            ggg=agnkey.agnsqldef.getfromdataraw(conn, dataredutable, 'namefile',str(img), '*')
            if not ggg:
               agnkey.agnsqldef.insert_values(conn,dataredutable,dictionary)
            else:
               for voce in dictionary:
#               for voce in ['filetype','ra0','dec0','jd','exptime','filter']:
                  agnkey.agnsqldef.updatevalue(dataredutable,voce,dictionary[voce],string.split(img,'/')[-1])

         ######################################
            if not os.path.isdir(dictionary['wdirectory']): os.mkdir(dictionary['wdirectory'])
            if not os.path.isfile(dictionary['wdirectory']+img) or force=='yes': 
               print 'cp '+_dir+img+' '+dictionary['wdirectory']+img
               os.system('cp '+_dir+img+' '+dictionary['wdirectory']+img)
               os.chmod(dictionary['wdirectory']+img,0664)

         elif _type=='2m': 
            import agnkey
            from agnkey.util import readkey3,readhdr
            hdr=readhdr(_dir+img)
            if 'WCSERR' in hdr:
               wcs='WCSERR'
            elif 'WCS_ERR' in hdr:
               wcs='WCS_ERR'
            else:
               wcs='WCSERR'
            _targid=agnkey.agnsqldef.targimg(_dir+img)
            dictionary={'dateobs':readkey3(hdr,'date-obs'),'exptime':readkey3(hdr,'exptime'), 'filter':readkey3(hdr,'filter'),'jd':readkey3(hdr,'JD'),\
                           'telescope':readkey3(hdr,'TELID'),'airmass':readkey3(hdr,'airmass'),'objname':readkey3(hdr,'object'),'ut':readkey3(hdr,'ut'),\
                           'wcs':readkey3(hdr,wcs),'instrument':readkey3(hdr,'instrume'),'ra0':readkey3(hdr,'RA'),'dec0':readkey3(hdr,'DEC')}
            dictionary['namefile']=string.split(img,'/')[-1]
            dictionary['wdirectory']=agnkey.util.workingdirectoy+'2mtel/'+readkey3(hdr,'date-night')+'/'
            dictionary['filetype']=filetype
            dictionary['targid']=_targid
            print 'insert reduced'
            ggg=agnkey.agnsqldef.getfromdataraw(conn, dataredutable, 'namefile',str(img), '*')
            if not ggg:
               agnkey.agnsqldef.insert_values(conn,dataredutable,dictionary)
            else:
               for voce in dictionary:
#               for voce in ['filetype','ra0','dec0']:
                  agnkey.agnsqldef.updatevalue(dataredutable,voce,dictionary[voce],string.split(img,'/')[-1])

         elif _type=='floyds': print 'floyds'
         else: sys.exit('instrument not recognised')
      else:
         print 'already ingested'

###############################################################################################################################

def getvaluefromarchive(table,column,value,column2):
   import sys
   import MySQLdb,os,string
   import agnkey
   #from mysqldef import dbConnect, getfromdataraw, getconnection
   hostname, username, passwd, database=agnkey.agnsqldef.getconnection('agnkey')
   conn = agnkey.agnsqldef.dbConnect(hostname, username, passwd, database)
   resultSet=agnkey.agnsqldef.getfromdataraw(conn, table, column, value,column2)
   if resultSet:
      result=resultSet
   else:
      result=[]
   return result


def deleteredufromarchive(namefile,archive='dataredulco',column='namefile'):
   import sys
   import MySQLdb,os,string
   import agnkey
#   from mysqldef import dbConnect, getfromdataraw, getconnection
   hostname, username, passwd, database=agnkey.agnsqldef.getconnection('agnkey')
   conn = agnkey.agnsqldef.dbConnect(hostname, username, passwd, database)
#######
   try:
      cursor = conn.cursor (MySQLdb.cursors.DictCursor)
      cursor.execute ("delete  from "+str(archive)+" where "+str(column)+"="+"'"+namefile+"'")
      resultSet = cursor.fetchall ()
      if cursor.rowcount == 0:
         pass
      cursor.close ()
   except MySQLdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit (1)
   return resultSet

###################################################################################################################

def getfromcoordinate(conn, table, ra0, dec0,distance):
   import sys
   import MySQLdb,os,string
   if table=='lsc_sn_pos':
      ra1='ra_sn'
      dec1='dec_sn'
   elif table=='datarawlco':
      ra1='ra0'
      dec1='dec0'
   try:
      cursor = conn.cursor (MySQLdb.cursors.DictCursor)
      command=["set @sc = pi()/180","set @ra = "+str(ra0), "set @dec = "+str(dec0),"set @distance = "+str(distance),"SELECT *,abs(2*asin( sqrt( sin((a.dec_sn-@dec)*@sc/2)*sin((a.dec_sn-@dec)*@sc/2) + cos(a.dec_sn*@sc)*cos(@dec*@sc)*sin((a.ra_sn-@ra)*@sc/2)*sin((a.ra_sn-@ra)*@sc/2.0) )))*180/pi() as hsine FROM "+str(table)+" as a HAVING hsine<@distance order by a.ra_sn desc"]
      for ccc in command:
         cursor.execute (ccc)
      resultSet = cursor.fetchall ()
      if cursor.rowcount == 0:
         pass
      cursor.close ()
   except MySQLdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit (1)
   return resultSet

###################################################################################


def targimg(img):
    import agnkey
    from agnkey.util import readkey3,readhdr
    from agnkey.agnsqldef import getfromcoordinate
    hostname, username, passwd, database=agnkey.agnsqldef.getconnection('agnkey')
    conn = agnkey.agnsqldef.dbConnect(hostname, username, passwd, database)

    import string
    _targid=''
    hdrt=agnkey.util.readhdr(img)
    _ra=agnkey.util.readkey3(hdrt,'RA')
    _dec=agnkey.util.readkey3(hdrt,'DEC')
    _object=agnkey.util.readkey3(hdrt,'object')
    if ':' in str(_ra):         _ra,_dec=agnkey.agnabsphotdef.deg2HMS(_ra,_dec)

    aa=agnkey.agnsqldef.getfromdataraw(conn, 'recobjects', 'name', _object,'*')
    if len(aa)>=1: 
       _targid=aa[0]['targid']
       print _targid
       aa=agnkey.agnsqldef.getfromdataraw(conn, 'lsc_sn_pos','targid',str(_targid),'*')
       _RA,_DEC,_SN=aa[0]['ra_sn'],aa[0]['dec_sn'],aa[0]['name']
    else:
       aa=agnkey.agnsqldef.getfromcoordinate(conn, 'lsc_sn_pos', _ra, _dec,.3)
       if len(aa)==1:
          _RA,_DEC,_SN,_targid=aa[0]['ra_sn'],aa[0]['dec_sn'],aa[0]['name'],aa[0]['targid']
       else:
          _RA,_DEC,_SN,_targid='','','',''
    if not _targid:
       dictionary={'name':_object,'ra_sn':_ra,'dec_sn':_dec}
       agnkey.agnsqldef.insert_values(conn,'lsc_sn_pos',dictionary)
       bb=agnkey.agnsqldef.getfromcoordinate(conn, 'lsc_sn_pos', _ra, _dec,.01056)
       agnkey.agnsqldef.updatevalue('lsc_sn_pos','targid',bb[0]['id'],_object,connection='agnkey',namefile0='name')
       dictionary1={'name':_object,'targid':bb[0]['id']}
       agnkey.agnsqldef.insert_values(conn,'recobjects',dictionary1)
       _targid=bb[0]['id']
    if _targid:
       cc=agnkey.agnsqldef.getfromdataraw(conn,'permissionlog','targid', str(_targid),column2='groupname')
       if len(cc)==0:
          _JDn=agnkey.agnsqldef.JDnow()
          dictionary2={'targid':_targid,'jd':_JDn,'groupname':32769}
          agnkey.agnsqldef.insert_values(conn,'permissionlog',dictionary2)
    return _targid

#################################################################################
def getsky(data):
  """
  Determine the sky parameters for a FITS data extension.

  data -- array holding the image data
  """
  from numpy import random

  # maximum number of interations for mean,std loop
  maxiter = 30

  # maximum number of data points to sample
  maxsample = 10000

  # size of the array
  ny,nx = data.shape

  # how many sampels should we take?
  if data.size > maxsample:
    nsample = maxsample
  else:
    nsample = data.size

  # create sample indicies
  xs = random.uniform(low=0, high=nx, size=nsample).astype('L')
  ys = random.uniform(low=0, high=ny, size=nsample).astype('L')

  # sample the data
  sample = data[ys,xs].copy()
  sample = sample.reshape(nsample)

  # determine the clipped mean and standard deviation
  mean = sample.mean()
  std = sample.std()
  oldsize = 0
  niter = 0
  while oldsize != sample.size and niter < maxiter:
    niter += 1
    oldsize = sample.size
    wok = (sample < mean + 3*std)
    sample = sample[wok]
    wok = (sample > mean - 3*std)
    sample = sample[wok]
    mean = sample.mean()
    std = sample.std()
 
  return mean,std

################################################################################

def getlike(conn, table, column, value,column2='*'):
   import sys
   import MySQLdb,os,string
   try:
      cursor = conn.cursor (MySQLdb.cursors.DictCursor)
      cursor.execute ("select "+column2+" from "+str(table)+" where "+column+" like "+"'%"+value+"%'")
      resultSet = cursor.fetchall ()
      if cursor.rowcount == 0:
         pass
      cursor.close ()
   except MySQLdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit (1)
   return resultSet

##################################################################

def query(command):
   import MySQLdb,os,string
   lista=''
   import agnkey
   from agnkey.agnsqldef import conn
   try:
        cursor = conn.cursor (MySQLdb.cursors.DictCursor)
        for i in command:
            cursor.execute (i)
            lista = cursor.fetchall ()
            if cursor.rowcount == 0:
                pass
        cursor.close ()
   except MySQLdb.Error, e: 
        print "Error %d: %s" % (e.args[0], e.args[1])
   return lista

###########################################################3
#def JDnow(verbose=False):
#    import datetime
#    _MJD0=55927.8333333333333333
#    _MJDtoday=_MJD0+(datetime.datetime.now()-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
#        (datetime.datetime.now()-datetime.datetime(2012, 01, 01,00,00,00)).days
#    if verbose: print 'JD= '+str(_MJDtoday)
#    return _MJDtoday
###############################
def JDnow(datenow='',verbose=False):
   import datetime
   import time
   _JD0=2455927.5
   if not datenow:
      datenow=datetime.datetime(time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec)
   _JDtoday=_JD0+(datenow-datetime.datetime(2012, 01, 01,00,00,00)).seconds/(3600.*24)+\
             (datenow-datetime.datetime(2012, 01, 01,00,00,00)).days
   if verbose: print 'JD= '+str(_JDtoday)
   return _JDtoday
###################################
