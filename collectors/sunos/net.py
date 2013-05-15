#!/usr/bin/env python3.2
import subprocess, time, sys

def main():

	Interval = 15
	PrevT = 0
	Net_Hold = dict()
	inb = 0
	outb = 0
	Cmd = 'kstat -p :::/^.bytes/'.split()
	while True:
		CurrT = time.time()
		P = subprocess.Popen(Cmd, stdout=subprocess.PIPE)
		Text = P.stdout.readlines()
		for L in Text:
			Line = L.decode().strip()
			A = Line.split()
			if 'rbytes\t' in Line:
				if A[0] in Net_Hold:
					inb += float(A[1])-Net_Hold[A[0]]
				Net_Hold[A[0]] = float(A[1])
			elif 'obytes\t' in Line:
				if A[0] in Net_Hold:
					outb += float(A[1])-Net_Hold[A[0]]
				Net_Hold[A[0]] = float(A[1])
		if PrevT > 0:
			TimeSpan = CurrT - PrevT
			inb *= 8  #### convert from bytes to bits
			outb *= 8
			inb /= 1024*1024  #### convert from bits to Mbits
			outb /= 1024*1024
			inb /= TimeSpan   #### Divide by time between 2 samples
			outb /= TimeSpan
			sys.stdout.write ("tcollector.net %d %.2f type=%s\n" % (int(CurrT), inb, 'inMBps'))
			sys.stdout.write ("tcollector.net %d %.2f type=%s\n" % (int(CurrT), outb, 'outMBps'))
			sys.stdout.flush()
			inb = 0
			outb = 0
		PrevT = CurrT
		SleepT = Interval - (time.time()-CurrT)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
