#!/bin/bash

###FUNCTIONS###
# Function to generate help message
function help_message () {
    echo -e "Usage: rotate_contig.sh [-h] <input_fasta> <contig_name> <start_position> [-r -o <out_fasta> -e <end_position> -r <-n <new_contig_name>]"
    echo -e "\t-h:\t\tshow help message and exit"
    echo -e "\t<input_fasta>:\tfasta file containing the contig to be rotated"
    echo -e "\t<contig_name>:\tname of the contig to be rotated"
    echo -e "\t<start_position>:\twhich nucleotide should the sequence start at"
	echo -e "\t-r:\t\tgenerate the reverse complement of the rotated sequence"
    echo -e "\t-o <out_fasta>:\tsave the output to the specified file name (prints to standard out by default)"
    echo -e "\t-e <end_position>:\twhich nucleotide should the sequence end at (defaults to the nucelotide immediately preceding specified start)"
    echo -e "\t-n <new_contig_name>:\trename the output contig as specified string (default = '<contig_name>_rotated')"
}

# Function to parse arguments
function parse_args () {
	# Parse the optional arguments, if present
    for i in ${!args[@]}; do
        if [[ ${args[i]} = -h || ${args[i]} = --help ]]; then
            help_message
            exit 0
        elif [[ ${args[i]} = -r ]]; then
            reverse_complement=true
            unset 'args[i]'
        elif [[ ${args[i]} = -o ]]; then
            out_fasta=${args[i+1]}
            unset 'args[i]' 'args[i+1]'
		elif [[ ${args[i]} = -e ]]; then
            end_position=${args[i+1]}
            unset 'args[i]' 'args[i+1]'
		elif [[ ${args[i]} = -n ]]; then
            out_contig_name=${args[i+1]}
            unset 'args[i]' 'args[i+1]'
        elif [[ ${args[i]} = -* ]]; then
            echo -e "ERROR: unknown flag:\t${args[i]}"
            exit 1
        fi
    done

	# Parse the required arguments
    if (( (${#args[@]}) > 3 )); then
        remainargs=( ${args[@]} )
        echo -e "ERROR: too many arguments provided"
        printf '  > extra arg: %s\n' ${remainargs[@]:3}
		exit 1	
    elif (( (${#args[@]}) < 3 )); then
        echo -e "ERROR: missing at least one required argument\n"
        help_message
        exit 1
    else
        in_fasta=${args[0]}
		contig_name=${args[1]}
		# Ensure start position is greater than one (since default end position is <start> - 1)
		if (( (${args[2]}) > 1 )); then
			start_position=${args[2]}
		else
			echo -e "ERROR: start position must be greater than 1"
			exit 1
		fi
    fi

    # If any optional arguments are absent, set the variables to their default values
	if [[ ! $out_fasta ]]; then out_fasta=/dev/stdout; fi  
	if [[ ! $end_position ]]; then end_position=$(($start_position - 1)); fi  
	if [[ ! $out_contig_name ]]; then out_contig_name=${contig_name}_rotated; fi  
}

# Function to rotate the contig sequence to start at specified position
rotate_contig(){
	echo ">$out_contig_name"
	extract_contig.py $in_fasta $contig_name -r $start_position: | grep -v "^>${contig_name}"
	extract_contig.py $in_fasta $contig_name -r :$end_position | grep -v "^>${contig_name}"
}

# Function to ensure that the rotated sequence perfectly matches the original one (when the original sequence is repeated)
check_align(){
	org_contig=$1
	rot_contig=$2

	# Remove the header line and the line endings from each fasta entry to turn the sequence into a string
	subject=$(grep -v "^>" $org_contig | sed -z 's/\n//g')
	query=$(grep -v "^>" $rot_contig | sed -z 's/\n//g')

	# Count the number of times the query sequence appears in the duplicated original sequence
	matches=$(echo "${subject}${subject}" | grep -o $query | wc -l)

	# Produce a boolean output to specify if the rotated sequence aligned
	if (( $matches == 1 )); then
		aligns=true
	elif (( $matches > 1 )); then
		echo "WARNING: rotated contig matches multiple times along duplicated original sequence"
		aligns=true
	elif (( $matches == 0 )); then
		aligns=false
	else
		echo "ERROR: function 'check_align' could not be completed"
		exit 1
	fi
}

# Function to generate the reverse complement of a sequence in fasta format
reverse_complement(){
	local input=$1
	local header=$(grep "^>" $input)
	local seq=$(grep -v "^>" $input | sed -z 's/\n//g')
	
	# Reverse the sequence
	r_seq=$(echo $seq | rev)
	
	# Complement the sequence
	rc_seq=$(echo $r_seq | tr 'AaTtGgCc' 'TtAaCcGg')
	
	echo $header
	echo $rc_seq
}

# Function to print fasta with 60 characters per line
print_nicely(){
	local input=$1
	local header=$(grep "^>" $input)
	local seq=$(grep -v "^>" $input | sed -z 's/\n//g')
	
	echo $header
	echo $seq | fold -w 60 
}

###MAIN###
# Interpret the arugments
declare -a args=( "$@" )
parse_args

# Rotate the contig
rot_temp=$(mktemp)
rotate_contig > $rot_temp

# Double check the rotated contig perfectly aligns with the original
orig_temp=$(mktemp)
extract_contig.py $in_fasta $contig_name > $orig_temp
check_align $orig_temp $rot_temp
if [[ $aligns = false ]]; then
	echo "ERROR: rotated contig does not align with original"
	exit 1
fi 

# If the reverse complement flag (-r) is used, find the reverse complement of the rotated sequence before generating output
if [[ $reverse_complement = true ]]; then
	int_temp=$(mktemp)
	cat $rot_temp > $int_temp
	reverse_complement $int_temp > $rot_temp
fi

# Output the rotated sequence in fasta format
print_nicely $rot_temp > $out_fasta

# Clean up temp files
rm $rot_temp $orig_temp $int_temp