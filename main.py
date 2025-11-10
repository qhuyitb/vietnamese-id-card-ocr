"""
Main entry point để test pipeline
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.main_pipeline import IDCardPipeline
from src.utils.config import Config
import json

def main():
    # Load config
    config = Config()
    
    # Initialize pipeline
    pipeline = IDCardPipeline(config.config)
    
    # Test image
    test_image = "test_images/cccd_sample.jpg"
    
    if not Path(test_image).exists():
        print(f"Test image not found: {test_image}")
        print("Please add a test image to test_images/cccd_sample.jpg")
        return
    
    # Process
    print(f"Processing: {test_image}")
    result = pipeline.process(test_image)
    
    # Print result
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()