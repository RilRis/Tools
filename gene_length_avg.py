#!/usr/bin/env python

import argparse

#FUNCTIONS
def arg_parser():
      """ Defines named arguments, provides the --help/-h flag, and allows the option to use required arguments """
      parser = argparse.ArgumentParser(description = 'arguments')
      parser.add_argument('gff_file', help = 'REQUIRED: GFF file containing genomic feature coordinates', nargs = '?', type = str)
      parser.add_argument('-t','--table-out', help = 'OPTIONAL: Output a table containing the length of each gene (instead of printing the average gene length)', action='store_true')

      return parser.parse_args()
    
def filter_for_genes(gff):
    matching_lines = []
    with open(gff, 'r') as file:
        for line in file:
            #Remove leading and trailing whitespace
            stripped_line = line.strip()
            
            #If line contains text and doesnt start with #...
            if stripped_line and not stripped_line.startswith('#'):
                #... and the value in the third column is "gene" (case insensitive) ...
                if stripped_line.split('\t')[2].casefold() == 'gene':
                    #Add the line to the "matching_lines" list 
                    matching_lines.append(stripped_line)
    return(matching_lines)

def calc_gene_lengths(list_of_lines):
    gene_dict = {}
    for entry in list_of_lines:
        #Split the row's contents to get the values from specific columns
        field_list = entry.split('\t')
        seqname = field_list[0]
        start = int(field_list[3])
        end = int(field_list[4])

        #Calculate the length of the gene using the beginning and end coordinates
        gene_len = (abs(end - start))

        #Try to find the gene ID in the last column (if absent, use the chromesome and coordinates to act as an ID)
        if field_list[8].startswith('ID='):
            notes = field_list[8]
            gene_id = notes.split(';', 2)[0].split('=')[1]
        else:
            gene_id = f'{seqname}:{start}-{end}'
        gene_dict[gene_id] = gene_len
    return(gene_dict)

def dict_as_tsv(dictionary):
    for key,val in dictionary.items():
        print(f'{key}\t{val}')
        
#MAIN
if __name__ == "__main__":
    args = arg_parser()
    
    filtered_gff = filter_for_genes(args.gff_file) 
    genelength_dict = calc_gene_lengths(filtered_gff)
    if args.table_out:
        dict_as_tsv(genelength_dict)
    else:
        avg_length = sum(genelength_dict.values()) / len(genelength_dict.keys())
        print(avg_length)
