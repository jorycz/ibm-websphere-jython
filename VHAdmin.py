import os
import re
import sys

if len(sys.argv) < 2:
  print "\nUSAGE: script.jy <CONFIG_RESET|DANGER_CONFIG_SAVE_AND_SYNC> ACTION_PARAMS\n"
  print "EXAMPLES of ACTION_PARAMS:\n"
  print "       printAllVirtualHosts\n"
  print "       printVirtualHostAliases VH\n"
  print "       createVirtualHostWithAlias VH hostname port\n"
  print "       addVirtualHostAlias VH hostname port\n"
  print "       removeVirtualHostAlias VH hostname port\n"
  print "       removeVirtualHost VH   ### DANGER !!!\n"
  print "       checkAllVirtualHostsAndAddNewNodeIPPrefixWhenFoundOldOne 10.1.3. 10.1.13.\n"
  print "       checkAllVirtualHostsAndRemoveOldNodeIPAlias 10.1.3.   ### DANGER !!!\n"
  os._exit(1)
else:
  print "\nCONFIG   : " + sys.argv[0]
  print "\nACTION   : " + sys.argv[1]

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

print "\n"

# CREATE WHOLE VH
def createVirtualHost (virtualHostName): 
  AdminConfig.create("VirtualHost", AdminConfig.list("Cell"), [["name", virtualHostName]]) 

def createVirtualHostWithAliases (virtualHostName, aliases): 
  vh = AdminConfig.create("VirtualHost", AdminConfig.list("Cell"), [["name", virtualHostName]]) 
  for alias in aliases:
    AdminConfig.create("HostAlias", vh, [["hostname", alias[0]], ["port", alias[1]]])

# PRINT
def printAllVirtualHosts():
  for vh in AdminUtilities.convertToList(AdminConfig.list("VirtualHost")):
    print ''
    print "%s : " %(AdminConfig.showAttribute(vh, "name"))
    for alias in AdminUtilities.convertToList(AdminConfig.showAttribute(vh, 'aliases')):
      print "\t%s:%s" %(AdminConfig.showAttribute(alias, 'hostname'), AdminConfig.showAttribute(alias, 'port'))

def printVirtualHostAliases(virtualHost):
  vh = AdminConfig.getid("/VirtualHost:" + virtualHost)
  if len(vh) > 0:
    for alias in AdminUtilities.convertToList(AdminConfig.showAttribute(vh, 'aliases')):
      print "%s:%s" % (AdminConfig.showAttribute(alias, 'hostname'), AdminConfig.showAttribute(alias, 'port'))
  else:
    print "VirtualHost '%s' not found" % (vh)

# ADD ALIASES
def addVirtualHostAlias(virtualHostName, aliases):
  vh = AdminConfig.getid("/VirtualHost:" + virtualHostName)
  for alias in aliases:
    AdminConfig.create("HostAlias", vh, [["hostname", alias[0]], ["port", alias[1]]])

# REMOVE ALIAS
def removeVirtualHostAlias(virtualHostName, hostName, port):
  vh = AdminConfig.getid("/VirtualHost:" + virtualHostName)
  for alias in AdminUtilities.convertToList(AdminConfig.showAttribute(vh, 'aliases')):
    if AdminConfig.showAttribute(alias, 'hostname') == hostName:
      if AdminConfig.showAttribute(alias, 'port') == port:
        AdminConfig.remove(alias)
        print "REMOVING alias " + hostName + ":" + port + " from VirtualHost " + virtualHostName

# REMOVE WHOLE VH !
def removeVirtualHost(virtualHostName):
  vh = AdminConfig.getid("/VirtualHost:" + virtualHostName)
  if len(vh) > 0:
    print "REMOVING VirtualHost '%s'" % (vh)
    AdminConfig.remove(vh)
  else:
    print "VirtualHost '%s' not found" % (vh)

