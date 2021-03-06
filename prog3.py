# Eric Perez, Alisa Bohac, Mike Keck
# Op Systems Program 3

import sys
import math

verbose = 0
# Total Memory available for allocation
MSIZE = -1
# Smallest block that can be used to allocate a request
ASIZE = -1
# A lists of lists to represent the free lists
buddy_lists = []
# The number of lists within the buddy_lists
num_lists = 0
# Dictionary to hold requests
requests = []

class Request:
    request_id = 0
    request_size = 0
    state = 0
    memory_size = 0 
    address = 0

    def __init__(self, request_id, request_size, state, memory_size, address):
        self.request_id = request_id
        self.request_size = request_size
        self.state = state
        self.memory_size = memory_size
        self.address = address

def main():
    # Get the file from the command line argument
    file_input = open_input_file()
    # Set the MSIZE and ASIZE
    set_memory_sizes(file_input)
    # The main loop of the program (actually iterate through the different lines of the program)
    make_buddy_lists()
    if verbose == 1:
        print_initial_blocks()
    for line in file_input:
        # Split the lines into different tokens
        line = line.split()
        # If the middle token is a +, then allocate
        if line[1] == "+":
            allocate(int(line[0]), int(line[2]))
        # If the middle token is a - then dallocate
        if line[1] == "-":
            deallocate(int(line[0]))
        if verbose == 1:
            print_status_of_request()
            print_buddy_lists()
            print_deferred_requests()

def allocate(process, memory_size):
    global buddy_lists
    global requests
    block_size = next_power_of_2(memory_size)
    free_list_number = get_list_number(block_size)
    # If free list is empty, then theres no memory in that space to allocate
    if buddy_lists[free_list_number] == []:
        # Save the original list number
        next_list_number = free_list_number
        # Increment up through the lists until you find a non empty list
        while buddy_lists[next_list_number] == []:
            # Move to the next list
            next_list_number = next_list_number + 1
            # If there's nothing bigger, then it is deferred
            if next_list_number == num_lists:
                new_request = Request(process, memory_size, 1, block_size, -1)
                requests.append(new_request)
                print_request(new_request)
                return
        # Works it's way back down the buddy_lists to smaller sizes
        while next_list_number != free_list_number:
            # Divides the memory by two
            next_size = buddy_lists[next_list_number][0][0] / 2
            old_memory_address = buddy_lists[next_list_number][0][1]
            # Takes it off the bigger list
            buddy_lists[next_list_number].pop(0)
            # Moves to the smaller list
            next_list_number = next_list_number - 1
            # Adds that memory in as two smaller parts
            buddy_lists[next_list_number].append((next_size, old_memory_address))
            buddy_lists[next_list_number].append((next_size, old_memory_address + next_size))
        # Updates the requests list to show it is allocated
        new_request = Request(process, memory_size, 2, next_size, old_memory_address)
        requests.append(new_request)
        print_request(new_request)
        # Removes the memory that was allocated from the free list
        buddy_lists[next_list_number].pop(0)
    else:
        new_request = Request(process, memory_size, 2, block_size, buddy_lists[free_list_number][0][1])
        requests.append(new_request)
        print_request(new_request)
        buddy_lists[free_list_number].pop(0)

def deallocate(request_id):
    request = None
    for data in requests:
        if data.request_id == request_id and data.state == 2:
            request = data
            break
    if request == None:
        return
    memory_size = request.memory_size
    address = request.address
    flag = True
    while flag:
        flag, address, memory_size = combine_blocks(address, memory_size)
    request.state = 3
    print_request(request)
    reallocate()

def reallocate():
    for request in requests:
        if request.state == 1:
            allocate_deferred(request)

def allocate_deferred(request):
    global buddy_lists
    global requests
    memory_size = request.memory_size
    block_size = next_power_of_2(memory_size)
    free_list_number = get_list_number(block_size)
    # If free list is empty, then theres no memory in that space to allocate
    if buddy_lists[free_list_number] == []:
        # Save the original list number
        next_list_number = free_list_number
        # Increment up through the lists until you find a non empty list
        while buddy_lists[next_list_number] == []:
            # Move to the next list
            next_list_number = next_list_number + 1
            # If there's nothing bigger, then it is deferred
            if next_list_number == num_lists:
                request.state = 1
                request.size = block_size
                request.address = -1
                # print_request(request)
                return
        # Works it's way back down the buddy_lists to smaller sizes
        while next_list_number != free_list_number:
            # Divides the memory by two
            next_size = buddy_lists[next_list_number][0][0] / 2
            old_memory_address = buddy_lists[next_list_number][0][1]
            # Takes it off the bigger list
            buddy_lists[next_list_number].pop(0)
            # Moves to the smaller list
            next_list_number = next_list_number - 1
            # Adds that memory in as two smaller parts
            buddy_lists[next_list_number].append((next_size, old_memory_address))
            buddy_lists[next_list_number].append((next_size, old_memory_address + next_size))
        # Updates the requests list to show it is allocated
        request.state = 2
        request.memory_size = next_size
        request.address = old_memory_address
        print_reallocated(request)
        # Removes the memory that was allocated from the free list
        buddy_lists[next_list_number].pop(0)
    else:
        request.state = 2
        request.memory_size = block_size
        request.address = buddy_lists[free_list_number][0][1]
        print_reallocated(request)
        buddy_lists[free_list_number].pop(0)

