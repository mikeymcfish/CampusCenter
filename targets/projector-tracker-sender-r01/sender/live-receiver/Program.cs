using CampusCenter.Projection;
using CampusCenter.Tracker;
using System.Text.Json;
using System.Diagnostics;

internal static class Program
{
 [STAThread]
 static void Main(string[] args)
 {
  ApplicationConfiguration.Initialize();
  string root=Path.GetFullPath(args[0]);Directory.CreateDirectory(root);
  string scope=args.Length>1?args[1]:"owned packaged Unreal, actual focus, no simulator";
  var model=ModelProfile.Load((Environment.GetEnvironmentVariable("CC_COMPANION_PROFILE") ?? throw new InvalidOperationException("Set CC_COMPANION_PROFILE to the extracted P02 sample profile")));
  // Uses the exact sealed production WinForms and Core assemblies. No simulator or projector output.
  using var main=new MainWindow(model,Path.Combine(root,"calibration.json"),false,true,true);
  var rows=new List<object>();var clock=Stopwatch.StartNew();bool visible=false,staleAfterVisible=false;
  long lastSequence=-1;long accepted=0,rejected=0;bool actualUE=false;
  using var timer=new System.Windows.Forms.Timer(){Interval=50};
  timer.Tick+=(_,_)=>
  {
   var view=main.CurrentTracking;
   if(view is not null)
   {
    accepted=view.Accepted;rejected=view.Rejected;
    if(view.Snapshot is not null)
    {
     actualUE|=!view.Snapshot.Simulation&&view.Snapshot.Session.StartsWith("ue-");
     if(view.Snapshot.Sequence!=lastSequence || (!view.Visible&&visible&&view.AgeMs>=500))
     {rows.Add(new{time_ms=clock.ElapsedMilliseconds,view});lastSequence=view.Snapshot.Sequence;}
     if(view.Visible)visible=true;
     if(visible&&!view.Visible&&view.AgeMs>=500)staleAfterVisible=true;
    }
   }
   if(clock.Elapsed.TotalSeconds>=85 || File.Exists(Path.Combine(root,"stop-live.txt")))
   {
    timer.Stop();bool passed=main.IsListening&&actualUE&&accepted>100&&rejected==0&&visible&&staleAfterVisible;
    File.WriteAllText(Path.Combine(root,"live-receiver-validation.json"),JsonSerializer.Serialize(new{passed,method="Exact sealed production MainWindow/Core assemblies; "+scope+"; simulator disabled, output closed; no screenshot",actualUE,accepted,rejected,visible,staleAfterVisible,rows},ProfileStore.Options));
    Environment.ExitCode=passed?0:1;main.Close();
   }
  };
  timer.Start();Application.Run(main);
 }
}
