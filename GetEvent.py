#!/usr/bin/python
#this script needs taup_time(calculate travel time) ,distaz(calculate distance between two points)
#GetEvent souce_acrchive  destination_acrchive array_info_file event_list
import sys
import os
import commands
import time
import datetime
#user function define
###################################################
#this function is used to push pde info to header of the ascii file
def edit_asc(fname,pde):
	inf=file(fname,'r')
	if(not inf):
		print "file ",fname," not found "
		return
	abc=[]
	for line in inf.readlines():
		abc.append(line)
	inf.close()

	inf=file(fname,'w')
	print >> inf,pde,
	for i in range(0,len(abc)):
		print >> inf,abc[i],
	inf.close()
###################################################
#this function compare station info provide by user and staion info in original data
def check_sta(fname,stla,stlo):
	inf=file(fname,'r')
	if(not inf):
		print "file ",fname," not found "
		return
	for i in range(0,20):
		str0=inf.readline()
		if(str0[0:4]=="$LLA"):
			break
	inf.close()

	l0=str0.split()
	lat=l0[0][5:len(l0[0])]
	lon=l0[1]
	distaz="distaz "+stla+" "+stlo+" "+lat+" "+lon
	status, out1= commands.getstatusoutput(distaz)
	if(status!=0):
		print distaz
		print "Command distaz failed"
		return 99
	dist=float(out1.split()[0])
	print distaz,"dist ",dist
	return dist
###################################################

#main program start

###################################################
outf=file("GetEvent.sh",'w')
###################################################
print "\tDeal with command line parameters\n"
s_arc=""
d_arc=""
s_info=""
event_l=""
for i in range(1,len(sys.argv)):
	if(sys.argv[i]=="-par"):
		par_path=sys.argv[i+1]
		i=i+1
		continue
print "\tBegin to read parameters list file...."
inf=file(par_path,'r')
if(not inf):
	print "\terror: parameters file not found"
	quit()
tmp = inf.readline()
#tmp = inf.readline()
par=[]
while inf:
	tmp = inf.readline()
	if(tmp==""):
		break
	par.append(tmp.split())		
inf.close()
b_dist=""
e_dist=""
formt=""
for i in range(1,len(par)):
#	print par[i]
	if(par[i][0]=="source_acrchive"):
		s_arc=par[i][1]
		i=i+1

		continue
	if(par[i][0]=="destination_acrchive"):

		if(len(par[i])<2):
			print "\t error destination archive must be specified"
			quit()
		d_arc=par[i][1]
		i=i+1
		continue
	if(par[i][0]=="array_info"):
		s_info=par[i][1]
		i=i+1
		continue
	if(par[i][0]=="event_list"):
		event_l=par[i][1]
		i=i+1
		continue
	if(par[i][0]=="phase"):
		if(len(par[i])<2):
			print "\terror phase must be specified"
		phase=par[i][1]
		i=i+1
		continue
	if(par[i][0]=="epicentral_distance_range"):
		if(len(par[i])<3):
			i=i+1
			continue
		b_dist=par[i][1]
		e_dist=par[i][2]
		i=i+1
		continue
	if(par[i][0]=="magnitude_range"):
		if(len(par[i])<3):
			i=i+1
			continue
		b_mag=par[i][1]
		e_mag=par[i][2]
		i=i+1
		continue
	if(par[i][0]=="time_window"):
		if(len(par[i])<3):
			print "\t error time window must be specified"
			quit()
		b_t=par[i][1]
		e_t=par[i][2]
		i=i+1
		continue
	if(par[i][0]=="file_format"):
		if(len(par[i])<2):
			print "\t error file format must be specified"
			quit()
		formt=par[i][1]
		i=i+1
		continue
if(s_arc[len(s_arc)-1:len(s_arc)]!='/'):
	s_arc+='/'
if(d_arc[len(d_arc)-1:len(d_arc)]!='/'):
	d_arc+='/'
s_info=s_arc+s_info
event_l=s_arc+event_l	

if(s_arc=="" or d_arc=="" or s_info=="" or event_l=="" ):
	print "error ussage of GetEvent.py"
	print "GetEvent.py ussage:"
	print "GetEvent.py -par parameters list file",
	quit()

##############################################################
print "\tOpen station info file and read them all\n"
inf=file(s_info,'r')
if(not inf):
	print "station info file not found"
	quit()
station=[]
while inf:
	tmp = inf.readline()
	if(tmp==""):
		break
	if(tmp[0]=="#" or len(tmp)<3):
		continue
	print tmp
	station.append(tmp.split())		
inf.close()


print "\tOpen event list file and read them all\n"
inf=file(event_l,'r')
if(not inf):
	print "event list file not found"
	quit()
event=[]
while inf:
	tmp = inf.readline()
	if(tmp==""):
		break
	event.append(tmp)		
