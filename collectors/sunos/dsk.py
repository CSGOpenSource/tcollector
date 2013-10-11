#!/usr/bin/env python3.2
import subprocess, time, sys

def main():

	Interval = 15
	PrevT = 0
	State = {'R': {}, 'W': {}}
	PrevVal = {'R': {}, 'W': {}}
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
					Diff = float(Val)-State['R'][Dev]
					if Diff < 0.: Diff = PrevVal['R'][Dev]
					readb += Diff
					PrevVal['R'][Dev] = Diff
				else:
					PrevVal['R'][Dev] = 0.
				State['R'][Dev] = float(Val)
			elif 'nwritten' in Line:
				Dev = A[2]
				Item, Val = A[3].split()
				if Dev in State['W']:
					Diff = float(Val)-State['W'][Dev]
					if Diff < 0.: Diff = PrevVal['W'][Dev]
					writeb += Diff
					PrevVal['W'][Dev] = Diff
				else:
					PrevVal['W'][Dev] = 0.
				State['W'][Dev] = float(Val)
		if PrevT > 0:
			TimeSpan = CurrT - PrevT
			readb /= 1024   ####  Convert from bytes to kBytes
			writeb /= 1024
			readb /= TimeSpan   #### Divide by time between 2 samples
			writeb /= TimeSpan
			sys.stdout.write ("stats.machine.dsk %d %.2f type=%s\n" % (int(CurrT), readb, 'rkBps'))
			sys.stdout.write ("stats.machine.dsk %d %.2f type=%s\n" % (int(CurrT), writeb, 'wkBps'))
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
