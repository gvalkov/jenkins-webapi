CLASSPATH = ../../tmp/latest/jenkins-cli.jar

%.class: %.java
	javac -cp $(CLASSPATH) $<

all: JenkinsCLIPersist.class
	cp $< ../$<

jenkins-cli-persist.jar: JenkinsCLIPersist.class
	jar -cvfm $@ Manifest.txt $<

clean:
	-rm -f jenkins-cli-persist.jar JenkinsCLIPersist.class

.PHONY: all clean
