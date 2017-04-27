
## generate parsing data for french

mkdir -p parse_data


function dofqb {

    sdir=FQBv1.0
    tdir=disco_fqb
    conll=${sdir}/FQB.v1.np_conll
    dbrackets=${tdir}/disco_fqb1.discbracket
    ctbk=${tdir}/disco_fqb1.ctbk
    silver=${tdir}/disco_fqb1.silver.conll


    dfqb=parse_data/fqb
    mkdir ${dfqb}

    python3 replace_brackets.py ${conll} ${dfqb}/corpus.conll
    conll=${dfqb}/corpus.conll
    python3 discbracket_to_ctbk.py ${conll} ${dbrackets} ${ctbk} > ${tdir}/d2ctbk.log
    python3 ctbk.py ${ctbk} ${silver}


    python3 eval_and_log_silver.py ${conll} ${silver} ${tdir}/silver.log
    cp ${ctbk} ${dfqb}/corpus.ctbk
    python3 strip_functional_labels.py ${dbrackets} ${dfqb}/corpus.discbrackets
    python3 ctbk_to_raw.py ${ctbk} ${dfqb}/corpus.raw
}

function dosequoia {

    dseq=parse_data/sequoia
    mkdir ${dseq}


    sdir=sequoia-7.0
    tdir=disco_sequoia
    conll=${sdir}/sequoia.surf.conll
    dbrackets=${tdir}/disco_sequoia.discbracket
    ctbk=${tdir}/disco_sequoia.ctbk
    silver=${tdir}/disco_sequoia.silver.conll


    python3 replace_brackets.py ${conll} ${dseq}/corpus.conll
    conll=${dseq}/corpus.conll
    python3 discbracket_to_ctbk.py ${conll} ${dbrackets} ${ctbk} > ${tdir}/d2ctbk.log
    python3 ctbk.py ${ctbk} ${silver}

    python3 eval_and_log_silver.py ${conll} ${silver} ${tdir}/silver.log
    cp ${ctbk} ${dseq}/corpus.ctbk
    python3 strip_functional_labels.py ${dbrackets} ${dseq}/corpus.discbrackets
    python3 ctbk_to_raw.py ${ctbk} ${dseq}/corpus.raw

}


function doftb {

    dftb=parse_data/ftb
    mkdir ${dftb}
    for corpus in train dev test
    do
        sdir=disco_ftb

        conll=${sdir}/surf.ftb.${corpus}.np_conll
        dbrackets=${sdir}/disco_spmrl_${corpus}_with_paths.discbracket
        ctbk=${sdir}/disco_spmrl_${corpus}.ctbk
        silver=${sdir}/disco_spmrl_${corpus}.silver.conll


        python3 replace_brackets.py ${conll} ${dftb}/${corpus}.conll
        conll=${dftb}/${corpus}.conll

        python3 discbracket_to_ctbk.py ${conll} ${dbrackets} ${ctbk} > ${sdir}/d2ctbk_${corpus}.log
        python3 ctbk.py ${ctbk} ${silver}
        
        python3 eval_and_log_silver.py ${conll} ${silver} ${sdir}/silver_${corpus}.log
        cp ${ctbk} ${dftb}/${corpus}.ctbk
        python3 strip_functional_labels.py ${dbrackets} ${dftb}/${corpus}.discbrackets
        python3 ctbk_to_raw.py ${ctbk} ${dftb}/${corpus}.raw
    done

}


dofqb & dosequoia & doftb