inf.close()
#############################################################################
#
#os.system("echo >error.fatal")
str0=s_arc+"error.fatal"
errf=file(str0,'wb')
#############################################################################
print "\tBegin to cut event data from raw data\n"

for i in range(0,len(station)):
	print "\tprocessing station:	",station[i][0],"\n"
	cmd="mkdir "+d_arc+station[i][0]
	print >> outf,cmd
	os.system(cmd)
#copy archive.sta to data directory
	cmd="cp archive.sta "+s_arc+station[i][0]
	print >> outf,cmd

	os.system(cmd)

	for j in range(0,len(event)):
		str0=event[j][62:65]
		if(len(str0.split())==0):
			continue
		if(event[j][1:4]!="PDE" or float(str0)<float(b_mag) or float(str0)>float(e_mag)):
			continue
		print "\tProcessing event infomation","\n",

		elat=event[j][32:39]
		elon=event[j][40:48]
		edep=event[j][49:53]
		eyear=int(event[j][9:13])
		emonth=int(event[j][14:16])
		eday=int(event[j][17:19])
		ehour=int(event[j][20:22])
		emin=int(event[j][22:24])
		esec=float(event[j][24:26])
		emmsec=0
		str0=event[j][26:29]
		if len(str0.split())!=0:
			emmsec=float(str0)*1000000
		slat=station[i][1]
		slon=station[i][2]
		distaz="distaz "+elat+" "+elon+" "+slat+" "+slon
		status, out1= commands.getstatusoutput(distaz)
		if(status!=0):
			print distaz
			print "Command distaz failed"
			continue

		dist=float(out1.split()[0])
		if(dist>float(e_dist) or dist<float(b_dist)):
			continue	

#day=get day 
		d1=datetime.datetime(eyear, emonth, eday)
		d0=datetime.datetime(eyear, 1, 1)
		day=(d1-d0).days+1

#time=calculate phase arriving time
		cmd="taup_time -mod prem -h "+edep+" -evt "+elat+"  "+elon+"  "+" -sta "+slat+"  "+slon+" -ph "+phase+" -time"
		status, out1= commands.getstatusoutput(cmd)
#		print cmd
#		print out1,status
		if(status!=0 or out1=='\n'):
			print cmd
			print "Command taup_time failed"
			continue
		time=float(out1.split()[0])
		time=time-abs(float(b_t))
		
#get_event using arcfetch	
		d2=datetime.datetime(eyear,emonth,eday,ehour,emin,esec,emmsec)+datetime.timedelta(seconds=time)
		str0=str(d2)
		kyear=str0[0:4]
		ktime=str0[11:len(str0)-1]
		path=s_arc+station[i][0]
		time=abs(float(b_t))+abs(float(e_t))
		arcfetch="./arcfetch "+path+" -C  *,*,*,"+kyear+":"+str(day)+":"+ktime+",+"+str(time)+" lqm.rt"

		status, out1= commands.getstatusoutput(arcfetch)
#		print arcfetch 
#		print status,out1
		if(status!=0):
			print arcfetch
			print "Command arcfetch failed"
			continue		
#convert the data to proper format
		path=d_arc+station[i][0]
#################################################################
#convert to sac file
		if(formt=="sac"):
#first add event header to data file convert by rt_asc
			os.system("rm *.atr")
			print >> outf,"rm *.atr"
			cmd="./rt_asc  lqm.rt ."
			os.system(cmd)
			print >> outf,cmd
			status, out1= commands.getstatusoutput("ls *.atr")
			asc_lst=out1.split()
			if(status!=0):
				print "no atr file found "
				continue
			
			for k in range(0,len(asc_lst)):
				dist=check_sta(asc_lst[k],slat,slon)
				if(dist*111.19>10):
#the error of station position estimation > 10km
					print >> errf,arcfetch
					print >> errf,"the error of station position estimation of ",station[i][0]," is ",str(dist),"km"
#					cmd0="echo "+arcfetch+">>error.fatal"
#					os.system(cmd0)
#					cmd0="echo the error of station position estimation of "+station[i][0]
#					cmd0=cmd0+" is "+str(dist)+" >>error.fatal"
#					os.system(cmd0)
				edit_asc(asc_lst[k],event[j])
				cmd="asc2sac  "+asc_lst[k]+"  "
				print >> outf,cmd
				os.system(cmd)
			cmd="cp *.sac "+d_arc+station[i][0]
			print >> outf,cmd
			os.system(cmd)
			print >> outf,"rm *.sac"
			os.system("rm *.sac")
#################################################################
#convert to mseed file
		elif(formt=="mseed"):
			cmd="./rt_mseed -P"+path+" lqm.rt"
			print >> outf,cmd
			os.system(cmd)
		else:
			print "this is end "

outf.close()
