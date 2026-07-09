#!/usr/bin/env python

import argparse
import sys
import os
import re

#Functions
def arg_parser():
      """ Defines named arguments, provides the --help/-h flag, and allows the option to use required arguments """
      parser = argparse.ArgumentParser(description = 'arguments')
      parser.add_argument('fasta_file', help = 'REQUIRED: FASTA file containing contig sequences', nargs = None, type = str)
      parser.add_argument('start_position', help = 'REQUIRED: Which nucleotide the sequence start at', nargs = None, type = int)
      parser.add_argument('--contig_name', help = 'OPTIONAL: If FASTA file contains multiple sequences, ID of the contig to be rotated as it appears in the fasta header', nargs = "?", type = str, required = False)
      parser.add_argument('-r', '--reverse_complement', action='store_true', help='OPTIONAL: Generate the reverse complement of the rotated sequence (default: False)')
      parser.add_argument('-o', '--out_file', help = 'OPTIONAL: Send output to specified file (will overwrite existing files)', nargs = '?', type = str, required = False)
      parser.add_argument('-n', '--new_name', help = 'OPTIONAL: Rename the rotated contig using specified string (default: "<contig_name>_rotated")', nargs = '?', type = str, required = False)
      return parser.parse_args()


def read_fasta(fasta_file):
    """ Parses the fasta file, creating a list in which each contig (consisting of header + seqeunce) is an item """
    # Read the fasta file
    with open(fasta_file, 'r') as f:
        assemb = f.read()
        
    # Split the assembly into a list, putting each contig into its own string
    contig_list = re.split(',', re.sub('\n>', ',>', assemb))
    return(contig_list)


def return_contig(contig_list, contig_name, fasta_file):
    """ searches the list of contigs for items with a header that matches the contig name, then returns it """
    
    if contig_name is None:
        sys.tracebacklimit = 0
        raise Exception('Contig name must be specified if input FASTA contains multiple sequences')
    
    head = None
    matches = []
    # Find the entry that has the contig_name in the header and extract that sequence
    for i in contig_list:
        #if (bool(re.match(f'>[^0-9]*{contig_name}[^a-zA-Z-0-9].*\n', i))):
        if f'>{contig_name}' in i.split():
            head = re.search(f'>.*{contig_name}(?=.*\n)', i).group()
            seq = re.sub('\n', '', re.sub(f'>.*{contig_name}.*\n', '', i))
            matches.append(re.search(f'>.*{contig_name}.*(?=\n)', i).group())

    if len(matches) > 1:
        sys.tracebacklimit = 0
        raise Exception('More than one header matches the provided contig name:\n' + 
                        '\n'.join(['\t' + item for item in matches]))
    elif len(matches) < 1:
        sys.tracebacklimit = 0
        raise Exception(f'{contig_name} not found in {os.path.basename(fasta_file)}')
    else:
        return head, seq    
    return


def rotate_sequence(seq, start_pos):
    # Determine length of sequence
    length = len(seq)
    
	# Ensure the specified start point is not out of range (greater than the contig length)
    if start_pos > length:
        raise Exception(f'Specified start position out of range\n\tstart position:\t{start_pos}\n\tcontig length:\t{length}')
    
    # Mimic the circular nature of the contig by duplicating it, connecting the start to the end
    dup = seq + seq
    
	# Convert start position to zero-indexed value 
    adj_start = start_pos - 1
    
	# Starting at specified (zero-indexed) start position, print the nucleotides in the sequence until the contig length is reached
    seq_out = dup[adj_start:(adj_start + length)]
    
    return(seq_out)


def reverse_complement(seq):
    # Ensure there are no invalid characters (characters other than AaTtGgCcNn) in the sequence
    valid_chars = ('A', 'a', 'T', 't', 'G', 'g', 'C', 'c', 'N', 'n')
    violations = {char for char in seq if char not in valid_chars}
    if len(violations) > 0:
        raise Exception('Sequence contains invalid characters: ' + violations)
    
    # Generate complement sequence
    trans_table = seq.maketrans('AaTtGgCc', 'TtAaCcGg')
    complement_seq = seq.translate(trans_table)
    
    # Now reverse the complement sequence
    rev_comp_seq = complement_seq[::-1]
    
    return(rev_comp_seq)
    

def insert_newlines(string, every):
    """ Splits the contig sequence into 60 characters per line (for printing purposes) """
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    return '\n'.join(lines)



#Main
if __name__ == "__main__":
    # Parse the arguments
    args = arg_parser() 
    
    # Load the fasta file and save each contig as an entry within the list "all_contigs"
    all_contigs = read_fasta(args.fasta_file)
    
    # Separate the contig header and the sequence (if there is more than one contig in the fasta file, find the contig specified by contig_name argument)
    if len(all_contigs) > 1:
        header, sequence = return_contig(all_contigs, args.contig_name, args.fasta_file)
    elif len(all_contigs) == 1:
        header = all_contigs[0].splitlines()[0].split()[0]
        sequence = "".join(all_contigs[0].splitlines()[1:])
    
    # Rotate the sequence
    sequence_out = rotate_sequence(sequence, args.start_position)
    
    # If the --reverse_complement flag was used, generate the reverse complement sequence of the rotated contig
    if args.reverse_complement:
        sequence_out = reverse_complement(sequence_out)
        
    # Change the header line
    if args.new_name is None:
        header = header + '_rotated'
    else:
        header = args.new_name
        
    # Generate the output
    if args.out_file is None:
        print(header)
        print(insert_newlines(sequence_out, 60))
    else:
        with open(args.out_file, 'w') as f:
            f.write(header + '\n')
            f.write(insert_newlines(sequence_out, 60) + '\n')
