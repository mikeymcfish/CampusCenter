using CampusCenter.Tracker;
using System.Drawing.Imaging;
using System.Text.Json;

namespace CampusCenter.Projection;
public static class Evidence
{
    public static void Create(string directory,ModelProfile model)
    {
        Directory.CreateDirectory(directory);var p=new CalibrationProfile();using var renderer=new SceneRenderer();
        string[] names=["Ground_sharp","Upstairs_blurred","Invalid_hidden","Stale_hidden","Teleport_snap","Outside_hidden"];
        int[] frameSeq=[0,120,210,260,300,370];
        for(int i=0;i<names.Length;i++)
        {
            var s=Simulator.Frame("sim-00000000-0000-0000-0000-000000000000",frameSeq[i],DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
            if(i<2)s=s with{WorldX=-1200,WorldY=-2895,ModelX=140,ModelY=125,Yaw=90};
            bool visible=s.Valid&&model.Contains(s.ModelX,s.ModelY)&&i!=3;
            using var b=new Bitmap(1000,750);using var g=Graphics.FromImage(b);renderer.Draw(g,b.Size,model,p,s,visible,true,true);
            using var f=new Font("Segoe UI",14,FontStyle.Bold);g.DrawString("SIMULATOR / SOFTWARE RENDER — "+names[i].Replace('_',' '),f,Brushes.Orange,15,700);
            b.Save(Path.Combine(directory,names[i]+".png"),ImageFormat.Png);
            using var live=new Bitmap(1000,750);using var lg=Graphics.FromImage(live);renderer.Draw(lg,live.Size,model,p,s,visible,false,true);
            live.Save(Path.Combine(directory,names[i]+"_output.png"),ImageFormat.Png);
        }
        File.WriteAllText(Path.Combine(directory,"EVIDENCE.json"),JsonSerializer.Serialize(new {source="Simulator.Frame and production SceneRenderer; offscreen software render, not physical projection or packaged-game test",width=1000,height=750,frames=names},ProfileStore.Options));
    }
}
