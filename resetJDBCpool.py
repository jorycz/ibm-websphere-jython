import re
import os
import sys

if len(sys.argv) < 2:
  print "\nUSAGE: script.jy <nodename|all> <server|all> (<yes>)\n"
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

def question_y_n(quest,a1,a0):
  c1 = [a1,str((a1)[0])]
  c0 = [a0,str((a0)[0])]
  while 1:
    print quest+"\n",
    test = raw_input()
    if test in c1:
      return "1"
    elif test in c0:
      return "0"
    else:
      print "Please respond with "+a1+" or "+a0+":\n"

def arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return ''
        #sys.exit("Missing argument number [%s]" % (index))
    else:
        return sys.argv[index]

def resetJdbcWithQuery(query):
  print 'Getting specified datasources details ...\n'
  dsToReset = AdminControl.queryNames(query)
  for ds in dsToReset.splitlines():
    if re.search('^(?!.*DefaultEJBTimerDataSource.*|.*built-in-derby-datasource.*)',ds):
      dsNode = AdminControl.getAttribute(ds, 'objectName').split(',')[3].split('=')[1]
      dsJndi = AdminControl.getAttribute(ds, 'jndiName')
      print 'RESETTING : [ ' + dsNode + ' - ' + dsJndi + ' ]'
      connPool = AdminControl.invoke(ds,"showPoolContents")
      if re.search('Total number of connections',connPool):
        print ' BEFORE RESET : ' + AdminControl.invoke(ds,"showPoolContents").splitlines()[3]
        AdminControl.invoke(ds, "purgePoolContents")
        AdminControl.invoke(ds,"pause")
        AdminControl.invoke(ds,"resume")
        AdminControl.invoke(ds, "purgePoolContents")
        print '  AFTER RESET : ' + AdminControl.invoke(ds,"showPoolContents").splitlines()[3]
      else:
        print ' -> Connection Pool is NOT active !'
      print '------------------------------------------------------------------'

print '\n'

if len(server) > 0:
  serverSearchPart = 'process=' + server + ','
else:
  print '---> all servers specified - performing JDBC Connection Pool reset on ALL JVM servers ...'

if len(node) > 0:
  nodeSearchPart = 'node=' + node + ','

query = '*:' + serverSearchPart + nodeSearchPart + 'type=DataSource,j2eeType=JDBCDataSource,*'

print 'QUERY for JDBC pool reset : [ ' + query + ' ]\n'

if len(arg(2)) < 1:
  q = question_y_n("\nDo you want to continue?\nyes/no", "yes", "no")
  if q == '1':
    resetJdbcWithQuery(query)
  if q == '0':
    print 'Exitting ...\n'
    os._exit(0)
else:
  resetJdbcWithQuery(query)

