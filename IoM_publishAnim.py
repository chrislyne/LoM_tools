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
	unityTemplateFile = '%s/Unity/Assets/Scenes/Templates/shotTemplsate.unity'%(parentFolder)
	unitySceneFile = '%s/Unity/Assets/Scenes/%s/%s.unity'%(parentFolder,remainingPath,filename.split('.')[0])
	#make folder
	folder = unitySceneFile.rsplit('/',1)[0]
	if not os.path.exists(folder):
	    os.makedirs(folder)
	#copy file
	copyfile(unityTemplateFile, unitySceneFile)

#export fbx
def exportAnimation(obj,filename):
	#select object to export
	cmds.select(obj,r=True)
	#define full file name
	ns = obj.split(':')[0]
	ns = ns.replace('|',':')
	
	refFileName  = ('%s.fbx'%(filename.rsplit('/',1)[-1].split('.')[0]))

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

	return remainingPath

def prepFile():
	#save scene
	filename = cmds.file(save=True)

	#get start and end frame
	startFrame = sceneVar.getStartFrame()
	endFrame = sceneVar.getEndFrame()

	#find the deformation system
	sel = cmds.ls(sl=True)

	rigNodes = []
	for obj in sel:
		rigNodes.append('|%s|*:DeformationSystem'%obj)

	cmds.select(rigNodes,r=True)

	#bake keys
	cmds.bakeResults(rigNodes,simulation=True,t=(startFrame,endFrame),hierarchy='below',sampleBy=1,oversamplingRate=1,disableImplicitControl=True,preserveOutsideKeys=True,sparseAnimCurveBake=False,removeBakedAttributeFromLayer=False,removeBakedAnimFromLayer=False,bakeOnOverrideLayer=False,minimizeRotation=True,controlPoints=False,shape=True)

	#start dictionary
	sceneDict = {"characters": []}

	for obj in rigNodes:
		objName = obj.split('|')[1].split(':')[-1]
		newName = '%s_%s'%(filename.rsplit('.',1)[0],objName)
		cmds.file(rename=newName)
		remainingPath = exportAnimation(obj,newName)

		#character dictionary
		charDict = {"name":  newName.split('_')[-1],"model": "Characters/%s"%obj.split(':')[0].replace('|',''),"anim": "%s/%s"%(remainingPath,newName.split('/')[-1])}
		sceneDict["characters"].append(charDict)

	#write json file
	jsonFileName  = ('%s.json'%(filename.rsplit('/',1)[-1].split('.')[0]))
	parentFolder,remainingPath = getParentFolder()
	pathName = '%s/Unity/Assets/Resources/json/%s'%(parentFolder,jsonFileName)
	with open(pathName, mode='w') as feedsjson:
		json.dump(sceneDict, feedsjson, indent=4, sort_keys=True)

	#revert to pre baked file
	cmds.file(filename,open=True,force=True,iv=True)

	#make new unity scene file
	copyUnityScene()

#prepFile()

#import IoM_publishAnim
#IoM_publishAnim.prepFile()