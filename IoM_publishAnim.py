import maya.cmds as cmds
import baseIO.sceneVar as sceneVar
import baseIO.getProj as getProj
import maya.mel as mel
import os
import baseIO.loadSave as IO
from shutil import copyfile
import json
import platform
import subprocess

def disableMenu():
	checkValue = cmds.checkBox('unityCheck',v=True,q=True)
	cmds.optionMenu('versionSelection',e=True,en=checkValue)


def preferedUnityVersion():
    projPath = getProj.getProject()
    settingsFile = '%sdata/projectSettings.json'%(projPath)
    with open(settingsFile) as json_data:
        data = json.load(json_data)
        json_data.close()
        return (data['unity']['preferedVersion'])

def getUnityVersions():
	try:
		#list all versions of Unity on the system
		versions = []
		#define install path based on the operating system
		if platform.system() == "Windows":
			myPath = "C:/Program Files/Unity/Hub/Editor"
		else:
			myPath = "/Applications/Unity/Hub/Editor"
		#filter out unnecessary folders 
		for f in os.listdir(myPath):
			if f[0] != '.':
				#build new list
				versions.append(f)
	except:
		pass
	return versions
		

def exportAsAlembic(abcFilename):

	#get file/folder path
	parentFolder,remainingPath = getParentFolder()

	#get workspace
	workspace = cmds.workspace( q=True, directory=True, rd=True)
	workspaceLen = len(workspace.split('/'))
	#get filename
	filename = cmds.file(q=True,sn=True)
	#get relative path (from scenes)
	relativePath = ''
	for dir in filename.split('/')[workspaceLen:-1]:
		relativePath += '%s/'%(dir)

	#string of objects to export
	exportString = ''
	returnString = ''
	sel = cmds.textScrollList('extrasList',q=True,allItems=True)
	if sel:
		for item in sel:
			exportString += ' -root %s'%(item)

		#get timeline
		startFrame = int(cmds.playbackOptions(q=True,minTime=True))
		endFrame = int(cmds.playbackOptions(q=True,maxTime=True))

		#set folder to export to  
		folderPath = '%s/Unity/Assets/Resources/%s'%(parentFolder,remainingPath)
		if not os.path.exists(folderPath):
			os.makedirs(folderPath)

		#check if plugin is already loaded
		if not cmds.pluginInfo('AbcImport',query=True,loaded=True):
			try:
				#load abcExport plugin
				cmds.loadPlugin( 'AbcImport' )
			except: 
				cmds.error('Could not load AbcImport plugin')

		#export .abc
		command = '-frameRange %d %d -uvWrite -writeVisibility -wholeFrameGeo -worldSpace -writeUVSets -dataFormat ogawa%s -file \"%s/%s_cache.abc\"'%(startFrame,endFrame,exportString,folderPath,abcFilename)
		#load plugin
		if not cmds.pluginInfo('AbcExport',query=True,loaded=True):
			try:
				#load abcExport plugin
				cmds.loadPlugin( 'AbcExport' )
			except: cmds.error('Could not load AbcExport plugin')
		#write to disk
		cmds.AbcExport ( j=command )

		returnString = "%s/%s_cache"%(remainingPath,abcFilename)
	
	return returnString

def getParentFolder():
	#get parent folder
	projPath = getProj.getProject()
	scenePath = cmds.file(q=True,sn=True)
	parentFolder = projPath.rsplit('/',2)[0]
	pathLen = len(projPath.split('/'))
	remainingPath = scenePath.split('/',pathLen)[-1].rsplit('/',1)[0]
	return parentFolder,remainingPath

