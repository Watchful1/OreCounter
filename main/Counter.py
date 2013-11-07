#!/usr/bin/env python
"""
Finds and prints different entities in a game file, including mobs, items, and vehicles.
"""

import locale, os, sys, time
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

class Position(object):
	def __init__(self, x,y,z):
		self.x = x
		self.y = y
		self.z = z

class Entity(object):
	def __init__(self, type, pos):
		self.type  = type
		self.pos   = Position(*pos)


def entities_per_chunk(chunk):
	"""Given a chunk, find all entities (mobs, items, vehicles)"""
	entities = []
	for entity in chunk['Entities']:
		x,y,z = entity["Pos"]
		entities.append(Entity(entity["id"].value, (x.value,y.value,z.value)))
	return entities

def bsearch(array, element, first, last, calls):
	print first, last, calls
	print(first,last)
	if (last - first) < 2:
		print("First check")
		if array[first][0] == element:
			return first
		elif array[last][0] == element:
			return last
		else:
			return False
	mid = first + (last - first)/2
	print(first,last,mid)
	if array[mid][0] == element:
		print("Mid is element")
		return True
	if array[mid][0] > element:
		print("Bigger than element, going down")
		return bsearch(array, element, first, mid - 1, calls+1)
	print("Smaller than element, going up")
	return bsearch(array, element, mid + 1, last, calls + 1)

def search(array, element):
	return bsearch(array, element, 0, len(array) - 1, 1)

def inBlockArray(array, ele):
	#print("\nLooking for "+str(ele)+" in "+str(array))
	i = 0
	for sub in array:
		if sub[0] == ele:
			#if i == 0:
				#print("It was zero!")
			#print("Found it")
			return i
		i += 1
	#print("Didn't find it")
	return -1

def main(world_folder):
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
			return
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
			return
		except ValueError:
			print("Aborting, bad value in line "+str(i)+" : "+line)
			return
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
			#if chunknum > 938:
			#	return
			if chunknum > 0:
				for microchunk in chunk["Level"]["Sections"]:
					i = 0
					for block in microchunk["Blocks"]:
						tempblock = block
						if microchunk.__contains__("Add"):
							if block != 0:
								add = microchunk["Add"][int(i/2)]
								if i%2 == 0:
									add = (add & 0x0F) << 8
								else:
									add = (add & 0xF0) << 4
								#if add != 0:
								#	counter += 1
								tempblock = tempblock | add
								#if tempblock > 256:
								#	print(tempblock)
						subid = 0
						if block != 0:
							subid = microchunk["Data"][int(i/2)]
							if i%2 == 0:
								subid = (subid & 0x0F)
							else:
								subid = (subid & 0xF0) >> 4
						
						#if tempblock == 2502 and subid == 13:
						#	print("\nX: "+str(i%16+int(chunk["Level"]["xPos"].__str__())*16)+" Y: "+str(int(i/256)+int(microchunk["Y"].__str__())*16)+" Z: "+str(int(i/16)%16+int(chunk["Level"]["zPos"].__str__())*16)+"\n")
							#print("\n\nAdd: "+str(hex(block))+" i: "+str(i)+"\n\n")
						
						#x = i%16+int(chunk["Level"]["xPos"].__str__())*16
						#y = int(i/256)+int(microchunk["Y"].__str__())*16
						#z = int(i/16)%16+int(chunk["Level"]["zPos"].__str__())*16
						
						
						
						#found[tempblock] += 1
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
		return 75 # EX_TEMPFAIL
	print()
	#print("Counter "+str(counter))
	#print(found)
	#print(find)
	i = 0
	for block in find:
		if block != 0:
			if block[0][0] == -1:
				print("Block "+str(i)+" has distribution "+str(block[0][1]))
			else:
				for subid in block:
					print("Block "+str(i)+" with data value "+str(subid[0])+" has distribution "+str(subid[1]))
		i += 1
	return 0 # NOERR


if __name__ == '__main__':
	if (len(sys.argv) == 1):
		print("No world folder specified!")
		sys.exit(64) # EX_USAGE
	world_folder = sys.argv[1]
	# clean path name, eliminate trailing slashes:
	world_folder = os.path.normpath(world_folder)
	if (not os.path.exists(world_folder)):
		print("No such folder as "+world_folder)
		sys.exit(72) # EX_IOERR
	
	sys.exit(main(world_folder))
