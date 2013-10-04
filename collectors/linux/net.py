#!/usr/bin/python3
import subprocess, time, sys

def main():

	Interval = 15
	Net_Hold = dict()
	PrevTS = 0
	while True:
		CurrTS = time.time()
		P = subprocess.Popen('cat /proc/net/dev'.split(), stdout=subprocess.PIPE)
		Text = P.stdout.read()
		inb = 0
		outb = 0
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
				if Iface in Net_Hold:   #### Not first call, so data to be sent
					inb += BytesRec - Net_Hold[Iface]['inBytes']
					outb += BytesSent - Net_Hold[Iface]['outBytes']
				else:
					Net_Hold[Iface] = dict()
				Net_Hold[Iface]['inBytes'] = BytesRec
				Net_Hold[Iface]['outBytes'] = BytesSent

		#print ('raw in, raw out:', inb, outb) #!!!
		if (PrevTS > 0) :
			TimeSpan = CurrTS - PrevTS
			inb *= 8  #### convert from bytes to bits
			outb *= 8
			inb /= 1024*1024  #### convert from bits to Mbits
			outb /= 1024*1024
			inb /= TimeSpan   #### Divide by time between 2 samples
			outb /= TimeSpan
			sys.stdout.write ("stats.machine.net %d %.2f type=%s\n" % (int(CurrTS), inb, 'inMbps'))
			sys.stdout.write ("stats.machine.net %d %.2f type=%s\n" % (int(CurrTS), outb, 'outMbps'))
			sys.stdout.flush()

		P.wait()
		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
