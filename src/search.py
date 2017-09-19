import re,math
from Stemmer import Stemmer
stem=Stemmer('english')
stopword={}
TITLE=0
BODY=1
INFOBOX=2
REF=3
EXTERNAL=4
CATEGORY=5
dir_list=["title","body","infobox","reference","external_links","category"]
tf_idf={}
no_of_doc = 0
def remove_stopwords_and_stem(text):
    global stopwords
    Text = []
    for i in xrange(len(text)):
        if text[i] not in stopwords:
            Text.append(stem.stemWord(text[i]))
            #Text.append(stem(text[i]))
    return Text

def calc_tf_idf(term, typ):
    i=1
    f = open('Index/'+dir_list[typ]+'/secondary.txt','r')
    f_name = ''
    for i in f:
       if term <= i[i.find(':')+1:-1]:
           f_name = i[:i.find(':')]
           break
    f.close()
    try:
        f=open(f_name,'r')
    except IOError:
        return
    for i in f:
        if term == i[:i.find(':')]:
            s = i[i.find(':')+1:-1]
            idf = int(s[:s.find(',')])
            s = s[s.find(',')+1:]
            l = s.split(',')
            l1=[]
            l2=[]
            #print l
            for j in l:
                l1.append(j.split(':')[0])
                l2.append(j.split(':')[1])
           
            l3 = zip(l1, l2)
            #print l3
            l3.sort(reverse=True)
            l3=l3[:5000]
            for j in l3:
                N = no_of_doc
                #print j[1]
                if j[0] in tf_idf:
                    tf_idf[j[0]]+=int(j[1])*math.log(N/idf)*(6-typ)
                else:
                    tf_idf[j[0]]=int(j[1])*math.log(N/idf)*(6-typ)
            break


title_id={}
f = open('title_id.txt','r')
for i in f:
    i=i.split(':')
    try:
        title_id[i[0]]=i[1].strip()
    except:
        pass
    
f.close()

t=input()
while(t>0):
    
    #global tf_idf, no_of_doc

    f = open('stopwords.txt','r')
    global stopwords
    stopwords={}
    for i in f:
        for j in re.compile(r'[^A-Za-z]+').split(i.lower()):
            if len(j)>0:
                stopwords[j.strip()]=True
    f.close()

    typ = 1

    s = raw_input()

    if s[1]==':':
        typ = 2
    else:
        typ = 1

    tf_idf={}

    if typ==1:
        l = [j.strip() for j in re.compile(r'[^A-Za-z]+').split(s.lower()) if len(j)>0]
        l = remove_stopwords_and_stem(l)
           
        f = open('Index/doc_count.txt','r')
        no_of_doc=int(f.readlines()[0][:-1])
        f.close()

        for i in l:
                calc_tf_idf(i,BODY)
                calc_tf_idf(i,CATEGORY)
                calc_tf_idf(i,EXTERNAL)
                calc_tf_idf(i,INFOBOX)
                calc_tf_idf(i,REF)
                calc_tf_idf(i,TITLE)
            
        l1,l2 =[],[]

        for i in tf_idf: 
            l1.append(i)
            l2.append(tf_idf[i])
            
        l3 = zip(l2,l1)

        l3.sort(reverse=True)
        for (x,y) in l3[:10]:
            print title_id[y]

    else:
        """
            Format : t:words b:words i:infobox e:external r:reference c:category 
                                                                                 """
        l = s.strip().split(' ')
        f = open('Index/doc_count.txt','r')
        no_of_doc=int(f.readlines()[0][:-1])
        f.close()

        for i in l:
            form = i[:i.find(':')]
            s=i[i.find(':')+1:]
            l1 = [j.strip() for j in re.compile(r'[^A-Za-z]+').split(s.lower()) if len(j)>0]
            l1 = remove_stopwords_and_stem(l1)


            if form == 'b':
                form = BODY
            elif form == 't':
                form = TITLE
            elif form == 'i':
                form = INFOBOX
            elif form == 'c':
                form = CATEGORY
            elif form == 'e':
                form = EXTERNAL
            else:
                form = REF

            for j in l1:
                print j
                calc_tf_idf(j,form)


        l1, l2 = [], []

        for i in tf_idf: 
            l1.append(i)
            l2.append(tf_idf[i])
            
        l3 = zip(l2,l1)

        l3.sort(reverse=True)
        for (x,y) in l3[:10]:
            print title_id[y]
           
        pass
    print 
t-=1