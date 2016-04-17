Title: Getting Started with Spark: Running a Simple Spark Job in Java
Date: 4-18-2016
Category: Tutorials
Tags: Spark, Java

[Apache Spark](http://spark.apache.org/) has a useful command prompt interface but its true power comes from complex data pipelines that are run non-interactively. Implementing such pipelines can be a daunting task for anyone not familiar with the tools used to build and deploy application software. This article is meant show all the required steps to get a Spark application up and running, including submitting an application to a Spark cluster.

### Goal

The goal is to read in data from a text file, perform some analysis using Spark, and output the data. This will be done both as a standalone (embedded) application and as a Spark job submitted to a Spark master node.

#### Step 1: Environment setup

Before we write our application we need a key tool called an IDE (Integrated Development Environment). I've found [IntelliJ IDEA](https://www.jetbrains.com/idea/) to be an excellent (and free) IDE for Java. I also recommend [PyCharm](https://www.jetbrains.com/pycharm/) for python projects.

1. Download and install [IntelliJ (community edition)](https://www.jetbrains.com/idea/#chooseYourEdition).

#### Step 2: Project setup

1. With IntelliJ ready we need to start a project for our Spark application. Start IntelliJ and select `File` -> `New` -> `Project...`
<img src="/extra/images/spark-getting-started/intellij-new-project.png" title="IntelliJ New Project">
1. Select "Maven" on the left column and a Java SDK from the dropdown at top. If you don't have a Java SDK available you may need to download one from [Oracle](http://www.oracle.com/technetwork/java/javase/downloads/index.html). Hit next.
<img src="/extra/images/spark-getting-started/intellij-new-project-1-maven.png" title="IntelliJ New Project 1 - Maven">
1. Select a GroupId and ArtifactId. Feel free to choose any GroupId, since you won't be publishing this code ([typical conventions](https://maven.apache.org/guides/mini/guide-naming-conventions.html)). Hit next.
<img src="/extra/images/spark-getting-started/intellij-new-project-2-groupid.png" title="IntelliJ New Project 2 - GroupId">
1. Give you project a name and select a directory for IntelliJ to create the project in. Hit finish.
<img src="/extra/images/spark-getting-started/intellij-new-project-3-project-name.png" title="IntelliJ New Project 3 - ProjectName">

#### Step 3: Including Spark

1. After creating a new project IntelliJ will open the project. If you expand the directory tree on the left you'll see the files and folders IntelliJ created. We'll first start with the file named `pom.xml`, which defines our project's dependencies (such as Spark), and how to build the project. All of this is handled by a tool called [Maven](https://maven.apache.org/).
<img src="/extra/images/spark-getting-started/adding-maven-deps.png" title="Adding Maven Dependencies">
1. Open IntelliJ Preferences and make sure "_Import Maven projects automatically_", and "_Automatically download: |x| Sources |x| Documentation_" are checked under Build, Execution, Deployment -> Build Tools -> Maven -> Importing, on the left. This tells IntelliJ to download any dependencies we need.
<img src="/extra/images/spark-getting-started/maven-settings.png" title="IntelliJ Maven Settings">
1. Add the following snippet to `pom.xml`, above the `</project>` tag. See the complete example `pom.xml` file [here](/extra/spark-getting-started/pom.xml).

        :::xml
        <dependencies>
            <dependency>
                <groupId>org.apache.spark</groupId>
                <artifactId>spark-core_2.10</artifactId>
                <version>1.6.1</version>
            </dependency>
        </dependencies>
    This tells Maven that our code depends on Spark and to bundle Spark in our project.

#### Step 4: Writing our application

1. Select the "java" folder on IntelliJ's project menu (on the left), right click and select New -> Java Class. Name this class `SparkAppMain`.
<img src="/extra/images/spark-getting-started/create-class.png" title="Create Main Class">
1. To make sure everything is working, paste the following code into the `SparkAppMain` class and run the class (Run -> Run... in IntelliJ's menu bar).

        :::java
        public class SparkAppMain {
            public static void main(String[] args) {
                System.out.println("Hello World");
            }
        }

    You should see "Hello World" print out below the editor window.

1. Now we'll finally write some Spark code. Our simple application will read from a csv of National Park data. The data is [here](/data/nationalparks.csv), originally from [wikipedia](http://en.wikipedia.org/wiki/List_of_areas_in_the_United_States_National_Park_System#National_parks). To make things simple for this tutorial I copied the file into `/tmp`. In practice such data would likely be stored in [S3](https://aws.amazon.com/s3/) or on a [hadoop cluster](https://en.wikipedia.org/wiki/Apache_Hadoop). Replace the `main()` method in `SparkAppMain` with this code:

        :::java
        public static void main(String[] args) throws IOException {
          SparkConf sparkConf = new SparkConf()
                  .setAppName("Example Spark App")
                  .setMaster("local[*]")  // Delete this line when submitting to a cluster
          JavaSparkContext sparkContext = new JavaSparkContext(sparkConf);
          JavaRDD<String> stringJavaRDD = sparkContext.textFile("/tmp/nationalparks.csv");
          System.out.println("Number of lines in file = " + stringJavaRDD.count());
        }

Run the class again. Amid the Spark log messages you should see "Number of lines in file = 59" in the output. We now have an application running embedded Spark, next we'll submit the application to run on a Spark cluster.

#### Step 5: Submitting to a local cluster

1. To run our application on a cluster we need to remove the "Master" setting from the Spark configuration so our application can use the cluster's master node. Delete the `.setMaster("local[*]")` line from the app. Here's the new `main()` method:

        :::java
        public static void main(String[] args) throws IOException {
          SparkConf sparkConf = new SparkConf()
                  .setAppName("Example Spark App")
          JavaSparkContext sparkContext = new JavaSparkContext(sparkConf);
          JavaRDD<String> stringJavaRDD = sparkContext.textFile("/tmp/nationalparks.csv");
          System.out.println("Number of lines in file = " + stringJavaRDD.count());
        }


1. We'll use Maven to compile our code so we can submit it to the cluster. Run the command `mvn install` from the command line in your project directory (you may need to [install Maven](https://maven.apache.org/install.html)). Alternatively you can run the command from IntelliJ by selecting View -> Tool Windows -> Maven Projects, then right click on install under Lifecycle and select "Run Maven Build". You should see a the compiled jar at `target/spark-getting-started-1.0-SNAPSHOT.jar` in the project directory.
1. Download a packaged Spark build from [this page](http://spark.apache.org/downloads.html), select "Pre-built for Hadoop 2.6 and later" under "package type". Move the unzipped contents (i.e. the `spark-1.6.1-bin-hadoop2.6` directory) to the project directory (`spark-getting-started`).
1. Submit the Job! From the project directory run:

        :::console
        ./spark-1.6.1-bin-hadoop2.6/bin/spark-submit \
          --master local[*] \
          --class SparkAppMain \
          target/spark-getting-started-1.0-SNAPSHOT.jar

    This will start a local spark cluster and submit the application jar to run on it. You will see the result, "Number of lines in file = 59", output among the logging lines.

#### Step 6: Submit the application to a remote cluster

Now we'll bring up a standalone Spark cluster on our machine. Although not technically "remote" it is a persistent cluster and the submission procedure is the same. If you're interested in renting some machines and spinning up a cluster in AWS see [this tutorial](http://blog.insightdatalabs.com/spark-cluster-step-by-step/) from Insight.

1. To start a Spark master node, run this command from the project directory:

        :::console
        ./spark-1.6.1-bin-hadoop2.6/sbin/start-master.sh

1. View your Spark master by going to `localhost:8080` in your browser. Copy the value in the `URL:` field. This is the URL our worker nodes will connect to.
<img src="/extra/images/spark-getting-started/spark-master.png" title="Spark Master Homepage">
1. Start a worker with this command, filling in the URL you just copied for "master-url":

        :::console
        ./spark-1.6.1-bin-hadoop2.6/sbin/start-slave.sh spark://master-url

    You should see the worker show up on the master's homepage upon refresh.
    <img src="/extra/images/spark-getting-started/spark-worker.png" title="Spark Worker Added">

1. We can now submit our job to this cluster, again pasting in the URL for our master:

        :::console
        ./spark-1.6.1-bin-hadoop2.6/bin/spark-submit \
          --master spark://master-url \
          --class SparkAppMain \
          target/spark-getting-started-1.0-SNAPSHOT.jar

    On the master homepage (at `localhost:8080`), you should see the job show up:
    <img src="/extra/images/spark-getting-started/spark-job.png" title="Spark Job">

This tutorial is meant to show a minimal example of a Spark job. I encourage you to experiment with more complex applications and different configurations.  The Spark project provides [documentation on how to do more complex analysis](http://spark.apache.org/docs/latest/programming-guide.html). Below are links to books I've found helpful, it helps support Data Science Bytes when you purchase [anything](http://amzn.to/1SoU4LP) through these links.

<iframe style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//ws-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=US&source=ac&ref=tf_til&ad_type=product_link&tracking_id=datscibyt-20&marketplace=amazon&region=US&placement=1449358624&asins=1449358624&linkId=N7HFWC6K3AWIS5UX&show_border=true&link_opens_in_new_window=true">
</iframe>
<iframe style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//ws-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=US&source=ss&ref=as_ss_li_til&ad_type=product_link&tracking_id=datscibyt-20&marketplace=amazon&region=US&placement=1491901632&asins=1491901632&linkId=3b01281bd287c71483ab28059449740e&show_border=true&link_opens_in_new_window=true"></iframe>
<iframe style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//ws-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=US&source=ac&ref=tf_til&ad_type=product_link&tracking_id=datscibyt-20&marketplace=amazon&region=US&placement=0321356683&asins=0321356683&linkId=KOWAM4ZS5L5MLGC7&show_border=true&link_opens_in_new_window=true">
</iframe>
