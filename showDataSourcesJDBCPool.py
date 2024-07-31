import re
import os
import sys

if len(sys.argv) < 2:
  print "\nUSAGE: script.jy <nodename|all> <server|all> (<showSettings>)\n"
  os._exit(1)

def arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return ''
        #sys.exit("Missing argument number [%s]" % (index))
    else:
        return sys.argv[index]

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

print '\nListing data sources on specified node(s) ' + sys.argv[0] + ' and server(s) ' + sys.argv[1] + '\n'

if len(server) > 0:
  serverSearchPart = 'process=' + server + ','

if len(node) > 0:
  nodeSearchPart = 'node=' + node + ','

query = '*:' + serverSearchPart + nodeSearchPart + 'type=DataSource,j2eeType=JDBCDataSource,*'
print 'QUERY : [ ' + query + ' ]\n'

dsToReset = AdminControl.queryNames(query)

for ds in dsToReset.splitlines():
  if re.search('^(?!.*DefaultEJBTimerDataSource.*|.*built-in-derby-datasource.*)',ds):
    dsNode = AdminControl.getAttribute(ds, 'objectName').split(',')[3].split('=')[1]
    dsJndi = AdminControl.getAttribute(ds, 'jndiName')
    dsName = AdminControl.getAttribute(ds, 'name')
    currentData = AdminControl.invoke(ds,"showPoolContents").splitlines()[3]
    print dsNode + ' / DS: ' + dsName + ' [' + dsJndi + '] - ' + currentData
    if arg(2) == 'showSettings':
      print '\t>>> Connection timeout : ' + AdminControl.getAttribute(ds, "connectionTimeout")
      print '\t>>> Maximum connections : ' + AdminControl.getAttribute(ds, "maxConnections")
      print '\t>>> Minimum connections : ' + AdminControl.getAttribute(ds, "minConnections")
      print '\t>>> Reap time : ' + AdminControl.getAttribute(ds, "reapTime")
      print '\t>>> Unused timeout : ' + AdminControl.getAttribute(ds, "unusedTimeout")
      print '\t>>> Aged timeout : ' + AdminControl.getAttribute(ds, "agedTimeout")
      print '\t>>> Purge policy : ' + AdminControl.getAttribute(ds, "purgePolicy")

print '\nDone.\n'
