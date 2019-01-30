import time
import logging

from keyczar import keyczar
location = '/opt/kz'

# create logger
lgr = logging.getLogger('mpesa_api')

class Wrapper:

	
	def executeAction(self, payload):
	'''
	Implement your custom action.
	'''
		lgr.info('ResponseCode: %s|ServiceStatus: %s|OriginatorConversationID:%s' % (ResponseCode, ServiceStatus, OriginatorConversationID))

		if ResponseCode == '0':
				lgr.info('Transaction Successful')
				ConversationID = ResponseMsg.find('{http://api-v1.gen.mm.vodafone.com/mminterface/response}ConversationID').text
				lgr.info('ConversationID: %s' % ConversationID)
				payload['response'] = ConversationID
				payload['response_status'] = '32'

		else:
				lgr.info('Transaction Failed')
				ResponseDesc = ResponseMsg.find('{http://api-v1.gen.mm.vodafone.com/mminterface/response}ResponseDesc').text
				lgr.info('ResponseDesc: %s' % ResponseDesc)
				payload['response_status'] = '96'

		return payload
