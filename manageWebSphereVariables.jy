import re
import os
import sys

def help():
  print "\nUSAGE: script.jy <scope> <show|create|remove|modify> <nodename/clustername|all> <servername|all> <variable_name|all> (<variable_value>) (<variable_description>)\n"
  print "       <scope> MUST be one of all, cluster, node, server - scope where action happens."
  print "       <show|create|remove|modify>"
  print "       <nodename/clustername|all> - perform action on node, cluster, or all nodes / clusters."
  print "       <servername|all> - perform action on server or on all servers. Specify whatever here in case of nodes / clusters actions only. It's ignored in scope cluster OR node."
  print "       <variable_name|all> - specify variable name to manage or all in case of show action."
  print "       <variable_value> is OPTIONAL - depending on action."
  print "       <variable_description> is OPTIONAL - depending on action.\n"

if len(sys.argv) < 5:
  help()
  os._exit(1)

def arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return ''
        #sys.exit("Missing argument number [%s]" % (index))
    else:
        return sys.argv[index]

if sys.argv[2] == 'all':
  node = '.*'
else:
  node = sys.argv[2]

if sys.argv[3] == 'all':
  server = '.*'
else:
  server = sys.argv[3]

if sys.argv[4] == 'all':
  variableName = '.*'
else:
  variableName = sys.argv[4]

scopeParam = sys.argv[0]
actionParam = sys.argv[1]

variableValue = arg(5)
variableDescription = arg(6)

if actionParam != 'show' and actionParam != 'create' and actionParam != 'remove' and actionParam != 'modify':
  help()
  os._exit(1)

if actionParam == 'create' or actionParam == 'modify':
  if len(variableValue) < 1:
    print "\nThis action requires content!\n"
    help()
    os._exit(1)

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




def showVariable(scope, variableMapId):
  print 'SCOPE: [ ' + scope.replace('/VariableMap:/', '') + ' ] --- ' + variableMapId
  variables = AdminConfig.list('VariableSubstitutionEntry', variableMapId).splitlines()
  for variable in variables:
    vName = AdminConfig.showAttribute(variable, 'symbolicName')
    if re.search('^' + variableName + '$', vName):
      value = AdminConfig.showAttribute(variable, 'value')
      description = AdminConfig.showAttribute(variable, 'description')
      print '--> [' + vName + '] --- Value [' + value + '] --- Description [' + description + ']'
  print '\n'

def createVariable(scope, variableMapId):
  print 'SCOPE: [ ' + scope.replace('/VariableMap:/', '') + ' ] --- ' + variableMapId + '\n'
  print '!! Creating variable [' + variableName + '] with value [' + variableValue + '] and description [' + variableDescription + '] ...'
  AdminConfig.create('VariableSubstitutionEntry', variableMapId, '[[symbolicName "' + variableName + '"] [description "' + variableDescription + '"] [value "' + variableValue + '"]]')

def removeVariable(scope, variableMapId):
  print 'SCOPE: [ ' + scope.replace('/VariableMap:/', '') + ' ] --- ' + variableMapId + '\n'
  variables = AdminConfig.list('VariableSubstitutionEntry', variableMapId).splitlines()
  for variable in variables:
    vName = AdminConfig.showAttribute(variable, 'symbolicName')
    if re.search('^' + variableName + '$', vName):
      value = AdminConfig.showAttribute(variable, 'value')
      description = AdminConfig.showAttribute(variable, 'description')
      print '!! Deleting variable [' + vName + '] with value [' + value + '] and description [' + description + '] ... --- ' + variable
      AdminConfig.remove(variable)

def modifyVariable(scope, variableMapId):
  print 'SCOPE: [ ' + scope.replace('/VariableMap:/', '') + ' ] --- ' + variableMapId + '\n'
  variables = AdminConfig.list('VariableSubstitutionEntry', variableMapId).splitlines()
  for variable in variables:
    vName = AdminConfig.showAttribute(variable, 'symbolicName')
    if re.search('^' + variableName + '$', vName):
      value = AdminConfig.showAttribute(variable, 'value')
      description = AdminConfig.showAttribute(variable, 'description')
      print '!! Setting variable [' + vName + '] with old value [' + value + '] to [' + variableValue + '] and old description [' + description + '] to [' + variableDescription + '] ... --- ' + variable
      AdminConfig.modify(variable, '[[symbolicName "' + variableName + '"] [description "' + variableDescription + '"] [value "' + variableValue + '"]]')


wasNodes.append(dmgrNode)
print '\n'

clusters = AdminConfig.list('ServerCluster').split()
for cluster in clusters:
  clusterName = AdminConfig.showAttribute(cluster, 'name')
  if re.search('^' + node + '$', clusterName):
    scope = '/ServerCluster:' + clusterName + '/VariableMap:/'
    variableMapID = AdminConfig.getid(scope)

    if scopeParam == 'cluster' or scopeParam == 'all':
      if actionParam == 'show':
        showVariable(scope, variableMapID)
      if actionParam == 'create':
        createVariable(scope, variableMapID)
      if actionParam == 'remove':
        removeVariable(scope, variableMapID)
      if actionParam == 'modify':
        modifyVariable(scope, variableMapID)

for nName in wasNodes:
  if re.search('^' + node + '$', nName) or re.search('^' + node + '$', dmgrNode):
    scope = '/Node:' + nName + '/VariableMap:/'
    variableMapID = AdminConfig.getid(scope)

    if scopeParam == 'node' or scopeParam == 'all':
      if actionParam == 'show':
        showVariable(scope, variableMapID)
      if actionParam == 'create':
        createVariable(scope, variableMapID)
      if actionParam == 'remove':
        removeVariable(scope, variableMapID)
      if actionParam == 'modify':
        modifyVariable(scope, variableMapID)

    if scopeParam == 'server' or scopeParam == 'all':
      nodeID = AdminConfig.getid('/Node:' + nName)
      serversEntry = AdminConfig.list('ServerEntry', nodeID).split()
      for serverEntry in serversEntry:
        # print 'SERVER ENTRY: ' + serverEntry + '\n'
        sName = AdminConfig.showAttribute(serverEntry, "serverName")
        if re.search('^' + server + '$', sName):
          scope = '/Node:' + nName + '/Server:' + sName + '/VariableMap:/'
          variableMapID = AdminConfig.getid(scope)
          # print 'SERVER ID: ' + serverID + '\n'

          if actionParam == 'show':
            showVariable(scope, variableMapID)
          if actionParam == 'create':
            createVariable(scope, variableMapID)
          if actionParam == 'remove':
            removeVariable(scope, variableMapID)
          if actionParam == 'modify':
            modifyVariable(scope, variableMapID)


### RESET / SAVE & SYNC
print '\n'
if actionParam != 'show':
  while 1:
    answer = str(raw_input('Do you want to continue and save & sync configuration to all WAS nodes? [y/n] : '))
    if re.search('^[YyNn]', answer):
      break

  if answer:
    if re.search ('^(y|Y)',answer):
      print '\n!!! SAVING & SYNCING configuration to nodes ...\n'
      AdminConfig.save()
      AdminNodeManagement.syncActiveNodes()
    else:
      print '\nCONFIG RESET ... No change to configuration was performed.\n'
      AdminConfig.reset()

print '\nDone.\n'
