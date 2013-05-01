#!/usr/bin/env python3.2
import subprocess, time, sys

def get_windows_header(Text):

	Windows_header = dict()
	A = Text.split(',')
	for i in range(len(A)):
		if 'Processor(_Total)' in A[i] and 'User Time' in A[i]:  Windows_header['usr'] = i
		elif 'Processor(_Total)' in A[i] and 'Privileged Time' in A[i]:  Windows_header['sys'] = i
		elif 'Processor(_Total)' in A[i] and 'Idle Time' in A[i]:  Windows_header['idl'] = i

	return Windows_header

def main():

	Interval = 15
	Cmd = ['typeperf', '-si', str(Interval), '-cf', 'typerf.txt']
	print ('*** Command:', Cmd) #!!!
	#sys.exit()
	P = subprocess.Popen(Cmd, stdout=subprocess.PIPE)
	while True:
		TextRaw = P.stdout.readline().decode().strip()
		Text = TextRaw.replace('"','')
		print ('Text:', Text) #!!
		if P.poll() is not None:  sys.exit()
		if len(Text) > 1 and not Text[0].isdigit():   ####  First line, so extract locations of CPU stats
			FieldLoc = get_windows_header(Text)
		elif len(Text) > 1:
			A = Text.split(',')
			CurrTS = time.time()
			Sum = 0
			for Key,Loc in FieldLoc.items():
				V = float(A[Loc])
				sys.stdout.write ("tcollector.cpu %d %.2f type=%s\n" % (int(CurrTS), V, Key))
				Sum += V
			sys.stdout.write ("tcollector.cpu %d %.2f type=%s\n" % (int(CurrTS), max(100.-Sum,0), 'iow'))
			sys.stdout.flush()

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
