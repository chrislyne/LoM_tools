using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System.IO;
using System;
using UnityEngine.Playables;
using UnityEngine.Timeline;
using UnityEngine.Formats.Alembic.Timeline;
using UnityEditor.Recorder.Timeline;

public class Extras : EditorWindow
{
    
    
    // Start is called before the first frame update
    static public void addExtras(BuildScene.MyClass abcObject,PlayableDirector director,TimelineAsset timelineAsset)
    {
        GameObject abcobj = (GameObject)Instantiate(Resources.Load(abcObject.characterPath), new Vector3(0, 0, 0), Quaternion.identity);
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
}

   
