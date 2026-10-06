using System.Buffers.Binary;
using System.Text;
using System.Text.RegularExpressions;
using System.Net;
using System.Net.Sockets;
using System.Diagnostics;

namespace CampusCenter.Tracker;

public sealed record Snapshot(string Session, int Sequence, long UnixMs, float WorldX, float WorldY,
    float ModelX, float ModelY, float Yaw, int Floor, bool Valid, bool Teleport)
{
    public bool Simulation => Session.StartsWith("sim-", StringComparison.Ordinal);
}

public static class Osc
{
    public const int Port = 9001;
    public const string Profile = "campuscenter-r29-p02-sample-1-250-v1";
    public const string Address = "/campuscenter/player/v1";
    public const string Tags = ",issisfffffiii";

    public static bool TryDecode(byte[] bytes, out Snapshot? snapshot, out string error)
    {
        snapshot = null; error = "Malformed OSC";
        if (bytes.Length > 1024 || bytes.Length < 16 || bytes.Length % 4 != 0) return false;
        try
        {
            var r = new Reader(bytes);
            if (r.String() != Address || r.String() != Tags || r.Int() != 1 || r.String() != Profile)
            { error = "Wrong contract"; return false; }
            var session = r.String(); var sequence = r.Int(); var stamp = r.String();
            if (!Regex.IsMatch(session, @"^(ue|sim)-[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$") ||
                sequence < 0 || stamp.Length is < 1 or > 16 || !stamp.All(char.IsAsciiDigit) || !long.TryParse(stamp, out var ms) || ms <= 0)
            { error = "Invalid session/sequence/timestamp"; return false; }
            var x = r.Float(); var y = r.Float(); var mx = r.Float(); var my = r.Float(); var yaw = r.Float();
            var floor = r.Int(); var valid = r.Int(); var teleport = r.Int();
            if (!r.AtEnd || !new[] {x,y,mx,my,yaw}.All(float.IsFinite) || valid is < 0 or > 1 || teleport is < 0 or > 1 ||
                floor is < -1 or > 1 || (valid == 1 && floor < 0) || Math.Abs(x)>1e7 || Math.Abs(y)>1e7 || Math.Abs(yaw)>1e6)
            { error = "Invalid pose/flags"; return false; }
            if (Math.Abs(mx - (x + 4700d) / 25) > .05 || Math.Abs(my - (-y + 230d) / 25) > .05)
            { error = "World/model registration mismatch"; return false; }
            snapshot = new(session,sequence,ms,x,y,mx,my,yaw,floor,valid==1,teleport==1); error = ""; return true;
        }
        catch (Exception ex) when (ex is ArgumentException or IndexOutOfRangeException or InvalidDataException)
        { return false; }
    }

    public static byte[] Encode(Snapshot s)
    {
        using var m = new MemoryStream();
        void Str(string t) { var b=Encoding.ASCII.GetBytes(t); m.Write(b); m.WriteByte(0); while(m.Length%4!=0)m.WriteByte(0); }
        void Int(int i) { Span<byte> b=stackalloc byte[4]; BinaryPrimitives.WriteInt32BigEndian(b,i);m.Write(b); }
        void F(float f)=>Int(BitConverter.SingleToInt32Bits(f));
        Str(Address);Str(Tags);Int(1);Str(Profile);Str(s.Session);Int(s.Sequence);Str(s.UnixMs.ToString(System.Globalization.CultureInfo.InvariantCulture));
        F(s.WorldX);F(s.WorldY);F(s.ModelX);F(s.ModelY);F(s.Yaw);Int(s.Floor);Int(s.Valid?1:0);Int(s.Teleport?1:0);return m.ToArray();
    }
    private sealed class Reader(byte[] bytes)
    {
        private int p;
        public bool AtEnd => p==bytes.Length;
        public string String()
        {
            int start=p; while(p<bytes.Length && bytes[p]!=0) { if(bytes[p]>127)throw new InvalidDataException();p++; }
            if(p==bytes.Length)throw new InvalidDataException();
            var value=Encoding.ASCII.GetString(bytes,start,p-start);p++;
            while(p%4!=0) { if(p>=bytes.Length || bytes[p++]!=0)throw new InvalidDataException(); }return value;
        }
        public int Int() { if(p+4>bytes.Length)throw new InvalidDataException();var v=BinaryPrimitives.ReadInt32BigEndian(bytes.AsSpan(p,4));p+=4;return v; }
        public float Float()=>BitConverter.Int32BitsToSingle(Int());
    }
}

