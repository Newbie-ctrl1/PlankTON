import requests
import base64
import json
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings()

class PlantIdService:
    def __init__(self, api_key):
        """
        Initialize Plant.id API client
        
        Args:
            api_key (str): Your Plant.id API key
        """
        self.api_key = api_key
        self.url = "https://plant.id/api/v3/identification"
        self.headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def encode_image(self, image_path):
        """
        Encode image to base64 string
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            str: Base64 encoded image with data URI prefix
        """
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded}"
    
    def identify_plant(self, image_path, classification_level="all", health="auto", similar_images=True):
        """
        Identify plant from image using Plant.id API v3
        Includes health assessment and disease detection
        
        Args:
            image_path (str): Path to the image file
            classification_level (str): 'all', 'genus', or 'species'
            health (str): 'all', 'auto', 'only', or 'probability'
            similar_images (bool): Include similar images in response
        
        Returns:
            Dictionary with plant identification and health assessment results
        """
        # Check if API key is configured
        if not self.api_key or self.api_key.startswith('your_'):
            raise Exception(
                "Plant.id API key tidak dikonfigurasi. "
                "Silakan set PLANTID_API_KEY di file .env. "
                "Dapatkan API key dari https://plant.id"
            )
        
        try:
            # Encode image
            image_data = self.encode_image(image_path)
            
            # Prepare payload dengan health assessment
            payload = {
                "images": [image_data],
                "similar_images": similar_images,
                "classification_level": classification_level,
                "health": "all"  # Request semua informasi kesehatan
            }
            
            # Send request dengan retry dan error handling lebih baik
            headers_with_ua = self.headers.copy()
            headers_with_ua["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            headers_with_ua["Connection"] = "keep-alive"
            
            # Retry strategy - don't retry on 429 (rate limit)
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            retry_strategy = Retry(
                total=2,
                backoff_factor=2,
                status_forcelist=[500, 502, 503, 504],  # Removed 429
                allowed_methods=["POST", "GET"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            
            session = requests.Session()
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            
            response = session.post(
                self.url,
                headers=headers_with_ua,
                json=payload,
                timeout=90,
                verify=False
            )
            
            # Check for rate limit first
            if response.status_code == 429:
                print("Rate limit exceeded (429)")
                raise Exception(
                    "🚫 Quota API Plant.id habis atau rate limit tercapai. "
                    "Silakan tunggu beberapa saat atau upgrade paket API Anda di https://plant.id"
                )
            
            # Check response
            if response.status_code not in [200, 201]:
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 401:
                    raise Exception("Plant.id API key tidak valid. Periksa kembali PLANTID_API_KEY di .env")
                
                raise Exception(f"Plant.id API error: {response.status_code}")
            
            result = response.json()
            
            # Extract suggestions
            suggestions = self.get_suggestions(result, top_n=1)
            
            if suggestions:
                plant = suggestions[0]
                analysis_result = {
                    'name': plant.get('name', 'Tidak diketahui'),
                    'probability': plant.get('probability', 0),
                    'confidence': plant.get('probability', 0) * 100,
                    'plant_details': plant.get('details', {})
                }
                
                # Extract health assessment if available
                health_info = self.get_health_assessment(result)
                if health_info:
                    analysis_result['health'] = health_info
                
                return analysis_result
            else:
                return {
                    'name': 'Tanaman tidak dikenali',
                    'confidence': 0,
                    'message': 'Tidak dapat mengidentifikasi tanaman dari gambar'
                }
        
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            print(f"Error connecting to Plant.id API: {e}")
            
            # Better error message
            if "429" in error_msg or "too many" in error_msg.lower():
                raise Exception(
                    "🚫 Quota API Plant.id habis atau rate limit tercapai. "
                    "Silakan tunggu beberapa saat atau upgrade paket API Anda di https://plant.id"
                )
            elif "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception("Plant.id API key tidak valid. Periksa kembali PLANTID_API_KEY di .env")
            elif "Connection" in error_msg:
                raise Exception("Gagal terhubung ke Plant.id API. Periksa koneksi internet Anda.")
            else:
                raise Exception(f"Plant.id API error: {error_msg}")
        except Exception as e:
            error_str = str(e)
            print(f"Error in plant identification: {e}")
            # Don't wrap if already a proper error message
            if "Plant.id" in error_str or "Quota" in error_str or "API" in error_str:
                raise
            else:
                raise Exception(f"Gagal menganalisis tanaman: {error_str}")
    
    def get_suggestions(self, result, top_n=5):
        """
        Extract top plant suggestions from API result
        
        Args:
            result (dict): API response
            top_n (int): Number of top suggestions to return
            
        Returns:
            list: List of plant suggestions
        """
        try:
            if "result" in result and "classification" in result["result"]:
                suggestions = result["result"]["classification"]["suggestions"]
                return suggestions[:top_n]
        except (KeyError, TypeError):
            pass
        return []
    
    def get_health_assessment(self, result):
        """
        Extract health assessment and disease information from API result
        
        Args:
            result (dict): API response from Plant.id
            
        Returns:
            dict: Health assessment including diseases, pests, and deficiencies
        """
        health_info = {}
        
        try:
            if "result" not in result:
                return health_info
            
            api_result = result["result"]
            
            # Extract overall health status
            if "is_healthy" in api_result:
                health_status = api_result["is_healthy"]
                if isinstance(health_status, dict):
                    health_info['is_healthy'] = {
                        'status': health_status.get('probability', 0) > 0.5,
                        'probability': health_status.get('probability', 0)
                    }
                else:
                    # If is_healthy is just a boolean
                    health_info['is_healthy'] = {
                        'status': bool(health_status),
                        'probability': 1.0 if health_status else 0.0
                    }
            
            # Extract disease information
            if "disease" in api_result:
                diseases = api_result["disease"]
                health_info['diseases'] = self.parse_disease_info(diseases)
            
            # Extract pest information
            if "pest" in api_result:
                pests = api_result["pest"]
                health_info['pests'] = self.parse_pest_info(pests)
            
            # Extract nutrient deficiency information
            if "nutrient_deficiency" in api_result:
                deficiencies = api_result["nutrient_deficiency"]
                health_info['nutrient_deficiency'] = self.parse_deficiency_info(deficiencies)
            
            return health_info
        
        except Exception as e:
            print(f"Error extracting health assessment: {e}")
            import traceback
            traceback.print_exc()
            return health_info
    
    def parse_disease_info(self, disease_data):
        """
        Parse disease information from API response
        
        Args:
            disease_data (dict): Disease data from API
            
        Returns:
            dict: Parsed disease information
        """
        parsed = {
            'detected': False,
            'confidence': 0,
            'suggestions': []
        }
        
        try:
            if not disease_data or not isinstance(disease_data, dict):
                return parsed
            
            confidence = disease_data.get('probability', 0)
            if isinstance(confidence, (int, float)):
                parsed['detected'] = confidence > 0.3
                parsed['confidence'] = confidence
            
            suggestions = disease_data.get('suggestions', [])
            if isinstance(suggestions, list):
                for suggestion in suggestions[:3]:  # Top 3 diseases
                    if isinstance(suggestion, dict):
                        parsed['suggestions'].append({
                            'name': suggestion.get('name', 'Unknown'),
                            'probability': suggestion.get('probability', 0),
                            'description': suggestion.get('description', ''),
                            'treatment': suggestion.get('treatment', {})
                        })
        except Exception as e:
            print(f"Error parsing disease info: {e}")
        
        return parsed
    
    def parse_pest_info(self, pest_data):
        """
        Parse pest information from API response
        
        Args:
            pest_data (dict): Pest data from API
            
        Returns:
            dict: Parsed pest information
        """
        parsed = {
            'detected': False,
            'confidence': 0,
            'suggestions': []
        }
        
        try:
            if not pest_data or not isinstance(pest_data, dict):
                return parsed
            
            confidence = pest_data.get('probability', 0)
            if isinstance(confidence, (int, float)):
                parsed['detected'] = confidence > 0.3
                parsed['confidence'] = confidence
            
            suggestions = pest_data.get('suggestions', [])
            if isinstance(suggestions, list):
                for suggestion in suggestions[:3]:  # Top 3 pests
                    if isinstance(suggestion, dict):
                        parsed['suggestions'].append({
                            'name': suggestion.get('name', 'Unknown'),
                            'probability': suggestion.get('probability', 0),
                            'description': suggestion.get('description', '')
                        })
        except Exception as e:
            print(f"Error parsing pest info: {e}")
        
        return parsed
    
    def parse_deficiency_info(self, deficiency_data):
        """
        Parse nutrient deficiency information from API response
        
        Args:
            deficiency_data (dict): Deficiency data from API
            
        Returns:
            dict: Parsed nutrient deficiency information
        """
        parsed = {
            'detected': False,
            'confidence': 0,
            'suggestions': []
        }
        
        try:
            if not deficiency_data or not isinstance(deficiency_data, dict):
                return parsed
            
            confidence = deficiency_data.get('probability', 0)
            if isinstance(confidence, (int, float)):
                parsed['detected'] = confidence > 0.3
                parsed['confidence'] = confidence
            
            suggestions = deficiency_data.get('suggestions', [])
            if isinstance(suggestions, list):
                for suggestion in suggestions[:3]:  # Top 3 deficiencies
                    if isinstance(suggestion, dict):
                        parsed['suggestions'].append({
                            'nutrient': suggestion.get('nutrient', 'Unknown'),
                            'probability': suggestion.get('probability', 0),
                            'symptoms': suggestion.get('symptoms', []) if isinstance(suggestion.get('symptoms'), list) else [],
                            'treatment': suggestion.get('treatment', []) if isinstance(suggestion.get('treatment'), list) else []
                        })
        except Exception as e:
            print(f"Error parsing deficiency info: {e}")
        
        return parsed

