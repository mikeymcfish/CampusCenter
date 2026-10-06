using System.Net;
using System.Net.Sockets;

namespace CampusCenter.Tracker;
public sealed class Simulator : IDisposable
{
    private readonly UdpClient udp=new(AddressFamily.InterNetwork);
    private readonly CancellationTokenSource stop=new();
    public Task Completion {get;}
    public string Session {get;}="sim-"+Guid.NewGuid();
    public Simulator(int port=Osc.Port){Completion=Run(port);}
    private async Task Run(int port)
    {
        using var timer=new PeriodicTimer(TimeSpan.FromMilliseconds(50));int seq=0;
        try
        {
            do
            {
                var s=Frame(Session,seq++,DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
                // 12-14 seconds demonstrates stale hiding by intentionally sending no packets.
                if((s.Sequence*.05)%20 is <12 or >=14)
                    await udp.SendAsync(Osc.Encode(s),new IPEndPoint(IPAddress.Loopback,port),stop.Token).ConfigureAwait(false);
            }while(await timer.WaitForNextTickAsync(stop.Token).ConfigureAwait(false));
        }
        catch(Exception ex)when(ex is OperationCanceledException or ObjectDisposedException){ }
    }
    public static Snapshot Frame(string session,int sequence,long timestamp)
    {
        double t=sequence*.05%20;
        float mx=(float)(120+35*Math.Sin(t*.7)),my=(float)(125+20*Math.Cos(t*.7));
        int floor=t is >=5 and <10?1:0;bool valid=t is <10 or >=12;
        bool teleport=sequence==0||t is >=14 and <14.05;
        if(t>=14){mx=200;my=100;}
        if(t>=17){mx=280;my=210;}
        return new(session,sequence,timestamp,mx*25-4700,230-my*25,mx,my,(float)(t*45),floor,valid,teleport);
    }
    public void Dispose(){stop.Cancel();udp.Dispose();}
}
