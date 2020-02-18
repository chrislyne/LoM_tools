import maya.cmds as cmds
import baseIO.sceneVar as sceneVar
import baseIO.getProj as getProj
import maya.mel as mel
import os
import baseIO.loadSave as IO
from shutil import copyfile
import json

def getParentFolder():
	#get parent folder
	projPath = getProj.getProject()
	scenePath = cmds.file(q=True,sn=True)
	parentFolder = projPath.rsplit('/',2)[0]
	pathLen = len(projPath.split('/'))
	remainingPath = scenePath.split('/',pathLen)[-1].rsplit('/',1)[0]
	return parentFolder,remainingPath

def copyUnityScene():
	#get file/folder path
	parentFolder,remainingPath = getParentFolder()
	filename = cmds.file(q=True,sn=True,shn=True)
	#paths
	unityTemplateFile = '%s/Unity/Assets/Scenes/Templates/shotTemplate.unity'%(parentFolder)
	unitySceneFile = '%s/Unity/Assets/Scenes/%s/%s.unity'%(parentFolder,remainingPath,filename.split('.')[0])
	#make folder
	folder = unitySceneFile.rsplit('/',1)[0]
	if not os.path.exists(folder):
	    os.makedirs(folder)
	#copy file
	copyfile(unityTemplateFile, unitySceneFile)

#export fbx
def exportAnimation(obj):
	#rename file temporarily
	filename = cmds.file(q=True,sn=True)
	try:
		objName = obj.split('|')[1].split(':')[-1]
	except:
		objName = obj.split('|')[-1].split(':')[-1]
	newName = '%s_%s'%(filename.rsplit('.',1)[0],objName)
	cmds.file(rename=newName)

	#select object to export
	cmds.select(obj,r=True)
	#define full file name
	if ':' in obj:
		ns = obj.split(':')[0]
		ns = ns.replace('|',':')
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

	cmds.file(rename=filename)

	return newName,remainingPath


def prepFile():
	#save scene
	filename = cmds.file(save=True)

	#get start and end frame
	startFrame = sceneVar.getStartFrame()
	endFrame = sceneVar.getEndFrame()

	#find the deformation system
	sel = []
	checkBoxes = cmds.columnLayout('boxLayout',ca=True,q=True)
	for c in checkBoxes:
		if cmds.checkBox(c,v=True, q=True):
			print cmds.checkBox(c,label=True, q=True) 
			sel.append(cmds.checkBox(c,label=True, q=True) )
	#sel = cmds.ls(sl=True)

	rigNodes = []
	for obj in sel:
		rigNodes.append('|%s|*:DeformationSystem'%obj)

	cameraName = cmds.optionMenu('cameraSelection',q=True,v=True)
	rigNodes.append('|%s'%cameraName)

	cmds.select(rigNodes,r=True)

	#bake keys
	cmds.bakeResults(rigNodes,simulation=True,t=(startFrame,endFrame),hierarchy='below',sampleBy=1,oversamplingRate=1,disableImplicitControl=True,preserveOutsideKeys=True,sparseAnimCurveBake=False,removeBakedAttributeFromLayer=False,removeBakedAnimFromLayer=False,bakeOnOverrideLayer=False,minimizeRotation=True,controlPoints=False,shape=True)

	#start dictionary
	sceneDict = {"characters": []}

	#publishCamera()

	for obj in rigNodes:
		newName,remainingPath = exportAnimation(obj)

		#character dictionary
		try:
			objParent = cmds.listRelatives( obj, parent=True )
			publishName = cmds.getAttr('%s.publishName'%objParent[0])
			publishName = "Characters/%s"%publishName
		except:
			publishName = "%s/%s"%(remainingPath,newName.split('/')[-1])
		charDict = {"name":  newName.split('_')[-1],"model": publishName,"anim": "%s/%s"%(remainingPath,newName.split('/')[-1])}
		sceneDict["characters"].append(charDict)

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

#create file name for export camera
def makeCameraName():
    filename = cmds.file(q=True,sn=True,shn=True).split('.')[0]
    camFileName = filename+'_CAMERA'
    return camFileName


#update name and run
def runWithUI():
    selectionCamera = cmds.optionMenu('cameraSelection',q=True,v=True)
    #check if a camera is selected and run
    if selectionCamera != '':
        publishCamera()
    else:
        cmds.error( 'no valid camera in scene')

###        UI        ###

def IoM_exportAnim_window():

    #find all published objects by searching for the 'publishName' attribute

    publishedAssets = []
    allTransforms = cmds.ls(transforms=True)
    for t in allTransforms:
        if cmds.attributeQuery( 'publishName', node=t, exists=True):
            publishedAssets.append(t)

    exportForm = cmds.formLayout()
    cameraLabel = cmds.text('cameraLabel',label='Camera')
    
    allCameras = listAllCameras()
    cameraSelection = cmds.optionMenu('cameraSelection')
    for cam in allCameras:
        cmds.menuItem(l=cam)

    boxLayout = cmds.columnLayout('boxLayout',columnAttach=('both', 5), rowSpacing=10, columnWidth=250 )
    for asset in publishedAssets:
    	cmds.checkBox( label=asset, v=True)
    
    cmds.setParent( '..' )
    
    Button1 = cmds.button('Button1',l='Publish',h=50,c='prepFile()')
    Button2 = cmds.button('Button2',l='Close',h=50,c='cmds.deleteUI(\'Publish Camera\')') 
             
    cmds.formLayout(
        exportForm,
        edit=True,
        attachForm=[
        (cameraLabel,'top',20),
        (cameraSelection,'top',15),
        (cameraSelection,'right',10),
        (cameraLabel,'left',10),
        (cameraSelection,'right',10),
        (Button1,'bottom',0),
        (Button1,'left',0),
        (Button2,'bottom',0),
        (Button2,'right',0)
        ],
        attachControl=[
        (cameraSelection,'left',40,cameraLabel),
        (boxLayout,'top',20,cameraLabel),
        (boxLayout,'left',40,cameraLabel),
        (Button2,'left',0,Button1)
        ],
        attachPosition=[
        (Button1,'right',0,50)
        ])

    exportForm
    
    #get filename
    filename = makeCameraName()

def IoM_exportAnim():

    workspaceName = 'Publish Camera'
    if(cmds.workspaceControl(workspaceName, exists=True)):
        cmds.deleteUI(workspaceName)
    cmds.workspaceControl(workspaceName,initialHeight=100,initialWidth=300,uiScript = 'IoM_exportAnim_window()')

#IoM_exportAnim()
#prepFile()

#import IoM_publishAnim
#IoM_publishAnim.prepFile()