package similarity;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.IntStream;

import org.bson.Document;

import com.mongodb.client.FindIterable;
import com.mongodb.client.model.Projections;

public class SimilarityCalculator {
	public static void main(String[] args) {
		System.out.println("Querying for TF-IDF vectors...");
		Document query = new Document("tfidfVector", new Document("$exists", 1));
		FindIterable<Document> mongoDocs = MongoProvider.getPublicationsCollection()
						.find(query)
						.projection(Projections.include("tfidfVector"));
		
		Map<Integer, Map<String, Double>> tfidfVectors = new ConcurrentHashMap<>();
		for (Document doc : mongoDocs) {
			int id = doc.getInteger("_id");
			@SuppressWarnings("unchecked")
			Map<String, Double> tfidfVector = (Map<String, Double>) doc.get("tfidfVector");
			
			tfidfVectors.put(id, tfidfVector);
		}
		List<Integer> pmids = new ArrayList<>(tfidfVectors.keySet());
		
		System.out.println("Start similarity calculation...");
		Map<Integer, Map<Integer, Double>> neighbors = new ConcurrentHashMap<>();
		
		AtomicInteger status = new AtomicInteger();
		int threads = 4;
		double threshold = 0.1;
		ForkJoinPool forkJoinPool = new ForkJoinPool(threads);
		try {
			forkJoinPool.submit(() -> IntStream.range(0, pmids.size()).parallel().forEach(i -> {
				if (status.incrementAndGet() % 5000 == 0) {
					System.out.println("STATUS: " + status.get());
				}
				
				int id1 = pmids.get(i);
				Map<String, Double> v1 = tfidfVectors.get(id1);
				
				IntStream.range(i + 1, pmids.size()).forEach(j -> {
					int id2 = pmids.get(j);
					Map<String, Double> v2 = tfidfVectors.get(id2);
					
					double score = dotProduct(v1, v2);
					if (score > threshold) {
						neighbors.computeIfAbsent(id1, id -> new ConcurrentHashMap<>())
										.put(id2, score);
					}
				});
				
			})).get();
		}
		catch (InterruptedException e) {
			e.printStackTrace();
		}
		catch (ExecutionException e) {
			e.printStackTrace();
		}
		System.out.println("STATUS: " + status.get());
		
		System.out.println("Updating MongoDB...");
		neighbors.entrySet().stream().forEach(e -> {
			Document filterDoc = new Document("_id", e.getKey());
			
			List<Integer> pmidNeighbors = new ArrayList<>();
			List<Double> scores = new ArrayList<>();
			e.getValue()
							.entrySet()
							.stream()
							.sorted(Collections.reverseOrder(Map.Entry.comparingByValue()))
							.forEach(sortedEntry -> {
								pmidNeighbors.add(sortedEntry.getKey());
								scores.add(sortedEntry.getValue());
							});
							
			Document updateNeighborsDoc = new Document("$set",
							new Document("neighbors", pmidNeighbors));
			Document updateScoresDoc = new Document("$set", new Document("scores", scores));
			
			MongoProvider.getPublicationsCollection().updateOne(filterDoc, updateNeighborsDoc);
			MongoProvider.getPublicationsCollection().updateOne(filterDoc, updateScoresDoc);
		});
		
		System.out.println("Done.");
	}
	
	/**
	 * Calculates the dot product of two maps. The maps are a sparse representation of two vectors.
	 * 
	 * @param map1
	 * @param map2
	 * @return
	 */
	public static float dotProduct(Map<?, ? extends Number> map1, Map<?, ? extends Number> map2) {
		float sum = 0;
		
		for (Map.Entry<?, ? extends Number> entry : map1.entrySet()) {
			Number valueFromMap2 = map2.get(entry.getKey());
			
			if (valueFromMap2 != null) {
				sum += entry.getValue().floatValue() * valueFromMap2.floatValue();
			}
		}
		
		return sum;
	}
}
