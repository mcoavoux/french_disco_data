


def get_dybro_headrules() :
    return get_headrules("ftb.headrules")

def get_headrules(filename) :
    rules = {}
    lines = [line.strip() for line in open(filename).readlines() if line.strip() and line[0] != "%"]

    for l in lines :
        l = l.split()

        nt = l[0]
        direction = l[1]
        cats = l[2:]

        if nt not in rules :
            rules[nt] = [(direction, cats)]
        else :
            rules[nt].append((direction, cats))

    if filename.endswith("negra.headrules") :

        tmprules = rules
        rules = {}
        for nt in tmprules :
            rules[nt.upper()] = [(direction, [cat.upper() for cat in cats]) for direction,cats in tmprules[nt]]
        rules["PN"] = [("left-to-right", [])]  # fix for german headrules

        rules["__LANG__"] = "german"
    else :
        rules["__LANG__"] = "french"

    for nt in rules :
        if nt != "__LANG__" :
            for d,cats in rules[nt] :
                print("{} {} {}".format(nt, d, " ".join(cats)))
    return rules
