import hudson.cli.CLI;

import java.io.*;
import java.util.ArrayList;
import java.util.List;


//----------------------------------------------------------------------------
public class JenkinsCLIPersist {
    //----------------------------------------------------------------------------
    // Shell tokenizer by Ray Myers:
    // https://gist.github.com/raymyers/8077031
    public static List<String> shellSplit(CharSequence string) {
        List<String> tokens = new ArrayList<String>();
        boolean escaping = false;
        char quoteChar = ' ';
        boolean quoting = false;
        StringBuilder current = new StringBuilder() ;
        for (int i = 0; i<string.length(); i++) {
            char c = string.charAt(i);
            if (escaping) {
                current.append(c);
                escaping = false;
            } else if (c == '\\' && !(quoting && quoteChar == '\'')) {
                escaping = true;
            } else if (quoting && c == quoteChar) {
                quoting = false;
            } else if (!quoting && (c == '\'' || c == '"')) {
                quoting = true;
                quoteChar = c;
            } else if (!quoting && Character.isWhitespace(c)) {
                if (current.length() > 0) {
                    tokens.add(current.toString());
                    current = new StringBuilder();
                }
            } else {
                current.append(c);
            }
        }
        if (current.length() > 0) {
            tokens.add(current.toString());
        }
        return tokens;
    }

    //----------------------------------------------------------------------------
    public static int jenkinsCli(String[] args) {
        try {
            return hudson.cli.CLI._main(args);
        } catch (Exception e) {
            return -1;
        }
    }

    //----------------------------------------------------------------------------
    public static void main(String[] args) {
        InputStreamReader stream = new InputStreamReader(System.in);
        BufferedReader reader = new BufferedReader(stream);

        List<String> command = null;
        String[] jenkins_args = null;

        try {
            while (true) {
                String line = reader.readLine();
                //System.out.println(line);

                if (line == null || line.equals("null"))
                    System.exit(1);

                command = shellSplit(line);
                jenkins_args = new String[command.size()];
                command.toArray(jenkins_args);

                int exitcode = jenkinsCli(jenkins_args);
                System.out.println();
                System.out.println("### EXIT STATUS: " + exitcode);
                System.out.flush();
            }
        } catch (IOException e) {
            System.exit(1);
        }
    }
}
