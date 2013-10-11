#!/usr/bin/env python3.2
import subprocess, time, sys

def main():

	Interval = 15
	PrevT = 0
	State = {'R': {}, 'S': {}}
	PrevVal = {'R': {}, 'S': {}}
	recb = 0
	sentb = 0
	Cmd = 'kstat -p :::/^.bytes/'.split()
	while True:
		CurrT = time.time()
		P = subprocess.Popen(Cmd, stdout=subprocess.PIPE)
		P.wait()
		Text = P.stdout.readlines()
		for L in Text:
			Line = L.decode().strip()
			A = Line.split()
			Iface = A[0]
			if 'rbytes\t' in Line:
				if Iface in State['R']:   ####  Not first pass. Data to be collected
					Diff = float(A[1])-State['R'][Iface]
					if Diff < 0.: Diff = PrevVal['R'][Iface]
					recb += Diff
					PrevVal['R'][Iface] = Diff
				else:
					PrevVal['R'][Iface] = 0.
				State['R'][Iface] = float(A[1])
			elif 'obytes\t' in Line:
				if Iface in State['S']:   ####  Not first pass. Data to be collected
					Diff = float(A[1])-State['S'][Iface]
					if Diff < 0.: Diff = PrevVal['S'][Iface]
					sentb += Diff
					PrevVal['S'][Iface] = Diff
				else:
					PrevVal['S'][Iface] = 0.
				State['S'][Iface] = float(A[1])
		if PrevT > 0:
			TimeSpan = CurrT - PrevT
			recb *= 8  #### convert from bytes to bits
			sentb *= 8
			recb /= 1024*1024  #### convert from bits to Mbits
			sentb /= 1024*1024
			recb /= TimeSpan   #### Divide by time between 2 samples
			sentb /= TimeSpan
			sys.stdout.write ("stats.machine.net %d %.2f type=%s\n" % (int(CurrT), recb, 'inMbps'))
			sys.stdout.write ("stats.machine.net %d %.2f type=%s\n" % (int(CurrT), sentb, 'outMbps'))
			sys.stdout.flush()
			recb = 0
			sentb = 0
		PrevT = CurrT
		SleepT = Interval - (time.time()-CurrT)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
