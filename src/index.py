import xml.sax

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