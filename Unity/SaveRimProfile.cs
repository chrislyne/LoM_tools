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


public class SaveRimProfile : EditorWindow
{
    [System.Serializable]
    public class LightProperties
    {
        public float Intensity;
        public Vector3 Angle;
        public Color Colour;
    }


    [MenuItem("IoM/Save Rim Profile")]
    static void ShowWindow()
    {
        EditorWindow.GetWindow(typeof(SaveRimProfile));
    }

    void OnInspectorUpdate()
    {
        Repaint();
    }
    string profileName = "";
    int index = 0;
    //string[] options = { "Rigidbody", "Box Collider", "Sphere Collider" };

    string[] options = Directory.GetFiles(@"Assets\Resources\Profiles\rimlight", "*.json");
    

    void OnGUI()
    {
        
 
        //set window title
        this.titleContent = new GUIContent("Rim Light Profile");

        profileName = EditorGUILayout.TextField(profileName);

        if (GUILayout.Button("Save Profile"))
        {
            GameObject rimLight = GameObject.Find("Rim Light");
            float rimIntensity = rimLight.GetComponent<Light>().intensity;
            Vector3 rimAngle = new Vector3(rimLight.transform.localEulerAngles.x, rimLight.transform.localEulerAngles.y, rimLight.transform.localEulerAngles.z);
            Color Colour = rimLight.GetComponent<Light>().color;
            LightProperties rim = new LightProperties();
            rim.Intensity = rimIntensity;
            rim.Angle = rimAngle;
            rim.Colour = Colour;
            string json = JsonUtility.ToJson(rim, true);

            string path = "Assets/Resources/Profiles/rimlight/"+ profileName + ".json";

            //Write some text to the test.txt file
            StreamWriter writer = new StreamWriter(path, false);
            writer.Write(json);
            writer.Close();
        }
        GUILayout.Space(60);
        string[] rimProfileNames = new String[options.Length];

        for (int runs = 0; runs < options.Length; runs++)
        {
            string[] profileSplit = options[runs].Split('\\');
            string nameSplit = profileSplit[profileSplit.Length - 1].Split('.')[0];
            rimProfileNames[runs] = nameSplit;
        }
        index = EditorGUILayout.Popup(index, rimProfileNames);

        if (GUILayout.Button("Load Profile"))
        {
            GameObject cam = GameObject.Find("CAM");
            Debug.Log("Profiles/rimlight" + rimProfileNames[index]);
            RimLight.createRimLight(cam, "Profiles/rimlight/" + rimProfileNames[index]);

        }
    }
}