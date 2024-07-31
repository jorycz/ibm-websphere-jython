import re
import time
import os
import sys

if len(sys.argv) < 3:
  print "\nUSAGE: script.jy <nodename> <server> <action> (<appname>)\n"
  os._exit(1)

nodeToProcess = sys.argv[0]
serverToProcess = sys.argv[1]
action = sys.argv[2]

adminControlAction = action+'Application'
appToRestart = ''

if re.search('^(?!start|stop|restart)', action):
  print 'ERROR: Action must be start, stop or restart!'
  os._exit(1)

if len(sys.argv) > 3:
  appToRestart = sys.argv[3]
  print "\n - APP [ " + appToRestart + " ] will be processed."
else:
  print "\n - No APP was specified, looking for all apps on server ..."

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

dmgrNodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+dmgrNode)
print ' DMGR    : ' + dmgrNode + ' , ID : ' + dmgrNodeID
for web in webNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+web)
  webNodesID.append(nodeID)
  print ' WEB node: ' + web + ' , ID : ' + nodeID
for was in wasNodes:
  nodeID = AdminConfig.getid('/Cell:'+cName+'/Node:'+was)
  wasNodesID.append(nodeID)
  print ' WAS node: ' + was + ' , ID : ' + nodeID
print '=============================================='


installedAppNames = []
indexes = []

def restartApp(action,appManager,adminControlAction,appToChange):
  if re.search ('restart',action):
    adminControlAction = 'stopApplication'
    print "STOPPING : ", time.strftime('%c')
    AdminControl.invoke(appManager, adminControlAction, appToChange)
    adminControlAction = 'startApplication'
    print "STARTING : ", time.strftime('%c')
    AdminControl.invoke(appManager, adminControlAction, appToChange)
  else:
    print "Action [ " +action.upper()+ " ] invoked."
    AdminControl.invoke(appManager, adminControlAction, appToChange)

# SORT BY NODE

currentNumber = 0
restartAppFound = ''

for nName in wasNodes:
  
  if re.search(nodeToProcess, nName):
    servers = AdminControl.queryNames('type=Server,cell=' + cName + ',node=' + nName + ',*').split()
    for server in servers:
      sName = AdminControl.getAttribute(server, 'name')
      if serverToProcess == sName:
        print 'Server [ ' + sName + ' ] found on NODE [ ' + nName + ' ], installed applications: \n'
        aNames = AdminApp.list("WebSphere:cell="+cName+",node="+nName+",server="+sName).splitlines()
        for aName in aNames:
          if re.search("^(?!ibmasyncrsp).*", aName):
            installedAppNames.append(aName)
            print("[ %d ] %s" %(currentNumber,aName))
            indexes.append(str(currentNumber))
            currentNumber = int(currentNumber) + 1
            if re.search("^("+appToRestart+")$", aName):
              restartAppFound = appToRestart
            
        if len(restartAppFound) > 1:
          print "\nWorking on [ " + restartAppFound + " ] ... "
          appManager = AdminControl.queryNames('cell='+cName+',node='+nName+',type=ApplicationManager,process='+sName+',*')
          restartApp(action,appManager,adminControlAction,restartAppFound)
        else:
          appNumber = str(input('\nWhich application you wanna to ' + action.upper() + ' (choose number): '))
          if re.search ('^[0-9]',appNumber):
            if appNumber in indexes:
              appToChange = installedAppNames[int(appNumber)]
              print '\n' +action.upper()+ ' [ ' + appNumber + ' ] ' + appToChange
              appManager = AdminControl.queryNames('cell='+cName+',node='+nName+',type=ApplicationManager,process='+sName+',*')
              restartApp(action,appManager,adminControlAction,appToChange)
            else:
              print 'No application found on this position.'

print "- DONE - : ", time.strftime('%c')
print ''

