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
	State = {'R': {}, 'W': {}}
	PrevVal = {'R': {}, 'W': {}}
	PrevTS = 0
	readLoc = 5
	writeLoc = 9
	while True:
		CurrTS = time.time()
		P = subprocess.Popen('cat /proc/diskstats'.split(), stdout=subprocess.PIPE)
		P.wait()
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
				if Dev in State['R']:   #### Not first call, so data to be sent
					Diff = kBr - State['R'][Dev]
					if Diff < 0:  Diff = PrevVal['R'][Dev]
					kBrTot += Diff
					PrevVal['R'][Dev] = Diff
					Diff = kBw - State['W'][Dev]
					if Diff < 0:  Diff = PrevVal['W'][Dev]
					kBwTot += Diff
					PrevVal['W'][Dev] = Diff
				else:
					PrevVal['R'][Dev] = 0.
					PrevVal['W'][Dev] = 0.
				State['R'][Dev] = kBr
				State['W'][Dev] = kBw

		#print ('raw read, raw write:', kBrTot, kBwTot) #!!!
		if (PrevTS > 0) :
			TimeSpan = CurrTS - PrevTS
			kBrTot /= TimeSpan   #### Divide by time between 2 samples
			kBwTot /= TimeSpan
			sys.stdout.write ("stats.machine.dsk %d %.2f type=%s\n" % (int(CurrTS), kBrTot, 'rkBps'))
			sys.stdout.write ("stats.machine.dsk %d %.2f type=%s\n" % (int(CurrTS), kBwTot, 'wkBps'))
			sys.stdout.flush()

		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
