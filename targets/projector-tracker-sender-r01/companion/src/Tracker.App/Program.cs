using CampusCenter.Tracker;

namespace CampusCenter.Projection;
internal static class Program
{
    [STAThread]
    private static void Main(string[] args)
    {
        ApplicationConfiguration.Initialize();
        string modelPath=Path.Combine(AppContext.BaseDirectory,"profiles","p02-sample-1-250.json");
        try
        {
            var model=ModelProfile.Load(modelPath);
            if(args.Contains("--evidence"))
            {
                int i=Array.IndexOf(args,"--evidence");Evidence.Create(args.Length>i+1?args[i+1]:Path.Combine(AppContext.BaseDirectory,"evidence"),model);return;
            }
            int p=Array.IndexOf(args,"--profile");var path=p>=0&&args.Length>p+1?Path.GetFullPath(args[p+1]):Path.Combine(AppContext.BaseDirectory,"data","calibration.json");
            int smoke=Array.IndexOf(args,"--smoke");
            using var main=new MainWindow(model,path,args.Contains("--simulate")||smoke>=0,args.Contains("--live")||smoke>=0,args.Contains("--quiet")||smoke>=0);
            if(smoke>=0)
            {
                string folder=args.Length>smoke+1?Path.GetFullPath(args[smoke+1]):Path.Combine(AppContext.BaseDirectory,"smoke");Directory.CreateDirectory(folder);
                using var timer=new System.Windows.Forms.Timer(){Interval=6100};
                timer.Tick+=(_,_)=>
                {
                    timer.Stop();var view=main.CurrentTracking;
                    using var screenshot=new Bitmap(main.Width,main.Height);main.DrawToBitmap(screenshot,new Rectangle(0,0,main.Width,main.Height));screenshot.Save(Path.Combine(folder,"Portable_UI_upstairs.png"));
                    bool passed=main.IsListening&&view?.Visible==true&&view.Snapshot!.Simulation&&view.Snapshot.Floor==1;
                    File.WriteAllText(Path.Combine(folder,"PORTABLE_SMOKE.json"),System.Text.Json.JsonSerializer.Serialize(new {passed,source="simulator UDP into real receiver and WinForms executable",tracking=view,local_dotnet_root=System.Runtime.InteropServices.RuntimeEnvironment.GetRuntimeDirectory(),output_opened=false},ProfileStore.Options));
                    Environment.ExitCode=passed?0:1;main.Close();
                };
                timer.Start();Application.Run(main);
            }
            else Application.Run(main);
        }
        catch(Exception ex)when(ex is IOException or UnauthorizedAccessException or InvalidDataException)
        {MessageBox.Show(ex.Message,"CampusCenter tracker",MessageBoxButtons.OK,MessageBoxIcon.Error);}
    }
}
