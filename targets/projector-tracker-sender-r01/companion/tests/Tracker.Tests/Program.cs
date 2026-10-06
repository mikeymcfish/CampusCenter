using CampusCenter.Tracker;
using CampusCenter.Projection;
using System.Net;
using System.Net.Sockets;
using System.Text.Json;
using System.Drawing;
using System.Diagnostics;
using System.Runtime.InteropServices;

internal static class Tests
{
    private static readonly List<object> outcomes=[];
    private static ModelProfile model=null!;
    private const long Utc=1791295000000;
    private const string Session="ue-00000000-0000-0000-0000-000000000001";
    private const string Restart="ue-00000000-0000-0000-0000-000000000002";
    private static string root="";
    [DllImport("user32.dll")]private static extern IntPtr GetForegroundWindow();
    [STAThread]
    private static int Main(string[] args)
    {
        Application.SetHighDpiMode(HighDpiMode.PerMonitorV2);
        Application.SetUnhandledExceptionMode(UnhandledExceptionMode.ThrowException);
        Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);
        root=args.Length>0?Path.GetFullPath(args[0]):Path.GetFullPath("../../..");
        Directory.CreateDirectory(Path.Combine(root,"qa"));model=ModelProfile.Load(Path.Combine(root,"profiles","p02-sample-1-250.json"));
        Test("Exact P02 world registration and independent landmarks",()=>
        {
            Equal((1504+4700d)/25,248.16);Equal((-162+230d)/25,2.72);
            Equal(model.Landmarks[9].X,248.16);Equal(model.Landmarks[9].Y,2.72,1e-7);
            Equal(model.MaxX-model.MinX,263.36);Equal(model.MaxY-model.MinY,196.8);
            Assert(model.SourceSha256=="d14d518971fb4c5265544eb84ba0d2bdd0b620097afe12cdd8ab9a08e86fa032");
        });
        Test("Footprint includes exact loops and rejects bounding rectangle cutouts",()=>
        {
            Assert(model.FootprintLoops.Length==4);Assert(model.Contains(140,125));Assert(!model.Contains(-1,10));Assert(!model.Contains(280,210));
            var rejected=new List<PointD>();
            for(double y=model.MinY+2;y<model.MaxY;y+=4)for(double x=model.MinX+2;x<model.MaxX;x+=4)if(!model.Contains(x,y))rejected.Add(new(x,y));
            Assert(rejected.Count>500);File.WriteAllText(Path.Combine(root,"qa","outside_bounds_examples.json"),JsonSerializer.Serialize(rejected.Take(10),ProfileStore.Options));
        });
        Test("Independent golden OSC binary fixture matches codec",()=>
        {
            var expected=Convert.FromHexString(File.ReadAllText(Path.Combine(root,"tests","golden_packet.hex")).Trim());
            var s=Pose(0,stamp:Utc,mx:140,my:125,yaw:90);Assert(expected.SequenceEqual(Osc.Encode(s)));
            Assert(Osc.TryDecode(expected,out var decoded,out _));Assert(decoded==s);
        });
        Test("Reject every truncated packet, bundles, wrong tags and trailing data",()=>
        {
            var b=Osc.Encode(Pose(0));for(int i=0;i<b.Length;i++)Assert(!Osc.TryDecode(b[..i],out _,out _));
            var bad=b.Concat(new byte[4]).ToArray();Assert(!Osc.TryDecode(bad,out _,out _));
            bad=(byte[])b.Clone();bad[0]=(byte)'#';Assert(!Osc.TryDecode(bad,out _,out _));
            bad=(byte[])b.Clone();bad[32]=(byte)'x';Assert(!Osc.TryDecode(bad,out _,out _));
            Assert(!Osc.TryDecode(new byte[2048],out _,out _));
        });
        Test("Malformed flags, nonfinite pose, wrong model mapping rejected",()=>
        {
            Assert(!Osc.TryDecode(Osc.Encode(Pose(0) with{WorldX=float.NaN}),out _,out _));
            Assert(!Osc.TryDecode(Osc.Encode(Pose(0) with{Yaw=float.PositiveInfinity}),out _,out _));
            Assert(!Osc.TryDecode(Osc.Encode(Pose(0) with{ModelX=141}),out _,out _));
            Assert(!Osc.TryDecode(Osc.Encode(Pose(0) with{Floor=5}),out _,out _));
            Assert(!Osc.TryDecode(Osc.Encode(Pose(0) with{Floor=-1,Valid=true}),out _,out _));
            Assert(Osc.TryDecode(Osc.Encode(Pose(0) with{Floor=-1,Valid=false}),out _,out _));
            Assert(!Osc.TryDecode(Osc.Encode(Pose(-1)),out _,out _));Assert(!Osc.TryDecode(Osc.Encode(Pose(0) with{Session="sim-bad"}),out _,out _));
        });
        Test("Sharp ground, same XY upstairs, invalid hide and exact teleport snap",()=>
        {
            var state=new TrackerState();Assert(state.Accept(Osc.Encode(Pose(0)),0,Utc));var v=state.View(1,model.Contains);Assert(v.Visible&&v.Snapshot!.Floor==0);
            Assert(state.Accept(Osc.Encode(Pose(1) with{Floor=1}),50,Utc));v=state.View(51,model.Contains);Assert(v.Visible&&v.Snapshot!.Floor==1);Equal(v.Snapshot!.ModelX,140);
            Assert(state.Accept(Osc.Encode(Pose(2) with{Valid=false}),100,Utc));Assert(!state.View(100,model.Contains).Visible);
            Assert(state.Accept(Osc.Encode(Pose(3,mx:200,my:100) with{Teleport=true}),150,Utc));v=state.View(150,model.Contains);Assert(v.Visible&&v.Snapshot!.Teleport);Equal(v.Snapshot!.ModelX,200);
        });
        Test("Receiver monotonic timeout at 500ms; duplicates/malformed cannot refresh",()=>
        {
            var state=new TrackerState();Assert(state.Accept(Osc.Encode(Pose(0)),100,Utc));Assert(state.View(599.9,model.Contains).Visible);
            Assert(!state.Accept(Osc.Encode(Pose(0)),450,Utc));Assert(!state.Accept([1,2,3],550,Utc));Assert(!state.View(600,model.Contains).Visible);
            Assert(state.Accept(Osc.Encode(Pose(1)),601,Utc));Assert(state.View(601,model.Contains).Visible);
        });
        Test("Reject old timestamps, UTC delayed/future packets, out-of-order sequences",()=>
        {
            var s=new TrackerState();Assert(s.Accept(Osc.Encode(Pose(3)),0,Utc));Assert(!s.Accept(Osc.Encode(Pose(2)),50,Utc));
            Assert(!s.Accept(Osc.Encode(Pose(4,stamp:Utc-1)),100,Utc));Assert(!s.Accept(Osc.Encode(Pose(4,stamp:Utc-501)),100,Utc));
            Assert(!s.Accept(Osc.Encode(Pose(4,stamp:Utc+1001)),100,Utc));Assert(!s.View(500,model.Contains).Visible);
        });
        Test("Sender restart, retired packets, competing sender and stale reconnect",()=>
        {
            var s=new TrackerState();Assert(s.Accept(Osc.Encode(Pose(10)),0,Utc));
            Assert(!s.Accept(Osc.Encode(Pose(2) with{Session=Restart}),50,Utc));
            Assert(s.Accept(Osc.Encode(Pose(0) with{Session=Restart,Teleport=true}),100,Utc));
            Assert(!s.Accept(Osc.Encode(Pose(11)),150,Utc));
            var later=Pose(35) with{Session="ue-00000000-0000-0000-0000-000000000003"};Assert(s.Accept(Osc.Encode(later),700,Utc));
            Assert(s.View(700,model.Contains).Snapshot!.Session==later.Session);
        });
        Test("Shared UTC clock jumps recover; stale hide still monotonic",()=>
        {
            var s=new TrackerState();Assert(s.Accept(Osc.Encode(Pose(0)),0,Utc));
            Assert(s.Accept(Osc.Encode(Pose(1,stamp:Utc-3_600_000)),50,Utc-3_600_000));Assert(s.View(100,model.Contains).Visible);
            Assert(!s.Accept(Osc.Encode(Pose(0,stamp:Utc-3_600_000)),150,Utc-3_600_000));Assert(!s.View(550,model.Contains).Visible);
            Assert(s.Accept(Osc.Encode(Pose(2,stamp:Utc+3_600_000)),600,Utc+3_600_000));Assert(s.View(600,model.Contains).Visible);
            Assert(!s.Accept(Osc.Encode(Pose(3,stamp:Utc)),650,Utc+3_600_000));
        });
        Test("Homography exact corner constraints and corrected heading direction",()=>
        {
            var p=new CalibrationProfile{Corners=[new(.13,.2),new(.85,.1),new(.94,.86),new(.05,.9)]};p.Validate();
            var h=Homography.FromUnitSquare(p.Corners);PointD[] src=[new(0,0),new(1,0),new(1,1),new(0,1)];
            for(int i=0;i<4;i++){var q=h.Map(src[i]);Equal(q.X,p.Corners[i].X);Equal(q.Y,p.Corners[i].Y);}
            p=new();var c=p.Map(model,140,125,1920,1080);var east=p.Map(model,145,125,1920,1080);var worldPlusY=p.Map(model,140,120,1920,1080);
            Assert(east.X>c.X);Assert(worldPlusY.Y>c.Y); // UE +Y -> model -Y -> screen down.
            var rotated=new CalibrationProfile{RotationDegrees=90};var e=rotated.Map(model,145,125,1920,1080);var r=rotated.Map(model,140,125,1920,1080);Assert(e.Y>r.Y);Equal(e.X,r.X);
        });
        Test("Reject crossed/degenerate/nonfinite calibration",()=>
        {
            Throws(()=>new CalibrationProfile{Corners=[new(0,0),new(1,1),new(1,0),new(0,1)]}.Validate());
            Throws(()=>new CalibrationProfile{Scale=double.NaN}.Validate());
            Throws(()=>new CalibrationProfile{Corners=[new(0,0),new(0,0),new(1,1),new(0,1)]}.Validate());
            Throws(()=>new CalibrationProfile{Corners=null!}.Validate());Throws(()=>new CalibrationProfile{DisplayDevice=null!}.Validate());
        });
        Test("Save/relaunch profile, normalized DPI mapping and resolution refusal",()=>
        {
            var path=Path.Combine(root,"qa","test-calibration.json");var p=new CalibrationProfile{TranslationX=.03,TranslationY=-.01,Scale=1.05,RotationDegrees=2,DisplayDevice="TEST",DisplayWidth=1920,DisplayHeight=1080};
            ProfileStore.Save(path,p);var loaded=ProfileStore.Load(path);Assert(loaded.DisplayDevice=="TEST");Equal(loaded.TranslationX,.03);
            var a=p.Map(model,140,125,1280,720);var b=loaded.Map(model,140,125,1920,1080);Equal(b.X/a.X,1.5);Equal(b.Y/a.Y,1.5);
            Assert(!DisplayPolicy.CanOpen("",false,0,0,1920,1080,out _));Assert(!DisplayPolicy.CanOpen("TEST",true,0,0,1920,1080,out _));
            Assert(!DisplayPolicy.CanOpen("TEST",false,1920,1080,1280,720,out _));Assert(DisplayPolicy.CanOpen("TEST",false,1920,1080,1920,1080,out _));
            Assert(DisplayPolicy.IsMissing("PROJECTOR",["GAME"]));Assert(!DisplayPolicy.IsMissing("PROJECTOR",["GAME","PROJECTOR"]));
        });
        Test("Production renderer sharp vs Gaussian blur, invalid/outside black",()=>
        {
            using var renderer=new SceneRenderer();var p=new CalibrationProfile();var pose=Pose(0);var c=p.Map(model,140,125,1000,750);
            using var sharp=new Bitmap(1000,750);using var sg=Graphics.FromImage(sharp);renderer.Draw(sg,sharp.Size,model,p,pose,true,false,false);
            using var soft=new Bitmap(1000,750);using var bg=Graphics.FromImage(soft);renderer.Draw(bg,soft.Size,model,p,pose with{Floor=1},true,false,false);
            Assert(sharp.GetPixel((int)c.X+20,(int)c.Y).R==0);Assert(soft.GetPixel((int)c.X+20,(int)c.Y).R>30);
            Assert(soft.GetPixel((int)c.X+10,(int)c.Y).R>soft.GetPixel((int)c.X+20,(int)c.Y).R);
            renderer.Draw(bg,soft.Size,model,p,pose,false,false,false);Assert(soft.GetPixel((int)c.X,(int)c.Y).R==0);
        });
        Test("Live UDP binds only loopback, port conflict refused, close/relaunch",()=>
        {
            int port;using(var select=new UdpClient(new IPEndPoint(IPAddress.Loopback,0)))port=((IPEndPoint)select.Client.LocalEndPoint!).Port;
            using(var receiver=new LoopbackReceiver(port))
            {
                Assert(IPGlobalSocket(port));
                bool conflict=false;try{using var second=new LoopbackReceiver(port);}catch(SocketException){conflict=true;}Assert(conflict);
                using var sender=new UdpClient();var fresh=Pose(0,stamp:DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());sender.Send(Osc.Encode(fresh),new IPEndPoint(IPAddress.Loopback,port));
                var watch=Stopwatch.StartNew();while(receiver.State.View(TrackerState.ClockMs,model.Contains).Accepted==0&&watch.ElapsedMilliseconds<1500)Thread.Sleep(10);
                Assert(receiver.State.View(TrackerState.ClockMs,model.Contains).Visible);
                sender.Send(new byte[]{1,2,3},new IPEndPoint(IPAddress.Loopback,port));
                Thread.Sleep(550);Assert(!receiver.State.View(TrackerState.ClockMs,model.Contains).Visible);
            }
            using var reopened=new LoopbackReceiver(port);Assert(reopened.Error is null);
        });
        Test("WinForms launch/simulator screenshot, no activation, close/relaunch",()=>
        {
            var foreground=GetForegroundWindow();var path=Path.Combine(root,"qa","ui-calibration.json");
            using(var window=new MainWindow(model,path,true,true,true))
            {
                window.Show();var watch=Stopwatch.StartNew();while(watch.ElapsedMilliseconds<650){Application.DoEvents();Thread.Sleep(15);}
                Assert(!window.IsDisposed&&window.Visible,"UI not visible");Assert(GetForegroundWindow()==foreground,"UI took foreground focus");
                Assert(window.IsListening,"Receiver failed to bind");Assert(window.CurrentTracking?.Visible==true&&window.CurrentTracking.Snapshot!.Simulation,"Simulator not visible: "+window.CurrentTracking?.Reason);
                using var screenshot=new Bitmap(window.Width,window.Height);window.DrawToBitmap(screenshot,new Rectangle(0,0,window.Width,window.Height));
                screenshot.Save(Path.Combine(root,"qa","Companion_UI_simulator.png"));window.Close();Application.DoEvents();
            }
            using var reopened=new MainWindow(model,path,false,false,true);reopened.Show();Application.DoEvents();Assert(reopened.Visible);reopened.Close();Application.DoEvents();
        });
        Evidence.Create(Path.Combine(root,"qa","evidence"),model);
        var report=new {at_utc=DateTimeOffset.UtcNow, tests=outcomes, physical_projector_tested=false, headset_tested=false, packaged_game_integration_tested=false, ui_display_resolution=Screen.PrimaryScreen?.Bounds.Size.ToString(), display_count=Screen.AllScreens.Length};
        File.WriteAllText(Path.Combine(root,"qa","QA_RESULTS.json"),JsonSerializer.Serialize(report,ProfileStore.Options));
        int failed=outcomes.Count(o=>JsonSerializer.Serialize(o).Contains("\"passed\":false"));Console.WriteLine($"{outcomes.Count-failed}/{outcomes.Count} passed");return failed==0?0:1;
    }
    private static bool IPGlobalSocket(int port)=>System.Net.NetworkInformation.IPGlobalProperties.GetIPGlobalProperties().GetActiveUdpListeners().Any(e=>e.Port==port&&e.Address.Equals(IPAddress.Loopback));
    private static Snapshot Pose(int seq,long stamp=Utc,float mx=140,float my=125,float yaw=90)=>new(Session,seq,stamp,mx*25-4700,230-my*25,mx,my,yaw,0,true,seq==0);
    private static void Test(string name,Action body){try{body();outcomes.Add(new{name,passed=true});Console.WriteLine("PASS "+name);}catch(Exception ex){outcomes.Add(new{name,passed=false,error=ex.ToString()});Console.WriteLine("FAIL "+name+": "+ex.Message);}}
    private static void Assert(bool value,string message="Assertion failed"){if(!value)throw new InvalidOperationException(message);}
    private static void Equal(double a,double b,double tolerance=1e-8){if(Math.Abs(a-b)>tolerance)throw new InvalidOperationException($"{a} != {b}");}
    private static void Throws(Action action){bool caught=false;try{action();}catch(InvalidDataException){caught=true;}Assert(caught);}
}
