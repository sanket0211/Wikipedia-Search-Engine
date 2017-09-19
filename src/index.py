import xml.sax,re,os
import sys
import os
from heapq import *
from Stemmer import Stemmer
#from stemming.porter2 import stem
spChar=' \r\t\n/.,\';\\][|":}{`=_)(&^%@#0987654321'

stem=Stemmer('english')

BODY=0
CATEGORY=1
EXTERNAL=2
INFOBOX=3
REF=4
TITLE=5


DOCUMENT_PER_FILE=15000
LINES_PER_DOC=1000
dicts=[dict() for i in xrange(6)]
count=0
file_count=1
stopwords={}
no_of_doc = 0

dir_list=["body","category","external_links","infobox","reference","title"]

ft = open('title_id.txt','w')

path=""

class ABContentHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.doc_id = ""
        self.title = ""
        self.text = ""
        self.infobox = ""
        self.category = ""
        self.ref = ""
        self.external = ""
        self.content =  ""
        self.body =""
     
        self.current = ""
        self.parent = ""
        self.elements = []

    def parse_text(self):
        text = self.text.strip()
        l = text.split('\n')
        flag = 0
        self.infobox = ""
        self.category = ""
        self.ref = ""
        self.external =""
        self.body = ""
        for line in l:
            #line = line.strip()
            
            if line.startswith("{{Infobox"):
                flag = 1
                continue
            elif flag == 1 and line == "}}":
                flag = 0
                continue
            elif line.startswith("==References=="):
                flag = 2
                continue
            elif flag ==2 and (( line.startswith("==")  and line.find("Reference")==-1) or line.startswith("[[Category:") or line.startswith("{{")):
                flag=0
            elif flag ==3 and ( line.startswith("[[Category:")):
                flag = 0
                continue
            elif line.startswith("==External links=="):
                flag = 3
                continue
        
            if line.startswith("[[Category:"):
                self.category += line[11:-2] + '\n'
            elif flag==0:
                self.body += line + '\n'
            elif flag ==1: 
                self.infobox+=line+'\n'
            elif flag ==2:
                self.ref += line + '\n'
            elif flag ==3:
                self.external +=line +'\n'

    def startElement(self, name, attrs):

        self.elements.append(name)
        if self.current:
            self.parent = self.current
        self.current = name
        if name=="page":
            pass
    #print "*** PAGE STARTS ***"     

    def endElement(self, name):  
        if name=="page":
            global count, no_of_doc
            count+=1
            no_of_doc +=1
            Tokenize(self.doc_id.strip(), self.title, self.infobox, self.category, self.ref, self.external,self.body)
            #print "** PAGE ENDS ***"
        if name=="id":
            if self.parent == "page":
                self.doc_id = self.content
          
        if name=="title":
            self.title = self.content

        if name=="text":
            self.text = self.content
            self.parse_text()

        # pop out from the stack
        self.elements.pop()
        if self.elements:
            self.current = self.parent
            if len(self.elements) ==1:
                self.parent=""
            else:
                self.parent= self.elements[-1]
        else:
            self.current=""
        self.content ="" 

        #print("endElement '" + name + "'")
 
    def characters(self, content):

        uni = content.encode("utf-8").strip()
        if uni:
            self.content = self.content + uni + "\n"                                                                    


class Tokenize:
    def __init__(self, doc_id,title,infobox,category,ref,external,body):

        global ft
        self.doc_id = doc_id
        self.title = title
        self.infobox = infobox
        self.category = category
        self.ref = ref
        self.external = external
        self.body = body

        self.process()

        ft.write(str(self.doc_id)+':'+str(title))


    def remove_stopwords_and_stem(self, text):
        global stopwords
        Text = []
        for i in xrange(len(text)):
            if text[i] not in stopwords:
                Text.append(stem.stemWord(text[i]))
                #Text.append(stem(text[i]))
        return Text
 

    def create_dict(self, text, flag):

        temp = list(set(text))
        for word in temp:
            if word not in dicts[flag]:
                dicts[flag][word]=[1, str(self.doc_id)+":"+str(text.count(word))+","]
            else:
                dicts[flag][word][0]+=1
                dicts[flag][word][1]+=str(self.doc_id)+":"+str(text.count(word))+","


    def write_file(self,flag,directory):

        global dicts
        global file_count
        if not os.path.exists(directory):
            os.makedirs(directory)
        keys = dicts[flag].keys()
        keys.sort()
        #l = sorted(dicts[flag].iteritems(), key=lambda key_value: key_value[0])

        f = open(directory+'/file'+str(file_count)+".txt",'w')
        for i in keys:
            tgif = dicts[flag][i][0]
            doc_list = dicts[flag][i][1][:-1]
            
            final = i+":"+str(tgif)+","+doc_list+'\n'
            #print final
            f.write(final)
        f.close()


    def process(self):
        self.infobox = [j.strip() for j in re.compile(r'[^A-Za-z]+').split(self.infobox.lower()) if len(j)>0]
        self.category = [j.strip() for j in re.compile(r'[^A-Za-z]+').split(self.category.lower()) if len(j)>0]
        self.ref = [j.strip() for j in re.compile(r'[^A-Za-z]+').split(self.ref.lower()) if len(j)>0]
        self.body = [j.strip() for j in re.compile(r'[^A-Za-z]+').split(self.body.lower()) if len(j)>0]
        self.external = [j.strip() for j in re.compile(r'[^A-Za-z]+').split(self.external.lower()) if len(j)>0]
        self.title = [j.strip() for j in re.compile(r'[^A-Za-z]+').split(self.title.lower()) if len(j)>0]

        self.infobox=self.remove_stopwords_and_stem(self.infobox)
        self.category=self.remove_stopwords_and_stem(self.category)
        self.ref=self.remove_stopwords_and_stem(self.ref)
        self.body=self.remove_stopwords_and_stem(self.body)
        self.external=self.remove_stopwords_and_stem(self.external)
        self.title=self.remove_stopwords_and_stem(self.title)
        

        self.create_dict(self.infobox, INFOBOX)
        self.create_dict(self.category, CATEGORY)
        self.create_dict(self.ref, REF)
        self.create_dict(self.body, BODY)
        self.create_dict(self.external, EXTERNAL)
        self.create_dict(self.title, TITLE)

        global count
        if count==DOCUMENT_PER_FILE:
            for i in xrange(len(dir_list)):
                self.write_file(i, path+"/"+dir_list[i])

            global dicts,file_count
            dicts = [dict() for i in xrange(6)]
            file_count+=1
            #print file_count
            count=0




