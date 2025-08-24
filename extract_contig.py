#!/usr/bin/env python

import argparse
import sys
import os
import re

#Functions
def arg_parser():
      """ Defines named arguments, provides the --help/-h flag, and allows the option to use required arguments """
      parser = argparse.ArgumentParser(description = 'arguments')
      parser.add_argument('fasta_file', help = 'REQUIRED: Fasta file containing contig sequences', nargs = '?', type = str)
      parser.add_argument('contig_name', help = 'REQUIRED: Contig ID as it appears in the fasta header', nargs = "?", type = str)
      parser.add_argument('-r', '--bp-range', help = 'OPTIONAL: Range of bp in contig sequence to return', nargs = '?', type = str, required = False)
      return parser.parse_args()


def find_contig(fasta_file, contig_name):
    """ Parses the fasta file and finds the specified contig """
    header = None

    #Read the fasta file
    with open(fasta_file, 'r') as f:
        assemb = f.read()
        
    #Split the assembly into a list, putting each contig into its own string
    contig_list = re.split(',', re.sub('\n>', ',>', assemb))
    
    #Find the entry that has the contig name in the header and extract just the sequence
    for i in contig_list:
        if (bool(re.match(f'>[^0-9]*{contig_name}[^a-zA-Z-0-9].*\n', i))):
            header = re.search(f'>.*{contig_name}(?=.*\n)', i).group()
            sequence = re.sub('\n', '', re.sub(f'>.*{contig_name}.*\n', '', i))
            break
    if not header:
        sys.tracebacklimit=0
        raise Exception(f'{contig_name} not found in {os.path.basename(fasta_file)}')
    
    #If the contig name consists of only numbers, add "contig_" prefix to make output easier to understand
    if re.sub('>', '', header).isdigit():
        header = '>contig_' + (re.sub('>', '', header))
    return header,sequence


def insert_newlines(string, every):
    """ Splits the contig sequence into 60 characters per line (for printing purposes) """
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    return '\n'.join(lines)




#Main
if __name__ == "__main__":
    args = arg_parser()
    header, sequence = find_contig(args.fasta_file, args.contig_name)
    
    #Depending on if a range of positions was provided from the command line...
    if args.bp_range:
        first_pos = args.bp_range.split(':')[0] or 1
        last_pos = args.bp_range.split(':')[1] or len(sequence)
        if int(last_pos) > len(sequence):
            last_pos = len(sequence)

        print(f'{header}:{first_pos}-{last_pos}')
        print(insert_newlines(sequence[(int(first_pos)-1):int(last_pos)], 60))
    else:
        print(header)
        print(insert_newlines(sequence, 60))

