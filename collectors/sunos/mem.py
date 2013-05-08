#!/usr/bin/env python3.2
import subprocess, time, sys

def get_totmem():

	Cmd = 'kstat -p unix:0:system_pages:physmem'
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	Text = P.stdout.readline().decode().strip()
	Stuff, TotMem = Text.split()
	Cmd = 'pagesize'
	P = subprocess.Popen(Cmd, stdout=subprocess.PIPE)
	PageSize = P.stdout.readline().decode().strip()
	
	return float(TotMem), float(PageSize)

#____________________________________________________________________________

def realmem(TotMem):

	Cmd = 'kstat -p unix:0:system_pages:freemem'
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	Text = P.stdout.readline().decode().strip()
	Stuff, FreeMem = Text.split()
	PctMem = 100. - 100.*(float(FreeMem)/TotMem)
	CurrTS = time.time()
	sys.stdout.write ("tcollector.mem %d %.2f type=%s\n" % (int(CurrTS), PctMem, 'realmem'))
	sys.stdout.flush()

	return

#____________________________________________________________________________

def swap():

	Cmd = 'swap -l'
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	Text = P.stdout.readlines()
	for L in Text:
		Line = L.decode()
		if not Line.startswith('swapfile'):   #### This line contains the real data
			A = Line.strip().split()
			L = len(A)
			PctSwap = 100.*(float(A[L-2])-float(A[L-1]))/float(A[L-2])
			CurrTS = time.time()
			sys.stdout.write ("tcollector.mem %d %.2f type=%s\n" % (int(CurrTS), PctSwap, 'swap'))
			sys.stdout.flush()
			break

	return

#____________________________________________________________________________

def zfsmem(TotMem, PageSize):

	Cmd = 'kstat -p zfs:0:arcstats:size'
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	Text = P.stdout.readline().decode().strip()
	Stuff, ZFSMem = Text.split()
	PctZFS = 100.*float(ZFSMem)/(PageSize*TotMem)
	CurrTS = time.time()
	sys.stdout.write ("tcollector.mem %d %.2f type=%s\n" % (int(CurrTS), PctZFS, 'zfsmem'))
	sys.stdout.flush()

	return

#____________________________________________________________________________

def main(TotMem, PageSize):

	Interval = 15
	while True:
		CurrTS = time.time()
		realmem(TotMem)
		swap()
		zfsmem(TotMem, PageSize)
		SleepTime = Interval - (time.time()-CurrTS)
		if SleepTime > 0:  time.sleep(SleepTime)

	return

#_______________________________________________________________

if __name__ == "__main__":
	TotMem, PageSize = get_totmem()   ####  TotMem in Number of pages
	main(TotMem, PageSize)
