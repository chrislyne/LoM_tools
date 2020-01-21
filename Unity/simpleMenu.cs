using UnityEngine;
using System.Collections;
using UnityEditor;
using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine.Playables;
using UnityEngine.Timeline;


public class BuildScene : EditorWindow
{
    [Serializable]
    public class MyClass
    {
        public string characterPath;
        public string animPath;
    }

    GameObject tempobj = null;
    UnityEngine.Object animObject = null;
    public GameObject timeline;
    string jsonPath = "testScene01";
    public UnityEngine.Object source;

    [Serializable]
    public class PlayerStats
    {
        public string name;
        public string model;
        public string anim;
    }

    [Serializable]
    public class PlayerStatsList
    {

        public List <PlayerStats> characters;
    }

    [MenuItem("IoM/Build Scene")]
    static void ShowWindow()
    {
        EditorWindow.GetWindow(typeof(simpleMenu));
    }

    void OnInspectorUpdate()
    {
        Repaint();
    }
    void OnGUI()
    {
        
        source = EditorGUILayout.ObjectField(source, typeof(TextAsset), true);

        if (GUILayout.Button("Add to scene"))
        {
            //find director
            timeline = GameObject.Find("TIMELINE");
            PlayableDirector director = timeline.GetComponent<PlayableDirector>();
            TimelineAsset timelineAsset = (TimelineAsset)director.playableAsset;

            //load json into class
            string jsonText = File.ReadAllText(Application.dataPath + "/Resources/json/" + source.name + ".json");
            PlayerStatsList myPlayerStatsList = new PlayerStatsList();
            JsonUtility.FromJsonOverwrite(jsonText, myPlayerStatsList);
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
                animObject = Resources.Load("AnimTest/" + myObject.animPath);
                AnimationClip animClip;
                animClip = Resources.Load<AnimationClip>("AnimTest/" + myObject.animPath);
                newTrack.CreateClip(animClip);
            }

        }

    }
}