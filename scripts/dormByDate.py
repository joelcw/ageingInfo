import sys,re,string,glob
sys.path.append("/root/.local/bin")
from nltk.tokenize import sent_tokenize
from uidodorm import dorm,uido,getDORM,infovec


textlist = glob.glob("../rawtexts/*.clean.txt")
#textlist = glob.glob("../rawtexts/1921.christie.styles.clean.txt")

#The list is reversed to debug last files
textlist.reverse()

sys.stdout.write("Year,Author,Age,Text,DormNoPenalty,Dorm,Uido,DormUido,SentenceNumber\n")

for text in textlist:
    sys.stderr.write("We're on %s\n\n" % text)
    intext = open(text,"r").read()

    namex = re.compile("(.*/)(.*)\.(.*)\.(.*)\.clean\.txt")
    textname = namex.search(text)

    date = int(textname.group(2))
    author = textname.group(3)
    id = textname.group(4)
    if author == "christie":
        age = date-1890
    elif author == "wentworth":
        age = date-1877
    else:
        age = "NA"

    #Fix bad quotes that cause tokenization probs
    intext = re.sub("[“”]","\"",intext)

    #tokenize into sentences
    sentences = sent_tokenize(intext)

    ii = 1
    for s in sentences:
        sys.stderr.write("%s\n\n" % s) #debug
        Dorm = getDORM(s,lenCorrect=True)
        DormNoPenalty = getDORM(s,lenCorrect=False)
        Uido = dorm(uido(s))
        dormUido = Dorm - Uido
        sys.stdout.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (date,author,age,id,DormNoPenalty,Dorm,Uido,dormUido,ii))
        ii=ii+1