def copyUnityScene():
	#get version of Unity from selection menu
	unityVersion = cmds.optionMenu('versionSelection',v=True,q=True)
	#check if checkBox is checked and a Unity version exists
	if cmds.checkBox('unityCheck',v=True,q=True) and len(unityVersion) > 0:
		#get file/folder path
		parentFolder,remainingPath = getParentFolder()
		filename = cmds.file(q=True,sn=True,shn=True)
		#paths
		unityTemplateFile = '%s/Unity/Assets/Scenes/Templates/shotTemplate.unity'%(parentFolder)
		unitySceneFile = '%s/Unity/Assets/Scenes/%s/%s.unity'%(parentFolder,remainingPath,filename.split('.')[0])
		#make folder
		print "parentFolder = %s/Unity"%parentFolder
		print "remainingPath = Assets/Scenes/%s/%s.unity"%(remainingPath,filename.split('.')[0])
		print "filename.split('.')[0] = %s"%filename.split('.')[0]
		folder = unitySceneFile.rsplit('/',1)[0]
		if not os.path.exists(folder):
			os.makedirs(folder)
		
		#make Unity Scene File
		try:
			projectPath = "%s/Unity"%parentFolder
			scenePath = "Assets/Scenes/%s/%s.unity"%(remainingPath,filename.split('.')[0])
			shotName = "%s"%filename.split('.')[0]
			if platform.system() == "Windows":
				subprocess.check_output('\"C:/Program Files/Unity/Hub/Editor/%s/Editor/Unity.exe\" -quit -batchmode -projectPath \"%s\" -executeMethod BuildSceneBatch.PerformBuild -shotName \"%s\" -scenePath \"%s\" '%(unityVersion,projectPath,shotName,scenePath))
			else:
				subprocess.check_output('/Applications/Unity/Hub/Editor/%s/Unity.app/Contents/MacOS/Unity -quit -batchmode -projectPath %s -executeMethod BuildSceneBatch.PerformBuild -shotName \"%s\" -scenePath \"%s\" '%(unityVersion,projectPath,shotName,scenePath),shell=True)
		except:
			print "Unable to populate Unity scene file"
			#copy blank Unity scene if auto population fails
			try:
				copyfile(unityTemplateFile, unitySceneFile)
			except:
				print "no Unity scene file created"
		


#export fbx
def exportAnimation(obj):
	#rename file temporarily
	filename = cmds.file(q=True,sn=True)
	objName = obj.split('|')[-1].split(':')[-1]
	newName = '%s_%s'%(filename.rsplit('.',1)[0],objName)
	cmds.file(rename=newName)
	#move object to the root and redefine as itself if it's not already
	try:
		obj = cmds.parent(obj,w=True)[0]
	except:
		pass

	#select object to export
	try:
		exportObject = '%s|*:DeformationSystem'%(obj)
		cmds.select(exportObject,r=True)
	except:
		exportObject = obj
		cmds.select(exportObject,r=True)
	#define full file name
	if ':' in exportObject:
		ns = exportObject.split(':',1)[0]
		ns = ns.split('|')[-1]
		ns = ':%s'%ns
	else:
		ns = ':'
	refFileName  = ('%s.fbx'%(newName.rsplit('/',1)[-1].split('.')[0]))

	#output name
	parentFolder,remainingPath = getParentFolder()
	pathName = '%s/Unity/Assets/Resources/%s/%s'%(parentFolder,remainingPath,refFileName)
	#make folder if it doesn't exist
	if not os.path.exists(pathName.rsplit('/',1)[0]):
		os.makedirs(pathName.rsplit('/',1)[0])
	
	#load fbx presets from file
	mel.eval("FBXLoadExportPresetFile -f \"%s/data/IoM_animExport.fbxexportpreset\";"%getProj.getProject())
	#export fbx
	cmds.file(pathName,force=True,type='FBX export',relativeNamespace=ns,es=True)
	#restore the filename
	cmds.file(rename=filename)

	return obj,newName,remainingPath


