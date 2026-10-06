using System.Text.Json;

namespace CampusCenter.Tracker;
public readonly record struct PointD(double X,double Y);

public sealed class ModelProfile
{
    public string Id {get;set;}=Osc.Profile;
    public double MinX {get;set;}=4.48;
    public double MinY {get;set;}=2.72;
    public double MaxX {get;set;}=267.84;
    public double MaxY {get;set;}=199.52;
    public PointD[][] FootprintLoops {get;set;}=[];
    public PointD[] Landmarks {get;set;}=[];
    public string[] LandmarkIds {get;set;}=[];
    public string SourceSha256 {get;set;}="";
    public bool Contains(double x,double y)
    {
        if(x<MinX||y<MinY||x>MaxX||y>MaxY||FootprintLoops.Length==0)return false;
        bool inside=false;
        foreach(var loop in FootprintLoops)
        for(int i=0,j=loop.Length-1;i<loop.Length;j=i++)
        {
            var a=loop[i];var b=loop[j];
            double cross=(x-a.X)*(b.Y-a.Y)-(y-a.Y)*(b.X-a.X);
            if(Math.Abs(cross)<1e-7 && x>=Math.Min(a.X,b.X)-1e-7 && x<=Math.Max(a.X,b.X)+1e-7 && y>=Math.Min(a.Y,b.Y)-1e-7 && y<=Math.Max(a.Y,b.Y)+1e-7)return true;
            if((a.Y>y)!=(b.Y>y) && x<(b.X-a.X)*(y-a.Y)/(b.Y-a.Y)+a.X)inside=!inside;
        }
        return inside;
    }
    public static ModelProfile Load(string path)
    {
        var p=JsonSerializer.Deserialize<ModelProfile>(File.ReadAllText(path),ProfileStore.Options)??throw new InvalidDataException("Missing model profile");
        if(p.Id!=Osc.Profile||p.FootprintLoops.Length==0||p.FootprintLoops.Any(l=>l.Length<3)||p.FootprintLoops.Sum(l=>l.Length)>10000||p.FootprintLoops.SelectMany(l=>l).Any(a=>!double.IsFinite(a.X)||!double.IsFinite(a.Y)))throw new InvalidDataException("Wrong P02 profile/footprint");return p;
    }
}

public sealed class CalibrationProfile
{
    public int Version {get;set;}=1;
    public string ModelId {get;set;}=Osc.Profile;
    public string DisplayDevice {get;set;}="";
    public int DisplayWidth {get;set;}
    public int DisplayHeight {get;set;}
    public double TranslationX {get;set;}
    public double TranslationY {get;set;}
    public double Scale {get;set;}=1;
    public double RotationDegrees {get;set;}
    // Normalized output coordinates; source order is model bounds TL,TR,BR,BL.
    public PointD[] Corners {get;set;}=[new(.1,.1),new(.9,.1),new(.9,.9),new(.1,.9)];
    public double DotRadiusPixels {get;set;}=9;
    public double BlurSigmaPixels {get;set;}=14;
    public bool HeadingArrow {get;set;}
    public double HeadingLengthMm {get;set;}=5;
    public CalibrationProfile Copy()=>JsonSerializer.Deserialize<CalibrationProfile>(JsonSerializer.Serialize(this),ProfileStore.Options)!;
    public void Validate()
    {
        if(Version!=1||ModelId!=Osc.Profile||Corners is null||DisplayDevice is null||Corners.Length!=4||Corners.Any(c=>!double.IsFinite(c.X)||!double.IsFinite(c.Y)||c.X is < -.5 or >1.5||c.Y is < -.5 or >1.5)||
           !double.IsFinite(Scale)||Scale is < .1 or > 4||!double.IsFinite(RotationDegrees)||Math.Abs(RotationDegrees)>360||
           !double.IsFinite(TranslationX)||!double.IsFinite(TranslationY)||Math.Abs(TranslationX)>1||Math.Abs(TranslationY)>1||
           !double.IsFinite(DotRadiusPixels)||DotRadiusPixels is < 2 or >100||!double.IsFinite(BlurSigmaPixels)||BlurSigmaPixels is < 2 or >100||
           !double.IsFinite(HeadingLengthMm)||HeadingLengthMm is < 1 or >30||DisplayDevice.Length>256)
            throw new InvalidDataException("Calibration values are invalid");
        // Require a convex, uncrossed quad with a stable orientation.
        double sign=0;
        for(int i=0;i<4;i++)
        {
            var a=Corners[i];var b=Corners[(i+1)%4];var c=Corners[(i+2)%4];
            var z=(b.X-a.X)*(c.Y-b.Y)-(b.Y-a.Y)*(c.X-b.X);
            if(Math.Abs(z)<.0001 || (sign!=0&&Math.Sign(z)!=sign))throw new InvalidDataException("Four points must form a convex uncrossed quadrilateral");sign=Math.Sign(z);
        }
        _=Homography.FromUnitSquare(Corners);
    }
    public PointD Map(ModelProfile model,double x,double y,int width,int height)
        =>new CalibrationMapper(this,model,width,height).Map(x,y);
}