def combine_blocks(address, memory_size):
    address_check = address / memory_size
    if address_check % 2 == 0:
        buddy_address = address + memory_size
    else:
        buddy_address = address - memory_size
    list_number = get_list_number(memory_size)
    if list_number == num_lists:
        return False, address, memory_size
    if buddy_lists[list_number] == []:
        buddy_lists[list_number].append((memory_size, address))
        if verbose:
            print_deallocate_verbose(address, memory_size, buddy_address, False)
            print "\n"
        return False, address, memory_size
    else:
        for block in buddy_lists[list_number]:
            if buddy_address == block[1]:
                new_memory_size = memory_size * 2
                if address < buddy_address:
                    new_address = address
                else:
                    new_address = buddy_address
                # Pop off lower
                buddy_lists[list_number].remove(block)
                # buddy_lists[list_number+1].append((new_memory_size, new_address))
                if verbose:
                    print_deallocate_verbose(address, memory_size, buddy_address, True)
                    print "\n"
                return True, new_address, new_memory_size
        buddy_lists[list_number].append((memory_size, address))
        if verbose:
            print_deallocate_verbose(address, memory_size, buddy_address, False)
            print "\n"
        return False, address, memory_size

def make_buddy_lists():
    global MSIZE
    global ASIZE
    global buddy_lists
    global num_lists
    while((ASIZE << num_lists) != MSIZE):
        num_lists = num_lists + 1
        buddy_lists.append([])
    num_lists = num_lists + 1
    buddy_lists.append([])
    buddy_lists[num_lists-1].append((MSIZE,0))
    
def open_input_file():
    global verbose
    if (sys.argv[1] == '-v'):
        verbose = 1
        filename = sys.argv[2]
    else:
        filename = sys.argv[1]
    file = open(filename, "r")
    return file

def set_memory_sizes(file_input):
    global MSIZE
    global ASIZE
    first_line = file_input.readline().split()
    MSIZE = int(first_line[0])
    ASIZE = int(first_line[1])

def next_power_of_2(x):  
    if x < ASIZE:
        return ASIZE
    else:
        if x == 0:
            return 1
        else:
            return 2**(x - 1).bit_length()

def get_list_number(x):
    return int(math.log(x,2) - math.log(ASIZE,2))

def print_initial_blocks():
    if (verbose == 1):
        temp = MSIZE
        print('\nNumber of block sizes = ' + str(num_lists) + ':')
        print('\t'),
        for i in range (0, num_lists):
            print(temp),
            if (i != num_lists - 1):
                print(','),
                temp = temp / 2
            else:
                print('\n')

def print_request(request):
    # If request is deferred
    if request.state == 1:
        print "Request ID " + str(request.request_id) + ": allocate " + str(request.request_size) + " bytes."
        print "\t Request deferred."
    if request.state == 2:
        print "Request ID " + str(request.request_id) + ": allocate " + str(request.request_size) + " bytes."
        print "\t Success: addr = " + str('{:#010x}'.format(request.address)+"")
    if request.state == 3:
        print "Request ID " + str(request.request_id) + ": deallocate."
        print "\tSuccess."

def print_reallocated(request):
    print "\tDeferred request " + str(request.request_id) + " allocated; addr = " + str('{:#010x}'.format(request.address))

def print_status_of_request():
    print "Status of Requests..."
    for request in requests:
        if request.state == 1:
            print "\tID " + str(request.request_id) + " deferred"
        if request.state == 2:
            print "\tID " + str(request.request_id) + " active, addr " + str('{:#010x}'.format(request.address)) +", size " + str(request.memory_size)
        if request.state == 3:
             print "\tID " + str(request.request_id) + " freed, (addr was " + str('{:#010x}'.format(request.address)) +", size was " + str(request.memory_size) + ")"
        
def print_buddy_lists():
    print "\nFree Lists..."
    iterations = 1
    for buddy_list in reversed(buddy_lists):
        print "  Size " + str(MSIZE/iterations) + ":"
        if buddy_list == []:
            print "    (none)"
        else:
            for block in buddy_list:
                print "    addr = " + str('{:#010x}'.format(block[1])) + ", size = " + str(block[0])
        iterations = iterations * 2

def print_deferred_requests():
    flag = True
    print "\nDeferred requests..."
    for request in requests:
        if request.state == 1:
            print "\tID " + str(request.request_id) + ", size " + str(request.memory_size)
            flag = False
    if flag:
        print "\t(none)"
    print "\n"

def print_deallocate_verbose(address, memory_size, buddy_address, buddy_flag):
    print "Deallocating block at " + str('{:#010x}'.format(address)) + " with size = " + str(memory_size)
    print "\tBuddy of " + str(memory_size) + "-byte block at " + str('{:#010x}'.format(address)) + " is at " + str('{:#010x}'.format(buddy_address))
    if buddy_flag:
        print "\tBuddy at " + str('{:#010x}'.format(buddy_address)) + " is free."
    else:
        print "\tBuddy at " + str('{:#010x}'.format(buddy_address)) + " is not free."

if __name__ == '__main__':
    main()
