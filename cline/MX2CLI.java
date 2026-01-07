import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * MX2CLI — command-line wrapper around the CLINE Java tools.
 *
 * Features:
 * - Canonicalization/conformance via ConformanceRunner (same as original CLI)
 * - Model registry with built-in CLINE entry
 * - Commands to add/list/remove models and pick which model to run with
 */
public final class MX2CLI {

    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            usage();
            return;
        }
        String cmd = args[0];
        switch (cmd) {
            case "canon":
            case "conformance":
                handleCanon(Arrays.copyOfRange(args, 1, args.length));
                return;
            case "models":
                handleModels(Arrays.copyOfRange(args, 1, args.length));
                return;
            case "help":
            default:
                usage();
        }
    }

    private static void handleCanon(String[] args) throws Exception {
        String modelName = null;
        List<String> positional = new ArrayList<>();
        for (int i = 0; i < args.length; i++) {
            String a = args[i];
            if ("--model".equals(a) && i + 1 < args.length) {
                modelName = args[++i];
            } else {
                positional.add(a);
            }
        }
        if (positional.size() != 1) {
            System.err.println("Usage: java MX2CLI canon <test_vector_dir> [--model <name>]");
            System.exit(2);
        }

        ModelRegistry registry = new ModelRegistry();
        ModelRegistry.ModelRecord model = registry.resolveOrDefault(modelName);

        System.out.println("Running ConformanceRunner with model: " + model.name);
        System.out.println("Model location: " + model.location);
        if (!model.description.isEmpty()) {
            System.out.println("Model note: " + model.description);
        }

        ConformanceRunner.run(positional.get(0));
    }

    private static void handleModels(String[] args) throws Exception {
        if (args.length == 0) {
            modelUsage();
            return;
        }
        String sub = args[0];
        ModelRegistry registry = new ModelRegistry();
        switch (sub) {
            case "list":
                listModels(registry);
                return;
            case "add":
                addModel(registry, args);
                return;
            case "remove":
                removeModel(registry, args);
                return;
            case "default":
                setDefault(registry, args);
                return;
            case "show-default":
                showDefault(registry);
                return;
            default:
                modelUsage();
        }
    }

    private static void listModels(ModelRegistry registry) {
        ModelRegistry.ModelRecord def = registry.getDefaultModel();
        System.out.println("Models (default marked with *):");
        for (ModelRegistry.ModelRecord m : registry.list()) {
            String marker = m.name.equalsIgnoreCase(def.name) ? "*" : " ";
            System.out.println(marker + " " + m.name + " — " + m.location +
                    (m.description.isEmpty() ? "" : " (" + m.description + ")"));
        }
    }

    private static void addModel(ModelRegistry registry, String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage: java MX2CLI models add <name> <location> [description]");
            System.exit(2);
        }
        String name = args[1];
        String location = args[2];
        String description = args.length > 3 ? String.join(" ", Arrays.copyOfRange(args, 3, args.length)) : "";
        registry.addModel(name, location, description);
        registry.save();
        System.out.println("Added model: " + name);
    }

    private static void removeModel(ModelRegistry registry, String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: java MX2CLI models remove <name>");
            System.exit(2);
        }
        String name = args[1];
        if (!registry.removeModel(name)) {
            System.err.println("Model not found: " + name);
            System.exit(1);
        } else {
            registry.save();
            System.out.println("Removed model: " + name);
        }
    }

    private static void setDefault(ModelRegistry registry, String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: java MX2CLI models default <name>");
            System.exit(2);
        }
        registry.setDefaultModel(args[1]);
        registry.save();
        System.out.println("Default model set to: " + args[1]);
    }

    private static void showDefault(ModelRegistry registry) {
        ModelRegistry.ModelRecord def = registry.getDefaultModel();
        System.out.println("Default model: " + def.name);
        System.out.println("Location: " + def.location);
        if (!def.description.isEmpty()) System.out.println("Description: " + def.description);
    }

    private static void usage() {
        System.err.println("MX2CLI — CLINE Java CLI with model registry");
        System.err.println("Usage:");
        System.err.println("  java MX2CLI canon <test_vector_dir> [--model <name>]");
        System.err.println("  java MX2CLI models <list|add|remove|default|show-default> ...");
    }

    private static void modelUsage() {
        System.err.println("Model registry commands:");
        System.err.println("  java MX2CLI models list");
        System.err.println("  java MX2CLI models add <name> <location> [description]");
        System.err.println("  java MX2CLI models remove <name>");
        System.err.println("  java MX2CLI models default <name>");
        System.err.println("  java MX2CLI models show-default");
    }
}
