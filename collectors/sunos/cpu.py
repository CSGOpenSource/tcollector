#!/usr/bin/env python3.2
import subprocess, time, sys

def main():

	Interval = 15
	Tags = ['usr', 'sys', 'iow', 'idl']
	FieldLoc = [0,1,2,3]
	Cmd = 'iostat -c ' + str(Interval)
	P = subprocess.Popen(Cmd.split(), stdout=subprocess.PIPE)
	UseData = False
	while True:
		Text = P.stdout.readline().decode().strip()
		if  len(Text) > 0 and Text[0].isdigit():
			if UseData:  ###  Skip over first iostat entry because it is erroneous
				for Line in Text.splitlines():
					L = Line.strip()
					A = L.split()
					CurrTS = time.time()
					for i in range(len(Tags)):
						sys.stdout.write ("stats.machine.cpu %d %.2f type=%s\n" % (int(CurrTS), float(A[FieldLoc[i]]), Tags[i]))
					sys.stdout.flush()
			UseData = True

	return

#_______________________________________________________________

if __name__ == "__main__":
	main()
