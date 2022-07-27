import sys,re,string,glob
sys.path.append("/root/.local/bin")
from nltk.tokenize import sent_tokenize
from uidodorm import dorm,uido,getDORM,infovec

#textlist = glob.glob("../rawtexts/*.clean.txt")
textlist = glob.glob("../rawtexts/1977.christie.autobiography.clean.txt")

sys.stdout.write("Year,Author,Age,Text,Dorm,DormUido,SentenceNumber\n")

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

    sentences = sent_tokenize(intext)

    ii = 1
    for s in sentences:
        sys.stdout.write("%s\n\n" % s) #debug
        Dorm = getDORM(s,lenCorrect=True)
        dormUido = Dorm - dorm(uido(s))
        sys.stdout.write("%s,%s,%s,%s,%s,%s,%s\n" % (date,author,age,id,Dorm,dormUido,ii))
        ii=ii+1
