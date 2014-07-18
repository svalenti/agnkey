#!/Users/svalenti/usr/Ureka/variants/common/bin/python

description=">> Calibrate local reference stars"
usage = "%prog filelist (.cat or all) [options] "

from numpy import mean, compress, std, zeros, cos,pi,array,sqrt,where,unique,argsort,arange,argmin,arccos,sin,median
import os,sys,string,re,glob
import pylab as plt
from pyraf import iraf
from optparse import OptionParser
import agnkey

def convertra(ra):
    import numpy
    ra=float(ra)
    ra1=int(ra)
    ra2=int((ra-ra1)*60.)
    ra3=round((((ra-ra1)*60.)-int((ra-ra1)*60.))*60,3)
    return '00'[len(str(ra1)):]+str(ra1)+':'+'00'[len(str(ra2)):]+str(ra2)+':'+'00'[len(str(int(ra3))):]+str(float(ra3))

def convertdec(ra):
    import numpy
    if float(ra)<0: sign='-'
    else: sign=''
    ra=float(abs(ra))
    ra1=int(ra)
    ra2=int((ra-ra1)*60.)
    ra3=round((((ra-ra1)*60.)-int((ra-ra1)*60.))*60,3)
    return str(sign)+'00'[len(str(ra1)):]+str(ra1)+':'+'00'[len(str(ra2)):]+str(ra2)+':'+'00'[len(str(int(ra3))):]+str(float(ra3))
#    return str(sign)+str(ra1)+':'+str(ra2)+':'+str(float(ra3))

def avgNight(allstar,mask):
    global ljd,f

    diffstar = zeros(allstar.shape)
                                          # average each star for all night
    for r in range(allstar.shape[1]):
        _mask = mask[:,r]
        _allstar = allstar[:,r]
        _diffstar = diffstar[:,r]
        d1 = where(_mask>=1)
        d2 = where(_mask>=2)
        d3 = where(_mask==3)
        if len(d3[0])>1:
            _magmean = mean(_allstar[d3])
            _magstd = std(_allstar[d3])
        elif len(d2[0])>1:
            _magmean = mean(_allstar[d2])
            _magstd = std(_allstar[d2])
        elif len(d1[0])>1:
            _magmean = mean(_allstar[d1])
            _magstd = std(_allstar[d1])
        _diffstar[d1] = _allstar[d1] - _magmean
        diffstar[:,r] = _diffstar

    dmean,dstd = [],[]
    for d in range(allstar.shape[0]):  # average night diff for all star
        _mask = mask[d,:]
        _diffstar = diffstar[d,:]
        d1 = where(_mask>=1)
        d2 = where(_mask>=2)
        if len(d2[0])>1:
            dmean.append(mean(_diffstar[d2]))
            dstd.append(std(_diffstar[d2]))
        elif len(d1[0])>1:
            dmean.append(mean(_diffstar[d1]))
            dstd.append(std(_diffstar[d1]))
            print '!!! WARNING: only poor stars left for filter',f,'& date',ljd[d] 
        else:
            dmean.append(0)
            dstd.append(999)
            print '!!! WARNING: no reference star left for filter',f,'& date',ljd[d] 
    
    rmean,rstd = [],[]
    for r in range(diffstar.shape[1]):     #  compute star dispersion
        _mask = mask[:,r]
        d1 = where(_mask>=1)
        _diffstar = array(dmean) - diffstar[:,r]
        if len(d1[0])>1: 
            rmean.append(mean(_diffstar[d1]))
            rstd.append(std(_diffstar[d1]))
        else: 
            rmean.append(999)
            rstd.append(999)

    return diffstar,array(dmean),array(dstd),array(rmean),array(rstd)