def prepFile(assetObject):
	#save scene
	filename = cmds.file(save=True)

	#get start and end frame
	startFrame = sceneVar.getStartFrame()
	endFrame = sceneVar.getEndFrame()

	#add objects to selection if if they are checked
	sel = []
	checkBoxes = cmds.columnLayout('boxLayout',ca=True,q=True)
	for i,c in enumerate(checkBoxes):
		if cmds.checkBox(c,v=True, q=True):
			sel.append(assetObject[i])

	#add scene camera to export list
	cameraName = cmds.optionMenu('cameraSelection',q=True,v=True)
	if cameraName:
		sel.append('|%s'%cameraName)

	#bake keys
	cmds.bakeResults(sel,simulation=True,t=(startFrame,endFrame),hierarchy='below',sampleBy=1,oversamplingRate=1,disableImplicitControl=True,preserveOutsideKeys=True,sparseAnimCurveBake=False,removeBakedAttributeFromLayer=False,removeBakedAnimFromLayer=False,bakeOnOverrideLayer=False,minimizeRotation=True,controlPoints=False,shape=True)

	#start dictionary
	sceneDict = {"characters": [],"extras": []}
	#export animation one object at a time
	for obj in sel:
		#do the export
		obj,newName,remainingPath = exportAnimation(obj)
		#make character dictionary
		try:
			#get REF filename
			publishName = cmds.getAttr('%s.publishName'%obj)
			#get asset type from parent folder
			refPath = cmds.referenceQuery( obj,filename=True )
			assetType = os.path.split(os.path.dirname(refPath))[1]
			publishName = "%s/%s"%(assetType,publishName)
		except:
			#make a name if publishName attribute doesn't exist
			publishName = "%s/%s"%(remainingPath,newName.split('/')[-1])
		#format json
		charDict = {"name":  newName.split('_')[-1],"model": publishName,"anim": "%s/%s"%(remainingPath,newName.split('/')[-1])}
		sceneDict["characters"].append(charDict)

	#export as alembic
	abcPath = exportAsAlembic(filename.rsplit('/',1)[-1].split('.')[0])

	if len(abcPath) > 0:
		extraDict = {"name":  "extras","abc": abcPath}
		sceneDict["extras"].append(extraDict)

	#write json file
	jsonFileName  = ('%s.json'%(filename.rsplit('/',1)[-1].split('.')[0]))
	parentFolder,remainingPath = getParentFolder()
	pathName = '%s/Unity/Assets/Resources/json/%s'%(parentFolder,jsonFileName)
	with open(pathName, mode='w') as feedsjson:
		json.dump(sceneDict, feedsjson, indent=4, sort_keys=True)

	
	#revert to pre baked file
	try:
		cmds.file(filename,open=True,force=True,iv=True)
	except:
		pass

	#make new unity scene file
	copyUnityScene()

#list cameras
def listAllCameras():
	listAllCameras = cmds.listCameras(p=True)
	#remove 'persp' camera
	if 'persp' in listAllCameras: listAllCameras.remove('persp')
	return listAllCameras

def addObjectsToScrollList():
	#list selected objects
	sel = cmds.ls(sl=True)
	existing = cmds.textScrollList('extrasList',q=True,allItems=True)
	if existing:
		for text in existing:
			cmds.textScrollList('extrasList',e=True,removeItem=text)
		sel += existing
		sel = list(set(sel))
	
	cmds.textScrollList('extrasList',e=True,append=sel)
	
def removeObjectsFromScrollList():
	#list selected objects
	sel = cmds.textScrollList('extrasList',q=True,selectItem=True)
	for text in sel:
		cmds.textScrollList('extrasList',e=True,removeItem=text)


