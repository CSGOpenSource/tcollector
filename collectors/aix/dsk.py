#!/usr/bin/env python
import subprocess, time, sys

def main():

	Interval = 15
	PrevT = 0
        State = {'R': {}, 'W': {}}
        PrevVal = {'R': {}, 'W': {}}
	readb = 0
	writeb = 0
	Cmd = 'iostat -s'.split()
	while True:
		CurrT = time.time()
		P = subprocess.Popen(Cmd, stdout=subprocess.PIPE)
		Text = P.stdout.readlines()
		Process = False
		for Line in Text:
			if Line.startswith('Disks:'):  Process = True
			elif Process:
				A = Line.strip().split()
				Dev = A[0]
				if Dev in State['R']:
					Diff = float(A[4])-State['R'][Dev]
					if Diff < 0.: Diff = PrevVal['R'][Dev]
					readb += Diff
					PrevVal['R'][Dev] = Diff
					Diff = float(A[5])-State['W'][Dev]
					if Diff < 0.: Diff = PrevVal['W'][Dev]
					writeb += Diff
					PrevVal['W'][Dev] = Diff
				else:
					PrevVal['R'][Dev] = 0.
					PrevVal['W'][Dev] = 0.
				State['R'][Dev] = float(A[4])
				State['W'][Dev] = float(A[5])
		if PrevT > 0:
			TimeSpan = CurrT - PrevT
			readb /= TimeSpan   #### Divide by time between 2 samples
			writeb /= TimeSpan
			sys.stdout.write ("stats.machine.dsk %d %.2f type=%s\n" % (int(CurrT), readb, 'rKbps'))
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
