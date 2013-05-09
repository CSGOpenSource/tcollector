#!/usr/bin/env python3.2
import subprocess, time, sys

def main():

	Interval = 15
	PrevT = 0
	State = dict()
	State['R'] = dict()
	State['W'] = dict()
	readb = 0
	writeb = 0
	Cmd = 'kstat -c disk -p'.split()
	while True:
		CurrT = time.time()
		P = subprocess.Popen(Cmd, stdout=subprocess.PIPE)
		Text = P.stdout.readlines()
		for Linex in Text:
			Line = Linex.decode().strip()
			A = Line.split(':')
			if 'nread' in Line:
				Dev = A[2]
				Item, Val = A[3].split()
				if Dev in State['R']:
					readb += float(Val)-State['R'][Dev]
				State['R'][Dev] = float(Val)
			elif 'nwritten' in Line:
				Dev = A[2]
				Item, Val = A[3].split()
				if Dev in State['W']:
					writeb += float(Val)-State['W'][Dev]
				State['W'][Dev] = float(Val)
		if PrevT > 0:
			TimeSpan = CurrT - PrevT
			readb /= TimeSpan   #### Divide by time between 2 samples
			writeb /= TimeSpan
			sys.stdout.write ("tcollector.dsk %d %.2f type=%s\n" % (int(CurrT), readb, 'rKbps'))
			sys.stdout.write ("tcollector.dsk %d %.2f type=%s\n" % (int(CurrT), writeb, 'wkBps'))
			sys.stdout.flush()
			readb = 0
			writeb = 0
		PrevT = CurrT
		SleepT = Interval - (time.time()-CurrT)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
