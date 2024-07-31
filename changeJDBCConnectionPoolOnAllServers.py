import re
import os
import sys

if len(sys.argv) < 1:
  print "\nUSAGE: script.jy <server1|server2|...> OR <all> to setup JDBC max alive on all JVM servers.\n"
  os._exit(1)

# serversToFind = 'server1|server2'
# serversToFind = 'all'
serversToFind = sys.argv[0]

# Seconds to keep outgoing JDBC connection alive:
max_alive = "900"

# -------------------------------------

print '----------------'
print 'Looking for server [ ' + serversToFind + ' ]'

### TOPOLOGY CONFIG - DMGR, WEB nodes and WAS nodes are defined by part of hostname:
cName = AdminControl.getCell()
cID = AdminConfig.getid('/Cell:'+cName)

# In case of more Cells....
# cells = AdminConfig.list('Cell').split()
# cell = cells[0]
# cName = AdminConfig.showAttribute(cell, 'name')

print '----------------'
print ' Cell Name: ' + cName
print ' Cell ID  : ' + cID

dmgrNode = ''

webNodes = list('')
webNodesID = list('')
webNodeSearch = 'web'

wasNodes = list('')
wasNodesID = list('')
wasNodeSearch = '^.was'

dmgrNodeSearch = 'dmgr|Dmgr'

print '\n****************** Assigning role to nodes by part of hostname ******************'
print '\tDMGR: [' + dmgrNodeSearch + ']\tWEB nodes: [' + webNodeSearch + ']\tWAS nodes: [' + wasNodeSearch + ']'
print '*********************************************************************************\n'

nodes = AdminTask.listNodes()
for nod in nodes.splitlines():
  if re.search (dmgrNodeSearch, nod):
    dmgrNode = nod
  else:
    if re.search (wasNodeSearch, nod):
      wasNodes.append(nod)
    if re.search (webNodeSearch, nod):
      webNodes.append(nod)
####################################################################################

print '--- Topology ---'
dmgrNodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+dmgrNode)
print ' DMGR     : ' + dmgrNode + ' , ID : ' + dmgrNodeID
for web in webNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+web)
  webNodesID.append(nodeID)
  print ' WEB node: ' + web + ' , ID : ' + nodeID
for was in wasNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+was)
  wasNodesID.append(nodeID)
  print ' WAS node: ' + was + ' , ID : ' + nodeID
print '----------------'

appServers = []
installedApps = []

# SORT BY NODE

for nName in wasNodes:

  maxUsageMemory = 0
  print ' ========================================== '
  print ' ====== NODE SUMMARY [ '+nName+' ] ======'
  print ' ========================================== '
  node = AdminConfig.getid('/Node:' + nName )
  servers = AdminConfig.list('ServerEntry', node).split()
  print ''

  for server in servers:

    appServers.append(server)
    sName = AdminConfig.showAttribute(server, "serverName")
    serverID = AdminConfig.getid('/Node:' + nName + '/Server:' + sName + '/')

    if (re.search("(^" + serversToFind + "$)", sName) or serversToFind == 'all'):
      print ''
      print ' --------> FOUND SERVER : [ ' + sName + ' ] <-------- '
      dataSources = AdminTask.listDatasources('[-scope Cell='+cName+',Node='+nName+',Server='+sName+']').splitlines()
      for d in dataSources:
        # print AdminConfig.show(d)
        n = AdminConfig.showAttribute(d, 'name')
        if re.search("^(?!DefaultEJBTimerDataSource|built-in-derby-datasource).*", n):
          print ''
          print ' - DS: ' + n
          cpId = AdminConfig.showAttribute(d, 'connectionPool')
          # print '  - connectionPool ID >> ' + cpId
          # print AdminConfig.showall(cpId)
          ct = AdminConfig.showAttribute(cpId, 'connectionTimeout')
          maxc = AdminConfig.showAttribute(cpId, 'maxConnections')
          minc = AdminConfig.showAttribute(cpId, 'minConnections')
          reap = AdminConfig.showAttribute(cpId, 'reapTime')
          unused = AdminConfig.showAttribute(cpId, 'unusedTimeout')
          aged = AdminConfig.showAttribute(cpId, 'agedTimeout')
          # EntirePool or FailingConnectionOnly 
          purgep = AdminConfig.showAttribute(cpId, 'purgePolicy')
          print '    connectionTimeout [ ' + ct + ' ] maxConnections [ ' + maxc + ' ] minConnections [ ' + minc + ' ] reapTime [ ' + reap + ' ] unusedTimeout [ ' + unused + ' ] agedTimeout [ ' + aged + ' ] purgePolicy [ ' + purgep + ' ]'
          new_aged = max_alive
          new_purgep = "EntirePool"
          print '    SETTINGS Params: agedTimeout [ ' + new_aged + ' ] purgePolicy [ ' + new_purgep + ' ]'
          AdminConfig.modify(cpId, [['agedTimeout', new_aged]])
          AdminConfig.modify(cpId, [['purgePolicy', new_purgep]])
          # print '    - DEBUG - NEW Settings is: agedTimeout ' + AdminConfig.showAttribute(cpId, 'agedTimeout') + ' purgePolicy ' + AdminConfig.showAttribute(cpId, 'purgePolicy')