public sealed record TrackingView(Snapshot? Snapshot, bool Visible, string Reason, double AgeMs, long Accepted, long Rejected);

public sealed class TrackerState
{
    private readonly object gate=new();
    private readonly HashSet<string> retired=new(StringComparer.Ordinal);
    private Snapshot? latest;
    private double receivedMs;
    private long accepted,rejected;
    private string rejection="";
    private long? lastWallMs;
    private double lastWallMonotonicMs;
    private bool wallClockJump;
    public const double StaleMs=500;
    public bool Accept(byte[] data, double nowMonotonicMs, long nowUtcMs)
    {
        lock(gate)
        {
            if(lastWallMs is not null && Math.Abs((nowUtcMs-lastWallMs.Value)-(nowMonotonicMs-lastWallMonotonicMs))>1500)wallClockJump=true;
            lastWallMs=nowUtcMs;lastWallMonotonicMs=nowMonotonicMs;
            if(!Osc.TryDecode(data,out var s,out var why))return Reject(why);
            if(s!.UnixMs < nowUtcMs-500 || s.UnixMs > nowUtcMs+1000)return Reject("UTC timestamp outside freshness window");
            if(retired.Contains(s.Session))return Reject("Retired session");
            if(latest is not null)
            {
                if(s.Session==latest.Session && (s.Sequence<=latest.Sequence || (!wallClockJump&&s.UnixMs<latest.UnixMs)))return Reject("Old sequence/timestamp");
                if(s.Session!=latest.Session)
                {
                    // A second active sender must not alternate sessions and hijack the live stream.
                    // New sessions may replace promptly only at sequence 0 with a fresh first-snapshot flag.
                    if(nowMonotonicMs-receivedMs<StaleMs && (s.Sequence!=0 || !s.Teleport))return Reject("Competing session");
                    // Never evict retired IDs: at the cap refuse a new session until receiver restart.
                    if(retired.Count>=1024)return Reject("Session history full; restart receiver");
                    retired.Add(latest.Session);
                }
            }
            latest=s;receivedMs=nowMonotonicMs;accepted++;rejection="";wallClockJump=false;return true;
        }
    }
    private bool Reject(string why) {rejected++;rejection=why;return false;}
    public TrackingView View(double nowMonotonicMs, Func<double,double,bool> contains)
    {
        lock(gate)
        {
            double age=latest is null ? double.PositiveInfinity : Math.Max(0,nowMonotonicMs-receivedMs);
            string reason=latest is null?"Waiting for telemetry":age>=StaleMs?"Stale / disconnected":!latest.Valid?"Invalid tracking":!contains(latest.ModelX,latest.ModelY)?"Outside P02 footprint":latest.Floor==1?"Upstairs / blurred":"Ground / sharp";
            return new(latest,latest is not null&&age<StaleMs&&latest.Valid&&contains(latest.ModelX,latest.ModelY),reason+(rejection.Length>0?"; rejected: "+rejection:""),age,accepted,rejected);
        }
    }
    public static double ClockMs=>Stopwatch.GetTimestamp()*1000d/Stopwatch.Frequency;
}

public sealed class LoopbackReceiver : IDisposable
{
    private readonly CancellationTokenSource stop=new();
    private readonly UdpClient udp;
    public TrackerState State {get;}=new();
    public Task Completion {get;}
    public string? Error {get;private set;}
    public LoopbackReceiver(int port=Osc.Port)
    {
        udp=new UdpClient(AddressFamily.InterNetwork);
        udp.Client.ExclusiveAddressUse=true;
        udp.Client.ReceiveBufferSize=16384;
        try{udp.Client.Bind(new IPEndPoint(IPAddress.Loopback,port));}catch{udp.Dispose();stop.Dispose();throw;}
        Completion=Run();
    }
    private async Task Run()
    {
        try
        {
            while(!stop.IsCancellationRequested)
            {
                var packet=await udp.ReceiveAsync(stop.Token).ConfigureAwait(false);
                if(packet.RemoteEndPoint.Address.Equals(IPAddress.Loopback))
                    State.Accept(packet.Buffer,TrackerState.ClockMs,DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
            }
        }
        catch(Exception ex) when(ex is OperationCanceledException or ObjectDisposedException) { }
        catch(SocketException ex) { Error=ex.Message; }
    }
    public void Dispose() {stop.Cancel();udp.Dispose();}
}
