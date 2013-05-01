#!/usr/bin/python3
import subprocess, time, sys

def main():

	State = dict()
	PrevTS = 0
	Tags = ['usr', 'sys', 'iow', 'idl']
	FieldLoc = [1,3,5,4]
	while True:
		P = subprocess.Popen('cat /proc/stat'.split(), stdout=subprocess.PIPE)
		Text = P.stdout.read()
		CurrTS = time.time()
		for Line in Text.decode().splitlines():
			if Line.startswith('cpu '):
				A = Line.split()
				Key = A[0]
				if Key in State:   #### Not first call
					for i in range(len(Tags)):
						Val = (float(A[FieldLoc[i]]) - State[Key][Tags[i]]) / (CurrTS-PrevTS)
						sys.stdout.write ("tcollector.cpu %d %.2f type=%s\n" % (int(CurrTS), Val, Tags[i]))
					sys.stdout.flush()
				else:
					State[Key] = dict()
				for i in range(len(Tags)):
					State[Key][Tags[i]] = float(A[FieldLoc[i]])
		P.wait()
		PrevTS = CurrTS
		time.sleep(15)

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