print ' ========================================== '
print ' ================ CLUSTERS ================ '
print ' ========================================== '
cs = AdminConfig.list('ServerCluster', cID).split()
for cluster in cs:
#  print AdminConfig.showall(cluster)
  cName = AdminConfig.showAttribute(cluster, "name")
  if (re.search("(^" + serversToFind + "$)", cName) or serversToFind == 'all'):
    print  ''
    print ' Cluster [ ' + cName + ' ] Cluster ID [ ' + cluster + ' ]'
    dataSources = AdminConfig.list('DataSource', cluster).splitlines()
    for d in dataSources:
      n = AdminConfig.showAttribute(d, 'name')
      if re.search("^(?!DefaultEJBTimerDataSource|built-in-derby-datasource).*", n):
        print ''
        print ' - DS: ' + n
        cpId = AdminConfig.showAttribute(d, 'connectionPool')
        # print '  - connectionPool ID >> ' + cpId
        # print AdminConfig.showall(cpId)
        ct = AdminConfig.showAttribute(cpId, 'connectionTimeout')
        maxc = AdminConfig.showAttribute(cpId, 'maxConnections')
        minc = AdminConfig.showAttribute(cpId, 'minConnections')
        reap = AdminConfig.showAttribute(cpId, 'reapTime')
        unused = AdminConfig.showAttribute(cpId, 'unusedTimeout')
        aged = AdminConfig.showAttribute(cpId, 'agedTimeout')
        # EntirePool or FailingConnectionOnly 
        purgep = AdminConfig.showAttribute(cpId, 'purgePolicy')
        print '    connectionTimeout [ ' + ct + ' ] maxConnections [ ' + maxc + ' ] minConnections [ ' + minc + ' ] reapTime [ ' + reap + ' ] unusedTimeout [ ' + unused + ' ] agedTimeout [ ' + aged + ' ] purgePolicy [ ' + purgep + ' ]'
        new_aged = max_alive
        new_purgep = "EntirePool"
        print '    SETTINGS Params: agedTimeout [ ' + new_aged + ' ] purgePolicy [ ' + new_purgep + ' ]'
        AdminConfig.modify(cpId, [['agedTimeout', new_aged]])
        AdminConfig.modify(cpId, [['purgePolicy', new_purgep]])
        # print '    - DEBUG - NEW Settings is: agedTimeout ' + AdminConfig.showAttribute(cpId, 'agedTimeout') + ' purgePolicy ' + AdminConfig.showAttribute(cpId, 'purgePolicy')
  
print ''

print 'Reset ...'
AdminConfig.reset()

#print 'Saving ...'
#AdminConfig.save()
#AdminNodeManagement.syncActiveNodes()

print 'Done.'

