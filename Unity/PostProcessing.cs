using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System.IO;
using System;
using UnityEngine.Rendering.PostProcessing;

public class PostProcessing : EditorWindow
{
    [Serializable]
    public class RimSettingsList
    {
        //default values make a light with no effect
        public float Intensity = 0;
        public Vector3 Angle = new Vector3(0,180,0);
        public Color Colour = new Color(1,1,1,1);
    }
    // Start is called before the first frame update
    static public void addPostProcessing(GameObject cam,string profilePath)
    {
        if (profilePath != "")
        {
            //Set Main Camera layer to Postprocessing
            cam.layer = LayerMask.NameToLayer("Post-Processing");
            PostProcessLayer ppl = cam.AddComponent<PostProcessLayer>();

            ppl.antialiasingMode = PostProcessLayer.Antialiasing.FastApproximateAntialiasing;
            ppl.volumeLayer = 1 << LayerMask.NameToLayer("Post-Processing");
            PostProcessVolume ppv = cam.AddComponent<PostProcessVolume>();
            ppv.isGlobal = true;
            var ppp = Resources.Load<PostProcessProfile>(profilePath);

            ppv.profile = ppp;
        }
    }
}

   
