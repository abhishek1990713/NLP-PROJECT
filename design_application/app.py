import cv2
import os
import numpy as np
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
from sklearn.metrics.pairwise import cosine_similarity
import shutil
import pickle

class ImageSimilarity:
    def __init__(self, cache_file='feature_cache.pkl'):
        self.base_model = VGG16(weights='imagenet')
        self.model = Model(inputs=self.base_model.input, outputs=self.base_model.get_layer('fc1').output)
        self.cache_file = cache_file
        self.feature_cache = {}

    def extract_features(self, image_path):
        if image_path in self.feature_cache:
            # Return cached features if available
            return self.feature_cache[image_path]

        img = cv2.imread(image_path)
        img = cv2.resize(img, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        features = self.model.predict(img).flatten()

        # Cache the features
        self.feature_cache[image_path] = features

        return features

    def load_feature_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                self.feature_cache = pickle.load(f)

    def save_feature_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.feature_cache, f)

    def find_similar_images(self, query_image_path, folder_path, threshold=0.7, output_folder='similar_images'):
        query_features = self.extract_features(query_image_path)
        similarity_scores = []
        for image_file in os.listdir(folder_path):
            image_path = os.path.join(folder_path, image_file)
            image_features = self.extract_features(image_path)
            similarity_score = cosine_similarity([query_features], [image_features])[0][0]
            similarity_scores.append((image_file, similarity_score))

        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for image, score in similarity_scores:
            if score > threshold:
                image_path = os.path.join(folder_path, image)
                output_path = os.path.join(output_folder, image)
                shutil.copyfile(image_path, output_path)
                print(f"Similarity score: {score}, Image: {image} - Saved to {output_path}")

        # Save the feature cache
        self.save_feature_cache()

# Example usage
# similarity_finder = ImageSimilarity()
# similarity_finder.load_feature_cache()
# similarity_finder.find_similar_images('image_test/chair.jpg', 'furniture', threshold=0.7, output_folder='similar_images')
