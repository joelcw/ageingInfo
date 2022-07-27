import sys,re,string,glob
from uidodorm import dorm,uido,getDORM,infovec

textlist = glob.glob("../rawtexts/*.clean.txt")

sys.stdout.write("Year,Author,Age,Text,Dorm,DormUido,SentenceNumber\n")

for text in textlist:
    sys.stderr.write("We're on %s\n\n" % text)
    intext = open(text,"r").read()

    namex = re.compile("(.*/)(.*)\.(.*)\.(.*)\.clean\.txt")
    textname = namex.search(text)

    date = textname.group(2)
    author = textname.group(3)
    id = textname.group(4)
    if author == "christie":
        age = date-1890
    elif author == "wentworth":
        age = date-1877
    else:
        age = "NA"

    sentences = intext.split("[\.\?\!\n;]")

    ii = 1
    for s in sentences:
        dorm = getDORM(s,lenCorrect=True)
        dormuido = dorm - uido(s)
        sys.stdout.write("%s,%s,%s,%s,%s,%s,%s\n" % (date,author,age,text,dorm,dormuido,ii))
        ii=ii+1
