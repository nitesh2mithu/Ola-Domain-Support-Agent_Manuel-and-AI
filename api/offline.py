"""Acceptance/runtime audit: only IPv4 TCP 127.0.0.1 at one API port."""
import socket
import sys


class ExternalAccessBlocked(RuntimeError): pass


class LocalhostAudit:
    def __init__(self,port):
        if type(port) is not int or not 1<=port<=65535: raise ValueError('Valid API port required')
        self.port=port;self.blocked=[];self.allowed=[]

    def install(self):
        def audit(event,args):
            if event=='socket.getaddrinfo':
                if args[0]=='127.0.0.1' and str(args[1])==str(self.port):
                    self.allowed.append(event);return
                self.blocked.append(event);raise ExternalAccessBlocked('External DNS is disabled')
            if event in ('socket.gethostbyname','socket.gethostbyaddr','socket.sendto','subprocess.Popen','os.system','os.posix_spawn'):
                self.blocked.append(event);raise ExternalAccessBlocked('External access/process operation disabled')
            if event=='socket.connect' and args[0].family in (socket.AF_INET,socket.AF_INET6):
                if args[0].family==socket.AF_INET and args[0].type==socket.SOCK_STREAM and args[1]==('127.0.0.1',self.port):
                    self.allowed.append(event);return
                self.blocked.append(event);raise ExternalAccessBlocked('Only the configured localhost API connection is permitted')
            if event=='socket.bind' and args[0].family in (socket.AF_INET,socket.AF_INET6):
                # urllib3's IPv6 capability probe binds ::1:0, without traffic.
                if args[1] in [('127.0.0.1',self.port),('::1',0)]:return
                self.blocked.append(event);raise ExternalAccessBlocked('External/listener bind disabled')
        sys.addaudithook(audit)
