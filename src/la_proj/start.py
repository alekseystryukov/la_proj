from la_proj.storage import MONGODB_COLLECTION, get_mongodb_collection
import csv


def main():
    with open('/app/la_proj/Nasdaq.csv') as f:
        reader = csv.reader(f)
        symbols = [(row[1].strip(), row[2].strip()) for row in reader][1:11]

    collection = get_mongodb_collection(collection_name=MONGODB_COLLECTION)

    for uid, name in symbols:
        collection.insert_one(
            {
                "_id": uid,
                "name": name,
            }
        )


if __name__ == "__main__":
    main()
