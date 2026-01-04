import io.grpc.Server;
import io.grpc.ServerBuilder;
import bot.cline.host.proto.WorkspaceServiceGrpc;

public class MyWorkspaceServer extends WorkspaceServiceGrpc.WorkspaceServiceImplBase {
    // override RPC methods here
}

public class Main {
    public static void main(String[] args) throws Exception {
        Server server = ServerBuilder.forPort(8080)
            .addService(new MyWorkspaceServer())
            .build()
            .start();
        System.out.println("Server started on port 8080");
        server.awaitTermination();
    }
}