def merge(directory):
        
    global file_count
    latest_word = ''
    line_count=0
    sub_count = 1
    file_name = directory + "/final"
    sec_file_name = directory + "/secondary.txt"
    f_sec = open(sec_file_name,'w')

    f=open(file_name+str(sub_count)+".txt",'w')
    count =0
    l=[]
    stack = []
    file_poin=[]
    for i in xrange(1,file_count+1):
    	f0= open(directory+'/file'+str(i)+'.txt','r') 
    	s=f0.readline()[:-1]
    	s1 = s[:s[:s.find(',')].find(':')]
    	l.append((s1, s, f0))
    	file_poin.append(f0)
    heapify(l)
    while(count<file_count):
    	top = heappop(l)
    	s0 = top[0]
    	s1 = top[1]
    	f1 = top[2]
    	s_list = []
    	s_list.append(s1)
    	s=f1.readline()[:-1]
    	if s=='':
    		count+=1
    	else:
    		heappush(l, (s[:s[:s.find(',')].find(':')], s, f1))
    	if count==file_count:
    		break

    	while(1):
	    	try:
	        	tmp = heappop(l)
	    	except IndexError:
	        	break

	    	s0 = tmp[0]
	    	s2 = tmp[1]
	    	f2 = tmp[2]

	    
	    	#print s2
	    	#print s_list[-1][:s_list[-1][:s2[-1].find(',')].find(':')]
	    	if s0 != s_list[-1][:s_list[-1][:s2[-1].find(',')].find(':')]:
        	    heappush(l,(s0,s2,f2))
        	    break
	    	else:
        	    s_list.append(s2)
        	    s3 = f2.readline()[:-1]
        	    #print s3
        	    if s3=='':
            		count+=1
        	    else:
            		heappush(l,(s3[:s3[:s3.find(',')].find(':')],s3,f2))

        if len(s_list)==1:
        	s = s_list[0]
        	line_count+=1
        	latest_word = s[:s.find(':')]            
        	f.write(s+'\n')
        	if line_count==LINES_PER_DOC:
        		line_count=0
        		f.close()
        		f_sec.write(file_name + str(sub_count)+".txt"+":"+latest_word+'\n')
        		sub_count+=1
        		f = open(file_name+str(sub_count)+".txt",'w')
           
        else:
        	tfid=0

	    	word_pre = s_list[0][:s_list[0].find(',')]
	    	word = word_pre[:word_pre.find(':')]
	    	tgif =0
	    	s=""
	    	flag=0
	    	for i in s_list:
        	    content = i[i.find(',')+1:]
        	    content_pre = i[:i.find(',')]
        	    tgif_tmp = int(content_pre[content_pre.find(':')+1:])
        	    tgif += tgif_tmp
        	    if flag==0:
        	        s=content
        	        flag=1
        	    else:
            		s+=','+content
    	#print word+':'+str(tgif)+','+s+'\n'
    		line_count+=1
    		latest_word=word
    		f.write(word+':'+str(tgif)+','+s+'\n')
    		if line_count==LINES_PER_DOC:
    			line_count=0
               	f.close()
               	f_sec.write(file_name + str(sub_count)+".txt"+":"+word+'\n')
               	sub_count+=1
               	f = open(file_name+str(sub_count)+".txt",'w')
    if f:
        f.close()

    if line_count>0:
        f_sec.write(file_name + str(sub_count)+".txt"+":"+latest_word+'\n')
        
    f_sec.close()

    for i in file_poin:
		i.close()




def write_rest(flag, directory):
    global dicts
    global file_count
    if not os.path.exists(directory):
        os.makedirs(directory)
    keys = dicts[flag].keys()
    keys.sort()
    #l = sorted(dicts[flag].iteritems(), key=lambda key_value: key_value[0])
    m = open(directory+'/file'+str(file_count)+".txt",'w+')
    print directory
    print file_count
    print m
    for i in keys:
    	tgif = dicts[flag][i][0]
    	doc_list = dicts[flag][i][1][:-1]
    	final = i+":"+str(tgif)+","+doc_list+'\n'
    	m.write(final)

    #m.close()



def main(sourceFileName, path_var):
	
    f = open('./stopwords.txt','r')
    global stopwords, ft, path
    path = path_var
    stopwords={}
    for i in f:
        for j in re.compile(r'[^A-Za-z]+').split(i.lower()):
            if len(j)>0:
                stopwords[j.strip()]=True
    f.close()
    source = open(sourceFileName)
    xml.sax.parse(source, ABContentHandler())


    for i in xrange(len(dir_list)):
    	write_rest(i,"Index/"+dir_list[i])
    	merge("Index/"+dir_list[i])
    	os.system("rm Index/"+dir_list[i]+"/file*")


   	f = open('Index/doc_count.txt','w')
   	f.write(str(no_of_doc)+'\n')
   	f.close()	
   	ft.close()


 
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
