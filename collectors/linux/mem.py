#!/usr/bin/python3
import subprocess, time, sys

def main():

	Interval = 15
	State = dict()
	while True:
		CurrTS = time.time()
		P = subprocess.Popen('cat /proc/meminfo'.split(), stdout=subprocess.PIPE)
		Text = P.stdout.read()
		for Line in Text.decode().splitlines():
			if Line.startswith('MemTotal:'):
				A = Line.split()
				MemTotal = int(A[1])
			elif Line.startswith('MemFree:'):
				A = Line.split()
				MemFree = int(A[1])
			elif Line.startswith('SwapTotal:'):
				A = Line.split()
				SwapTotal = int(A[1])
			elif Line.startswith('SwapFree:'):
				A = Line.split()
				SwapFree = int(A[1])
			elif Line.startswith('Cached:'):
				A = Line.split()
				Cached = int(A[1])
		PctMem = 100.*(float(MemTotal)-float(MemFree))/float(MemTotal)
		PctSwap = 100.*(float(SwapTotal)-float(SwapFree))/float(SwapTotal)
		PctCached = 100.*float(Cached)/float(MemTotal)
		sys.stdout.write ("stats.machine.mem %d %.2f type=%s\n" % (int(CurrTS), PctMem, 'realmem'))
		sys.stdout.write ("stats.machine.mem %d %.2f type=%s\n" % (int(CurrTS), PctSwap, 'swap'))
		sys.stdout.write ("stats.machine.mem %d %.2f type=%s\n" % (int(CurrTS), PctCached, 'cached'))
		sys.stdout.flush()
		P.wait()
		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
