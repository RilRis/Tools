#!/usr/bin/env python

import argparse
import sys
import os
import re

#Functions
def arg_parser():
      """ Defines named arguments, provides the --help/-h flag, and allows the option to use required arguments """
      parser = argparse.ArgumentParser(description = 'arguments')
      parser.add_argument('fasta_file', help = 'REQUIRED: Fasta file containing sequences', nargs = '?', type = str)
      parser.add_argument('seq_id', help = 'REQUIRED: Sequence ID as it appears in the fasta header line', nargs = "?", type = str)
      parser.add_argument('-rg', '--range', help = 'OPTIONAL: Range of bp/aa in sequence to return (cannot be used with "--remove" flag)', nargs = '?', type = str, required = False)
      parser.add_argument('-rm', '--remove', action='store_true', help='OPTIONAL: Return all sequences except for specified sequence ID  (default: False)')
      return parser.parse_args()

def parse_fasta(fasta_file):
    """ Parses the fasta file, creating a dictionary in which each sequence is an entry composed of a key (sequence ID) and value (sequence) """
    # Read the fasta file
    with open(fasta_file, 'r') as f:
        fasta = f.read()
        
    # Split the multi fasta into a list, putting each entry into its own string
    seq_list = fasta.split('\n>')

    # For each entry, split the string into the key (seq ID) and value (sequence) and store within a dictionary
    seq_dict = {}

    for entry in seq_list:
        if entry:
            lines = entry.splitlines()
            header = re.sub(r'^>', '', lines[0])
            sequence = ''.join(lines[1:])
            key = header.split(' ')[0]
            val = [header, sequence]

            if key in seq_dict:
                raise Exception(f'FASTA file contains non-unique sequence ID (\"{key}\")')
            
            seq_dict[key] = val

    return(seq_dict)


def insert_newlines(string, every = 60):
    """ Splits long strings into 60 characters per line (for printing purposes) """
    # Remove any existing line breaks
    string = re.sub('\n', '', string)
    
    # Now insert a line break after every x number of characters
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    return '\n'.join(lines)


def return_seq(seqence_dict, seq_id, fasta_file, seq_range = ""):
    """ searches the sequence dictionary for an entry where the key matches the sequence ID, then returns the header and sequence """
    # Find the entry with the matching seqid and extract that sequence
    if seq_id in seqence_dict:
        entry = seqence_dict[seq_id]
        header = f'>{entry[0]}'
        # Make sure sequence doesn't contain newlines (it shouldn't, though)
        sequence = re.sub('\n', '', entry[1])
    else:
        raise Exception(f'{seq_id} not found in {os.path.basename(fasta_file)}')
    
    # If a the bp/aa range argument is provided..     
    if seq_range:
        
        # Figure out first or last position if part of range left empty
        first_pos = seq_range.split(':')[0] or 1
        last_pos = seq_range.split(':')[1] or len(sequence)
        if int(last_pos) > len(sequence):
            last_pos = len(sequence)
        
        # Print header (reflecting the new range) and formatted sequence
        comment = header.split(' ', 1)[1]
        print(f'>{seq_id}:{first_pos}-{last_pos} {comment}')
        print(insert_newlines(sequence[(int(first_pos)-1):int(last_pos)], 60))
    
    # Otherwise, print the header and full (formatted) sequence
    else:
        print(header)
        print(insert_newlines(sequence, 60))
    
    return


def remove_seq(seqence_dict, seq_id, fasta_file):
    """ searches the sequence dictionary for an entry where the key matches the sequence ID, then returns the header and sequence for each entry EXCEPT the matching one """
    # Make sure the specified sequence ID is actually present in file
    if seq_id not in seqence_dict:
        raise Exception(f'{seq_id} not found in {os.path.basename(fasta_file)}')
    
    # Print the full header and sequence for each entry except the one specified
    for key,val in seqence_dict.items():
        if key != seq_id:
            header = f'>{val[0]}'
            sequence = val[1]

            print(header)
            print(insert_newlines(sequence, 60))

    return


#Main
if __name__ == "__main__":
    sys.tracebacklimit = 0
    
    # Parse the arguments
    args = arg_parser() 
    
    # Ensure the -rg and -rm flags are not used together
    if args.range and args.remove: 
        raise Exception('cannot use "--range" argument with "--remove" flag')
        
    # If the sequence name is provided with the ">", remove it before continuing
    if args.seq_id.startswith('>'):
        args.seq_id = args.seq_id[1:]
    
    # Load the fasta file and save each sequence/ID/header as an entry within the dictionary "all_seqs"
    all_seqs = parse_fasta(args.fasta_file)
     
    # If -rm/--remove flag is present, print all sequences except for the one specified...
    if args.remove:
        remove_seq(all_seqs, args.seq_id, args.fasta_file)
    # ...otherwise, print just the specified sequence (or a portion of the sequence if -rg/--range is specified)
    else:
        return_seq(all_seqs, args.seq_id, args.fasta_file, args.range)
    

