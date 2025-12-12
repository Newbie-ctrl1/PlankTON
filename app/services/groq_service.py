from groq import Groq

class GroqService:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        # List model yang tersedia (diurut dari yang paling recommended)
        self.models = [
            "openai/gpt-oss-120b",
            
        ]
        self.model = self.models[0]  # Default ke model pertama
    
    def get_plant_response(self, user_message, plant_topic="tanaman umum"):
        """
        Get response from Groq AI focused on plant-related topics
        """
        for model in self.models:
            try:
                system_prompt = f"""Anda adalah asisten ahli pertanian dan botani yang berfokus pada {plant_topic}.
Anda memiliki pengetahuan mendalam tentang:
- Identifikasi jenis tanaman
- Perawatan tanaman
- Cara menanam dan budidaya
- Masalah penyakit tanaman
- Nutrisi dan pemupukan
- Teknologi pertanian modern
- Pertanian berkelanjutan

Berikan jawaban yang terperinci, praktis, dan mudah dimengerti dalam Bahasa Indonesia.
Jika ada pertanyaan di luar topik tanaman, tetap coba bantu tetapi ingatkan fokus pada tanaman."""
                
                message = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    model=model,
                    temperature=0.7,
                    max_tokens=2000,
                )
                
                self.model = model  # Update model yang berhasil
                return message.choices[0].message.content
            
            except Exception as e:
                error_msg = str(e)
                if "decommissioned" in error_msg or "not found" in error_msg:
                    print(f"Model {model} tidak tersedia, mencoba model lain...")
                    continue
                else:
                    print(f"Error from Groq API: {e}")
                    raise Exception(f"Gagal mendapatkan respons dari AI: {str(e)}")
        
        # Jika semua model gagal
        raise Exception("Semua model Groq tidak tersedia. Cek API key dan status layanan.")
