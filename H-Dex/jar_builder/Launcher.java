import java.io.*;
import java.nio.file.*;
import java.io.StringWriter;
import java.io.PrintWriter;

public class Launcher {
    public static void main(String[] args) {
        try {
            // Name of the executable resource
            String exeName = "lifesteel.exe";
            
            // Get input stream from the jar
            InputStream is = Launcher.class.getResourceAsStream("/" + exeName);
            if (is == null) {
                // If not found in JAR (e.g. running from IDE or unpacked), try local file
                File localFile = new File(exeName);
                if (localFile.exists()) {
                    startProcess(localFile.getAbsolutePath(), localFile.getParentFile());
                    return;
                }
                javax.swing.JOptionPane.showMessageDialog(null, "Could not find " + exeName + " inside the JAR or current directory.");
                System.exit(1);
            }

            // Create a temp file
            // We use a temp directory to avoid conflicts
            Path tempDir = Files.createTempDirectory("lifesteel_launcher");
            tempDir.toFile().deleteOnExit(); // Try to cleanup dir
            
            Path tempExe = tempDir.resolve(exeName);
            
            // Copy the exe to the temp file
            Files.copy(is, tempExe, StandardCopyOption.REPLACE_EXISTING);
            is.close();

            // Make executable
            tempExe.toFile().setExecutable(true);
            // tempExe.toFile().deleteOnExit(); // REMOVED: Caused race condition where file was deleted before execution

            // Run it
            startProcess(tempExe.toAbsolutePath().toString(), tempDir.toFile());

        } catch (Throwable e) {
            e.printStackTrace();
            StringWriter sw = new StringWriter();
            PrintWriter pw = new PrintWriter(sw);
            e.printStackTrace(pw);
            javax.swing.JOptionPane.showMessageDialog(null, "Error launching application:\n" + sw.toString());
        }
    }

    private static void startProcess(String path, File workingDir) throws IOException {
        ProcessBuilder pb = new ProcessBuilder(path);
        pb.directory(workingDir); // Set working directory to the temp dir where exe is
        pb.start();
        
        // Give it a moment to start before we exit the launcher
        try { Thread.sleep(2000); } catch (InterruptedException e) {}
        
        System.exit(0);
    }
}
