class RerankerManager:
    def __init__(self):
        """
        Function to initialize Reranker
        """
        self.reranker = CrossEncoder(RERANKER_MODEL)