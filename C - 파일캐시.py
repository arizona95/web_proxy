import threading
import socket
import time
import urllib
import urllib.request
import hashlib
from urllib import parse as urlparse
from operator import eq

HOST='127.0.0.1'
PORT=8080
BUFMAX=108192

flag=0
filecashlist=[]

class req_n_res(threading.Thread):
   def run(self):
      global flag
      conn,addr=s.accept()
      packet=conn.recv(BUFMAX)
      packet=packet.replace(b'Accept-Encoding: gzip, deflate, sdch',b'Accept-Encoding: gzip')
      #print(packet)
      if(packet.find(b'HTTP') == -1 ):
         return
      flag=flag-2
      host=packet.split(b'\r\n')
      if(host[0].find(b'CONNECT')!=-1) :
          return
      packeturl=b''
      if(host[0].find(b'http://') !=-1) :
          urlstart = host[0].rfind(b'http://')
          urlend=0
          if(host[0][urlstart+7:].find(b':')!=-1) :
              urlend=host[0][urlstart:].rfind(b':')
          else :
              urlend = host[0].rfind(b'HTTP')
          packeturl=host[0][urlstart:urlend]
      #print(packeturl)

      isincash=0
      res=""
      i=0
      hashurl=hashlib.sha1(packeturl).hexdigest()
      global filecashlist
      print(len(filecashlist))

      for i in range(0,len(filecashlist)) :
          if(eq(hashurl,filecashlist[i])) :
              isincash=1
              break

      if(isincash==1) :
          
          out= open(hashlib.sha1(packeturl).hexdigest()+'.txt','rb')
          res=out.read()
          res=res.replace(b'\r\r',b'\r')
          out.close()
          
          print(b"cashing")

      else :
          print(b"notcashing")
          res=send_req(packeturl,packet)
          filecashlist.insert(len(filecashlist),hashurl)
          out=open(hashurl+'.txt','w')
          print(res.decode(),file=out)
          out.close()

      print(filecashlist)
      print(res)
      time.sleep(1)
      conn.send(res)
      
def send_req(dest_url,packet):
   c=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   result = urllib.parse.urlparse(dest_url)
   c.connect((str(result.netloc.decode()),80))
   c.send(packet)
   data=c.recv(BUFMAX)
   #print(str(len(data)))
   c.close()
   return data



s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(5)
out=open('output.txt','w')
print('haha',file=out)
out.close()

while True:
   if flag<10 :
      th=req_n_res()
      th.start()
      flag = flag + 1
   continue

