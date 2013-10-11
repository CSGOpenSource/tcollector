#!/usr/bin/python3
import subprocess, time, sys

def main():

	Interval = 15
	State = {'R': {}, 'S': {}}
	PrevVal = {'R': {}, 'S': {}}
	PrevTS = 0
	while True:
		CurrTS = time.time()
		P = subprocess.Popen('cat /proc/net/dev'.split(), stdout=subprocess.PIPE)
		P.wait()
		Text = P.stdout.read()
		recb = 0
		sentb = 0
		for Line in Text.decode().splitlines():
			A = Line.split()
			if ':' in A[0]:
				B = A[0].strip().split(':')
				Iface = B[0]
				if len(B[1]) > 0:   ###  Bytes received part of first entity on line
					BytesRec = float(B[1])
					BytesSentLoc = 8
				else:
					BytesRec = float(A[3])
					BytesSentLoc = 9
				BytesSent = float(A[BytesSentLoc])
				if Iface in State['R']:   #### Not first call, so data to be sent
					Diff = BytesRec - State['R'][Iface]
					if Diff < 0.: Diff = PrevVal['R'][Iface]
					recb += Diff
					PrevVal['R'][Iface] = Diff
					Diff = BytesSent - State['S'][Iface]
					if Diff < 0.: Diff = PrevVal['S'][Iface]
					sentb += Diff
					PrevVal['S'][Iface] = Diff
				else:
					PrevVal['R'][Iface] = 0.
					PrevVal['S'][Iface] = 0.
				State['R'][Iface] = BytesRec
				State['S'][Iface] = BytesSent

		#print ('raw in, raw out:', recb, sentb) #!!!
		if (PrevTS > 0) :
			TimeSpan = CurrTS - PrevTS
			recb *= 8  #### convert from bytes to bits
			sentb *= 8
			recb /= 1024*1024  #### convert from bits to Mbits
			sentb /= 1024*1024
			recb /= TimeSpan   #### Divide by time between 2 samples
			sentb /= TimeSpan
			sys.stdout.write ("stats.machine.net %d %.2f type=%s\n" % (int(CurrTS), recb, 'inMbps'))
			sys.stdout.write ("stats.machine.net %d %.2f type=%s\n" % (int(CurrTS), sentb, 'outMbps'))
			sys.stdout.flush()

		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
