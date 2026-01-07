import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Lightweight registry for MX2CLI models.
 *
 * Stores a canonical JSON document at ~/.mx2cli/models.json:
 *
 * {
 *   "default": "cline",
 *   "models": [
 *     { "name": "cline", "location": "/abs/path/to/cline", "description": "Cline baseline model" }
 *   ]
 * }
 */
public final class ModelRegistry {
    private static final String DEFAULT_MODEL_NAME = "cline";
    private static final String DEFAULT_MODEL_DESCRIPTION = "Baseline CLINE model entry; update location to your weights.";
    private static final Path DEFAULT_REGISTRY_PATH =
            Paths.get(System.getProperty("user.home"), ".mx2cli", "models.json");

    private final Path registryPath;
    private final Map<String, ModelRecord> byName = new LinkedHashMap<>();
    private String defaultModelName = DEFAULT_MODEL_NAME;

    public ModelRegistry() throws IOException {
        this(DEFAULT_REGISTRY_PATH);
    }

    public ModelRegistry(Path registryPath) throws IOException {
        this.registryPath = registryPath;
        load();
    }

    public List<ModelRecord> list() {
        return new ArrayList<>(byName.values());
    }

    public ModelRecord require(String name) {
        if (name == null) throw new IllegalArgumentException("model name is required");
        ModelRecord m = byName.get(name.toLowerCase(Locale.ROOT));
        if (m == null) throw new IllegalArgumentException("Unknown model: " + name);
        return m;
    }

    public ModelRecord resolveOrDefault(String name) {
        if (name == null) return getDefaultModel();
        return require(name);
    }

    public ModelRecord getDefaultModel() {
        ModelRecord m = byName.get(defaultModelName);
        if (m != null) return m;
        if (byName.isEmpty()) throw new IllegalStateException("No models registered");
        ModelRecord fallback = byName.values().iterator().next();
        defaultModelName = fallback.name;
        return fallback;
    }

    public void addModel(String name, String location, String description) {
        requireNonEmpty(name, "model name");
        requireNonEmpty(location, "model location");
        String key = name.toLowerCase(Locale.ROOT);
        if (byName.containsKey(key)) {
            throw new IllegalArgumentException("Model already exists: " + name);
        }
        byName.put(key, new ModelRecord(name, location, description));
        if (byName.size() == 1) defaultModelName = key;
    }

    public boolean removeModel(String name) {
        if (name == null) return false;
        String key = name.toLowerCase(Locale.ROOT);
        ModelRecord removed = byName.remove(key);
        if (removed == null) return false;
        if (defaultModelName.equals(key)) {
            defaultModelName = byName.isEmpty() ? DEFAULT_MODEL_NAME : byName.keySet().iterator().next();
        }
        return true;
    }

    public void setDefaultModel(String name) {
        String key = name.toLowerCase(Locale.ROOT);
        if (!byName.containsKey(key)) throw new IllegalArgumentException("Unknown model: " + name);
        defaultModelName = key;
    }

    public void save() throws IOException {
        Files.createDirectories(registryPath.getParent());
        Map<String, Object> root = new LinkedHashMap<>();
        root.put("default", defaultModelName);
        List<Object> models = new ArrayList<>();
        for (ModelRecord m : byName.values()) {
            Map<String, Object> entry = new LinkedHashMap<>();
            entry.put("name", m.name);
            entry.put("location", m.location);
            if (m.description != null && !m.description.isEmpty()) {
                entry.put("description", m.description);
            }
            models.add(entry);
        }
        root.put("models", models);

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        CanonJson.writeCanonical(root, out);
        Files.write(registryPath, out.toByteArray());
    }

    private void load() throws IOException {
        if (!Files.exists(registryPath)) {
            seedDefault();
            return;
        }
        Object parsed = CanonJson.parse(Files.readAllBytes(registryPath));
        if (!(parsed instanceof Map)) throw new IllegalArgumentException("models.json must be an object");
        @SuppressWarnings("unchecked")
        Map<String, Object> root = (Map<String, Object>) parsed;
        Object defaultName = root.get("default");
        if (!(defaultName instanceof String)) throw new IllegalArgumentException("default model must be a string");
        defaultModelName = ((String) defaultName).toLowerCase(Locale.ROOT);

        Object models = root.get("models");
        if (!(models instanceof List)) throw new IllegalArgumentException("models must be an array");
        @SuppressWarnings("unchecked")
        List<Object> entries = (List<Object>) models;
        for (Object o : entries) {
            if (!(o instanceof Map)) throw new IllegalArgumentException("model entry must be object");
            @SuppressWarnings("unchecked")
            Map<String, Object> mm = (Map<String, Object>) o;
            String name = stringField(mm, "name");
            String location = stringField(mm, "location");
            String description = optionalStringField(mm, "description");
            byName.put(name.toLowerCase(Locale.ROOT), new ModelRecord(name, location, description));
        }

        if (!byName.containsKey(defaultModelName) && !byName.isEmpty()) {
            defaultModelName = byName.keySet().iterator().next();
        }
        if (byName.isEmpty()) seedDefault();
    }

    private static void requireNonEmpty(String s, String label) {
        if (s == null || s.trim().isEmpty()) throw new IllegalArgumentException(label + " is required");
    }

    private static String stringField(Map<String, Object> m, String key) {
        Object v = m.get(key);
        if (!(v instanceof String)) throw new IllegalArgumentException("field must be string: " + key);
        String s = ((String) v).trim();
        if (s.isEmpty()) throw new IllegalArgumentException("field is empty: " + key);
        return s;
    }

    private static String optionalStringField(Map<String, Object> m, String key) {
        Object v = m.get(key);
        if (v == null) return "";
        if (!(v instanceof String)) throw new IllegalArgumentException("field must be string: " + key);
        return ((String) v).trim();
    }

    private void seedDefault() {
        String location = Paths.get("cline").toAbsolutePath().normalize().toString();
        byName.put(DEFAULT_MODEL_NAME, new ModelRecord(DEFAULT_MODEL_NAME, location, DEFAULT_MODEL_DESCRIPTION));
        defaultModelName = DEFAULT_MODEL_NAME;
    }

    public static final class ModelRecord {
        public final String name;
        public final String location;
        public final String description;

        ModelRecord(String name, String location, String description) {
            this.name = name;
            this.location = location;
            this.description = description == null ? "" : description;
        }
    }
}
