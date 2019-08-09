package similarity;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.bson.Document;

import com.mongodb.MongoClient;
import com.mongodb.MongoClientOptions;
import com.mongodb.MongoClientOptions.Builder;
import com.mongodb.MongoCredential;
import com.mongodb.ServerAddress;
import com.mongodb.client.MongoCollection;

public class MongoProvider {
	private static class MongoConfig {
		private String db = "dsca-prod";
		private String host = "localhost";
		private String user = "";
		private String password = "";
		private Integer waitTime;
		private boolean tmp = false;
		
		private static MongoConfig _instance = new MongoConfig();
		
		private MongoConfig() {
			Path path = Paths.get(System.getProperty("user.home"), ".dsca", "app.config");
			try {
				Files.readAllLines(path).forEach(line -> {
					if (!line.startsWith("#") && line.contains("=")) {
						String[] params = line.split("=");
						switch (params[0]) {
							case "mongo.db":
								db = params[1];
								System.out.println(MongoConfig.class.getSimpleName()
												+ " set database: " + db);
								break;
							case "mongo.host":
								host = params[1];
								System.out.println(MongoConfig.class.getSimpleName() + " set host: "
												+ host);
								break;
							case "mongo.user":
								user = params[1];
								System.out.println(MongoConfig.class.getSimpleName() + " set user: "
												+ user);
								break;
							case "mongo.password":
								password = params[1];
								System.out.println(MongoConfig.class.getSimpleName()
												+ " set password");
								break;
							case "mongo.waitTime":
								try {
									waitTime = Integer.valueOf(params[1]);
									System.out.println(MongoConfig.class.getSimpleName()
													+ " set wait time: " + waitTime);
								}
								catch (NumberFormatException e) {
									System.out.println(
													"Incorrect number format for wait time. Using default.");
								}
								
								break;
						}
					}
				});
			}
			catch (Exception e) {
				System.out.println(MongoConfig.class.getSimpleName() + " " + path + " not found.");
			}
		}
		
		private static String getDatabase() {
			return _instance.db;
		}
		
		private static String getHost() {
			return _instance.host;
		}
		
		private static String getUser() {
			return _instance.user;
		}
		
		private static String getPassword() {
			return _instance.password;
		}
		
		private static Integer getWaitTime() {
			return _instance.waitTime;
		}
	}
	
	private static MongoClient MONGO_CLIENT;
	static {
		
		MongoCredential credential = MongoCredential.createCredential(MongoConfig.getUser(),
						MongoConfig.getDatabase(), MongoConfig.getPassword().toCharArray());
		
		Builder builder = MongoClientOptions.builder();
		if (MongoConfig.getWaitTime() != null) {
			builder.maxWaitTime(MongoConfig.getWaitTime());
		}
		MongoClientOptions options = builder.build();
		
		MONGO_CLIENT = new MongoClient(new ServerAddress(MongoConfig.getHost(), 27017), credential,
						options);
	}
	private static String DB = MongoConfig.getDatabase();
	
	public static MongoCollection<Document> getPublicationsCollection() {
		return MONGO_CLIENT.getDatabase(DB).getCollection("publications");
	}
}
