using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using CampusCenter.Tracker;

namespace CampusCenter.Projection;

public sealed class SceneRenderer : IDisposable
{
    private Bitmap? blur;
    private double blurSigma;
    public void Draw(Graphics g,Size size,ModelProfile model,CalibrationProfile profile,Snapshot? pose,bool visible,bool calibration,bool simulation)
    {
        g.Clear(Color.Black);g.SmoothingMode=SmoothingMode.AntiAlias;
        if(size.Width<=0||size.Height<=0)return;
        var mapper=new CalibrationMapper(profile,model,size.Width,size.Height);
        PointF P(double x,double y){var p=mapper.Map(x,y);return new((float)p.X,(float)p.Y);}
        if(calibration)
        {
            using var outline=new Pen(Color.FromArgb(130,180,200),1);
            foreach(var loop in model.FootprintLoops)g.DrawPolygon(outline,loop.Select(p=>P(p.X,p.Y)).ToArray());
            using var grid=new Pen(Color.FromArgb(30,65,80),1);
            for(double x=20;x<model.MaxX;x+=20)g.DrawLine(grid,P(x,model.MinY),P(x,model.MaxY));
            for(double y=20;y<model.MaxY;y+=20)g.DrawLine(grid,P(model.MinX,y),P(model.MaxX,y));
            using var font=new Font("Segoe UI",9);
            using var text=new SolidBrush(Color.FromArgb(185,205,215));
            for(int i=0;i<model.Landmarks.Length;i++)
            {
                var p=P(model.Landmarks[i].X,model.Landmarks[i].Y);
                g.DrawLine(outline,p.X-5,p.Y,p.X+5,p.Y);g.DrawLine(outline,p.X,p.Y-5,p.X,p.Y+5);
                g.DrawString(model.LandmarkIds[i],font,text,p.X+7,p.Y-7);
            }
            string[] labels=["1 TL","2 TR","3 BR","4 BL"];
            for(int i=0;i<4;i++)
            {
                var c=profile.Corners[i];var p=new PointF((float)c.X*size.Width,(float)c.Y*size.Height);
                g.DrawEllipse(Pens.Orange,p.X-7,p.Y-7,14,14);g.DrawString(labels[i],font,Brushes.Orange,p.X+10,p.Y-10);
            }
            g.DrawString("CALIBRATION / P02 1:250   +X east →   +Y north ↑",font,text,12,12);
        }
        if(!visible||pose is null)return;
        var center=P(pose.ModelX,pose.ModelY);
        if(!float.IsFinite(center.X)||!float.IsFinite(center.Y)||Math.Abs(center.X)>size.Width*10||Math.Abs(center.Y)>size.Height*10)return;
        if(pose.Floor==1)
        {
            EnsureBlur(profile.BlurSigmaPixels);
            g.DrawImageUnscaled(blur!, (int)Math.Round(center.X-blur!.Width/2d),(int)Math.Round(center.Y-blur.Height/2d));
        }
        else
        {
            float r=(float)profile.DotRadiusPixels;g.FillEllipse(Brushes.White,center.X-r,center.Y-r,2*r,2*r);
        }
        if(profile.HeadingArrow)
        {
            double yaw=pose.Yaw*Math.PI/180;
            var end=P(pose.ModelX+profile.HeadingLengthMm*Math.Cos(yaw),pose.ModelY-profile.HeadingLengthMm*Math.Sin(yaw));
            using var pen=new Pen(Color.FromArgb(pose.Floor==1?70:230,Color.White),2){CustomEndCap=new AdjustableArrowCap(3,4)};
            g.DrawLine(pen,center,end);
        }
        // Projection live output contains no UI text; simulation watermark belongs to control/preview only.
        _=simulation;
    }
    private void EnsureBlur(double sigma)
    {
        if(blur is not null&&Math.Abs(sigma-blurSigma)<.001)return;
        blur?.Dispose();blurSigma=sigma;
        int radius=(int)Math.Ceiling(sigma*3.5);blur=new Bitmap(radius*2+1,radius*2+1,PixelFormat.Format32bppArgb);
        for(int y=0;y<blur.Height;y++)for(int x=0;x<blur.Width;x++)
        {
            double d2=(x-radius)*(x-radius)+(y-radius)*(y-radius);int alpha=(int)Math.Round(240*Math.Exp(-d2/(2*sigma*sigma)));
            blur.SetPixel(x,y,Color.FromArgb(alpha,255,255,255));
        }
    }
    public void Dispose()=>blur?.Dispose();
}

public sealed class PreviewCanvas : Control
{
    [System.ComponentModel.DesignerSerializationVisibility(System.ComponentModel.DesignerSerializationVisibility.Hidden)]
    public Action<Graphics,Size>? DrawScene {get;set;}
    public PreviewCanvas(){DoubleBuffered=true;ResizeRedraw=true;BackColor=Color.Black;Dock=DockStyle.Fill;}
    protected override void OnPaint(PaintEventArgs e){base.OnPaint(e);DrawScene?.Invoke(e.Graphics,ClientSize);}
}

public sealed class ProjectionWindow : Form
{
    public string SelectedDevice {get;}
    [System.ComponentModel.DesignerSerializationVisibility(System.ComponentModel.DesignerSerializationVisibility.Hidden)]
    public Action<Graphics,Size>? DrawScene {get;set;}
    public ProjectionWindow(Screen screen)
    {
        SelectedDevice=screen.DeviceName;AutoScaleMode=AutoScaleMode.None;FormBorderStyle=FormBorderStyle.None;
        ShowInTaskbar=false;StartPosition=FormStartPosition.Manual;Bounds=screen.Bounds;BackColor=Color.Black;
        DoubleBuffered=true;Text="CampusCenter projection output";
    }
    protected override bool ShowWithoutActivation=>true;
    protected override CreateParams CreateParams
    {get{var cp=base.CreateParams;cp.ExStyle|=0x08000000|0x00000080|0x00000020;return cp;}}
    protected override void WndProc(ref Message m)
    {
        if(m.Msg==0x21){m.Result=(IntPtr)3;return;}
        if(m.Msg==0x84){m.Result=(IntPtr)(-1);return;}
        base.WndProc(ref m);
    }
    protected override void OnPaint(PaintEventArgs e){base.OnPaint(e);DrawScene?.Invoke(e.Graphics,ClientSize);}
}
