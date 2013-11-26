#!/usr/bin/env python
"""
Finds and prints different entities in a game file, including mobs, items, and vehicles.
"""

import locale, os, sys, time, argparse
# local module
try:
	import nbt
except ImportError:
	# nbt not in search path. Let's see if it can be found in the parent folder
	extrasearchpath = os.path.realpath(os.path.join(__file__,os.pardir,os.pardir))
	if not os.path.exists(os.path.join(extrasearchpath,'nbt')):
		raise
	sys.path.append(extrasearchpath)
from nbt.world import WorldFolder

world_folder = "blank"

def inBlockArray(array, ele):
	i = 0
	for sub in array:
		if sub[0] == ele:
			return i
		i += 1
	return -1

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Scan a minecraft Anvil world and count ores')
	parser.add_argument('world', metavar='W', nargs=1, help='the world folder to scan')
	parser.add_argument('-i', metavar='input', required=True, nargs=1, help='Input file, contains blocks to search for in the following format, one per line, blockID[:datavalue]  If no datavalue is given all blocks with the given ID are counted')
	parser.add_argument('-o', metavar='output', nargs=1, help='Output file. If not given, the program prints to console')
	parser.add_argument('-d', action='store_true', help='Calculate and output height distributions of ores')
	parser.add_argument('-b', action='store_true', help='Calculate per biome count of ores')
	parser.add_argument('-B', action='store_true', help='Calculate per biome height distribution, includes -b')
	parser.add_argument('-c', action='store_true', help='Calculate average cluster size (not implemented)')
	parser.add_argument('-n', action='store_true', help='Build a list of nearby blocks for each ore type (not implemented)')
	parser.add_argument('-s', action='store_true', help='Search a world to try to discover all ore types and output to given output file. Ignores other options. (not implemented)')
	args = parser.parse_args()
	if args.B:
		args.b = True
	print(args)
	
	world_folder = str(args.world).strip('"\'[]')
	# clean path name, eliminate trailing slashes:
	world_folder = os.path.normpath(world_folder)
	if (not os.path.exists(world_folder)):
		print("No such folder as "+world_folder)
		sys.exit(72) # EX_IOERR
	
	find = [0] * 4096
	found = [0] * 4096
	
	inputfile = open("input.txt","r")
	line = inputfile.readline().strip("\n\r")
	i = 1
	while line != "":
		ele = line.split(":")
		if len(ele) == 1:
			ele.append("-1")
		if len(ele) != 2:
			print("Aborting, wrong number of arguments in line "+str(i)+" : "+line)
			sys.exit()
		try:
			if find[int(ele[0])] == 0:
				find[int(ele[0])] = [[int(ele[1]), [0] * 256]]
			elif find[int(ele[0])][0][0] == -1 or [int(ele[1]), 0] in find[int(ele[0])]:
				print("Warning, block "+line+" already covered, ignoring")
			else:
				find[int(ele[0])].append([int(ele[1]), [0] * 256])
				find[int(ele[0])].sort()
		except IndexError:
			print("Aborting, ID too large in line "+str(i)+" : "+line)
			sys.exit()
		except ValueError:
			print("Aborting, bad value in line "+str(i)+" : "+line)
			sys.exit()
		line = inputfile.readline().strip("\n\r")
		i += 1
	inputfile.close()
	#print(find)

	#return

	counter = 0
	world = WorldFolder(world_folder)
	
	print("Counting chunks")
	numchunks = 0
	for chunk in world.iter_nbt():
		numchunks += 1
		sys.stdout.write('%d chunks\r' % (numchunks))
		sys.stdout.flush()
	#numchunks = 689
	print("")
	chunknum = 0
	try:
		for chunk in world.iter_nbt():
			chunknum += 1
			sys.stdout.write('%d / %d chunks searched\r' % (chunknum, numchunks))
			sys.stdout.flush()
			for microchunk in chunk["Level"]["Sections"]:
				i = 0
				for block in microchunk["Blocks"]:
					tempblock = block
					if microchunk.__contains__("Add"):
						if block != 0: # TODO
							add = microchunk["Add"][int(i/2)]
							if i%2 == 0:
								add = (add & 0x0F) << 8
							else:
								add = (add & 0xF0) << 4
							tempblock = tempblock | add
					subid = 0
					if block != 0:
						subid = microchunk["Data"][int(i/2)]
						if i%2 == 0:
							subid = (subid & 0x0F)
						else:
							subid = (subid & 0xF0) >> 4
					
					#x = i%16+int(chunk["Level"]["xPos"].__str__())*16
					#y = int(i/256)+int(microchunk["Y"].__str__())*16
					#z = int(i/16)%16+int(chunk["Level"]["zPos"].__str__())*16
					
					if find[tempblock] != 0:
						y = int(i/256)+int(microchunk["Y"].__str__())*16
						if find[tempblock][0][0] == -1:
							find[tempblock][0][1][y] += 1
						else:
							temp = inBlockArray(find[tempblock], subid)
							if temp != -1:
								find[tempblock][temp][1][y] += 1
					i += 1

	except KeyboardInterrupt:
		sys.exit() # EX_TEMPFAIL
	print()

	i = 0
	for block in find:
		if block != 0:
			if block[0][0] == -1:
				print("Block "+str(i)+" has distribution "+str(block[0][1]))
			else:
				for subid in block:
					print("Block "+str(i)+" with data value "+str(subid[0])+" has distribution "+str(subid[1]))
		i += 1
	
	
	sys.exit()
