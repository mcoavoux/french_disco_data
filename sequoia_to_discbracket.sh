

if ! [ -e sequoia-7.0.tgz ]
then
    wget http://talc2.loria.fr/deep-sequoia/sequoia-7.0.tgz
    tar zxvf sequoia-7.0.tgz
fi

folder=sequoia-7.0
newfolder=disco_sequoia

mkdir ${newfolder}

cut -f 2 ${folder}/sequoia.predeep.const > ${newfolder}/sequoia.brackets
discodop treetransforms ${newfolder}/sequoia.brackets --inputfmt=bracket --outputfmt=discbracket ${newfolder}/sequoia.discbrackets

python3 deep_to_discbracket.py ${newfolder}/sequoia.discbrackets > ${newfolder}/transformation.log

discodop treedraw --fmt=discbracket --output=html < ${newfolder}/modified_trees > ${newfolder}/modified_trees.html

