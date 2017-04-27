
folder=disco_ftb


tar zxvf FRENCH_SPMRL.tar.gz
mkdir disco_ftb
cp surf.ftb.np_conll ${folder}/


for c in dev test train
do
    cp FRENCH_SPMRL/gold/ptb/${c}/${c}.French.gold.ptb        ${folder}/spmrl_${c}.ptb
    discodop treetransforms ${folder}/spmrl_${c}.ptb --inputfmt=bracket --outputfmt=discbracket ${folder}/spmrl_${c}.discbracket
    cp FRENCH_SPMRL/gold/conll/${c}/${c}.French.gold.conll ${folder}/spmrl_${c}.conll
done

rm -r FRENCH_SPMRL


python3 do_ftb_preprocessing.py > ${folder}/log_path_annotation.txt
discodop treedraw --fmt=discbracket --output=html < ${folder}/paths_annotation_logger.txt > ${folder}/paths_annotation_logger.html


dotreebank(){

    echo python3 deep_to_discbracket.py ${folder}/spmrl_${1}_with_paths.discbracket
    python3 deep_to_discbracket.py ${folder}/spmrl_${1}_with_paths.discbracket > ${folder}/${1}_transformation.log

    discodop treedraw --fmt=discbracket --output=html < ${folder}/modified_trees > ${folder}/${1}_modified_trees.html
    cp ${folder}/modified_trees ${folder}/${1}_modified_trees.txt

}

#for c in dev test train
#do
    #echo python3 deep_to_discbracket.py ${folder}/spmrl_${c}_with_paths.discbracket
    #python3 deep_to_discbracket.py ${folder}/spmrl_${c}_with_paths.discbracket > ${folder}/${c}_transformation.log

    #discodop treedraw --fmt=discbracket --output=html < ${folder}/modified_trees > ${folder}/${c}_modified_trees.html
    #cp ${folder}/modified_trees ${folder}/${c}_modified_trees.txt
#done

dotreebank dev & dotreebank test & dotreebank train
