public class Main {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            System.err.println("Usage: java Main <test_vector_dir>");
            System.err.println("Runs ConformanceRunner to canonicalize input.json and verify hashes.json");
            System.exit(2);
        }
        ConformanceRunner.run(args[0]);
    }
}
