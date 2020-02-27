using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System.IO;
using System;

public class RimLight : EditorWindow
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
    static public void createRimLight(GameObject tempobj, string rimProfile)
    {
        //make rimSettingsList
        RimSettingsList rimSettingsList = new RimSettingsList();
        //load json into class if one is specified
        if (rimProfile != "")
        {
            string jsonText = File.ReadAllText(Application.dataPath + "/Resources/" + rimProfile + ".json");
            JsonUtility.FromJsonOverwrite(jsonText, rimSettingsList);
        }
        //make the light
        GameObject lightGameObject = new GameObject("Rim Light");
        Light rimLight = lightGameObject.AddComponent<Light>();
        rimLight.transform.Rotate(rimSettingsList.Angle.x, rimSettingsList.Angle.y, rimSettingsList.Angle.z, Space.Self);
        rimLight.transform.SetParent(tempobj.transform);
        rimLight.color = rimSettingsList.Colour;
        rimLight.intensity = rimSettingsList.Intensity;
        rimLight.type = LightType.Directional;
        rimLight.shadows = LightShadows.Soft;
        rimLight.cullingMask = 1 << LayerMask.NameToLayer("Characters");
    }
}

   