### CHECK OLD NODE IP PREFIX AND ADD NEW HOST ALIAS IF OLD NODE IP PREFIX IS FOUND
def checkAllVirtualHostsAndAddNewNodeIPPrefixWhenFoundOldOne(ipPrefixToFind, ipPrefixToAdd):
  print "\nLooking for IP prefix " + ipPrefixToFind + " and IF found, addding this IP prefix " + ipPrefixToAdd + " to same VH\n"
  for vh in AdminUtilities.convertToList(AdminConfig.list("VirtualHost")):
    print ''
    print "%s : " %(AdminConfig.showAttribute(vh, "name"))
    for alias in AdminUtilities.convertToList(AdminConfig.showAttribute(vh, 'aliases')):
      currentNode = AdminConfig.showAttribute(alias, 'hostname')
      currentPort = AdminConfig.showAttribute(alias, 'port')
      newNode = ''
      message = ''
      if re.search (ipPrefixToFind, currentNode):
        lastIPPart = splitted = currentNode.split('.')
        newNode = ipPrefixToAdd + lastIPPart[3]
        message = "   --- ADDING NEW IP ALIAS ---   " + newNode + ":" + currentPort
      if len(message) > 0:
        print "\t%s:%s %s" %(currentNode, currentPort, message)
        AdminConfig.create("HostAlias", vh, [["hostname", newNode], ["port", currentPort]])

### !!! REMOVING !!! CHECK NEW NODE IP PREFIX AND REMOVE OLD HOST ALIAS WHERE NEW NODE IP PREFIX IS FOUND
def checkAllVirtualHostsAndRemoveOldNodeIPAlias(ipPrefixToDelete):
  print "\nLooking for IP prefix " + ipPrefixToDelete + " and IF found, deleting alias with this IP prefix.\n"
  for vh in AdminUtilities.convertToList(AdminConfig.list("VirtualHost")):
    vhName = AdminConfig.showAttribute(vh, "name")
    for alias in AdminUtilities.convertToList(AdminConfig.showAttribute(vh, 'aliases')):
      currentNode = AdminConfig.showAttribute(alias, 'hostname')
      currentPort = AdminConfig.showAttribute(alias, 'port')
      message = ''
      if re.search (ipPrefixToDelete, currentNode):
        message = alias
      if len(message) > 0:
        print 'VH - ' + vhName + ' --- REMOVING IP ALIAS: ' + currentNode + ':' + currentPort
        AdminConfig.remove(alias)

if sys.argv[1] == 'printAllVirtualHosts':
  printAllVirtualHosts()

if sys.argv[1] == 'printVirtualHostAliases':
  printVirtualHostAliases(sys.argv[2])

if sys.argv[1] == 'createVirtualHostWithAlias':
  #createVirtualHostWithAliases(sys.argv[2], [['host1.com', 80], ['secure.host.com', 443]])
  createVirtualHostWithAliases(sys.argv[2], [[sys.argv[3], sys.argv[4]]])

if sys.argv[1] == 'addVirtualHostAlias':
  addVirtualHostAlias(sys.argv[2], [[sys.argv[3], sys.argv[4]]])

if sys.argv[1] == 'removeVirtualHostAlias':
  removeVirtualHostAlias(sys.argv[2], sys.argv[3], sys.argv[4])

### Remove WHOLE VH !
if sys.argv[1] == 'removeVirtualHost':
  removeVirtualHost(sys.argv[2])

### Add alias when specified IP prefix is found
if sys.argv[1] == 'checkAllVirtualHostsAndAddNewNodeIPPrefixWhenFoundOldOne':
  checkAllVirtualHostsAndAddNewNodeIPPrefixWhenFoundOldOne(sys.argv[2], sys.argv[3])

### !!! REMOVING !!! Remove IP alias when specified IP prefix is found
if sys.argv[1] == 'checkAllVirtualHostsAndRemoveOldNodeIPAlias':
  checkAllVirtualHostsAndRemoveOldNodeIPAlias(sys.argv[2])


### CONFIG RESET / SAVE & SYNC ###

if sys.argv[0] == 'DANGER_CONFIG_SAVE_AND_SYNC':
  print "\n\n!!! DANGER DANGER DANGER !!! Saving & Syncing ...\n"
  quest = question_y_n("\nDo you want to continue and save & sync configuration to all WAS nodes?\nyes/no", "yes", "no")
  if quest == "1":
    print "\n!!! SAVING & SYNCING configuration to nodes ...\n"
    AdminConfig.save()
    AdminNodeManagement.syncActiveNodes()
  if quest == "0":
    print "\n\nCONFIG RESET ... No change to configuration was performed.\n\n"
    AdminConfig.reset()
else:
  print "\n\nCONFIG RESET ... No change to configuration was performed.\n\n"
  AdminConfig.reset()