###		UI		###
def IoM_exportAnim_window():

	#find all published objects by searching for the 'publishName' attribute

	publishedAssets = []
	allTransforms = cmds.ls(transforms=True,l=True)
	for t in allTransforms:
		t=t[1:]
		if cmds.attributeQuery( 'publishName', node=t, exists=True):
			publishedAssets.append(t)

	exportForm = cmds.formLayout()
	#Camera selection
	cameraLabel = cmds.text('cameraLabel',label='Camera',w=40,al='left')
	allCameras = listAllCameras()
	cameraSelection = cmds.optionMenu('cameraSelection')
	for cam in allCameras:
		cmds.menuItem(l=cam)
	assetsLabel = cmds.text('assetsLabel',label='Assets',w=40,al='left')
	sep1 = cmds.separator("sep1",height=4, style='in' )
	#Asset export
	publishedAsset = []
	boxLayout = cmds.columnLayout('boxLayout',columnAttach=('both', 5), rowSpacing=10, columnWidth=250 )
	for asset in publishedAssets:
		publishedAsset.append(asset)
		cmds.checkBox( label=asset.split(':')[-1], annotation=asset,v=True)
	cmds.setParent( '..' )
	#Extras input
	sep2 = cmds.separator("sep2",height=4, style='in' )
	extrasLabel = cmds.text('extrasLabel',label='Extras',w=40,al='left')
	extrasList = cmds.textScrollList('extrasList',numberOfRows=8, allowMultiSelection=True,height=102)
	addButton = cmds.button('addButton',l='Add',h=50,w=50,c='addObjectsToScrollList()')
	removeButton = cmds.button('removeButton',l='Remove',h=50,w=50,c='removeObjectsFromScrollList()')
	#Unity export
	sep3 = cmds.separator("sep3",height=4, style='in' )
	versionLabel = cmds.text('versionLabel',label='Unity',w=40,al='left')
	versionSelection = cmds.optionMenu('versionSelection')
	versions = getUnityVersions()
	for v in versions:
		cmds.menuItem(l=v)
	preferedVersion = preferedUnityVersion()
	try:
		cmds.optionMenu('versionSelection',v=preferedVersion,e=True)
	except:
		pass
	unityCheck = cmds.checkBox('unityCheck',l="",annotation="Generate Unity scene file",v=True,cc='disableMenu()')
	#Main buttons
	Button1 = cmds.button('Button1',l='Publish',h=50,c='prepFile(%s)'%publishedAsset)
	Button2 = cmds.button('Button2',l='Close',h=50,c='cmds.deleteUI(\'Publish Animation\')') 
			 
	cmds.formLayout(
		exportForm,
		edit=True,
		attachForm=[
		(cameraLabel,'top',20),
		(cameraSelection,'top',15),
		(cameraSelection,'right',10),
		(cameraLabel,'left',10),
		(cameraSelection,'right',10),
		(sep1,'right',10),
		(sep1,'left',10),
		(assetsLabel,'left',10),
		(extrasLabel,'left',10),
		(extrasList,'left',10),
		(addButton,'right',10),
		(removeButton,'right',10),
		(sep2,'right',10),
		(sep2,'left',10),
		(sep3,'right',10),
		(sep3,'left',10),
		(versionLabel,'left',10),
		(versionSelection,'right',10),
		(Button1,'bottom',0),
		(Button1,'left',0),
		(Button2,'bottom',0),
		(Button2,'right',0)
		],
		attachControl=[
		(cameraSelection,'left',40,cameraLabel),
		(sep1,'top',20,cameraLabel),
		(assetsLabel,'top',40,cameraLabel),
		(boxLayout,'top',40,cameraLabel),
		(boxLayout,'left',40,cameraLabel),
		(sep2,'top',20,boxLayout),
		(extrasLabel,'top',40,boxLayout),
		(extrasList,'top',40,boxLayout),
		(extrasList,'right',10,addButton),
		(extrasList,'left',40,cameraLabel),
		(extrasList,'bottom',10,sep3),
		(addButton,'top',40,boxLayout),
		(removeButton,'top',2,addButton),
		(sep3,'bottom',20,versionSelection),
		(versionLabel,'bottom',24,Button1),
		(unityCheck,'left',40,versionLabel),
		(versionSelection,'bottom',20,Button1),
		(versionSelection,'left',10,unityCheck),
		(unityCheck,'bottom',24,Button1),
		(Button2,'left',0,Button1)
		],
		attachPosition=[
		(Button1,'right',0,50)
		])

	exportForm

def IoM_exportAnim():

	workspaceName = 'Publish Animation'
	if(cmds.workspaceControl(workspaceName, exists=True)):
		cmds.deleteUI(workspaceName)
	cmds.workspaceControl(workspaceName,initialHeight=100,initialWidth=300,uiScript = 'IoM_exportAnim_window()')

#IoM_exportAnim()
