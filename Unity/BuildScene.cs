using UnityEngine;
using System.Collections;
using UnityEditor;
using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine.Playables;
using UnityEngine.Timeline;
using UnityEngine.Formats.Alembic.Timeline;
using UnityEditor.Recorder.Timeline;
using UnityEngine.Rendering.PostProcessing;
using UnityEngine.SceneManagement;


public class BuildScene : EditorWindow
{
    [Serializable]
    public class MyClass
    {
        public string cameraPath;
        public string characterPath;
        public string animPath;
        public string setPath;
    }

    GameObject tempobj = null;
    GameObject abcobj = null;
    //public GameObject timeline;
    public UnityEngine.Object source;


    [Serializable]
    public class PlayerStats
    {
        public string name;
        public string model;
        public string anim;
        public string abc;
        public string profile;
    }

    public class PlayerStatsList
    {
        public List<PlayerStats> cameras;
        public List <PlayerStats> characters;
        public List<PlayerStats> extras;
        public List<PlayerStats> sets;
    }

    [MenuItem("IoM/Build Scene")]
    static void ShowWindow()
    {
        EditorWindow.GetWindow(typeof(BuildScene));
    }

    void OnInspectorUpdate()
    {
        Repaint();
    }

    void OnGUI()
    {   
        
        //set window title
        this.titleContent = new GUIContent("IoM - Build Scene");
        //object field
        source = EditorGUILayout.ObjectField(source, typeof(TextAsset), true);

        if (GUILayout.Button("Add to scene"))
        {
            //clear out any existing timeline objects
            if (GameObject.Find("TIMELINE") != null)
            {
                DestroyImmediate(GameObject.Find("TIMELINE"));
            }
            //create new timeline
            GameObject timeline = new GameObject("TIMELINE");
            PlayableDirector director = timeline.AddComponent<PlayableDirector>();
            TimelineAsset timelineAsset = CreateInstance<TimelineAsset>();
            director.playableAsset = timelineAsset;

            //load json into class
            string jsonText = File.ReadAllText(Application.dataPath + "/Resources/json/" + source.name + ".json");
            PlayerStatsList myPlayerStatsList = new PlayerStatsList();
            JsonUtility.FromJsonOverwrite(jsonText, myPlayerStatsList);

            //add abc cache to scene
            foreach (PlayerStats e in myPlayerStatsList.extras)
            {
                MyClass abcObject = new MyClass();
                abcObject.characterPath = e.abc;
                Debug.Log(abcObject.characterPath);
                //UnityEngine.Object abcObj = Resources.Load(abcObject.characterPath);
                abcobj = (GameObject)Instantiate(Resources.Load(abcObject.characterPath), new Vector3(0, 0, 0), Quaternion.identity);
                abcobj.name = "extras";

                
                //create animation track on TIMELINE
                AlembicTrack newTrack = timelineAsset.CreateTrack<AlembicTrack>(null, abcobj.name);
                director.SetGenericBinding(newTrack, abcobj);
                //abcObject.animPath = e.anim;
                AnimationClip animClip = Resources.Load<AnimationClip>(abcObject.animPath);

                TimelineClip timelineClip = newTrack.CreateDefaultClip();
                //var abcPlayableAsset = (PlayableAsset)timelineClip.asset;
                //abcPlayableAsset.

                //TrackAsset timelineClip.CreateDefaultClip();


            }

            //add camera to scene
            foreach (PlayerStats c in myPlayerStatsList.cameras)
            {
                //place asset in scene
                MyClass myObject = new MyClass();
                myObject.cameraPath = c.model;
                tempobj = (GameObject)Instantiate(Resources.Load(myObject.cameraPath), new Vector3(0, 0, 0), Quaternion.identity);
                tempobj.name = c.name;

                //create animation track on TIMELINE

                AnimationTrack newTrack = timelineAsset.CreateTrack<AnimationTrack>(null, "Animation Track " + tempobj.name);
                director.SetGenericBinding(newTrack, tempobj);
                myObject.animPath = c.anim;
                AnimationClip animClip = Resources.Load<AnimationClip>(myObject.animPath);

                TimelineClip timelineClip = newTrack.CreateClip(animClip);
                //Turn remove start offset off to fix camera position
                var animPlayableAsset = (AnimationPlayableAsset)timelineClip.asset;
                animPlayableAsset.removeStartOffset = false;

            }

            //loop through objects in class
            foreach (PlayerStats p in myPlayerStatsList.characters)
            {
                //place asset in scene
                MyClass myObject = new MyClass();
                myObject.characterPath = p.model;
                tempobj = (GameObject)Instantiate(Resources.Load(myObject.characterPath), new Vector3(0, 0, 0), Quaternion.identity);
                tempobj.name = p.name;

                //create animation track on TIMELINE

                AnimationTrack newTrack = timelineAsset.CreateTrack<AnimationTrack>(null, "Animation Track " + tempobj.name);
                director.SetGenericBinding(newTrack, tempobj);
                myObject.animPath = p.anim;
                AnimationClip animClip = Resources.Load<AnimationClip>(myObject.animPath);

                TimelineClip timelineClip = newTrack.CreateClip(animClip);
                //Turn remove start offset off to fix camera position
                var animPlayableAsset = (AnimationPlayableAsset)timelineClip.asset;
                animPlayableAsset.removeStartOffset = false;

            }
            //add sets to scene
            foreach (PlayerStats s in myPlayerStatsList.sets)
            {
                //place asset in scene
                MyClass myObject = new MyClass();
                myObject.setPath = s.model;
                tempobj = (GameObject)Instantiate(Resources.Load(myObject.setPath), new Vector3(0, 0, 0), Quaternion.identity);
                tempobj.name = s.name;
            }
            //add post processing to camera
            GameObject cam = GameObject.Find("CAM");
            if (cam != null)
            {
                cam.AddComponent<PostProcessLayer>();
                PostProcessVolume ppv = cam.AddComponent<PostProcessVolume>();
                var ppp = Resources.Load<PostProcessProfile>("Profiles/MainCameraProfile1");
                Debug.Log("foobar" + ppp);
                ppv.profile = ppp;
            }
            else
            {
                Debug.LogWarning("No Camera found. The camera must be named - CAM");
            }
            
            //EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), "C:/Users/Chris/Dropbox/Jobs/LoM_Production/Unity/Assets/Scenes/dev/saveTest2.unity");
        }
        if (GUILayout.Button("Add Post Effects"))
        {
            GameObject cam = GameObject.Find("CAM");
            if (cam != null)
            {
                PostProcessVolume ppv;
                var ppp = Resources.Load<PostProcessProfile>("Profiles/MainCameraProfile1");
                if (cam.GetComponent(typeof(PostProcessVolume)) == null)
                {
                    cam.AddComponent<PostProcessLayer>();
                    ppv = cam.AddComponent<PostProcessVolume>();
                }
                else
                {
                    ppv = cam.GetComponent<PostProcessVolume>();
                }
                ppv.profile = ppp;
            }
            else
            {
                Debug.LogWarning("No Camera found. The camera must be named - CAM");
            }
        }
        if (GUILayout.Button("Get Scene Name"))
        {
            //get name of scene
            Scene scene = SceneManager.GetActiveScene();
            //look for corresponding json file
            var jsonFile = Resources.Load<UnityEngine.Object>("JSON/"+scene.name);
            //set object feild text asset to use json file
            source = EditorGUILayout.ObjectField(jsonFile, typeof(TextAsset), true);
        }

    }
}