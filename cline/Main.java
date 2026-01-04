import io.grpc.Server;
import io.grpc.netty.shaded.io.grpc.netty.NettyServerBuilder;
import bot.cline.host.proto.WorkspaceServiceGrpc;

public class Main {
    public static void main(String[] args) throws Exception {
        Server server = NettyServerBuilder.forPort(8080)
            .addService(new WorkspaceServiceGrpc.WorkspaceServiceImplBase() {
                // Example override: you’d implement RPC methods here
                // public void getDiagnostics(GetDiagnosticsRequest req,
                //     io.grpc.stub.StreamObserver<GetDiagnosticsResponse> resp) {
                //     // respond with dummy data
                // }
            })
            .build()
            .start();

        System.out.println("WorkspaceService gRPC server started on port 8080");
        server.awaitTermination();
    }
}