def show_refstars(MAGST,star,filterlist,interactive):
    global f,ljd,lstars,ijd,ist,ajd,ast,allstar,diffstar,mask,dmean,\
        dstd,rmean,rstd

    answ=''
    MAGavg,zerocor = {},{}
    for f in filterlist:
        ljd,lstars,nstars,lt = [],[],[],[]    # list of available nights/stars
        for t in MAGST.keys():
            for r in MAGST[t].keys():
                for d in MAGST[t][r].keys():
                    if f in MAGST[t][r][d].keys():
                        if d not in ljd:  
                            ljd.append(d)
                            lt.append(t)
                        if r not in lstars: 
                            lstars.append(r)
                            nstars.append(1)
                        else:
                            ii = lstars.index(r)
                            nstars[ii]+=1
        if len(ljd)<2: continue
        lt = array(lt)[argsort(ljd)][:]
        ljd.sort()
        lstars = compress(array(nstars)>1,(array(lstars)))
        lstars.sort()

        allstar = zeros((len(ljd),len(lstars)))
        mask = zeros((len(ljd),len(lstars)))

        for d in range(len(ljd)):
            for t in MAGST.keys():     # fill r,d matrix
                for r in range(len(lstars)):
                    if ljd[d] in MAGST[t][lstars[r]].keys():
                        if f in MAGST[t][lstars[r]][ljd[d]].keys():
                            allstar[d,r] = MAGST[t][lstars[r]][ljd[d]][f]
                            mask[d,r] = 3

        diffstar,dmean,dstd,rmean,rstd = avgNight(allstar,mask)
        
        if len(dmean)>5:
            njd = where(abs(dmean-mean(dmean))>std(dmean))
            for d in njd[0]:                 # 1 sigma rejection on jds
                _mask = mask[d,:]
                ii = where(_mask==3)
                _mask[ii] = 2
                mask[d,:] = _mask

        if len(rstd)>5:
            njd = where((abs(rmean-mean(rmean))>2*std(rmean)) | 
                        (rstd>2*mean(rstd)+std(dstd)))
            for r in njd[0]:                 # 2 sigma rejection on stars
                _mask = mask[:,r] 
                ii = where(_mask>=2)
                _mask[ii] = 1
                mask[:,r] = _mask

        diffstar,dmean,dstd,rmean,rstd = avgNight(allstar,mask) 

        ajd,ijd = [],[]
        for d in range(diffstar.shape[0]):       # index of good nights
            if 1 in mask[d,:] or 2 in mask[d,:]: ajd.append(d)
            if 3 in mask[d,:]: ijd.append(d)
        ajd += ijd
        ast,ist = [],[]
        for r in range(diffstar.shape[1]):       # index of good stars
            if 1 in mask[:,r]: ast.append(r)
            if 2 in mask[:,r] or 3 in mask[:,r]: ist.append(r)
        ast += ist

        if interactive and answ!='q':         #  plots
            print "-"*80
            plt.ion()
            fig = plt.figure(1)

            ax1 = plt.subplot(212)   # plot dates average x filter
            plt.errorbar(arange(len(ljd))[ajd],dmean[ajd],yerr=dstd[ajd],\
                             fmt='ob') 
            plt.plot(arange(len(ljd))[ijd],dmean[ijd],'or')
            riga1 = plt.axhline(0,color='b')
            plt.title('average zero-point for the different nights ')
            plt.xticks(range(len(ljd)),ljd,rotation=45,fontsize=8)
            plt.xlim(-1,len(ljd)+1)

            plt.ylim(min(dmean[ajd])-.3,max(dmean[ajd])+.3)
            plt.figtext(.3,.4,'std=%4.2f error=%5.3f' %\
                     (std(dmean[ijd]),std(dmean[ijd])/\
                         sqrt(len(ijd))),fontsize=14)

            ax2 = plt.subplot(211)
            plt.errorbar(arange(len(lstars))[ast],rmean[ast],yerr=rstd[ast],\
                             fmt='ob') 
            plt.plot(arange(len(lstars))[ist],rmean[ist],'or')
            plt.axhline(0,color='b')
            plt.title('Filter '+f+'      star dispersion measurements ')
            plt.xlim(-1,len(lstars)+1)
            plt.ylim(min(rmean[ast])-max(rstd[ast])-.2,\
                             max(rmean[ast])+max(rstd[ast])+.2)
            plt.figtext(.3,.85,'<sigma>=%5.3f  std(sigma)=%5.3f' %\
                 (mean(rmean[ist]),std(rmean[ist])),fontsize=14)

            cid = fig.canvas.mpl_connect('button_press_event', onclick1)

            plt.draw()
            answ = raw_input('left-click remove point, right-click restore '+\
                              '... Return to continue, q to exit ...\n')
            if len(answ)>0: 
                if answ == 'q': break
        plt.clf()

        # Compute zero point correction for date d
        ddmean = []
        for i in range(len(ljd)):
            d = ljd[i]
            _mask = mask[i,:]
            _diffstar = diffstar[i,:]
            d1 = where(_mask>=1)
            d2 = where(_mask>=2)
            if len(d2[0])>1:
                _dmean = mean(_diffstar[d2])
                _dstd = std(_diffstar[d2])/sqrt(len(d2[0]))
            elif len(d1[0])>1:
                _dmean = mean(_diffstar[d1])
                _dstd = std(_diffstar[d1])/sqrt(len(d1[0]))
            if len(d1[0])>1 or len(d2[0])>1:
                t = lt[i]
                if t not in zerocor.keys():zerocor[t] = {}
                if d not in zerocor[t].keys():zerocor[t][d] = {}
                ddmean.append(_dmean)
                zerocor[t][d][f] = [_dmean,_dstd,len(d2[0])]
            else: ddmean.append(0.)

        # Compute avg star mag for selected dates
        for i in range(len(lstars)):
            r = lstars[i]
            _mask = mask[:,i]
            _allstar = allstar[:,i]-array(ddmean)
            d2 = where(_mask>=2)
            if len(d2[0])>1:
                _magmean = mean(_allstar[d2])
                _magstd = std(_allstar[d2])/sqrt(len(d2[0]))

                if r not in MAGavg.keys():MAGavg[r] = {}
                for d in star[t][r].keys():
