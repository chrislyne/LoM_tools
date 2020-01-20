import maya.cmds as cmds
import baseIO.sceneVar as sceneVar
import baseIO.getProj as getProj
import maya.mel as mel
import os

#export fbx
def exportAnimation(obj,filename):
	#select object to export
	cmds.select(obj,r=True)
	#define full file name
	ns = obj.split(':')[0]
	ns = ns.replace('|',':')
	
	refFileName  = ('%s.fbx'%(filename.rsplit('/',1)[-1].split('.')[0]))

	#get parent folder
	projPath = getProj.getProject()
	scenePath = cmds.file(q=True,sn=True)
	parentFolder = projPath.rsplit('/',2)[0]
	pathLen = len(projPath.split('/'))
	remainingPath = scenePath.split('/',pathLen)[-1].rsplit('/',1)[0]

	#output name
	pathName = '%s/Unity/Assets/%s/%s'%(parentFolder,remainingPath,refFileName)
	
	#make folder if it doesn't exist
	if not os.path.exists(pathName.rsplit('/',1)[0]):
		os.makedirs(pathName.rsplit('/',1)[0])
	
	#load fbx presets from file
	mel.eval("FBXLoadExportPresetFile -f \"%s/data/IoM_animExport.fbxexportpreset\";"%projPath)

	
	cmds.file(pathName,force=True,type='FBX export',relativeNamespace=ns,es=True)

def prepFile():
	#save scene
	filename = cmds.file(save=True)
	#cmds.file(rename=newName)
	#cmds.file(save=True)

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

	for obj in rigNodes:
		objName = obj.split('|')[1].split(':')[-1]
		newName = '%s_%s'%(filename.rsplit('.',1)[0],objName)
		cmds.file(rename=newName)
		exportAnimation(obj,newName)
	#revert to pre baked file
	cmds.file(filename,open=True,force=True,iv=True)

#prepFile()

#import IoM_publishAnim
#IoM_publishAnim.prepFile()