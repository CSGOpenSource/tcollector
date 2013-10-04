#!/usr/bin/env python
import subprocess, sys, time
	
def get_devlist():
	DevList = []
	P = subprocess.Popen('ifconfig -a'.split(), stdout=subprocess.PIPE)
	D = P.stdout.read()
	#print (D.decode())
	for Line in D.decode().splitlines():
		if not Line.startswith('\t'):  ####  Start of info for a network device
			if Line[0] != 'l':  ####  Not a loopback device
				Loc = Line.find(':')
				DevList.append(Line[:Loc])
	
	#print (DevList)
	return DevList

#________________________________________________________________

def parse_response(Text):

	for Line in Text.decode().splitlines():
		if Line.startswith('Bytes:'):
			A = Line.split()
			outcounter = int(A[1])
			incounter = int(A[3])
			break

	return incounter, outcounter

#________________________________________________________________


def main():

	Interval = 15
	DevList = get_devlist()
	State = dict()
	PrevTS = 0

	while True:
		inb = 0
		outb = 0
		CurrTS = time.time()
		for Dev in DevList:  ####  Iterate on each device
			Cmd = 'entstat -d ' + Dev
			P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
			Text = P.stdout.read()
			incounter, outcounter = parse_response(Text)
			if Dev not in State:
				State[Dev] = dict()
			else: 
				inb += incounter - State[Dev]['incounter']
				outb += outcounter - State[Dev]['outcounter']
			State[Dev]['incounter'] = incounter
			State[Dev]['outcounter'] = outcounter
			P.wait()
		#print('inb:', inb, '  outb:', outb) #!!!
		if PrevTS > 0:  ####  print out results
			inb *= 8  #### Convert bytes to bits
			outb *= 8  #### Convert bytes to bits
			inb /= 1024*1024   ####  Convert bits to Mbits
			outb /= 1024*1024   ####  Convert bits to Mbits
			sys.stdout.write("stats.machine.net %d %.2f type=inMbps\n" % (int(CurrTS), inb/(CurrTS-PrevTS)))
			sys.stdout.write("stats.machine.net %d %.2f type=outMbps\n" % (int(CurrTS), outb/(CurrTS-PrevTS)))
			sys.stdout.flush()
		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()

