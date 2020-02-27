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
        public string profilePath;
        public string rimPath;
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
        public string rimProfile;
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
        GUILayout.BeginHorizontal("box");
        source = EditorGUILayout.ObjectField(source, typeof(TextAsset), true);

        if (GUILayout.Button("Scene Name", GUILayout.Width(100)))
        {
            //get name of scene
            Scene scene = SceneManager.GetActiveScene();
            //look for corresponding json file
            var jsonFile = Resources.Load<UnityEngine.Object>("JSON/" + scene.name);
            //set object feild text asset to use json file
            source = EditorGUILayout.ObjectField(jsonFile, typeof(TextAsset), true);
        }

        GUILayout.EndHorizontal();
        if (GUILayout.Button("Add to scene", GUILayout.Height(60)))
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
            timelineAsset.editorSettings.fps = 25;
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

                //add post processing to camera
                GameObject cam = tempobj;

                //make rim light
                myObject.rimPath = c.rimProfile;
                RimLight.createRimLight(tempobj, myObject.rimPath);


                myObject.profilePath = c.profile;
                //add post processing
                PostProcessing.addPostProcessing(cam, myObject.profilePath);
                /*
                if (myObject.profilePath != "")
                {
                    //Set Main Camera layer to Postprocessing
                    cam.layer = LayerMask.NameToLayer("Post-Processing");
                    PostProcessLayer ppl = cam.AddComponent<PostProcessLayer>();
                    
                    ppl.antialiasingMode = PostProcessLayer.Antialiasing.FastApproximateAntialiasing;
                    ppl.volumeLayer = 1 << LayerMask.NameToLayer("Post-Processing");
                    PostProcessVolume ppv = cam.AddComponent<PostProcessVolume>();
                    ppv.isGlobal = true;
                    var ppp = Resources.Load<PostProcessProfile>(myObject.profilePath);
                    
                    ppv.profile = ppp;
                }*/
            }

            //add characters and props to scene
            foreach (PlayerStats p in myPlayerStatsList.characters)
            {
                //place asset in scene
                MyClass myObject = new MyClass();
                myObject.characterPath = p.model;
                tempobj = (GameObject)Instantiate(Resources.Load(myObject.characterPath), new Vector3(0, 0, 0), Quaternion.identity);
                tempobj.name = p.name;

                foreach (Transform trans in tempobj.GetComponentsInChildren<Transform>(true))
                {
                    trans.gameObject.layer = LayerMask.NameToLayer("Characters");
                }


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
            
            
            //EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), "C:/Users/Chris/Dropbox/Jobs/LoM_Production/Unity/Assets/Scenes/dev/saveTest2.unity");
        }
        if (GUILayout.Button("Add Post Effects"))
        {
            GameObject cam = GameObject.Find("CAM");
            if (cam != null)
            {
                MyClass myObject = new MyClass();
                string jsonText = File.ReadAllText(Application.dataPath + "/Resources/json/" + source.name + ".json");
                PlayerStatsList myPlayerStatsList = new PlayerStatsList();
                JsonUtility.FromJsonOverwrite(jsonText, myPlayerStatsList);
                PlayerStats c = myPlayerStatsList.cameras[0];
                myObject.profilePath = c.profile;
                PostProcessVolume ppv;
                var ppp = Resources.Load<PostProcessProfile>(myObject.profilePath);
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

    }
}