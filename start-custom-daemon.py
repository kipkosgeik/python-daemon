import sys
import time
import threading
import logging
import ConfigParser
from utils.daemon import Daemon
from utils.xmlrpc_client import xmlrpc_client
from utils.threadpool import ThreadPool
from backend.wrapper import *
from logging import handlers

cf = ConfigParser.ConfigParser() 
cf.read("conf/application.properties") 

#APP
PIDFILE = cf.get('APP',"PIDFILE")
LOGFILE = cf.get('APP',"LOGFILE")

# create logger and setup logging. You can set this up from the config file so that code changes are not
# necessary change stuff like log levels
lgr = logging.getLogger('my_daemon')
lgr.setLevel(logging.DEBUG)
fh = handlers.TimedRotatingFileHandler(LOGFILE, when="midnight")
fh.setLevel(logging.WARNING)
fh.setLevel(logging.DEBUG)
fh.setLevel(logging.INFO)
frmt = logging.Formatter('%(asctime)s - %(name)s (%(threadName)-2s) - %(levelname)s - %(message)s', datefmt="%d-%m-%Y %H:%M:%S")
fh.setFormatter(frmt)
lgr.addHandler(fh)

'''
Skeleton of what you task does. Many times it calls utilities on from Backend package
'''
class Job:
	responseParams = {'response_status':'30',}
	def __init__(self):
		pass
	def transact(self, payload):
		lgr.info('Starting transaction')

		start_time = time.time()
		try:
			#Call backend that has logic to do what you want
			payload = Wrapper().executeAction(payload)
		except Exception, e:
			lgr.critical('Error performing out transaction: %s' % e)
			payload['response_status'] = '96'

		payload['t-a-t'] =  "%s seconds" % (time.time() - start_time)
		item = {}
		item['URL'] = URL
		item['timeout_time'] = timeout_time
		
		credentials={
		        "username":username,
		        "password":password,
		        }

		payload["credentials"] = credentials
		payload["account_alias"] = 'M-PESA API'

		payload = self.call_api(item, payload)
		lgr,info('Response to API payload: %s' % payload)
		return payload

	def call_api(self, item, payload):
		lgr.info('processorFinal: We are now processing the transaction')

		try:
		        server_info = {'server_url': item['URL'],
		                       'timeout': item['timeout_time'],
		                       'key_file': item['key_path'],
		                       'cert_file': item['cert_path'],
		                       'use_ssl': item['use_ssl'],
		                       }
		        lgr.info('processorFinal: server_info %s' % server_info)
		        client = xmlrpc_client()
		        lgr.info('processorFinal: Client %s' % client)
		        server = client.server(server_info)
		        
			lgr.info('processorFinal: server %s' % server)
			
			lgr.info('Funcions(payload: %s)(function: %s)(node handler: %s)' % (payload, item['command_function'], item['node_handler']))

		        self.responseParams = client.clientcall(server, payload, item['command_function'], item['node_handler'])
		except Exception, e:
		        lgr.info('processFinal: Error %s' % e);
		return  self.responseParams


'''
Extends Daemon and Job above from Utils. It makes your job above a daemon
This runs for as long as the service is up.
'''
class Daemon(Daemon, Job):
	pool = ThreadPool(0)
	def run(self):
		while True:
			try:
				item = {}
				item['URL'] = URL
				item['timeout_time'] = timeout_time
				item['key_path'] = DEFAULTKEYFILE
				item['cert_path'] = DEFAULTKEYFILE
				item['use_ssl'] = use_ssl
				item['command_function'] = 'trans_fetch'
				item['node_handler'] = node_handler

				credentials={
					"username":username,
					"password":password,
					}

				payload={
						"credentials":credentials,
						"limit": '10',
						"account_alias": 'M-PESA API'
						}

				time.sleep(2)

				#GET UNPROCESSED REQUESTS
				results = self.call_api(item, payload)
				response = results['response'] 
				lgr.info('Just Started a task - Response: %s' % response)

				self.pool = ThreadPool(len(response))

				for k in response:
					if response[k]['MSISDN'] != '' and response[k]['amount'] != '':
						self.pool.add_task(self.transact, response[k])
						lgr.info('Started thread with info: %s' % response[k])
						self.pool.wait_completion() 
					else:
						lgr.info('Invalid Payload')
				# 3) Wait for completion
				time.sleep(2)

				#lgr.info ('Checking for Completion')
				#self.pool.wait_completion()
				#lgr.info ('Just completed a task')
			except Exception, e:
				lgr.critical('Shit Happens! Woi!!! %s ' % e)


'''
 Entry point for the starting script. Makes it possible to start|stop|restart|status

 You Hardly need to modify this part.
'''
if __name__ == "__main__":

	daemon = Daemon(PIDFILE)

	if len(sys.argv) == 2:

		if 'start' == sys.argv[1]:
			try:
				daemon.start()
			except:
				pass

		elif 'stop' == sys.argv[1]:
			print "Stopping ..."
			daemon.pool.wait_completion()
			print "Completed Tasks..."
			#daemon.driver.quit()
			print "closed drivers...."
			daemon.stop()
			print "Daemon Stopped"

		elif 'restart' == sys.argv[1]:
			print "Restaring ..."
			daemon.pool.wait_completion()
			print "Completed Tasks..."
			#daemon.driver.quit()
			print "closed drivers...."
			daemon.restart()
			print "Daemon Restarted"

		elif 'status' == sys.argv[1]:
			try:
				pf = file(PIDFILE,'r')
				pid = int(pf.read().strip())
				pf.close()
			except IOError:
				pid = None
			except SystemExit:
				pid = None

			if pid:
				print 'Daemon is running as pid %s' % pid
			else:
				print 'Daemon is not running.'

		else:
			print "Unknown command"
			sys.exit(2)
			sys.exit(0)
	else:
		print "usage: %s start|stop|restart|status" % sys.argv[0]
		sys.exit(2)

