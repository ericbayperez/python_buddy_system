import sys

# Total Memory available for allocation
MSIZE = -1
# Smallest block that can be used to allocate a request
ASIZE = -1

def main():
    # Get the file from the command line argument
    file_input = open_input_file()
    # Set the MSIZE and ASIZE
    set_memory_sizes(file_input)
    # The main loop of the program (actually iterate through the different lines of the program)
    for line in file_input:
        # Split the lines into different tokens
        line = line.split()
        # If the middle token is a +, then allocate
        if line[1] == "+":
            allocate()
        # If the middle token is a -, then deallocate
        else:
            deallocate()

def open_input_file():
    filename = sys.argv[1]
    file = open(filename, "r")
    return file

def set_memory_sizes(file_input):
    global MSIZE
    global ASIZE
    first_line = file_input.readline().split()
    MSIZE = first_line[0]
    ASIZE = first_line[1]

if __name__ == '__main__':
    main()
