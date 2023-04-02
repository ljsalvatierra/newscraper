from newscraper.pipelines import CloudFirestoreNewsPipeline

if __name__ == '__main__':
    firestore = CloudFirestoreNewsPipeline()
    firestore.remove_all_documents()
