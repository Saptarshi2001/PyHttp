import socket
import threading
import os,sys
import signal
import mimetypes
import logging
import json,time
from datetime import date
class TcpServer:
	host='127.0.0.1'
	port=8080
	conn=0
	addr=0
	allconn=[]
	def start(self):
		sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.bind((self.host,self.port))
		print("listening at ",sock.getsockname())
		sock.listen(1)
		try:
			while True:
				self.conn,self.addr=sock.accept()
				t=threading.Thread(target=self.handle_client,args=(self.conn,self.addr))
				t.start()
				self.allconn.append(t)	
		except socket.error:
			print("coudnt connect with the socket")
			sys.exit(1)
		
		finally:
			if sock:
				sock.close()
			for t in self.allconn:
				t.join()
	def handle_client(self,conn,addr):
		data=conn.recv(1024)
		print(data)
		response=self.handle_request(data)
		conn.sendall(response)
		conn.close()
		
	def handle_request(self,data):
		return data
	
class HttpServer(TcpServer):
	
	cntlngth=''
	headers={
		'Content-Type':'text/html ',
		'Server':'First server ',
		'Date'  :str(date.today()),
		'Last-Modified':'',
		'Content-length':'',
		'Set-Cookie':'',
		'Cache-Control':''
		}
	status_codes={
			200:'Ok \n',
			404:'Not found \n',
			501:'Not implemented \n',
			304:'Not Modified '
		}
	def __init__(self):
		self.uri=None
		self.method=None
		self.logger=logging.getLogger()
		self.logger.setLevel(logging.INFO)
		self.evnt_logger=logging.FileHandler("access.log",mode='w')
		self.evnt_logger.setFormatter(logging.Formatter('%(asctime)s  %(message)s'))
		
		
	def handle_request(self,data):
		blank_line = b'\r\n'
		res = self.parse(data)
		cntlngth=len(res)
		dict2={'Content-length':cntlngth}
		self.headers.update(dict2)
		if  res==b'':
			head=self.get_headers(self.headers).encode()
			stscds=self.get_codes(404)
			body=b'<h1>Error 404 Page not found</h1>'
			return b"".join([stscds,head,blank_line,body])

		elif res==b'Not operatable':
			head=self.get_headers(self.headers).encode()
			stscds=self.get_codes(501)
			body=b'<h1>Error 501 Not Implemented</h1>'
			return b"".join([stscds,head,blank_line,body])

		elif res==b'Deleted':
			head=self.get_headers(self.headers).encode()
			stscds=self.get_codes(200)
			body=b'<h1>File Deleted</h1>'
			return b"".join([stscds,head,blank_line,body])

        
		elif res==b'return head':
			head=self.get_headers(self.headers)
			stscds=self.get_codes(200)
			return b"".join([stscds,head.encode(),blank_line])
		
		elif res==b'Form post done':
			dict3={'Content-Type':'multipart/form-data'}
			self.headers.update(dict3)
			head=self.get_headers(self.headers).encode()
			stscds=self.get_codes(200)
			body=b'<h1>Happy hacking</h1>'
			return b"".join([stscds,head,blank_line,body])
		
		elif res==b'Cache handled':
			head=self.get_headers(self.headers)
			stscds=self.get_codes(304)
			return b"".join([stscds,head.encode(),blank_line])


            
		else:
			self.logger.addHandler(self.evnt_logger)
			self.logger.info("Connected to"+" "+f"{self.addr}"+"and page "+" "+f"{self.uri}"+"requested")
			head=self.get_headers(self.headers)
			self.setCookie(key='sessionId', value='3xhggd', expires='Sat, 05-Oct-2024 07:28:00 GMT', path='/', httpOnly=True)
			self.setCache(type='public',maxage=3600,nocache='no-cache',mustrevalid='must-revalidate')
			stscds=self.get_codes(200)
			return b"".join([stscds,head.encode(),blank_line,res])
	
		
	def parse(self,data):
		lines=data.split(b"\r\n")
		reqline=lines[0]
		cacheline=lines[2]
		if b'If-Modified-Since' in cacheline:

			moddate=cacheline[b'If-Modified-Since'].decode()
			if moddate==self.headers['Last-Modified']:
				return b'Cache handled'

		self.method=reqline.decode().split(' ')[0]
		if self.method!='GET' and self.method!='DELETE' and self.method!='POST'  and self.method!='HEAD':
			return b'Not operatable'
		elif self.method=='DELETE':
			self.handle_DELETE(reqline)
			return b'Deleted'
		elif self.method=='HEAD':
			return b'return head'
		
		elif self.method=='POST':
			self.handle_POST(reqline)
			return b'Form post done'
	
		response=self.handle_GET(reqline)
		return response
		

	def handle_DELETE(self,reqline):
		body=b''
		start=reqline.decode().find('/')+1
		end=reqline.decode().find(' ',start)
		self.uri=reqline[start:end]
		if os.path.exists(self.uri):
			os.remove(self.uri)
							
	def handle_GET(self,reqline):
		body=b''
		start=reqline.decode().find('/')+1
		end=reqline.decode().find(' ',start)
		self.uri=reqline[start:end].decode()
		if os.path.exists(self.uri) and not os.path.isdir(self.uri):
			with open(self.uri,'rb')as r:
				last_modified_time = os.path.getmtime(self.uri)  # Get the last modified time in seconds since the epoch
				last_modified_date ={'Last-Modified':time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(last_modified_time)) }
				self.headers.update(last_modified_date)    	
				body=r.read()
		return body

	def get_headers(self,headers):
		content_type = mimetypes.guess_type(self.uri)[0] or 'application/octet-stream'
		extra_header={'Content-Type':content_type}
		self.headers.update(extra_header)
        
		header_lines = [f'{key}: {value}' for key, value in headers.items()]
		
		return '\r\n'.join(header_lines)+'\r\n'
	
	
	def get_codes(self,code):
		msg=self.status_codes[code]
		msgresponse='HTTP/1.1 %s %s \r \n'%(code,msg)
		return msgresponse.encode()
	
	def setCookie(self,key,value,maxage=None,expires=None,path='/',domain=None,secure=None,httpOnly=False):
		cookies=[]
		cookies.append(f'{key}={value}')
		if maxage is not None:
			cookies.append(f'{maxage}')
		
		if expires is not None:
			cookies.append(f'{expires}')
		
		cookies.append(f'{path}')
		
		if domain is not None:
			cookies.append(f'{domain}')
		
		if secure is not None:
			cookies.append('secure')

		if httpOnly is not False:
			cookies.append('httpOnly')
		
		cookiestr=';'.join(cookies)

		self.headers['Set-Cookie']=cookiestr

	def setCache(self,type=None,maxage=None,nocache=None,nostore=None,mustrevalid=None,proxyrevalid=None):
		cachelist=[]
		if type=='private' or type=='public':
			cachelist.append(type)
		if maxage is not None:
			cachelist.append(f'max-age={maxage}')
		if nocache=='no-cache':
			cachelist.append(nocache)
		if nostore=='no-store':
			cachelist.append(nostore)

		if mustrevalid=='must-revalidate':
			cachelist.append(mustrevalid)
		if proxyrevalid=='proxy-revalidate':
			cachelist.append(proxyrevalid)
		cachestr=','.join(cachelist)
		self.headers['Cache-Control']=cachestr
	
	

		
if __name__ == '__main__':
	server=HttpServer()
	server.start()

