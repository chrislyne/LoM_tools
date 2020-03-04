import maya.cmds as cmds
import baseIO.getProj as getProj
import datetime
import socket
import platform

def setHud():
	#set HUD with custom values
	cmds.headsUpDisplay( rp=(5, 0) )
	cmds.headsUpDisplay( rp=(6, 0) )
	cmds.headsUpDisplay( rp=(9, 0) )
	cmds.headsUpDisplay( rp=(8, 0) )
	cmds.headsUpDisplay( 'HUDUser', s=5, b=0, ba='left', dw=50,dfs='large',command=hudUser,label="Machine:",lfs='large')
	cmds.headsUpDisplay( 'HUDCameraName', s=9, b=0, ba='right', dw=50,dfs='large',command=hudFilename)
	cmds.headsUpDisplay( 'HUDFrame', s=8, b=0, ba='right', dw=50,dfs='large',pre='currentFrame',label="Frame:",lfs='large')
	cmds.headsUpDisplay( 'HUDTime', s=6, b=0, ba='left', dw=50,dfs='large',command=hudTime)

def resetHud():
	#set HUD back to how it was
	cmds.headsUpDisplay( rp=(5, 0) )
	cmds.headsUpDisplay( rp=(6, 0) )
	cmds.headsUpDisplay( rp=(9, 0) )
	cmds.headsUpDisplay( rp=(8, 0) )

	cmds.headsUpDisplay( 'HUDViewAxis', s=5, b=0, ba='left', dw=50,dfs='large',pre='viewAxis')

def hudUser():
	hostname = socket.gethostname()
	return hostname

def hudFilename():
	filename = cmds.file(q=True,sn=True,shn=True)
	return filename
	
def hudTime():
	cDate = datetime.datetime.now().strftime("%Y-%m-%d")
	cTime = datetime.datetime.now().strftime("%H:%M")
	return cDate,cTime

def getParentFolder():
	#get parent folder
	projPath = getProj.getProject()
	scenePath = cmds.file(q=True,sn=True)
	parentFolder = projPath.rsplit('/',2)[0]
	pathLen = len(projPath.split('/'))
	remainingPath = scenePath.split('/',pathLen)[-1].rsplit('/',1)[0]
	return parentFolder,remainingPath

def doPlayblast():

	parentFolder,remainingPath = getParentFolder()

	Ep = remainingPath.split('/')[0]
	Seq = remainingPath.split('/')[1]

	filename = cmds.file(q=True,sn=True,shn=True)
	filename = filename.split('.')[0]

	filePath = '%s/Previs/%s/%s'%(Ep,Seq,filename)

	if platform.system() == "Windows":
		pbformat = 'qt'
	else:
		pbformat = 'avfoundation'

	cmds.playblast(
				format=pbformat,
				filename='movies/%s'%filePath,
				sequenceTime=0,
				clearCache=1,
				viewer=1,
				showOrnaments=1,
				percent=100,
				compression="H.264",
				quality=80,
				widthHeight=[1920,1080]
				)

def setPanel(currentStateDict,renderPanel):
	#set the diplay state for playblast
	for p in currentStateDict["panel"]:
		for k in p.keys():
			#set the diplay state for playblast
			eval('cmds.modelEditor(\'%s\',e=True,%s=%s)'%(renderPanel,k,p[k]))

def setCamera(currentStateDict,renderCam):
	#set the display state back to how it was 
	for c in currentStateDict["camera"]:
		for k in c.keys():
			#set the diplay state for playblast
			cmds.setAttr('%s.%s'%(renderCam,k),c[k])

def setupDisplay():

	renderCam = ''
	renderPanel = ''
	activePanel = cmds.getPanel (withFocus = True)

	try:
		cam = cmds.modelPanel (activePanel, query = True, camera = True)
		renderCam = cmds.listRelatives(cam,type="camera")[0]
		renderPanel = activePanel
	except:
		print "Must have active model panel"

	if renderPanel:

		stateDict = {"camera": [],"panel": []}
		currentStateDict = {"camera": [],"panel": []}
		
		stateDict["camera"].append({"displayResolution":  0})
		stateDict["camera"].append({"displayFilmGate":  0})

		stateDict["panel"].append({"nurbsCurves":  0})
		stateDict["panel"].append({"deformers":  0})
		stateDict["panel"].append({"lights":  0})
		stateDict["panel"].append({"pivots":  0})
		stateDict["panel"].append({"dimensions":  0})
		stateDict["panel"].append({"locators":  0})
		stateDict["panel"].append({"dynamicConstraints":  0})
		stateDict["panel"].append({"handles":  0})
		stateDict["panel"].append({"textures":  0})
		stateDict["panel"].append({"imagePlane":  0})
		stateDict["panel"].append({"cv":  0})
		stateDict["panel"].append({"polymeshes":  1})
		stateDict["panel"].append({"sel":  0})
		stateDict["panel"].append({"manipulators":  0})
		stateDict["panel"].append({"grid":  0})
		
		#get the current display state of the camera
		for c in stateDict["camera"]:
			for k in c.keys():
				#set the diplay state for playblast
				state = cmds.getAttr('%s.%s'%(renderCam,k))
				print '%s.%s'%(renderCam,k)
				currentStateDict["camera"].append({k:  state})

		#get the current display state of the camera
		for p in stateDict["panel"]:
			for k in p.keys():
				#set the diplay state for playblast

				state = eval('cmds.modelEditor(\'%s\',q=True,%s=True)'%(renderPanel,k))
				currentStateDict["panel"].append({k:  state})

		#set viewport for playblasting
		setCamera(stateDict,renderCam)
		setPanel(stateDict,renderPanel)
		setHud()

		#do the playblast
		try:
			doPlayblast()
		except Exception as e: 
			print(e)

		#set viewport state back
		setCamera(currentStateDict,renderCam)
		setPanel(currentStateDict,renderPanel)
		resetHud()

#setupDisplay()

#import IoM_playblast
#IoM_playblast.setupDisplay()






