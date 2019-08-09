package similarity;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.bson.Document;

import com.mongodb.client.FindIterable;
import com.mongodb.client.model.Projections;
import com.opencsv.CSVWriter;

public class SimilarityDataCSV {
	@SuppressWarnings("unchecked")
	public static void main(String[] args) {
		Document query = new Document("neighbors", new Document("$exists", 1));
		FindIterable<Document> docs = MongoProvider.getPublicationsCollection()
						.find(query)
						.projection(Projections.include("neighbors", "scores"));
		
		Map<Integer, Map<Integer, Double>> similarityData = new HashMap<>();
		for (Document doc : docs) {
			int id = doc.getInteger("_id");
			List<Integer> neighborIds = (List<Integer>) doc.get("neighbors");
			List<Double> scores = (List<Double>) doc.get("scores");
			
			Map<Integer, Double> similarity = new HashMap<>();
			for (int i = 0; i < neighborIds.size(); i++) {
				int neighborId = neighborIds.get(i);
				double score = scores.get(i);
				similarity.put(neighborId, score);
			}
			similarityData.put(id, similarity);
		}
		
		Path outputPath = Paths.get(System.getProperty("user.home"), "dissimilarity_data.csv");
		try (CSVWriter writer = setupWriter(outputPath)) {
			List<Integer> pmids = similarityData.keySet().stream().collect(Collectors.toList());
			String[] headers = determineHeaders(pmids);
			writer.writeNext(headers);
			
			int status = 0;
			for (int pmidRow : pmids) {
				if (++status % 1000 == 0) {
					System.out.println("STATUS: " + status);
				}
				
				String[] record = new String[pmids.size() + 1];
				record[0] = String.valueOf(pmidRow);
				
				Map<Integer, Double> similarity = similarityData.get(pmidRow);
				for (int i = 1; i < record.length; i++) {
					int pmidCol = pmids.get(i - 1);
					if (pmidRow == pmidCol) {
						record[i] = String.valueOf(1.0);
					}
					else {
						// double score = similarity.getOrDefault(pmidCol, 0.0);
						double score = 0.0;
						if (similarity.containsKey(pmidCol)) {
							score = similarity.get(pmidCol);
						}
						else {
							Map<Integer, Double> similarityPmidCol = similarityData.get(pmidCol);
							if (similarityPmidCol.containsKey(pmidRow)) {
								score = similarityPmidCol.get(pmidRow);
							}
						}
						score = 1.0 - score;
						if (score > 0.0) {
							record[i] = String.valueOf(Math.round(score * 100.0) / 100.0);
						}
					}
				}
				
				writer.writeNext(record);
			}
			System.out.println("STATUS: " + status);
		}
		catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		System.out.println("Done.");
	}
	
	private static String[] determineHeaders(List<Integer> pmids) {
		String[] headers = new String[pmids.size() + 1];
		headers[0] = "PMID";
		for (int i = 1; i < headers.length; i++) {
			headers[i] = String.valueOf(pmids.get(i - 1));
		}
		
		return headers;
	}
	
	private static CSVWriter setupWriter(Path outputPath) throws IOException {
		BufferedWriter bufferedWriter = Files.newBufferedWriter(outputPath);
		CSVWriter writer = new CSVWriter(bufferedWriter, ',', CSVWriter.NO_QUOTE_CHARACTER,
						CSVWriter.DEFAULT_ESCAPE_CHARACTER, CSVWriter.DEFAULT_LINE_END);
		return writer;
	}
}