public sealed class CalibrationMapper
{
    private readonly CalibrationProfile profile;
    private readonly ModelProfile model;
    private readonly int width,height;
    private readonly Homography homography;
    public CalibrationMapper(CalibrationProfile profile,ModelProfile model,int width,int height)
    {this.profile=profile;this.model=model;this.width=width;this.height=height;homography=Homography.FromUnitSquare(profile.Corners);}
    public PointD Map(double x,double y)
    {
        var uv=new PointD((x-model.MinX)/(model.MaxX-model.MinX),(model.MaxY-y)/(model.MaxY-model.MinY));
        double radians=profile.RotationDegrees*Math.PI/180;
        // Rotation is in actual model plane, so it remains physically correct for nonsquare samples.
        double aspect=(model.MaxX-model.MinX)/(model.MaxY-model.MinY);
        double dx=(uv.X-.5)*aspect*profile.Scale,dy=(uv.Y-.5)*profile.Scale;
        uv=new(.5+(dx*Math.Cos(radians)-dy*Math.Sin(radians))/aspect+profile.TranslationX,.5+dx*Math.Sin(radians)+dy*Math.Cos(radians)+profile.TranslationY);
        var mapped=homography.Map(uv);return new(mapped.X*width,mapped.Y*height);
    }
}

public sealed class Homography(double[] h)
{
    public PointD Map(PointD p)
    {double d=h[6]*p.X+h[7]*p.Y+1;if(Math.Abs(d)<1e-10)throw new InvalidDataException("Projection horizon intersects point");return new((h[0]*p.X+h[1]*p.Y+h[2])/d,(h[3]*p.X+h[4]*p.Y+h[5])/d);}
    public static Homography FromUnitSquare(PointD[] corners)
    {
        PointD[] src=[new(0,0),new(1,0),new(1,1),new(0,1)];var a=new double[8,9];
        for(int i=0;i<4;i++)
        {
            var p=src[i];var q=corners[i];int j=i*2;
            a[j,0]=p.X;a[j,1]=p.Y;a[j,2]=1;a[j,6]=-q.X*p.X;a[j,7]=-q.X*p.Y;a[j,8]=q.X;
            a[j+1,3]=p.X;a[j+1,4]=p.Y;a[j+1,5]=1;a[j+1,6]=-q.Y*p.X;a[j+1,7]=-q.Y*p.Y;a[j+1,8]=q.Y;
        }
        for(int col=0;col<8;col++)
        {
            int best=col;for(int row=col+1;row<8;row++)if(Math.Abs(a[row,col])>Math.Abs(a[best,col]))best=row;
            if(Math.Abs(a[best,col])<1e-10)throw new InvalidDataException("Degenerate four-point calibration");
            for(int j=col;j<=8;j++)(a[col,j],a[best,j])=(a[best,j],a[col,j]);
            double div=a[col,col];for(int j=col;j<=8;j++)a[col,j]/=div;
            for(int row=0;row<8;row++)if(row!=col){double v=a[row,col];for(int j=col;j<=8;j++)a[row,j]-=v*a[col,j];}
        }
        return new(Enumerable.Range(0,8).Select(i=>a[i,8]).ToArray());
    }
}

public static class ProfileStore
{
    public static JsonSerializerOptions Options {get;}=new(){PropertyNameCaseInsensitive=true,WriteIndented=true};
    public static CalibrationProfile Load(string path)
    {var p=JsonSerializer.Deserialize<CalibrationProfile>(File.ReadAllText(path),Options)??throw new InvalidDataException("Empty calibration");p.Validate();return p;}
    public static void Save(string path,CalibrationProfile p)
    {
        p.Validate();var full=Path.GetFullPath(path);Directory.CreateDirectory(Path.GetDirectoryName(full)!);
        var temporary=full+".tmp";File.WriteAllText(temporary,JsonSerializer.Serialize(p,Options));File.Move(temporary,full,true);
    }
}

public static class DisplayPolicy
{
    public static bool IsMissing(string selected,IEnumerable<string> available)=>selected.Length>0&&!available.Contains(selected,StringComparer.Ordinal);
    public static bool CanOpen(string selected,bool isPrimary,int savedWidth,int savedHeight,int width,int height,out string reason)
    {
        reason=selected.Length==0?"Select a secondary display explicitly":isPrimary?"Primary/game display is refused":savedWidth>0&&(savedWidth!=width||savedHeight!=height)?"Display resolution changed; reset/recalibrate before output":"";return reason.Length==0;
    }
}
