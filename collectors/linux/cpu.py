#!/usr/bin/python3
import subprocess, time, sys

def main():

	Interval = 15
	State = dict()
	PrevTS = 0
	Tags = ['usr', 'sys', 'iow', 'idl']
	Val = [0]*4
	FieldLoc = [1,3,5,4]
	while True:
		CurrTS = time.time()
		P = subprocess.Popen('cat /proc/stat'.split(), stdout=subprocess.PIPE)
		Text = P.stdout.read()
		for Line in Text.decode().splitlines():
			if Line.startswith('cpu '):
				A = Line.split()
				if 'usr' in State:   #### Not first call
					Sum = 0
					for i in range(len(Tags)):
						Val[i] = (float(A[FieldLoc[i]]) - State[Tags[i]]) / (CurrTS-PrevTS)
						Sum += Val[i]
					for i in range(len(Tags)):
						sys.stdout.write ("tcollector.cpu %d %.2f type=%s\n" % (int(CurrTS), 100.*Val[i]/Sum, Tags[i]))
					sys.stdout.flush()
				for i in range(len(Tags)):
					State[Tags[i]] = float(A[FieldLoc[i]])
		P.wait()
		PrevTS = CurrTS
		SleepT = Interval - (time.time()-CurrTS)
		if SleepT > 0:  time.sleep(SleepT)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
