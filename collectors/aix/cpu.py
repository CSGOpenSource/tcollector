#!/usr/bin/env python
import subprocess, time, sys

def get_NCPU():

	Cmd = 'lparstat -i'
	P = subprocess.Popen(Cmd, shell=True, stdout=subprocess.PIPE)
	for Line in P.stdout:
		if 'Online Virtual CPUs' in Line:   #### Get No. of CPUs
			A = Line.decode().split()
			NCPU = A[len(A)-1]
			break

	return NCPU

def main():

	NCPU = get_NCPU()
	Interval = 15
	Tags = ['usr', 'sys', 'iow', 'idl']
	FieldLoc = [0,1,2,3]
	Cmd = 'lparstat ' + str(Interval)
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	while True:
		Text = P.stdout.readline().decode().strip()
		if  len(Text) > 0 and Text[0].isdigit():
			for Line in Text.splitlines():
				L = Line.strip()
				if L[0].isdigit():    #!!!!  Data line
					A = L.split()
					CurrTS = time.time()
					CPURatio = float(A[4])/float(NCPU)
					Sum = 0
					for i in range(3):
						V = float(A[FieldLoc[i]])*CPURatio
						sys.stdout.write ("tcollector.cpu %d %.2f type=%s\n" % (int(CurrTS), V, Tags[i]))
						Sum += V
					sys.stdout.write ("tcollector.cpu %d %.2f type=%s\n" % (int(CurrTS), 100.-Sum, Tags[3]))
						
					sys.stdout.flush()

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
