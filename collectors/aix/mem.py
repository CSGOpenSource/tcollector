#!/usr/bin/env python
import subprocess, time, sys

def get_totmem():

	Cmd = 'lparstat -i'
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	for Line in P.stdout:
		if 'Online Memory' in Line:   ####  Get Real Memory Size
			A = Line.decode().split()
			TotMem = float(A[len(A)-2])*1024
	
	return TotMem

#____________________________________________________________________________

def realmem(TotMem):

	Cmd = 'vmstat 1 2'
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	P.wait()
	Text = P.stdout.readlines()
	Line = Text[len(Text)-1].decode()
	A = Line.split()
	PctMem = 400.*float(A[2])/TotMem
	CurrTS = time.time()
	sys.stdout.write ("stats.machine.mem %d %.2f type=%s\n" % (int(CurrTS), PctMem, 'realmem'))
	sys.stdout.flush()

	return

#____________________________________________________________________________

def swap():

	Cmd = 'lsps -s'
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	P.wait()
	Text = P.stdout.readlines()
	Line = Text[len(Text)-1].decode()
	A = Line.strip().split()
	P = A[1].replace('%','')
	PctSwap = float(P)
	CurrTS = time.time()
	sys.stdout.write ("stats.machine.mem %d %.2f type=%s\n" % (int(CurrTS), PctSwap, 'swap'))
	sys.stdout.flush()

	return

#____________________________________________________________________________

def main(TotMem):

	Interval = 15
	while True:
		CurrTS = time.time()
		realmem(TotMem)
		swap()
		SleepTime = Interval - (time.time()-CurrTS)
		if SleepTime > 0:  time.sleep(SleepTime)

	return

#_______________________________________________________________

if __name__ == "__main__":
	TotMem = get_totmem()   ####  TotMem in KBytes
	main(TotMem)
