import re
import os
import sys

if len(sys.argv) < 1:
  print "\nUSAGE: script.jy <listOnly|listAndDelete|deleteOnly> (<showBody>)\n"
  print "       listOnly - list all error messages in SIB exception destination.\n"
  print "       listAndDelete - list and delete all messages.\n"
  print "       deleteOnly - do not list messages, delete them right away.\n"
  print "       showBody - OPTIONAL - show data of messages body when listing.\n"
  os._exit(1)

def arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return ''
        #sys.exit("Missing argument number [%s]" % (index))
    else:
        return sys.argv[index]

queue = "type=SIBQueuePoint,name=_SYSTEM.Exception.Destination*,*"

print ('\nReading SIB Queue Points. Please wait ...')
sibQueue = AdminControl.queryNames(queue)
queueDepth = AdminControl.invoke(sibQueue, 'getDepth')
print('Queue Depth: ' + queueDepth)

queueDepthInt = int(queueDepth)
if queueDepthInt < 1:
  print '\nNo error messages in SIB System Exception Queue.\n'
  os._exit(1)
else:
  print '\nSome error messages in SIB System Exception Queue found.\n'

# LIST
if re.search('^(listAndDelete|listOnly)', sys.argv[0]):

  sibQueue_id = AdminControl.getAttribute(sibQueue, 'id')
  print 'Querying Messaging Engines ...'
  sibME = AdminControl.queryNames('type=SIBMessagingEngine,process=*,*')

  sibME_obj = AdminControl.makeObjectName(sibME)
  messages = AdminControl.invoke_jmx(sibME_obj,'getQueuePointMessages',[sibQueue_id], ['java.lang.String'])
  
  for msg in messages:
       msg_id = msg.getId()
       msg_sysid = msg.getSystemMessageId()
       msg_length = msg.getApproximateLength()
       msg_detail = AdminControl.invoke_jmx(sibME_obj, 'getQueuePointMessageData',[sibQueue_id, msg_id, msg_length], ['java.lang.String','java.lang.String', 'java.lang.Integer'])
       print( '-'*120 )
       print( 'id: %s' % msg_id)
       print( 'sysid: %s' % msg_sysid)
       print( 'length: %d' % msg_length)
       # Print hexa array:
       # print( ' hexa: %s' % ':'.join( [ '%02x' % x for x in msg_detail]))
       # Print byte array:
       # print(msg_detail)
       # Java's byte is signed (range -128 to 127) but we need byte value unsigned.
       # So we need to use: x & 0xff - this is conversion from signed byte value to unsigned
       if arg(1) == 'showBody':
         print('=============== BODY ===============')
         print( ' ascii: %s' % ''.join( [ chr(x & 0xff) for x in msg_detail]))
         print( '-'*120 )
  

# DELETE
if re.search('^(listAndDelete|deleteOnly)', sys.argv[0]):
  
  while 1:
    answer = raw_input('Really want to DELETE ALL messages in ' + queue + ' [y/n]: ')
    if re.search('^[YyNn]', answer):
      break
  
  if re.search('^[Yy]', answer):
    print('\nDeleting ' + queueDepth + ' messages from queue ' + queue + ' ...')
    objName = AdminControl.makeObjectName(queue)
    print 'Filtering messages to delete. Please wait ...'
    qps = AdminControl.queryNames_jmx(objName, None)
    print 'Deleting messages ...'
    try:
      qps_list = list(qps)
      qp = qps_list[0]
      AdminControl.invoke_jmx(qp, 'deleteAllQueuedMessages', [java.lang.Boolean('false')], ['java.lang.Boolean'])
    except AttributeError:
      qp = qps[0]
      AdminControl.invoke_jmx(qp, 'deleteAllQueuedMessages', [java.lang.Boolean('false')], ['java.lang.Boolean'])
  else:
    print('Do not delete. Exitting ...')
  
queueDepth = AdminControl.invoke(sibQueue, 'getDepth')
print('\nFinal Queue Depth: ' + queueDepth)
print('Done.')

