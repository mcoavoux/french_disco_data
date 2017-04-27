
# download corpus
if ! [ -e FQBv1.0.tar.gz ]
then
    wget http://alpage.inria.fr/Treebanks/FQB/FQBv1.0.tar.gz
    tar zxvf FQBv1.0.tar.gz
fi


folder=FQBv1.0
newfolder=disco_fqb
mkdir ${newfolder}


## to discbracket
discodop treetransforms ${folder}/FQB.v1.fct_deep.mrg.ptb --inputfmt=bracket --outputfmt=discbracket ${newfolder}/fqb1.discbrackets

## move extracted constituents
python3 deep_to_discbracket.py ${newfolder}/fqb1.discbrackets > ${newfolder}/transformation.log

## print modified trees for manual inspection
discodop treedraw --fmt=discbracket --output=html < ${newfolder}/modified_trees > ${newfolder}/modified_trees.html

