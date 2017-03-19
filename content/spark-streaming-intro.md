Title: Creating a Spark Streaming Application in Java
Date: 4-30-2016
Category: Tutorials
Tags: Spark, Java

[Spark Streaming](http://spark.apache.org/docs/latest/streaming-programming-guide.html) uses the power of Spark on streams of data, often data generated in real time by many producers. A typical use case is analysis on a streaming source of events such as website clicks or ad impressions. In this tutorial I'll create a Spark Streaming application that analyzes fake events streamed from another process. If you're new to running Spark take a look at the [_Getting Started With Spark_]({filename}/spark-getting-started.md) tutorial to get yourself up and running. The code used in this tutorial is [available on github](https://github.com/frankcleary/spark-streaming-intro).

**Note: The code below is written against Spark 1.6 and may need changes to run against Spark 2.0**

### The streaming data source

Spark Streaming can read input from many sources, most are designed to consume the input data and buffer it for consumption by the streaming application ([Apache Kafka](http://kafka.apache.org/) and [Amazon Kinesis](https://aws.amazon.com/kinesis/) fall into this category). For this tutorial we'll feed data to Spark from a TCP socket written to by a process running locally.

Here is the Java code for the data generating server. The server sets up a socket and generates data of the form `"username:event"`, where event could be `"login"` or `"purchase"`. There is also a python version, which you can see [here](https://github.com/frankcleary/spark-streaming-intro/blob/master/python-server/server.py).

    :::java
    import java.io.*; // wildcard import for brevity in tutorial
    import java.net.*;
    import java.util.Random;
    import java.util.concurrent.*;

    public class EventServer {
        private static final Executor SERVER_EXECUTOR = Executors.newSingleThreadExecutor();
        private static final int PORT = 9999;
        private static final String DELIMITER = ":";
        private static final long EVENT_PERIOD_SECONDS = 1;
        private static final Random random = new Random();

        public static void main(String[] args) throws IOException, InterruptedException {
            BlockingQueue<String> eventQueue = new ArrayBlockingQueue<>(100);
            SERVER_EXECUTOR.execute(new SteamingServer(eventQueue));
            while (true) {
                eventQueue.put(generateEvent());
                Thread.sleep(TimeUnit.SECONDS.toMillis(EVENT_PERIOD_SECONDS));
            }
        }

        private static String generateEvent() {
            int userNumber = random.nextInt(10);
            String event = random.nextBoolean() ? "login" : "purchase";
            // In production use a real schema like JSON or protocol buffers
            return String.format("user-%s", userNumber) + DELIMITER + event;
        }

        private static class SteamingServer implements Runnable {
            private final BlockingQueue<String> eventQueue;

            public SteamingServer(BlockingQueue<String> eventQueue) {
                this.eventQueue = eventQueue;
            }

            @Override
            public void run() {
                try (ServerSocket serverSocket = new ServerSocket(PORT);
                     Socket clientSocket = serverSocket.accept();
                     PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
                ) {
                    while (true) {
                        String event = eventQueue.take();
                        System.out.println(String.format("Writing \"%s\" to the socket.", event));
                        out.println(event);
                    }
                } catch (IOException|InterruptedException e) {
                    throw new RuntimeException("Server error", e);
                }
            }
        }
    }

Run this class before any of the streaming programs so they have something to get data from!

### A "hello world" Spark Streaming application

Here is a "hello world" Spark Streaming application. It connects to the server running in `EventServer.java` (above), reads the data as it comes in and prints the data that's been received every 5 seconds.

    :::java
    import org.apache.log4j.*;
    import org.apache.spark.SparkConf;
    import org.apache.spark.streaming.Durations;
    import org.apache.spark.streaming.api.java.*;

    public class VerySimpleStreamingApp {
        private static final String HOST = "localhost";
        private static final int PORT = 9999;

        public static void main(String[] args) {
            // Configure and initialize the SparkStreamingContext
            SparkConf conf = new SparkConf()
                    .setMaster("local[*]")
                    .setAppName("VerySimpleStreamingApp");
            JavaStreamingContext streamingContext =
                    new JavaStreamingContext(conf, Durations.seconds(5));
            Logger.getRootLogger().setLevel(Level.ERROR);

            // Receive streaming data from the source
            JavaReceiverInputDStream<String> lines = streamingContext.socketTextStream(HOST, PORT);
            lines.print();

            // Execute the Spark workflow defined above
            streamingContext.start();
            streamingContext.awaitTermination();
        }
    }

### A more complex Spark Streaming application

Moving on to a more complicated application we'll collect aggregate results from all the data that has come in on the stream so far. For this we need to enable checkpointing, otherwise Spark would need to keep a full history of the stream to recreate data lost due the failure of a Spark worker. With checkpointing Spark can pick up from the last checkpoint.

The Spark application below parses each event into a (userName, eventType) pair, then aggregates all the events over the life of the stream into per-user data. This is done through the [`updateStateByKey()`](http://spark.apache.org/docs/latest/streaming-programming-guide.html#updatestatebykey-operation) method of Sprak Streaming's [PairDStream](https://spark.apache.org/docs/latest/api/java/org/apache/spark/streaming/api/java/JavaPairDStream.html). Here we just print the output, in production calls to [`foreachRDD()`](http://spark.apache.org/docs/latest/streaming-programming-guide.html#output-operations-on-dstreams) would likely persist the data to a database or otherwise do something useful.

    :::java
    import com.google.common.base.Optional;
    import org.apache.log4j.*;
    import org.apache.spark.SparkConf;
    import org.apache.spark.api.java.JavaPairRDD;
    import org.apache.spark.api.java.function.*;
    import org.apache.spark.streaming.*;
    import org.apache.spark.streaming.api.java.*;
    import scala.Tuple2;

    import java.util.*;

    public class EventCollectionStreamingApp {
        private static final String HOST = "localhost";
        private static final int PORT = 9999;
        private static final String CHECKPOINT_DIR = "/tmp";
        private static final Duration BATCH_DURATION = Durations.seconds(5);

        public static void main(String[] args) {
            // Configure and initialize the SparkStreamingContext
            SparkConf conf = new SparkConf()
                    .setMaster("local[*]")
                    .setAppName("EventCollectionStreamingApp");
            JavaStreamingContext streamingContext =
                    new JavaStreamingContext(conf, BATCH_DURATION);
            Logger.getRootLogger().setLevel(Level.ERROR);
            streamingContext.checkpoint(CHECKPOINT_DIR);

            // Receive streaming data from the source
            JavaReceiverInputDStream<String> lines = streamingContext.socketTextStream(HOST, PORT);

            // Map lines of input data (user:event) into (user, event) pairs
            JavaPairDStream<String, String> events = lines.mapToPair(
                    new PairFunction<String, String, String>() {
                        @Override
                        public Tuple2<String, String> call(String rawEvent) throws Exception {
                            String[] strings = rawEvent.split(":");
                            return new Tuple2<>(strings[0], strings[1]);
                        }
                    }
            );

            // Print new events received in this batch
            events.foreachRDD(
                    new Function2<JavaPairRDD<String, String>, Time, Void>() {
                        @Override
                        public Void call(JavaPairRDD<String, String> newEventsRdd, Time time)
                                throws Exception {
                                System.out.println("\n===================================");
                                System.out.println("New Events for " + time + " batch:");
                                for (Tuple2<String, String> tuple : newEventsRdd.collect()) {
                                    System.out.println(tuple._1 + ": " + tuple._2);
                                }
                                return null;
                            }
                        });

            // Combine new events with a running total of events for each user.
            // userTotals holds pairs of (user, map of event to number of occurrences
            // of that event for that user)
            JavaPairDStream<String, Map<String, Long>> userTotals =
                    events.updateStateByKey(
                            new Function2<List<String>, Optional<Map<String, Long>>,
                                    Optional<Map<String, Long>>>() {
                        @Override
                        public Optional<Map<String, Long>> call(List<String> newEvents,
                            Optional<Map<String, Long>> oldEvents) throws Exception {
                            Map<String, Long> updateMap = oldEvents.or(new HashMap<>());
                            for (String event : newEvents) {
                                if (updateMap.containsKey(event)) {
                                    updateMap.put(event, updateMap.get(event) + 1L);
                                } else {
                                    updateMap.put(event, 1L);
                                }
                            }
                            return Optional.of(updateMap);
                        }
                    });

            userTotals.foreachRDD(
                    new Function2<JavaPairRDD<String, Map<String, Long>>, Time, Void>() {
                        @Override
                        public Void call(JavaPairRDD<String, Map<String, Long>> userTotals,
                                         Time time) throws Exception {
                            // Instead of printing this would be a good place to do
                            // something like writing the aggregation to a database
                            System.out.println("");
                            System.out.println("Per user aggregate events at " + time + ":");
                            // Consider rdd.foreach() instead of collectAsMap()
                            for (Map.Entry<String, Map<String, Long>> userData :
                                    userTotals.collectAsMap().entrySet()) {
                                System.out.println(String.format("%s: %s",
                                        userData.getKey(), userData.getValue()));
                            }
                            return null;
                        }
                    });

            streamingContext.start();
            streamingContext.awaitTermination();
        }
    }

### Adding more analysis

If you're interested in aggregating the data across all users, adding the following code would do that:

    :::java
    // siteTotals holds the total number of each event that has occurred across all users.
    JavaPairDStream<String, Long> siteTotals = userTotals.flatMapToPair(
            new PairFlatMapFunction<Tuple2<String, Map<String, Long>>, String, Long>() {
                @Override
                public Iterable<Tuple2<String, Long>> call(Tuple2<String,
                        Map<String, Long>> userEvents) throws Exception {
                    List<Tuple2<String, Long>> eventCounts = new ArrayList<>();
                    for (Map.Entry<String, Long> entry : userEvents._2.entrySet()) {
                        eventCounts.add(new Tuple2<>(entry.getKey(), entry.getValue()));
                    }
                    return eventCounts;
                }
            }
    ).reduceByKey(
            new Function2<Long, Long, Long>() {
                @Override
                public Long call(Long left, Long right) throws Exception {
                    return left + right;
                }
            }
    );
    siteTotals.print();

### Conclusion

The above code will get you starting running a simple Spark Streaming application. The source for this post is [available on github](https://github.com/frankcleary/spark-streaming-intro). See also the [_Getting Started With Spark_]({filename}/spark-getting-started.md) tutorial.

Below are links to books I've found helpful, it helps support Data Science Bytes when you purchase [anything](http://amzn.to/1SoU4LP) through these links.

<iframe style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//ws-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=US&source=ac&ref=tf_til&ad_type=product_link&tracking_id=datscibyt-20&marketplace=amazon&region=US&placement=1449358624&asins=1449358624&linkId=N7HFWC6K3AWIS5UX&show_border=true&link_opens_in_new_window=true">
</iframe>
<iframe style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//ws-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=US&source=ss&ref=as_ss_li_til&ad_type=product_link&tracking_id=datscibyt-20&marketplace=amazon&region=US&placement=1491901632&asins=1491901632&linkId=3b01281bd287c71483ab28059449740e&show_border=true&link_opens_in_new_window=true"></iframe>
<iframe style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//ws-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=US&source=ac&ref=tf_til&ad_type=product_link&tracking_id=datscibyt-20&marketplace=amazon&region=US&placement=0321356683&asins=0321356683&linkId=KOWAM4ZS5L5MLGC7&show_border=true&link_opens_in_new_window=true">
</iframe>