#############
#                    tmpra=[]
#                    tmpdec=[]
#                    if f in star[t][r][d].keys():
#                        tmpra.append(star[t][r][d][f]['ra'])
#                        tmpdec.append(star[t][r][d][f]['dec'])
############
                    if f in star[t][r][d].keys():
                        MAGavg[r]['ra'],MAGavg[r]['dec'] = \
                            star[t][r][d][f]['ra'],star[t][r][d][f]['dec']
                        break
                MAGavg[r][f] = [_magmean,_magstd,len(d2[0])]

    plt.close()
    return MAGavg,zerocor

def readasci(ascifile):
    f=open(ascifile,'r')
    ss=f.readlines()
    f.close()
    ra,dec,mag,dmag=[],[],[],[]
    for line in ss:
        if line[0]!='#':
            ra.append(iraf.real(line.split()[0]))
            dec.append(iraf.real(line.split()[1]))
            mag.append(line.split()[2])
            dmag.append(line.split()[3])
        else:
            if 'ra' in line:
                _filter=line.split()[2]
    return  ra,dec,mag,dmag,_filter
        

def onclick1(event):
    global f,ljd,lstars,ijd,ist,ajd,ast,allstar,diffstar,mask,dmean,dstd,rmean,rstd
    if event.inaxes:       
        if event.y<250:
            dx = abs(event.xdata-arange(len(ljd)))
            ii = argmin(dx)
            if event.button == 2 :
                if ii not in ijd: 
                    for r in arange(len(lstars)):
                        if mask[ii,r] == 2: mask[ii,r] = 3
            if event.button == 1:  
                if ii in ijd:
                    for r in arange(len(lstars)):
                        if mask[ii,r]==3: mask[ii,r] = 2

        if event.y>250:
            dx = abs(event.xdata-arange(len(lstars)))
            ii = argmin(dx)
            if event.button == 2 :
                if ii not in ist: 
                    for d in arange(len(ljd)):
                        if mask[d,ii] ==1: mask[d,ii] = 2
            if event.button == 1:  
                if ii in ist:
                    for d in arange(len(ljd)):
                        if mask[d,ii] >= 2: mask[d,ii] = 1
                                
        diffstar,dmean,dstd,rmean,rstd = avgNight(allstar,mask) 
        
        ajd,ijd = [],[]
        for d in range(diffstar.shape[0]):       # index of good nights
            if 1 in mask[d,:]  or 2 in mask[d,:]: ajd.append(d)
            if 3 in mask[d,:]: ijd.append(d)
        ajd += ijd
        ast,ist = [],[]
        for r in range(diffstar.shape[1]):       # index of good stars
            if 1 in mask[:,r]: ast.append(r)
            if 2 in mask[:,r] or 3 in mask[:,r]: ist.append(r)
        ast += ist

        plt.clf()
        ax1 = plt.subplot(212)   # plot dates average x filter
        plt.errorbar(arange(len(ljd))[ajd],dmean[ajd],yerr=dstd[ajd],fmt='ob') 
        plt.plot(arange(len(ljd))[ijd],dmean[ijd],'or')
        plt.axhline(0,color='b')
        plt.title('average zero-point for the different nights ')   
        plt.xticks(range(len(ljd)),ljd,rotation=45,fontsize=8)
        plt.xlim(-1,len(ljd)+1)
        plt.ylim(min(dmean[ajd])-.3,max(dmean[ajd])+.3)
        plt.figtext(0.3,.4,'sigma=%4.2f error=%5.3f' %\
                (std(dmean[ijd]),std(dmean[ijd])/\
                         sqrt(len(ijd))),fontsize=14)

        ax2 = plt.subplot(211)
        plt.errorbar(arange(len(lstars))[ast],rmean[ast],yerr=rstd[ast],\
                         fmt='ob') 
        plt.plot(arange(len(lstars))[ist],rmean[ist],'or')
        plt.axhline(0,color='b')
        plt.title('Filter '+f+'      star dispersion measurements ')
        plt.xlim(-1,len(lstars)+1)
        plt.ylim(min(rmean[ast])-max(rstd[ast])-.2,\
                         max(rmean[ast])+max(rstd[ast])+.2)
        plt.figtext(0.3,.85,'std(sigma)=%5.3f' %\
              (std(rmean[ist])),fontsize=14)

