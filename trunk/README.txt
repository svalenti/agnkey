###########################################################################
# 
#                                   agnkey Pipeline
#
#                              INSTALLATION
###########################################################################

NTT is written in python and requires the following package:

- Python 2.5 or Python 2.6 or Python 2.7
   these modules have to be installed:
            - numpy
	    - pyraf
	    - matplotlib
	    - pyfits
	    - mysqldb
            - ephem

- Iraf
	    
##############################################################################
extract the files from the tarball
> tar -xvf agnkey-version.tar

> cd agnkey-version
> python setup.py install  (--record files.txt) --prefix=/user_directory  (eg /Users/svalenti)

##########################################################################
To uninstall a previous version 

- delete the agnkey directory in your site-package path
- delete the agnkey****.egg-info from the same directory
- delete the agnkey executable:agnkey 

or if during installation  you used the option: --record files.txt
you can run the following command in the terminal:
> cat files.txt | xargs sudo rm -rf

############################################################

SET UP MARSHALL  STEP    BY    STEP 

###########################################################
MAKE THE REDUCTION DIRECTORY: 

mkdir xxx/xxx/AGNKEY/
mkdir xxx/xxx/AGNKEY/1mtel/
mkdir xxx/xxx/AGNKEY/floydsraw/
mkdir xxx/xxx/AGNKEY/logfile/ 
mkdir xxx/xxx/AGNKEY/spectra/

EDIT  agnkey/src/agnkey/util.py  AND CHANGE FEW DIRECTORIES

>>>>>>>>>
workingdirectory='/Users/svalenti/redu2/AGNKEY/'            TO BE CHANGE  in   xxx/xxx/AGNKEY/ 
execdirectory='/Users/svalenti/bin/'                        TO BE CHANGE  in   bin directory of the user than run the pipeline    
rawdata='/archive/engineering/' 
#  rawdata not needed for agnkey since we will download from ipac
#proposal=['LCOELP-001','DDTLCO-009','STANET-001']            #   proposals
#users=['stefano_valenti','stefano_valenti','stefano_valenti']     #   passwd for trigger
proposal=['STANET-001','DDTLCO-008'] #,'LCOELP-001']            #   proposals                 TO BE CHANGE
users=['stefano_valenti','stefano_valenti'] #,'stefano_valenti']     #   passwd for trigger   TO BE CHANGE

superusers=['SV','KH','CV','dsand','agnkey']                         
# 
# IPAC user and passwd
ipacuser='svalenti@lcogt.net'                      TO BE CHANGE  to the user that have access to IPAC
ipacpasswd='eIgheeK_'                              TO BE CHANGE  to the pass for IPAC
>>>>>

IN ORDER TO TRIGGER THE TELESCOPE THE PASSWORD FOR THE LCOGT PORTAL SHOULD BE THE SAME THAN THE ONE FOR IPAC
##############################################################################################
EDIT   src/agnkey/agnsqldef.py  AND CHANGE INFO ON THE DATABASE ON LINE 6 
  'agnkey':{'passwd':'agnkey_pass','username':'agnkey','hostname':'localhost','database':'AGNKEY'}}

#############################################################################################
COPY FILES FOR THE WEB IN THE cgi-bin/ DIRECTORY

cp src/agnkey/webpagescript/agnkeymain.py     WEBLOCATION/cgi-bin/
cp src/agnkey/webpagescript/agnkeyview.cgi    WEBLOCATION/cgi-bin/
cp src/agnkey/webpagescript/agnupdatetable.py WEBLOCATION/cgi-bin/
cp src/agnkey/webpagescript/fast_plot2.py     WEBLOCATION/cgi-bin/
cp src/agnkey/webpagescript/take_asci2.py     WEBLOCATION/cgi-bin/

############################################################################################
LINK DATA DIRECTORY ON THE WEB

ln -s xxx/xxx/AGNKEY/  WEBLOCATION/AGNKEY/

############################################################################################
# Crongjob to schedule new observations   (modified as needed)
55 * * * * . /dark/hal/.cronfile2 ;  /dark/anaconda/anaconda27/envs/halenv/bin/agnscheduler_V3.py >>  /dark/hal/cronfile/cronscheduler.log   2>&1

# cronjob to download the data
40 12 * * * . /dark/hal/.cronfile2 ; /dark/anaconda/anaconda27/envs/halenv/bin/runagn.py -X -i >>  /dark/hal/cronfile/cronagn.log  2>&1

#######################################
database structure here

https://www.dropbox.com/scl/fi/nvfai7587cgod4ss52zmf/agnkey.sql?rlkey=ykc27461wzdbvc1itam5137ka&st=gp3i0f8v&dl=0
