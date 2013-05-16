#!/usr/bin/python3
import subprocess, time, sys

def get_sector_size():

	#P = subprocess.Popen('cat /sys/block/sda/queue/hw_sector_size'.split(), stdout=subprocess.PIPE)
	P = subprocess.Popen('ls /sys/block'.split(), stdout=subprocess.PIPE)
	P.wait()
	L = P.stdout.readlines()
	SecSize = dict()
	for Item in L:
		Dev = Item.decode().strip()
		Text = 'cat /sys/block/' + Dev + '/queue/hw_sector_size'
		P = subprocess.Popen(Text.split(), stdout=subprocess.PIPE)
		P.wait()
		L = P.stdout.read()
		SecSize[Dev] = float(L.decode().strip())/1024.   #### SecSize in kBytes
	return SecSize

#______________________________________________________________________

def main():

	Interval = 15
	SecSize = get_sector_size()
	State = dict()
	PrevTS = 0
	readLoc = 5
	writeLoc = 9
	while True:
		CurrTS = time.time()
		P = subprocess.Popen('cat /proc/diskstats'.split(), stdout=subprocess.PIPE)
		Text = P.stdout.read()
		kBrTot = 0
		kBwTot = 0
		for Line in Text.decode().splitlines():
			A = Line.split()
			if len(A) > 8:  ####  Has enough data on line to parse
				Dev = A[2]
				if Dev in SecSize:  SSize = SecSize[Dev]
				else:  SSize = SecSize['sda']
				kBr = int(A[readLoc])*SSize
				kBw = int(A[writeLoc])*SSize
				if Dev in State:   #### Not first call, so data to be sent
					kBrTot += kBr - State[Dev]['kBr']
					kBwTot += kBw - State[Dev]['kBw']
				else:
					State[Dev] = dict()
				State[Dev]['kBr'] = kBr
				State[Dev]['kBw'] = kBw

		#print ('raw read, raw write:', kBrTot, kBwTot) #!!!
		if (PrevTS > 0) :
			TimeSpan = CurrTS - PrevTS
			kBrTot /= TimeSpan   #### Divide by time between 2 samples
			kBwTot /= TimeSpan
			sys.stdout.write ("tcollector.dsk %d %.2f type=%s\n" % (int(CurrTS), kBrTot, 'rkBps'))
			sys.stdout.write ("tcollector.dsk %d %.2f type=%s\n" % (int(CurrTS), kBwTot, 'wkBps'))
			sys.stdout.flush()

		P.wait()
		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
