
def replace_brackets(s) :
    return s.replace("(", "-LRB-").replace(")", "-RRB-").replace("[", "-LSB-").replace("]", "-RSB-")

if __name__=="__main__":
    import sys
    import argparse

    usage = """
        Replace ( and ) by -LRB- and -RRB- in a conll corpus
        
        Also: remove commentaries "# ...  "
    """

    parser = argparse.ArgumentParser(description = usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("conll", type = str, help="corpus .conll")
    parser.add_argument("output", type = str, help="Output")

    args = parser.parse_args()
    conllfile = args.conll
    output = args.output

    out = open(output, "w")
    
    for line in open(conllfile) :
        if line[0] == "#" :
            continue
        line = line.split("\t")
        if len(line) > 1 :
            line[1] = replace_brackets(line[1])
        out.write("\t".join(line))
    
    out.close()

