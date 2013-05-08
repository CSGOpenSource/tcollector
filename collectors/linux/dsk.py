#!/usr/bin/python3
import subprocess, time, sys

def get_sector_size():

	P = subprocess.Popen('cat /sys/block/sda/queue/hw_sector_size'.split(), stdout=subprocess.PIPE)
	L = P.stdout.read()
	SecSize = int(L.strip())
	P.wait()
	return SecSize

#______________________________________________________________________

def main():

	Interval = 15
	SecSize = get_sector_size()
	kBFactor = float(SecSize)/1024.
	State = dict()
	PrevTS = 0
	readLoc = 5
	writeLoc = 9
	while True:
		CurrTS = time.time()
		P = subprocess.Popen('cat /proc/diskstats'.split(), stdout=subprocess.PIPE)
		Text = P.stdout.read()
		readsec = 0
		writesec = 0
		for Line in Text.decode().splitlines():
			A = Line.split()
			if len(A) > 8:  ####  Has enough data on line to parse
				Dev = A[2]
				SectorsRead = int(A[readLoc])
				SectorsWritten = int(A[writeLoc])
				if Dev in State:   #### Not first call, so data to be sent
					readsec += SectorsRead - State[Dev]['readsec']
					writesec += SectorsWritten - State[Dev]['writesec']
				else:
					State[Dev] = dict()
				State[Dev]['readsec'] = SectorsRead
				State[Dev]['writesec'] = SectorsWritten

		#print ('raw read, raw write:', readsec, writesec) #!!!
		if (PrevTS > 0) :
			TimeSpan = CurrTS - PrevTS
			readb = readsec*kBFactor  #### convert from sectors to KBytes
			writeb = writesec*kBFactor
			readb /= TimeSpan   #### Divide by time between 2 samples
			writeb /= TimeSpan
			sys.stdout.write ("tcollector.dsk %d %.2f type=%s\n" % (int(CurrTS), readb, 'rkBps'))
			sys.stdout.write ("tcollector.dsk %d %.2f type=%s\n" % (int(CurrTS), writeb, 'wkBps'))
			sys.stdout.flush()

		P.wait()
		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
