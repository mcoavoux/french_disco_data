

Generate discontinuous versions of the 3 following French treebanks:

- [French Treebank (FTB, Abeillé et al. 2003)](http://ftb.linguist.univ-paris-diderot.fr/)
- [French Question Bank (FQB, Seddah and Candito, 2016 LREC)](http://alpage.inria.fr/Treebanks/FQB/)
- [Sequoia (Candito and Seddah, 2012 TALN)](http://alpage.inria.fr/Treebanks/FQB/)

Linguistic phenomena represented with discontinuous constituents
are those described in Candito and Seddah (2012, LREC), and consist mainly
of long distance extractions.


The scripts will be updated to handle additional phenomena, such as extraposed relative clauses.


### Dependencies

To run these scripts, you need:

- [discodop](https://github.com/andreasvc/disco-dop/) (Van Cranenburgh et al. 2016)
- `python3`
- `FRENCH_SPMRL.tar.gz`: the French data from the SPMRL dataset (Seddah et al. 2013)
- `surf.ftb.np_conll`: the version of the French Treebank annotated with functional paths (Candito et al. 2012)

### Formats used

- `.ctbk` files are pseudo-xml files with head annotations and morphological attributes (input format for [mind the gap](github.com/mcoavoux/mtg))
- `.conll` 
- `.discbracket`

### Run

    git clone https://github.com/mcoavoux/french_disco_data
    cd french_disco_data

    # Generate a discontinuous version of the Sequoia (automatically downloads the data)
    bash sequoia_to_discbracket.sh
    
    # Generate a discontinuous version of the FQB (automatically downloads the data)
    bash fqb_to_discbracket.sh

    # Generate a discontinuous version of the FTB
    #   needs surf.ftb.np_conll FRENCH_SPMRL.tar.gz in root directory
    bash ftb_to_discbracket.sh

    # This line generates the parsing data used in Coavoux and Crabbé (TALN 2017)
    bash generate_ctbk.sh