########################################################################################3
def getmag(asci):
    obs={}
    obs['fts']={}
    for _file in asci:
        ras,decs,mags,dmags,_filter=readasci(_file)
#        _filter=_file.split('-')[1]
#        _ut=_file.split('-')[2]
        try:
            _ut=_file.split('-')[1]+'_'+_file.split('-')[2]+'_'+_file.split('-')[3]
        except:
            _ut=_file.split('_')[2]+'_'+_file.split('_')[3]+'_'+_file.split('_')[4]
        if _ut not in obs['fts'].keys(): obs['fts'][_ut]={}
        if _filter not in  obs['fts'][_ut].keys(): obs['fts'][_ut][_filter]={}
        if 'ra' not in obs['fts'][_ut][_filter].keys():     obs['fts'][_ut][_filter]['ra'] = []
        if 'dec' not in obs['fts'][_ut][_filter].keys():    obs['fts'][_ut][_filter]['dec'] = []
        if 'mag' not in obs['fts'][_ut][_filter].keys():    obs['fts'][_ut][_filter]['mag'] = []
        if 'merr' not in obs['fts'][_ut][_filter].keys():    obs['fts'][_ut][_filter]['merr'] = []
        obs['fts'][_ut][_filter]['ra']=obs['fts'][_ut][_filter]['ra']+list(ras)
        obs['fts'][_ut][_filter]['dec']=obs['fts'][_ut][_filter]['dec']+list(decs)
        obs['fts'][_ut][_filter]['mag']=obs['fts'][_ut][_filter]['mag']+list(array(mags,float))
        obs['fts'][_ut][_filter]['merr']=obs['fts'][_ut][_filter]['merr']+list(array(dmags,float))


    ra,dec = [],[]
    for t in obs.keys():
        for d in obs[t].keys():
            for f in obs[t][d].keys():
                for i in range(len(obs[t][d][f]['ra'])):
                    _ra = obs[t][d][f]['ra'][i]
                    _dec = obs[t][d][f]['dec'][i]
                    ra.append(iraf.real(_ra))
                    dec.append(iraf.real(_dec))
    ra,dec = array(ra),array(dec)
    from pylab import ion,plot
    ion()
    plot(ra,dec,'.r')
    raw_input('go on')

    ii,idstar = 0,zeros(len(ra),dtype=int)         # match stars coordinates
    for i in range(len(ra)):
        if idstar[i] == 0:
            scal=pi/180.
            dist=arccos(sin(dec*scal)*sin(dec[i]*scal)+cos(dec*scal)*cos(dec[i]*scal)*cos((ra-ra[i])*scal))*((180/pi))
            #dist = sqrt(((ra-ra[i])*cos(dec[i]*pi/180.))**2+(dec-dec[i])**2)
            imatch = where(dist*3600. < 3.5)
            ii += 1
            idstar[imatch] = ii
    refstar =  unique(idstar)
    print ' Found ',len(refstar),' different stars'
    j = 0
    for t in obs.keys():                            # assign star names
        for d in obs[t].keys():
            for f in obs[t][d].keys():
                obs[t][d][f]['idstar'] = []
                for i in range(len(obs[t][d][f]['ra'])):
                    obs[t][d][f]['idstar'].append(idstar[j])
                    j += 1
    MAGST,star = {},{}
    for t in obs.keys():        
        MAGST[t],star[t] = {},{} 
        for r in refstar:
            star[t][r] = {}
            MAGST[t][r] = {}                  # compute calibrate mag
            for d in obs[t].keys():
                star[t][r][d]  = {}
                MAGST[t][r][d] = {}
                mag,_ra,_dec = {},{},{}
                for f in obs[t][d].keys():
                    for i in range(len(obs[t][d][f]['mag'])):
                        if r ==  obs[t][d][f]['idstar'][i]:
                             MAGST[t][r][d][f]=obs[t][d][f]['mag'][i]
                             star[t][r][d][f]={'dec':obs[t][d][f]['dec'][i],'ra':obs[t][d][f]['ra'][i]}

    return  MAGST,star,ra,dec

