import copy, glob

def func(filename):
	s=set()
	with open(filename) as fd:
		next(fd)
		for l in fd:
			line = l.strip()
			s.add(line)

	s2 = set()
	for l in s:
		r = l.split()[1]+" "+l.split()[0]
		if (r not in s2) and (l not in s2):
			s2.add(l)
	print(len(s), len(s2))

	with open(filename, "w+") as fd:
		fd.write("200\n")
		for l in s2:
			fd.write(l+"\n")

for source_file in glob.glob("[0-9]*.txt"):
	func(source_file)
