
ID,FORM,LEMMA,CPOS,FPOS,MORPH,HEAD,DEPREL,PHEAD,PDEPREL=range(10)

def read_conll(filename) :
    with open(filename) as f :
        sentences = [[line.split("\t") for line in sen.split("\n") if line and line[0] != "#"] for sen in f.read().split("\n\n") if sen.strip()]

    for s in sentences :
        for tok in s :
            tok[ID] = int(tok[ID])
            tok[HEAD] = int(tok[HEAD])
    return sentences

def evaluate(gold, silver, log) :
    assert(len(gold) == len(silver))
    uas = 0.0
    cpos = 0.0
    fpos = 0.0
    tot = 0.0

    sentid=0
    for sg, ss in zip(gold, silver) :
        logsent = True
        assert(len(sg) == len(ss))
        u,c,f = 0, 0, 0
        for tg, ts in zip(sg, ss) :
            if tg[FORM] != ts[FORM] :
                sys.stderr.write("{} {}\n".format(tg[FORM], ts[FORM]))
            assert(tg[FORM] == ts[FORM])
            if tg[CPOS] == ts[CPOS] :
                c += 1
            if tg[FPOS] == ts[FPOS] :
                f += 1
            if tg[HEAD] == ts[HEAD] :
                u += 1
            
            """## attempts at classifying error
            else :
                if sg[ts[HEAD]-1][FPOS][0] == "C" :
                    log.write("{} coord,sent\n".format(sg[0][MORPH]))
                    logsent = False
                if tg[FPOS] == "DET" and ts[HEAD] < ts[ID] :
                    log.write("{} det attached to preceding noun (Probably a case of NP apposition with flat structure)\n".format(sg[0][MORPH]))
                    logsent = False
                if tg[FORM] == "en" and tg[FPOS] == "CLO":
                    log.write("{} clitique en mal rattaché\n".format(sg[0][MORPH]))
                    logsent = False
                if tg[FPOS] == "CC" :
                    log.write("{} conjonction de coordination mal rattachée\n".format(sg[0][MORPH]))
                    logsent = False
                if tg[FPOS] == "PONCT" :
                    log.write("{} ponctuation mal rattachée\n".format(sg[0][MORPH]))
                    logsent = False
                if tg[FPOS] in {"P", "P+D", "P+PRO"}:
                    log.write("{} préposition mal rattachée\n".format(sg[0][MORPH]))
                    logsent = False
            """

            tot += 1
        uas += u
        cpos += c
        fpos += f

        if u != len(sg) and logsent:
            log.write("sent {}\n".format(sentid))
            for tg, ts in zip(sg, ss) :
                log.write("{}\n".format("\t".join(map(str, ts))))
                log.write("{}\n".format("\t".join(map(str, tg))))
            log.write("\n\n")

        sentid += 1
    log.write("UAS = {}\n".format(uas / tot))
    log.write("coarse tagging = {}\n".format(cpos / tot))
    log.write("fine tagging = {}\n".format(fpos / tot))

if __name__ == "__main__" :
        import sys
        import argparse

        usage = """
        Evaluates a silver (obtained by simple conversion from head-annotated
        constituency treebank) dependency corpus against the corresponding gold
        as regards pos tagging, head, (+ check morphology)
        """

        parser = argparse.ArgumentParser(description = usage, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("gold", type = str, help="gold conll corpus")
        parser.add_argument("silver", type = str, help="silver conll corpus)")
        parser.add_argument("log", type = str, help="file where to print log (wrong sentences, etc...)")

        args = parser.parse_args()
        gold = args.gold
        silver = args.silver
        out = args.log

        gold = read_conll(gold)
        silver = read_conll(silver)

        log = open(out, "w")

        evaluate(gold, silver, log)