##################################################################################################
if __name__ == "__main__":   ################################################
    parser = OptionParser(usage=usage,description=description)
    parser.add_option("-i", "--interactive",action="store_true",\
                      dest='interactive',default=False,\
                          help='Interactive \t\t\t [%default]')
    parser.add_option("-f", "--field",dest="field",default='landolt',type="str",
                  help='system landolt,sloan \t [%default]')
    parser.add_option("-o", "--output",dest="output",default='',type="str",
                  help='output name \t [%default]')

    option,args = parser.parse_args()
    if len(args)<1 : sys.argv.append('--help')
    option,args = parser.parse_args()
    _field=option.field
    _output=option.output
    _interactive=option.interactive
    if args[0] == 'all':
        lista = glob.glob('*sw.cat')
    else:
        ff= open(args[0])
        lista = [x.strip('\n') for x in ff.readlines()]

    MAGST,star,rra,ddec=getmag(lista)
    #name=lista[0].split('.')[0]
    if _field=='landolt':
        filterlist=['U','B','V','R','I']
    else:
        filterlist=['u','g','r','i','z']

    from pylab import ion,clf,plot
    avgra,avgdec={},{}
    for t in star.keys():
#########################
        for r in star[t].keys():
            print '_'*10+' Calibrated ref star n.',r
            tmpra=[]
            tmpdec=[]
#            clf()
            color='rbgmy'
            aaa=0
            for f in filterlist:
                hasfilt = False
                for d in star[t][r].keys():            
                    if f in MAGST[t][r][d].keys():
                        print d,'   ',f,'   ',star[t][r][d][f]['ra'],\
                            star[t][r][d][f]['dec'],\
                            '   ','%6.3f' % (MAGST[t][r][d][f])
                        tmpra.append(star[t][r][d][f]['ra'])
                        tmpdec.append(star[t][r][d][f]['dec'])
                        hasfilt = True            
            #            plot(star[t][r][d][f]['ra'],star[t][r][d][f]['dec'],'x'+color[aaa])
                if hasfilt: print 
                aaa=aaa+1
            if len(tmpra)>3:
                avgra[r]=median(tmpra)
                avgdec[r]=median(tmpdec)

    print '#'*80

    MAGavg,zerocor = show_refstars(MAGST,star,filterlist,_interactive)

    from numpy import sin,cos,arccos,pi, argmin
    import datetime
    now=datetime.datetime.now()
    datenow=now.strftime('20%y%m%d_%H_%M')
    for ll in [0,1,2,3,4,5,6,7]:
        try:
            _ra,_dec=MAGavg[ll]['ra']*15,MAGavg[ll]['dec']
            break
        except: pass
        
    std,rastd,decstd,magstd=agnkey.util.readstandard('supernovaelist.txt')
    scal=pi/180.
    dd=arccos(sin(_dec*scal)*sin(decstd*scal)+cos(_dec*scal)*cos(decstd*scal)*cos((_ra-rastd)*scal))*((180/pi)*3600)
    if min(dd)<1000: 
        _RA=rastd[argmin(dd)]
        _DEC=decstd[argmin(dd)]
        _SN=std[argmin(dd)]
    else:
        _RA,_DEC,_SN='','',''
    if not _output:
        if _SN: filename=_SN+'_'+_field+'_'+datenow+'.cat'
        else: filename='catalogue_'+_field+'_'+datenow+'.cat'
    else:
        filename=_output

    print '###### '+filename

    nfield=3+len(filterlist)*2
    ff = open(filename,'w')
    header='# BEGIN CATALOG HEADER\n# nfields '+str(nfield)+'\n#     ra     1  0 d degrees %10.5f\n#     dec    2  0 d degrees %10.5f\n'
    header=header+'#     id     3  0 c INDEF %15s\n'
    nn=4
    for f in filterlist:
        header=header+'#     '+str(f)+'      '+str(nn)+' 0 r INDEF %6.2f\n'
        nn=nn+1
        header=header+'#     '+str(f)+'err   '+str(nn)+' 0 r INDEF %6.2f\n'
        nn=nn+1
    header=header+'# END CATALOG HEADER\n#\n'
    ff.write(header)
    for r in MAGavg.keys():
        if r in avgra:
            ff.write('%14s %14s  %3s  ' % (str(avgra[r]*15),str(avgdec[r]),str(r)))
#        else:
#            ff.write('%14s %14s  %3s  ' % (str(MAGavg[r]['ra']*15),str(MAGavg[r]['dec']),str(r)))
            for f in filterlist:
                if f in MAGavg[r].keys():
                    ff.write(' %6.3f %6.3f  ' % (MAGavg[r][f][0],MAGavg[r][f][1]))
                else: ff.write(' %6.1f %6.3f  ' % (9999,0.00))
            ff.write('\n')
    ff.close()

