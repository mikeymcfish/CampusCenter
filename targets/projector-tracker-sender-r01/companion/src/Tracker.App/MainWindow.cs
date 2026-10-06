using CampusCenter.Tracker;

namespace CampusCenter.Projection;
public sealed class MainWindow : Form
{
    private readonly ModelProfile model;
    private CalibrationProfile profile=new();
    private readonly string profilePath;
    private readonly bool quiet;
    private readonly SceneRenderer renderer=new();
    private readonly PreviewCanvas canvas=new();
    private readonly System.Windows.Forms.Timer tick=new(){Interval=33};
    private LoopbackReceiver? receiver;
    private Simulator? simulator;
    private ProjectionWindow? output;
    private readonly ComboBox displays=new(){DropDownStyle=ComboBoxStyle.DropDownList,Width=400};
    private readonly ComboBox modes=new(){DropDownStyle=ComboBoxStyle.DropDownList,Width=220};
    private readonly Label status=new(){AutoSize=false,Dock=DockStyle.Fill,ForeColor=Color.DarkBlue,Padding=new Padding(8)};
    private readonly Label notices=new(){AutoSize=true,MaximumSize=new Size(450,0),ForeColor=Color.DarkRed};
    private readonly Button simButton=new(){Text="Start SIMULATOR",AutoSize=true};
    private readonly Button showButton=new(){Text="Open selected projector",AutoSize=true};
    private readonly Dictionary<string,NumericUpDown> numbers=new();
    private readonly NumericUpDown[] cornerX=new NumericUpDown[4],cornerY=new NumericUpDown[4];
    private readonly CheckBox heading=new(){Text="Show heading arrow",AutoSize=true};
    private readonly ComboBox previewFloor=new(){DropDownStyle=ComboBoxStyle.DropDownList,Width=160};
    private bool loading;
    private float previewX=140,previewY=125;
    public bool IsListening=>receiver is not null&&receiver.Error is null;
    public TrackingView? CurrentTracking=>receiver?.State.View(TrackerState.ClockMs,model.Contains);
    public MainWindow(ModelProfile model,string path,bool startSimulation=false,bool startLive=false,bool quiet=false)
    {
        this.model=model;profilePath=path;this.quiet=quiet;
        Text="CampusCenter • P02 player projection";Width=1350;Height=850;MinimumSize=new Size(1050,700);AutoScaleMode=AutoScaleMode.Dpi;
        var root=new TableLayoutPanel(){Dock=DockStyle.Fill,ColumnCount=1,RowCount=3};
        root.RowStyles.Add(new RowStyle(SizeType.Absolute,90));root.RowStyles.Add(new RowStyle(SizeType.Percent,100));root.RowStyles.Add(new RowStyle(SizeType.Absolute,70));Controls.Add(root);
        var top=new FlowLayoutPanel(){Dock=DockStyle.Fill,Padding=new Padding(8),WrapContents=true};root.Controls.Add(top,0,0);
        top.Controls.Add(new Label(){Text="Output",AutoSize=true,Margin=new Padding(0,10,5,0)});top.Controls.Add(displays);
        var refresh=new Button(){Text="Refresh displays",AutoSize=true};refresh.Click+=(_,_)=>RefreshDisplays();top.Controls.Add(refresh);top.Controls.Add(showButton);
        var close=new Button(){Text="Close output",AutoSize=true};close.Click+=(_,_)=>CloseOutput();top.Controls.Add(close);
        modes.Items.AddRange(["Preview / calibration","LIVE telemetry"]);modes.SelectedIndex=startLive?1:0;
        modes.SelectedIndexChanged+=(_,_)=>{canvas.Invalidate();output?.Invalidate();};top.Controls.Add(modes);top.Controls.Add(simButton);
        var split=new SplitContainer(){Size=new Size(1250,650),Dock=DockStyle.Fill,FixedPanel=FixedPanel.Panel2,SplitterDistance=800,Panel2MinSize=425};root.Controls.Add(split,0,1);
        split.Panel1.Controls.Add(canvas);
        canvas.DrawScene=(g,size)=>Draw(g,size,false);
        canvas.MouseDown+=(_,e)=>
        {
            if(modes.SelectedIndex!=0)return;
            // Test marker clicks use unwarped bounds; precise XY controls remain authoritative.
            previewX=(float)(model.MinX+Math.Clamp(e.X/(double)canvas.Width,0,1)*(model.MaxX-model.MinX));
            previewY=(float)(model.MaxY-Math.Clamp(e.Y/(double)canvas.Height,0,1)*(model.MaxY-model.MinY));
            SetNumber("Test X mm",previewX);SetNumber("Test Y mm",previewY);
        };
        var side=new FlowLayoutPanel(){Dock=DockStyle.Fill,FlowDirection=FlowDirection.TopDown,WrapContents=false,AutoScroll=true,Padding=new Padding(10)};split.Panel2.Controls.Add(side);
        side.Controls.Add(new Label(){Text="P02 whole sample · 1:250 · fixed coordinates",AutoSize=true,Font=new Font(Font,FontStyle.Bold)});
        side.Controls.Add(new Label(){Text="Preview shows outline; LIVE output draws only the dot.\nGround is sharp. Upstairs stays at the same XY with blur.\nInvalid, stale and outside-footprint positions hide.",AutoSize=true});
        side.Controls.Add(notices);
        AddNumber(side,"Translate X %",-100,100,0,.1m,v=>profile.TranslationX=(double)v/100);
        AddNumber(side,"Translate Y %",-100,100,0,.1m,v=>profile.TranslationY=(double)v/100);
        AddNumber(side,"Scale",.1m,4,1,.01m,v=>profile.Scale=(double)v);
        AddNumber(side,"Rotation degrees",-360,360,0,.1m,v=>profile.RotationDegrees=(double)v);
        side.Controls.Add(new Label(){Text="Four points: normalized % of output pixels (TL → TR → BR → BL)",AutoSize=true,MaximumSize=new Size(440,0)});
        for(int i=0;i<4;i++)
        {
            int n=i;var row=new FlowLayoutPanel(){AutoSize=true,WrapContents=false};row.Controls.Add(new Label(){Text=$"Point {i+1}",Width=70,Margin=new Padding(0,7,0,0)});
            cornerX[i]=Number(-50,150,(decimal)profile.Corners[i].X*100,.1m);
            cornerY[i]=Number(-50,150,(decimal)profile.Corners[i].Y*100,.1m);
            row.Controls.Add(new Label(){Text="X%",AutoSize=true,Margin=new Padding(3,7,3,0)});row.Controls.Add(cornerX[i]);row.Controls.Add(new Label(){Text="Y%",AutoSize=true,Margin=new Padding(3,7,3,0)});row.Controls.Add(cornerY[i]);side.Controls.Add(row);
            void Change(object? sender,EventArgs e)
            {
                if(loading)return;
                var old=profile.Corners[n];profile.Corners[n]=new((double)cornerX[n].Value/100,(double)cornerY[n].Value/100);
                try{profile.Validate();notices.Text="";}catch(InvalidDataException ex)
                {profile.Corners[n]=old;loading=true;cornerX[n].Value=(decimal)old.X*100;cornerY[n].Value=(decimal)old.Y*100;loading=false;notices.Text=ex.Message;}
                canvas.Invalidate();output?.Invalidate();
            }
            cornerX[i].ValueChanged+=Change;cornerY[i].ValueChanged+=Change;
        }
        AddNumber(side,"Sharp radius px",2,100,9,1,v=>profile.DotRadiusPixels=(double)v);
        AddNumber(side,"Upstairs blur sigma px",2,100,14,1,v=>profile.BlurSigmaPixels=(double)v);
        heading.CheckedChanged+=(_,_)=>{if(!loading)profile.HeadingArrow=heading.Checked;};side.Controls.Add(heading);
        AddNumber(side,"Heading length mm",1,30,5,1,v=>profile.HeadingLengthMm=(double)v);
        var buttons=new FlowLayoutPanel(){AutoSize=true};side.Controls.Add(buttons);
        var save=new Button(){Text="Save profile",AutoSize=true};save.Click+=(_,_)=>SaveProfile();buttons.Controls.Add(save);
        var load=new Button(){Text="Load saved",AutoSize=true};load.Click+=(_,_)=>LoadProfile();buttons.Controls.Add(load);
        var reset=new Button(){Text="Reset calibration",AutoSize=true};reset.Click+=(_,_)=>{CloseOutput();profile=new();Populate();RefreshDisplays();notices.Text="Calibration reset in memory; Save profile to persist.";};buttons.Controls.Add(reset);
        side.Controls.Add(new Label(){Text="Test pose (only Preview / calibration)",AutoSize=true,Font=new Font(Font,FontStyle.Bold)});
        AddNumber(side,"Test X mm",-20,300,140,.1m,v=>previewX=(float)v);
        AddNumber(side,"Test Y mm",-20,250,125,.1m,v=>previewY=(float)v);
        AddNumber(side,"Test yaw degrees",-360,360,0,1,_=>{});
        previewFloor.Items.AddRange(["Ground / sharp","Upstairs / blurred","Invalid / hidden"]);previewFloor.SelectedIndex=0;side.Controls.Add(previewFloor);
        side.Controls.Add(new Label(){Text="Simulator cycles 20s: ground, upstairs, invalid,\n2s silence, teleport, outside. Stop before live game.\nProfile saves normalized coordinates and display identity.\nNo monitor, firewall or Unreal settings are changed.",AutoSize=true});
        root.Controls.Add(status,0,2);
        simButton.Click+=(_,_)=>ToggleSimulator();showButton.Click+=(_,_)=>OpenOutput();
        try{receiver=new();}catch(System.Net.Sockets.SocketException ex){notices.Text="Receiver could not bind 127.0.0.1:9001: "+ex.Message;}
        RefreshDisplays();if(File.Exists(path))LoadProfile();
        tick.Tick+=(_,_)=>UpdateFrame();tick.Start();
        if(startSimulation)ToggleSimulator();
        FormClosed+=(_,_)=>{tick.Stop();tick.Dispose();CloseOutput();simulator?.Dispose();receiver?.Dispose();renderer.Dispose();};
    }
    protected override bool ShowWithoutActivation=>quiet;
    protected override CreateParams CreateParams
    {get{var cp=base.CreateParams;if(quiet)cp.ExStyle|=0x08000000;return cp;}}
    private static NumericUpDown Number(decimal min,decimal max,decimal value,decimal increment)=>new(){Minimum=min,Maximum=max,Value=value,Increment=increment,DecimalPlaces=2,Width=95};
    private void AddNumber(FlowLayoutPanel panel,string label,decimal min,decimal max,decimal value,decimal increment,Action<decimal> changed)
    {
        var row=new FlowLayoutPanel(){AutoSize=true,WrapContents=false};row.Controls.Add(new Label(){Text=label,Width=200,Margin=new Padding(0,7,0,0)});
        var n=Number(min,max,value,increment);numbers[label]=n;row.Controls.Add(n);panel.Controls.Add(row);
        n.ValueChanged+=(_,_)=>{if(!loading){changed(n.Value);canvas.Invalidate();output?.Invalidate();}};
    }
    private void SetNumber(string label,double value)=>numbers[label].Value=Math.Clamp((decimal)value,numbers[label].Minimum,numbers[label].Maximum);
    private void Populate()
    {
        loading=true;
        SetNumber("Translate X %",profile.TranslationX*100);SetNumber("Translate Y %",profile.TranslationY*100);SetNumber("Scale",profile.Scale);SetNumber("Rotation degrees",profile.RotationDegrees);
        SetNumber("Sharp radius px",profile.DotRadiusPixels);SetNumber("Upstairs blur sigma px",profile.BlurSigmaPixels);SetNumber("Heading length mm",profile.HeadingLengthMm);heading.Checked=profile.HeadingArrow;
        for(int i=0;i<4;i++){cornerX[i].Value=(decimal)profile.Corners[i].X*100;cornerY[i].Value=(decimal)profile.Corners[i].Y*100;}
        loading=false;canvas.Invalidate();output?.Invalidate();
    }
    private void RefreshDisplays()
    {
        string selected=displays.SelectedItem is DisplayItem item?item.Device:profile.DisplayDevice;
        displays.Items.Clear();foreach(var screen in Screen.AllScreens)displays.Items.Add(new DisplayItem(screen.DeviceName,screen.Primary,screen.Bounds.Size));
        displays.SelectedIndex=-1;
        for(int i=0;i<displays.Items.Count;i++)if(((DisplayItem)displays.Items[i]!).Device==selected)displays.SelectedIndex=i;
        if(DisplayPolicy.IsMissing(selected,Screen.AllScreens.Select(s=>s.DeviceName)))notices.Text="Saved/selected display is missing. Output stays closed; choose a connected secondary display.";
        else if(Screen.AllScreens.All(s=>s.Primary))notices.Text="No secondary display detected. Preview/simulator are available; projector output stays closed.";
    }
    private void OpenOutput()
    {
        if(displays.SelectedItem is not DisplayItem item){notices.Text="Select a secondary display explicitly.";return;}
        var screen=Screen.AllScreens.FirstOrDefault(s=>s.DeviceName==item.Device);
        if(screen is null){notices.Text="Selected display is missing; output stays closed.";return;}
        if(!DisplayPolicy.CanOpen(item.Device,screen.Primary,profile.DisplayDevice==item.Device?profile.DisplayWidth:0,profile.DisplayHeight,screen.Bounds.Width,screen.Bounds.Height,out var reason)){notices.Text=reason;return;}
        try{profile.Validate();}catch(InvalidDataException ex){notices.Text=ex.Message;return;}
        CloseOutput();profile.DisplayDevice=item.Device;profile.DisplayWidth=screen.Bounds.Width;profile.DisplayHeight=screen.Bounds.Height;
        output=new(screen){DrawScene=(g,size)=>Draw(g,size,true)};output.Show();notices.Text="Output opened without activation. Return to the game before VR use.";
    }
    private void CloseOutput(){output?.Close();output?.Dispose();output=null;}
    private void ToggleSimulator()
    {
        if(simulator is not null){simulator.Dispose();simulator=null;simButton.Text="Start SIMULATOR";notices.Text="Simulator stopped; stale telemetry hides within 0.5s.";}
        else{simulator=new();simButton.Text="Stop SIMULATOR";notices.Text="SIMULATION — synthetic OSC over loopback. This is not packaged-game integration.";}
    }
    private void SaveProfile()
    {
        try
        {
            if(displays.SelectedItem is DisplayItem item)
            {
                if(profile.DisplayDevice!=item.Device){profile.DisplayWidth=item.Size.Width;profile.DisplayHeight=item.Size.Height;}profile.DisplayDevice=item.Device;
            }
            ProfileStore.Save(profilePath,profile);notices.Text="Profile saved: "+profilePath;
        }
        catch(Exception ex)when(ex is IOException or UnauthorizedAccessException or InvalidDataException){notices.Text=ex.Message;}
    }
    private void LoadProfile()
    {
        CloseOutput();
        try{profile=ProfileStore.Load(profilePath);Populate();RefreshDisplays();notices.Text="Saved calibration loaded. Select/check the display; output stays closed until opened.";}
        catch(Exception ex)when(ex is IOException or UnauthorizedAccessException or InvalidDataException or System.Text.Json.JsonException){notices.Text="Profile load refused: "+ex.Message;}
    }
    private Snapshot PreviewPose()=>new("sim-00000000-0000-0000-0000-000000000000",0,1,previewX*25-4700,230-previewY*25,previewX,previewY,(float)numbers["Test yaw degrees"].Value,previewFloor.SelectedIndex==1?1:0,previewFloor.SelectedIndex!=2,false);
    private void Draw(Graphics g,Size size,bool projection)
    {
        var view=receiver?.State.View(TrackerState.ClockMs,model.Contains);
        bool calibration=modes.SelectedIndex==0;
        var pose=calibration?PreviewPose():view?.Snapshot;
        bool visible=calibration?pose is not null&&pose.Valid&&model.Contains(pose.ModelX,pose.ModelY):view?.Visible==true;
        try{renderer.Draw(g,size,model,profile,pose,visible,calibration,pose?.Simulation==true);}catch(InvalidDataException){g.Clear(Color.Black);}
        if(!projection)
        {
            using var font=new Font("Segoe UI",11,FontStyle.Bold);
            string source=calibration?"CALIBRATION TEST POSE":pose?.Simulation==true?"SIMULATOR TELEMETRY":pose is null?"WAITING FOR TELEMETRY":"UNREAL TELEMETRY (integration acceptance pending)";
            g.DrawString(source,font,pose?.Simulation==true?Brushes.Orange:Brushes.LightSteelBlue,12,size.Height-34);
        }
    }
    private void UpdateFrame()
    {
        if(output is not null)
        {
            var screen=Screen.AllScreens.FirstOrDefault(s=>s.DeviceName==output.SelectedDevice);
            if(screen is null||screen.Primary||screen.Bounds.Size!=output.Size){CloseOutput();notices.Text="Output display missing/changed; closed safely. Refresh and recalibrate.";}
        }
        var view=receiver?.State.View(TrackerState.ClockMs,model.Contains);var s=view?.Snapshot;
        var age=view is null||double.IsInfinity(view.AgeMs)?"—":$"{view.AgeMs:0} ms";
        status.Text=$"127.0.0.1:{Osc.Port} · {(receiver is null?"BIND FAILED":receiver.Error??"listening")} · {view?.Reason}\n"+
            $"Source: {(s is null?"none":s.Simulation?"SIMULATOR":"UNREAL telemetry")} · accepted {view?.Accepted??0} / rejected {view?.Rejected??0} · age {age} · model {(s is null?"—":$"{s.ModelX:0.00}, {s.ModelY:0.00} mm")} · seq {s?.Sequence} · output {(output is null?"closed":output.SelectedDevice)}";
        canvas.Invalidate();output?.Invalidate();
    }
    private sealed record DisplayItem(string Device,bool Primary,Size Size)
    {public override string ToString()=>$"{Device} · {Size.Width} × {Size.Height} · {(Primary?"PRIMARY — refused":"secondary")}";}
}
