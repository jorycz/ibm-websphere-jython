import re
import os
import sys

if len(sys.argv) < 3:
  print "\nUSAGE: script.jy <nodename|all> <server|all> <hsm|ldap|iso|spdh|...> (<yes>)\n"
  print "       <hsm|ldap|iso|spdh|...> - reset Connection Pool for all Data Sources which contains this string.\n"
  os._exit(1)

if sys.argv[0] == 'all':
  node = ''
else:
  node = sys.argv[0]

if sys.argv[1] == 'all':
  server = ''
else:
  server = sys.argv[1]

serverSearchPart = ''
nodeSearchPart = ''
dataSourceFilterWord = sys.argv[2]

def arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return ''
        #sys.exit("Missing argument number [%s]" % (index))
    else:
        return sys.argv[index]

def resetResourceWithQuery(query):
  print 'Getting specified datasources details ...\n'
  dsToReset = AdminControl.queryNames(query)
  for ds in dsToReset.splitlines():
    ### Filter DS here - using dataSourceFilterWord
    if re.search(dataSourceFilterWord, ds, re.IGNORECASE):
      # print '\n******************************************* DEBUG DS STRING *******************************************\n' + ds + '\n*******************************************************************************************************'
      dsNode = AdminControl.getAttribute(ds, 'objectName').split(',')[3].split('=')[1]
      dsJndi = AdminControl.getAttribute(ds, 'jndiName')
      print 'RESETTING : [ ' + dsNode + ' - ' + dsJndi + ' ]'
      connPool = AdminControl.invoke(ds,"showPoolContents")
      if re.search('Total number of connections', connPool):
        print ' BEFORE RESET : ' + AdminControl.invoke(ds, "showPoolContents").splitlines()[3]
        AdminControl.invoke(ds, "purgePoolContents")
        AdminControl.invoke(ds, "pause")
        AdminControl.invoke(ds, "resume")
        AdminControl.invoke(ds, "purgePoolContents")
        print '  AFTER RESET : ' + AdminControl.invoke(ds, "showPoolContents").splitlines()[3]
      else:
        print ' -> Connection Pool is NOT active !'
      print '-------------------------------------------------------------------------------------------------------'

print '\n'

if len(server) > 0:
  serverSearchPart = 'process=' + server + ','
else:
  print '---> all servers specified - performing Connection Pool reset on ALL JVM servers ...'

if len(node) > 0:
  nodeSearchPart = 'node=' + node + ','

query = '*:' + serverSearchPart + nodeSearchPart + 'type=J2CConnectionFactory,*'

print 'QUERY for Connection Pool reset : [ ' + query + ' ]\n'
print 'Resetting Data Sources when string [ ' + dataSourceFilterWord + ' ] is found.\n'

if len(arg(3)) < 1:
  answer = str(raw_input('Do you want to continue? [y/n] : '))
  if answer:
    if re.search('^(y|Y)', answer):
      resetResourceWithQuery(query)
    else:
      print 'Exitting ...\n'
      os._exit(0)
else:
  resetResourceWithQuery(query)

print '\n'
