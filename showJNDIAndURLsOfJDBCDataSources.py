import re
import os
import sys

if len(sys.argv) < 1:
  print "\nUSAGE: script.jy <server1|server2|...|all> (<onlyURLs>) to show JNDI URLs on all JDBC Data Sources.\n"
  os._exit(1)

def arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return ''
        #sys.exit("Missing argument number [%s]" % (index))
    else:
        return sys.argv[index]

# serversToFind = 'server1|server2'
# serversToFind = 'all'
serversToFind = sys.argv[0]

if arg(1) != 'onlyURLs':
  print '---------------------------\nLooking for servers [ ' + serversToFind + ' ]'

### TOPOLOGY CONFIG - DMGR, WEB nodes and WAS nodes are defined by part of hostname:
cName = AdminControl.getCell()
cID = AdminConfig.getid('/Cell:'+cName)

# In case of more Cells....
# cells = AdminConfig.list('Cell').split()
# cell = cells[0]
# cName = AdminConfig.showAttribute(cell, 'name')

if arg(1) != 'onlyURLs':
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

if arg(1) != 'onlyURLs':
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

if arg(1) != 'onlyURLs':
  print '--- Topology ---'
dmgrNodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+dmgrNode)
if arg(1) != 'onlyURLs':
  print ' DMGR     : ' + dmgrNode + ' , ID : ' + dmgrNodeID
for web in webNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+web)
  webNodesID.append(nodeID)
  if arg(1) != 'onlyURLs':
    print ' WEB node: ' + web + ' , ID : ' + nodeID
for was in wasNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+was)
  wasNodesID.append(nodeID)
  if arg(1) != 'onlyURLs':
    print ' WAS node: ' + was + ' , ID : ' + nodeID
if arg(1) != 'onlyURLs':    
  print '----------------'

appServers = []
installedApps = []

# SORT BY NODE

for nName in wasNodes:
  if arg(1) != 'onlyURLs':
    print '\n ========================================== '
    print ' ====== NODE SUMMARY [ '+nName+' ] ======'
    print ' ========================================== \n'
  node = AdminConfig.getid('/Node:' + nName )
  servers = AdminConfig.list('ServerEntry', node).split()

  for server in servers:
    appServers.append(server)
    sName = AdminConfig.showAttribute(server, "serverName")
    serverID = AdminConfig.getid('/Node:' + nName + '/Server:' + sName + '/')

    if (re.search("(^" + serversToFind + "$)", sName) or serversToFind == 'all'):
      if arg(1) != 'onlyURLs':
        print '\n ====== SERVER [' + sName + ']'
        apps = AdminConfig.showAttribute(server, "deployedApplications").split(';')
        for app in apps:
          aName = app.split('/')[0]
          if re.search("^(?!ibmasyncrsp).*", aName):
            print ' ============ INSTALLED APP [' + aName + ']'
        print ''

      dataSources = AdminTask.listDatasources('[-scope Cell='+cName+',Node='+nName+',Server='+sName+']').splitlines()
      for d in dataSources:
        n = AdminConfig.showAttribute(d, 'name')
        if re.search("^(?!DefaultEJBTimerDataSource|built-in-derby-datasource).*", n):
          ps = AdminConfig.showAttribute(d, 'propertySet')
          propList = AdminConfig.list('J2EEResourceProperty', ps).splitlines()
          for prop in propList:
            paramName = AdminConfig.showAttribute(prop, 'name')
            if re.search("URL", paramName):
              jname = AdminConfig.showAttribute(d, 'jndiName')
              print jname + ' ; ' + AdminConfig.showAttribute(prop, 'value')

#print ''
#print ' ========================================== '
#print ' ================ CLUSTERS ================ '
#print ' ========================================== '
#print ''
#cs = AdminConfig.list('ServerCluster', cID).split()
#for cluster in cs:
#  cName = AdminConfig.showAttribute(cluster, "name")
#  dataSources = AdminConfig.list('DataSource', cluster).splitlines()
#  for d in dataSources:
#    n = AdminConfig.showAttribute(d, 'name')
#    if re.search("^(?!DefaultEJBTimerDataSource|built-in-derby-datasource).*", n):
#      ps = AdminConfig.showAttribute(d, 'propertySet')
#      propList = AdminConfig.list('J2EEResourceProperty', ps).splitlines()
#      for prop in propList:
#        paramName = AdminConfig.showAttribute(prop, 'name')
#        if re.search("URL", paramName):
#          jname = AdminConfig.showAttribute(d, 'jndiName')
#          print jname + ' ; ' + AdminConfig.showAttribute(prop, 'value')
#          print ''

print ''

