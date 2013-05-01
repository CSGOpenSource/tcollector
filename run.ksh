set -x #!!
#python3 tcollector.py -d --logfile=logfile.txt -P pidfile.txt
python3 tcollector.py --logfile=logfile.txt -P pidfile.txt -H sqtrhel-test01.csg.csgsystems.com -p 4242 &
