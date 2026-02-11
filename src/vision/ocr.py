"""
OCR - Text extraction from images using pytesseract and easyocr
"""
from PIL import Image
from typing import List, Dict, Optional, Tuple
import time


class OCREngine:
    """Text extraction from images"""
    
    def __init__(self, engine: str = "tesseract"):
        """
        Initialize OCR engine
        
        Args:
            engine: "tesseract" (fast) or "easyocr" (accurate)
        """
        self.engine = engine
        
        if engine == "tesseract":
            try:
                import pytesseract
                self.tesseract = pytesseract
                print("✓ Tesseract OCR initialized")
            except ImportError:
                print("⚠ pytesseract not available")
                self.tesseract = None
        
        elif engine == "easyocr":
            try:
                import easyocr
                self.reader = easyocr.Reader(['en'], gpu=False)
                print("✓ EasyOCR initialized")
            except ImportError:
                print("⚠ easyocr not available")
                self.reader = None
        
        self.last_text = ""
        self.last_confidence = 0.0
    
    def extract_text(self, img: Image.Image) -> str:
        """
        Extract all text from image
        
        Args:
            img: PIL Image
        
        Returns:
            Extracted text as string
        """
        start_time = time.time()
        
        if self.engine == "tesseract" and self.tesseract:
            text = self._extract_tesseract(img)
        elif self.engine == "easyocr" and self.reader:
            text = self._extract_easyocr(img)
        else:
            print("⚠ No OCR engine available")
            return ""
        
        elapsed = (time.time() - start_time) * 1000
        print(f"✓ OCR completed in {elapsed:.1f}ms ({len(text)} chars)")
        
        self.last_text = text
        return text
    
    def _extract_tesseract(self, img: Image.Image) -> str:
        """Extract text using Tesseract"""
        try:
            text = self.tesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            print(f"⚠ Tesseract error: {e}")
            return ""
    
    def _extract_easyocr(self, img: Image.Image) -> str:
        """Extract text using EasyOCR"""
        try:
            import numpy as np
            
            # Convert PIL to numpy array
            img_array = np.array(img)
            
            # Extract text
            results = self.reader.readtext(img_array)
            
            # Combine all text
            text = " ".join([result[1] for result in results])
            
            # Calculate average confidence
            if results:
                confidences = [result[2] for result in results]
                self.last_confidence = sum(confidences) / len(confidences)
            
            return text.strip()
        except Exception as e:
            print(f"⚠ EasyOCR error: {e}")
            return ""
    
    def extract_text_with_positions(
        self,
        img: Image.Image
    ) -> List[Dict[str, any]]:
        """
        Extract text with bounding box positions
        
        Returns:
            List of dicts with 'text', 'bbox', 'confidence'
        """
        if self.engine == "easyocr" and self.reader:
            try:
                import numpy as np
                img_array = np.array(img)
                results = self.reader.readtext(img_array)
                
                return [
                    {
                        "text": result[1],
                        "bbox": result[0],  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                        "confidence": result[2]
                    }
                    for result in results
                ]
            except Exception as e:
                print(f"⚠ EasyOCR error: {e}")
                return []
        
        elif self.engine == "tesseract" and self.tesseract:
            try:
                # Get detailed data from Tesseract
                data = self.tesseract.image_to_data(
                    img,
                    output_type=self.tesseract.Output.DICT
                )
                
                results = []
                n_boxes = len(data['text'])
                
                for i in range(n_boxes):
                    if int(data['conf'][i]) > 0:  # Only confident detections
                        x, y, w, h = (
                            data['left'][i],
                            data['top'][i],
                            data['width'][i],
                            data['height'][i]
                        )
                        
                        results.append({
                            "text": data['text'][i],
                            "bbox": [[x, y], [x+w, y], [x+w, y+h], [x, y+h]],
                            "confidence": int(data['conf'][i]) / 100.0
                        })
                
                return results
            except Exception as e:
                print(f"⚠ Tesseract error: {e}")
                return []
        
        return []
    
    def find_text(self, img: Image.Image, search_text: str) -> Optional[Tuple[int, int]]:
        """
        Find text on screen and return its center coordinates
        
        Args:
            img: PIL Image
            search_text: Text to find
        
        Returns:
            (x, y) coordinates of text center, or None if not found
        """
        results = self.extract_text_with_positions(img)
        
        search_lower = search_text.lower()
        
        for result in results:
            if search_lower in result['text'].lower():
                # Calculate center of bounding box
                bbox = result['bbox']
                x = sum([point[0] for point in bbox]) / 4
                y = sum([point[1] for point in bbox]) / 4
                
                print(f"✓ Found '{search_text}' at ({int(x)}, {int(y)})")
                return (int(x), int(y))
        
        print(f"⚠ Text '{search_text}' not found")
        return None
    
    def get_confidence(self) -> float:
        """Get confidence of last OCR operation"""
        return self.last_confidence


# Global instance
_ocr_engine = None

def get_ocr_engine(engine: str = "tesseract") -> OCREngine:
    """Get or create global OCR engine"""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine(engine)
    return _ocr_engine


# Convenience functions
def extract_text(img: Image.Image, engine: str = "tesseract") -> str:
    """Extract all text from image"""
    return get_ocr_engine(engine).extract_text(img)


def find_text(
    img: Image.Image,
    search_text: str,
    engine: str = "tesseract"
) -> Optional[Tuple[int, int]]:
    """Find text and return coordinates"""
    return get_ocr_engine(engine).find_text(img, search_text)
