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
using UnityEditor.SceneManagement;
using UnityEngine.Rendering.PostProcessing;

public class BuildSceneBatch : EditorWindow
{
    // Helper function for getting the command line arguments
    private static string GetArg(string name)
    {
        var args = System.Environment.GetCommandLineArgs();
        for (int i = 0; i < args.Length; i++)
        {
            if (args[i] == name && args.Length > i + 1)
            {
                return args[i + 1];
            }
        }
        return null;
    }

    

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
        public List<PlayerStats> characters;
        public List<PlayerStats> extras;
        public List<PlayerStats> sets;
    }

    static void PerformBuild()
    {
        PostProcessVolume ppv;
        PostProcessProfile ppp;

        //clear out any existing timeline objects
        if (GameObject.Find("TIMELINE") != null)
        {
            DestroyImmediate(GameObject.Find("TIMELINE"));
        }
        //create new timeline
        GameObject timeline = new GameObject("TIMELINE");
        PlayableDirector director = timeline.AddComponent<PlayableDirector>();
        TimelineAsset timelineAsset = ScriptableObject.CreateInstance<TimelineAsset>();
        timelineAsset.editorSettings.fps = 25;
        director.playableAsset = timelineAsset;
        

        //load json into class
        string jsonText = File.ReadAllText(Application.dataPath + "/Resources/json/"+ GetArg("-shotName") + ".json");
        PlayerStatsList myPlayerStatsList = new PlayerStatsList();
        JsonUtility.FromJsonOverwrite(jsonText, myPlayerStatsList);

        //add abc cache to scene
        foreach (PlayerStats e in myPlayerStatsList.extras)
        {
            MyClass abcObject = new MyClass();
            abcObject.characterPath = e.abc;
            GameObject tempobj = (GameObject)Instantiate(Resources.Load(abcObject.characterPath), new Vector3(0, 0, 0), Quaternion.identity);
            tempobj.name = "extras";

            //create animation track on TIMELINE
            AlembicTrack newTrack = timelineAsset.CreateTrack<AlembicTrack>(null, tempobj.name);
            director.SetGenericBinding(newTrack, tempobj);

            AnimationClip animClip = Resources.Load<AnimationClip>(abcObject.animPath);

            TimelineClip timelineClip = newTrack.CreateDefaultClip();
            //abcObject.animPath = e.anim;
            //TrackAsset animClip = Resources.Load<TrackAsset>(tempobj);



            //newTrack.CreateClip
        }

        //add camera to scene
        foreach (PlayerStats c in myPlayerStatsList.cameras)
        {
            //place asset in scene
            MyClass myObject = new MyClass();
            myObject.cameraPath = c.model;
            GameObject tempobj = (GameObject)Instantiate(Resources.Load(myObject.cameraPath), new Vector3(0, 0, 0), Quaternion.identity);
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

            //make rim light
            myObject.rimPath = c.rimProfile;
            RimLight.createRimLight(tempobj, myObject.rimPath);

            //add post processing to camera
            myObject.profilePath = c.profile;
            if (myObject.profilePath != "")
            {
                //Set Main Camera layer to Postprocessing
                tempobj.layer = LayerMask.NameToLayer("Post-Processing");
                PostProcessLayer ppl = tempobj.AddComponent<PostProcessLayer>();
                ppl.antialiasingMode = PostProcessLayer.Antialiasing.FastApproximateAntialiasing;
                ppl.volumeLayer = 1 << LayerMask.NameToLayer("Post-Processing");
                ppv = tempobj.AddComponent<PostProcessVolume>();
                ppv.isGlobal = true;
                ppp = Resources.Load<PostProcessProfile>(myObject.profilePath);
                ppv.profile = ppp;
            }
        }

        //loop through objects in class
        foreach (PlayerStats p in myPlayerStatsList.characters)
        {
            //place asset in scene
            MyClass myObject = new MyClass();
            myObject.characterPath = p.model;
            GameObject tempobj = (GameObject)Instantiate(Resources.Load(myObject.characterPath), new Vector3(0, 0, 0), Quaternion.identity);
            tempobj.name = p.name;
            //set objects to "Characters" layer
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
            GameObject tempobj = (GameObject)Instantiate(Resources.Load(myObject.setPath), new Vector3(0, 0, 0), Quaternion.identity);
            tempobj.name = s.name;
        }
        //add post processing to camera
        /*
        GameObject cam = GameObject.Find("CAM");
        if (cam != null)
        {
            cam.AddComponent<PostProcessLayer>();
            ppv = cam.AddComponent<PostProcessVolume>();
            ppp = Resources.Load<PostProcessProfile>("Profiles/MainCameraProfile1");
            ppv.profile = ppp;
        }
        else
        {
            Debug.LogWarning("No Camera found. The camera must be named - CAM");
        }
        */
        //save scene
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), GetArg("-scenePath"));
    }

}
