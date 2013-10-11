#!/usr/bin/env python
import subprocess, sys, time
	
def get_devlist():
	IfaceList = []
	P = subprocess.Popen('ifconfig -a'.split(), stdout=subprocess.PIPE)
	D = P.stdout.read()
	#print (D.decode())
	for Line in D.decode().splitlines():
		if not Line.startswith('\t'):  ####  Start of info for a network device
			if Line[0] != 'l':  ####  Not a loopback device
				Loc = Line.find(':')
				IfaceList.append(Line[:Loc])
	
	#print (IfaceList)
	return IfaceList

#________________________________________________________________

def parse_response(Text):

	for Line in Text.decode().splitlines():
		if Line.startswith('Bytes:'):
			A = Line.split()
			sent_counter = int(A[1])
			rec_counter = int(A[3])
			break

	return rec_counter, sent_counter

#________________________________________________________________


def main():

	Interval = 15
	IfaceList = get_devlist()
	State = {'R': {}, 'S': {}}
	PrevVal = {'R': {}, 'S': {}}
	PrevTS = 0

	while True:
		recb = 0
		sentb = 0
		CurrTS = time.time()
		for Iface in IfaceList:  ####  Iterate on each device
			Cmd = 'entstat -d ' + Iface
			P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
			P.wait()
			Text = P.stdout.read()
			rec_counter, sent_counter = parse_response(Text)
			if Iface in State['R']:
				Diff = rec_counter - State['R'][Iface]
				if Diff < 0.: Diff = PrevVal['R'][Iface]
				recb += Diff
				PrevVal['R'][Iface] = Diff
				Diff = sent_counter - State['S'][Iface]
				if Diff < 0.: Diff = PrevVal['S'][Iface]
				sentb += Diff
				PrevVal['S'][Iface] = Diff
			else: 
				PrevVal['R'][Iface] = 0.
				PrevVal['S'][Iface] = 0.
			State['R'][Iface] = rec_counter
			State['S'][Iface] = sent_counter
		#print('recb:', recb, '  sentb:', sentb) #!!!
		if PrevTS > 0:  ####  print out results
			recb *= 8  #### Convert bytes to bits
			sentb *= 8  #### Convert bytes to bits
			recb /= 1024*1024   ####  Convert bits to Mbits
			sentb /= 1024*1024   ####  Convert bits to Mbits
			sys.stdout.write("stats.machine.net %d %.2f type=inMbps\n" % (int(CurrTS), recb/(CurrTS-PrevTS)))
			sys.stdout.write("stats.machine.net %d %.2f type=outMbps\n" % (int(CurrTS), sentb/(CurrTS-PrevTS)))
			sys.stdout.flush()
		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()

