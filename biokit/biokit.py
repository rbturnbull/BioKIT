#!/usr/bin/env python

import logging
import sys
import textwrap
from .version import __version__

from argparse import (
    ArgumentParser,
    RawTextHelpFormatter,
    SUPPRESS,
    RawDescriptionHelpFormatter,
)

from .services.text import (
    Faidx,
    FileFormatConverter,
    GCContent,
    L50,
    L90,
    N50,
    N90,
    RenameFastaEntries,
    SequenceComplement,
    SequenceLength,
)

from .services.tree import (
    TipLabels,
)

from .helpers.boolean_argument_parsing import str2bool


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

help_header = f"""
                 ____  _       _  _______ _______ 
                |  _ \(_)     | |/ /_   _|__   __|
                | |_) |_  ___ | ' /  | |    | |   
                |  _ <| |/ _ \|  <   | |    | |   
                | |_) | | (_) | . \ _| |_   | |   
                |____/|_|\___/|_|\_\_____|  |_|   
                            
                Version: {__version__}
                Citation: Steenwyk et al. 2021, CITATION INFORMATION

"""

class Biokit(object):
    help_header = f"""
                 ____  _       _  _______ _______ 
                |  _ \(_)     | |/ /_   _|__   __|
                | |_) |_  ___ | ' /  | |    | |   
                |  _ <| |/ _ \|  <   | |    | |   
                | |_) | | (_) | . \ _| |_   | |   
                |____/|_|\___/|_|\_\_____|  |_|   
                            
                Version: {__version__}
                Citation: Steenwyk et al. 2021, CITATION INFORMATION

    """
    
    def __init__(self):
        parser = ArgumentParser(
            add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {self.help_header}

                BioKIT is a broadly applicable command-line toolkit for bioinformatics research.

                Usage: biokit <command> [optional command arguments]

                Command specific help messages can be viewed by adding a 
                -h/--help argument after the command. For example, to see the
                to see the help message for the command 'get_entry', execute
                "biokit get_entry -h" or "biokit get_entry --help".

                Lastly, each function comes with aliases to save the user some
                key strokes. For example, to get the help message for the 'get_entry'
                function, you can type "biokit ge -h". All aliases are specified
                in parentheses after the long form of the function name. 

                Text sequence file-based commands
                =================================
                faidx (alias: get_entry; ge)
                    - extract query fasta entry from multi-fasta file
                file_format_converter (alias: format_converter; ffc)
                    - convert a multiple sequence file from one format
                      to another
                gc_content (alias: gc)
                    - calculate the GC content of a FASTA file
                rename_fasta_entries
                sequence_length                           

                Tree-based commands
                ===================
                tip_labels (alias: tree_labels; labels; tl)
                    - print leaf names in a phylogeny
                
                """
            ),
        )
        parser.add_argument("command", help=SUPPRESS)
        args = parser.parse_args(sys.argv[1:2])

        # if command is part of the possible commands (i.e., the long form
        # commands, run). Otherwise, assume it is an alias and look to the
        # run_alias function
        try:
            if hasattr(self, args.command):
                getattr(self, args.command)(sys.argv[2:])
            else:
                self.run_alias(args.command, sys.argv[2:])
        except NameError:
            sys.exit()

    ## Aliases
    def run_alias(self, command, argv):
        # version
        if command in ['v']:
            return self.version()
        # Text aliases
        elif command in ['con_len']:
            return self.consensus_sequence(argv)
        elif command in ['get_entry', 'ge']:
            return self.faidx(argv)
        elif command in ['format_converter', 'ffc']:
            return self.file_format_converter(argv)
        # Tree aliases
        elif command in ['labels', 'tree_labels', 'tl']:
            return self.tip_labels(argv)
        else:
            print("Invalid command option. See help for a complete list of commands and aliases.")
            parser.print_help()
            sys.exit(1)

    ## print version
    def version(self):
        print(textwrap.dedent(
            f"""\
            {self.help_header}
            """
        ))

    ## Alignment functions
    @staticmethod
    def consensus_sequence(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}

                Generates a consequence from a multiple sequence alignment
                file in FASTA format.
                
                Aliases:
                  consensus_sequence, con_len
                Command line interfaces: 
                  bk_consensus_sequence, bk_con_len

                Usage:
                biokit consensus_sequence <fasta> -t/--threshold <threshold>
                -ac/--ambiguous_character <ambiguous character>

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file

                -t/--threshold              threshold for how common
                                            a residue must be to be
                                            represented
                
                -ac/--ambiguous_character   the ambiguity character to
                                            use. Default is 'N'
                """
            ),
        )

        parser.add_argument("fasta", type=str, help=SUPPRESS)
        parser.add_argument("-t","--threshold", type=str, help=SUPPRESS)
        parser.add_argument("-ac","--ambiguous_character", type=str, help=SUPPRESS)
        args = parser.parse_args(argv)
        ConsensusSequence(args).run()

    @staticmethod
    def faidx(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}

                Extracts sequence entry from fasta file.

                This function works similarly to the faidx function 
                in samtools, but does not requiring an indexing function.

                Aliases:
                  faidx, get_entry, ge
                Command line interfaces: 
                  bk_faidx, bk_get_entry, bk_ge

                Usage:
                biokit faidx <fasta> -e/--entry <fasta entry>

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be a
                                            query fasta file

                -e/--entry                  entry name to be extracted
                                            from the inputted fasta file
                """
            ),
        )
        parser.add_argument("fasta", type=str, help=SUPPRESS)
        parser.add_argument("-e","--entry", type=str, help=SUPPRESS)
        args = parser.parse_args(argv)
        Faidx(args).run()

    @staticmethod
    def file_format_converter(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}

                Converts a multiple sequence file from one format to another.

                Acceptable file formats include FASTA, Clustal, MAF, Mauve,
                Phylip, Phylip-sequential, Phylip-relaxed, and Stockholm.
                Input and output file formats are specified with the
                --input_file_format and --output_file_format arguments; input
                and output files are specified with the --input_file and
                --output_file arguments.

                Aliases:
                  file_format_converter, format_converter, ffc
                Command line interfaces: 
                  bk_file_format_converter, bk_format_converter, bk_ffc
                  

                Usage:
                biokit file_format_converter -i/--input_file <input_file>
                -iff/--input_file_format <input_file_format> 
                -o/--output_file <output_file>
                -off/--output_file_format <output_file_format>

                Options
                =====================================================
                -i/--input_file             input file name 

                -iff/--input_file_format    input file format

                -o/--output_file            output file name

                -off/--output_file_format   output file format

                Input and output file formats are specified using one of
                the following strings: fasta, clustal, maf, mauve, phylip,
                phylip_sequential, phylip_relaxed, & stockholm.
                """
            ),
        )
        parser.add_argument("-i", "--input_file", type=str, help=SUPPRESS)
        parser.add_argument("-off", "--output_file_format", type=str, help=SUPPRESS)
        parser.add_argument("-iff", "--input_file_format", type=str, help=SUPPRESS)
        parser.add_argument("-o", "--output_file", type=str, help=SUPPRESS)

        args = parser.parse_args(argv)
        FileFormatConverter(args).run()

    @staticmethod
    def gc_content(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}
                
                Calculate GC content of a fasta file.
                
                Aliases:
                  gc_content, gc
                Command line interfaces: 
                  bk_gc_content, bk_gc

                Usage:
                biokit gc_content <fasta> [-v/--verbose]

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file 
            
                -v, --verbose               optional argument to print
                                            the GC content of each fasta
                                            entry
                """
            ),
        )
        parser.add_argument("fasta", type=str, help=SUPPRESS)
        parser.add_argument("-v", "--verbose", action="store_true", required=False, help=SUPPRESS)
        args = parser.parse_args(argv)
        GCContent(args).run()

    @staticmethod
    def l50(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}
                
                Calculates L50 for a genome assembly.
                
                Aliases:
                  l50
                Command line interfaces: 
                  bk_l50

                Usage:
                biokit l50 <fasta>

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file 
                """
            ),
        )
        parser.add_argument("fasta", type=str, help=SUPPRESS)
        args = parser.parse_args(argv)
        L50(args).run()

    @staticmethod
    def l90(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}
                
                Calculates L90 for a genome assembly.
                
                Aliases:
                  l90
                Command line interfaces: 
                  bk_l90

                Usage:
                biokit l90 <fasta>

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file 
                """
            ),
        )
        parser.add_argument("fasta", type=str, help=SUPPRESS)
        args = parser.parse_args(argv)
        L90(args).run()

    @staticmethod
    def n50(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}
                
                Calculates N50 for a genome assembly.
                
                Aliases:
                  n50
                Command line interfaces: 
                  bk_n50

                Usage:
                biokit n50 <fasta>

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file 
                """
            ),
        )
        parser.add_argument("fasta", type=str, help=SUPPRESS)
        args = parser.parse_args(argv)
        N50(args).run()

    @staticmethod
    def n90(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}
                
                Calculates N90 for a genome assembly.
                
                Aliases:
                  n90
                Command line interfaces: 
                  bk_n90

                Usage:
                biokit n90 <fasta>

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file 
                """
            ),
        )
        parser.add_argument("fasta", type=str, help=SUPPRESS)
        args = parser.parse_args(argv)
        N90(args).run()

    @staticmethod
    def rename_fasta_entries(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}
                Renames fasta entries.

                Renaming fasta entries will follow the scheme of a tab-delimited
                file wherein the first column is the current fasta entry name and
                the second column is the new fasta entry name in the resulting 
                output alignment. 

                Aliases:
                  rename_fasta_entries, rename_fasta
                Command line interfaces: 
                  bk_rename_fasta_entries, bk_rename_fasta
                
                Usage:
                biokit rename_fasta_entries <fasta> -i/--idmap <idmap>
                    [-o/--output <output_file>]
                
                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file
                -i/--idmap                  identifier map of current FASTA
                                            names (col1) and desired FASTA
                                            names (col2)
                -o/--output                 optional argument to write
                                            the renamed fasta file to.
                                            Default output has the same 
                                            name as the input file with
                                            the suffix ".renamed.fa" added
                                            to it.
                """
            ),
        )
        parser.add_argument("fasta", type=str, help=SUPPRESS)
        parser.add_argument("-i","--idmap", type=str, help=SUPPRESS)
        parser.add_argument("-o", "--output", type=str, required=False, help=SUPPRESS)
        args = parser.parse_args(argv)
        RenameFastaEntries(args).run()

    @staticmethod
    def sequence_length(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}

                Calculate sequence length of each FASTA entry.
                
                Aliases:
                  sequence_length, seq_len
                Command line interfaces: 
                  bk_sequence_length, bk_seq_len

                Usage:
                biokit sequence_length <fasta>

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file 
                """
            ),
        )

        parser.add_argument("fasta", type=str, help=SUPPRESS)
        args = parser.parse_args(argv)
        SequenceLength(args).run()

    @staticmethod
    def sequence_complement(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}

                Generates the sequence complement for all entries
                in a multi-FASTA file. To generate a reverse sequence
                complement, add the -r/--reverse argument.
                
                Aliases:
                  sequence_complement, seq_comp
                Command line interfaces: 
                  bk_sequence_complement, bk_seq_comp

                Usage:
                biokit sequence_complement <fasta> [-r/--reverse]

                Options
                =====================================================
                <fasta>                     first argument after 
                                            function name should be
                                            a fasta file

                -r/--reverse                if used, the reverse complement
                                            sequence will be generated
                """
            ),
        )

        parser.add_argument("fasta", type=str, help=SUPPRESS)
        parser.add_argument("-r", "--reverse", action="store_true", required=False, help=SUPPRESS)
        args = parser.parse_args(argv)
        SequenceComplement(args).run()

    ## Tree functions
    @staticmethod
    def tip_labels(argv):
        parser = ArgumentParser(add_help=True,
            usage=SUPPRESS,
            formatter_class=RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""\
                {help_header}

                Prints the tip labels (or names) a phylogeny.

                Aliases:
                  tip_labels, tree_labels; labels; tl
                Command line interfaces: 
                  bk_tip_labels, bk_tree_labels; bk_labels; bk_tl

                Usage:
                biokit tip_labels <tree>

                Options
                =====================================================
                <tree>                      first argument after 
                                            function name should be
                                            a tree file
                """
            ),
        )
        parser.add_argument("tree", type=str, help=SUPPRESS)
        args = parser.parse_args(argv)
        TipLabels(args).run()

def main(argv=None):
    BioKIT()

# Alignment-based functions
def faidx(argv=None):
    Biokit.faidx(sys.argv[1:])


# Tree-based functions
def tip_labels(argv=None):
    Biokit.tip_labels(sys.argv[1:])

